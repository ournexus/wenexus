"""
service.roundtable - Roundtable 域服务层。

实现讨论会话、专家、消息的业务逻辑。

Depends: repository.roundtable, util.schema
Consumers: facade.roundtable
"""

from sqlalchemy.ext.asyncio import AsyncSession


async def get_experts(
    db: AsyncSession, status: str = "active", page: int = 1, limit: int = 20
) -> list[dict]:
    """获取专家列表。

    Args:
        db: 数据库 session
        status: 专家状态 (默认: active)
        page: 分页页码
        limit: 每页数量

    Returns:
        专家列表
    """
    from sqlalchemy import text

    offset = (page - 1) * limit

    result = await db.execute(
        text(
            """
        SELECT id, name, role, avatar, stance, description,
               is_builtin, status, created_at
        FROM expert
        WHERE status = :status
        ORDER BY is_builtin DESC, created_at DESC
        LIMIT :limit OFFSET :offset
    """
        ),
        {"status": status, "limit": limit, "offset": offset},
    )

    experts = []
    for row in result:
        experts.append(
            {
                "id": row.id,
                "name": row.name,
                "role": row.role,
                "avatar": row.avatar,
                "stance": row.stance,
                "description": row.description,
                "isBuiltin": row.is_builtin,
                "status": row.status,
                "createdAt": row.created_at.isoformat() if row.created_at else None,
            }
        )

    return experts


async def get_sessions(
    db: AsyncSession, user_id: str, page: int = 1, limit: int = 20
) -> list[dict]:
    """获取用户的讨论会话列表。

    Args:
        db: 数据库 session
        user_id: 用户 ID
        page: 分页页码
        limit: 每页数量

    Returns:
        讨论会话列表
    """
    from sqlalchemy import text

    offset = (page - 1) * limit

    result = await db.execute(
        text(
            """
        SELECT ds.id, ds.topic_id, ds.status, ds.mode, ds.consensus_level,
               ds.is_private, ds.created_at, ds.updated_at,
               t.title as topic_title
        FROM discussion_session ds
        JOIN topic t ON ds.topic_id = t.id
        WHERE ds.user_id = :user_id
        ORDER BY ds.updated_at DESC
        LIMIT :limit OFFSET :offset
    """
        ),
        {"user_id": user_id, "limit": limit, "offset": offset},
    )

    sessions = []
    for row in result:
        sessions.append(
            {
                "id": row.id,
                "topicId": row.topic_id,
                "topicTitle": row.topic_title,
                "status": row.status,
                "mode": row.mode,
                "consensusLevel": row.consensus_level,
                "isPrivate": row.is_private,
                "createdAt": row.created_at.isoformat() if row.created_at else None,
                "updatedAt": row.updated_at.isoformat() if row.updated_at else None,
            }
        )

    return sessions


async def get_session_detail(db: AsyncSession, session_id: str) -> dict | None:
    """获取讨论会话详情。

    Args:
        db: 数据库 session
        session_id: 会话 ID

    Returns:
        会话详情或 None
    """
    import json

    from sqlalchemy import text

    result = await db.execute(
        text(
            """
        SELECT ds.id, ds.topic_id, ds.user_id, ds.status, ds.mode,
               ds.consensus_level, ds.is_private, ds.expert_ids,
               ds.created_at, ds.updated_at,
               t.title as topic_title
        FROM discussion_session ds
        JOIN topic t ON ds.topic_id = t.id
        WHERE ds.id = :session_id
    """
        ),
        {"session_id": session_id},
    )

    row = result.first()
    if not row:
        return None

    # Parse expert_ids JSON if it exists
    expert_ids = []
    if row.expert_ids:
        try:
            if isinstance(row.expert_ids, str):
                expert_ids = json.loads(row.expert_ids)
            elif isinstance(row.expert_ids, list):
                expert_ids = row.expert_ids
            else:
                expert_ids = row.expert_ids or []
        except (json.JSONDecodeError, TypeError):
            expert_ids = []

    return {
        "id": row.id,
        "topicId": row.topic_id,
        "userId": row.user_id,
        "topicTitle": row.topic_title,
        "status": row.status,
        "mode": row.mode,
        "consensusLevel": row.consensus_level,
        "isPrivate": row.is_private,
        "expertIds": expert_ids,
        "createdAt": row.created_at.isoformat() if row.created_at else None,
        "updatedAt": row.updated_at.isoformat() if row.updated_at else None,
    }


async def get_session_messages(
    db: AsyncSession, session_id: str, page: int = 1, limit: int = 50
) -> list[dict]:
    """获取讨论会话的消息列表。

    Args:
        db: 数据库 session
        session_id: 会话 ID
        page: 分页页码
        limit: 每页数量

    Returns:
        消息列表
    """
    from sqlalchemy import text

    offset = (page - 1) * limit

    result = await db.execute(
        text(
            """
        SELECT cm.id, cm.role, cm.content, cm.model, cm.provider,
               cm.status, cm.created_at
        FROM chat_message cm
        JOIN chat c ON cm.chat_id = c.id
        WHERE c.id IN (
            SELECT ds.id FROM discussion_session ds WHERE ds.id = :session_id
        )
        ORDER BY cm.created_at ASC
        LIMIT :limit OFFSET :offset
    """
        ),
        {"session_id": session_id, "limit": limit, "offset": offset},
    )

    messages = []
    for row in result:
        messages.append(
            {
                "id": row.id,
                "role": row.role,
                "content": row.content,
                "model": row.model,
                "provider": row.provider,
                "status": row.status,
                "createdAt": row.created_at.isoformat() if row.created_at else None,
            }
        )

    return messages


async def create_session(
    db: AsyncSession,
    topic_id: str,
    user_id: str,
    mode: str = "autopilot",
    is_private: bool = False,
    expert_ids: list[str] | None = None,
) -> dict | None:
    """创建新的讨论会话。

    Args:
        db: 数据库 session
        topic_id: 话题 ID
        user_id: 用户 ID
        mode: 会话模式 (autopilot, host, participant)
        is_private: 是否私密
        expert_ids: 专家 ID 列表

    Returns:
        新创建的会话或 None (如果验证失败)
    """
    import json
    import uuid

    from sqlalchemy import text

    # 1. 验证 topic 存在
    topic_result = await db.execute(
        text("SELECT id FROM topic WHERE id = :topic_id"),
        {"topic_id": topic_id},
    )
    if not topic_result.first():
        return None

    # 2. 创建讨论会话
    session_id = str(uuid.uuid4())
    expert_ids_json = json.dumps(expert_ids or [])

    await db.execute(
        text(
            """
        INSERT INTO discussion_session (
            id, topic_id, user_id, status, mode, consensus_level,
            is_private, expert_ids, created_at, updated_at
        )
        VALUES (
            :id, :topic_id, :user_id, :status, :mode, :consensus_level,
            :is_private, CAST(:expert_ids AS jsonb), NOW(), NOW()
        )
    """
        ),
        {
            "id": session_id,
            "topic_id": topic_id,
            "user_id": user_id,
            "status": "initializing",
            "mode": mode,
            "consensus_level": 0,
            "is_private": is_private,
            "expert_ids": expert_ids_json,
        },
    )
    await db.commit()

    # 3. 获取新创建的会话详情
    return await get_session_detail(db, session_id)
