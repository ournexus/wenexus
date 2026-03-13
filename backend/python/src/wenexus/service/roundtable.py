"""
service.roundtable - Roundtable 域服务层。

实现讨论会话、专家、消息的业务逻辑。

Depends: repository.roundtable, util.schema, util.llm
Consumers: facade.roundtable
"""

import asyncio

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from wenexus.repository.roundtable import (
    get_session_context,
    get_session_experts,
    save_message,
    update_session_status,
)
from wenexus.util.llm import generate_expert_response

logger = structlog.get_logger()


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
        SELECT dm.id, dm.role, dm.content, dm.status, dm.created_at,
               dm.expert_id, dm.user_id
        FROM discussion_message dm
        WHERE dm.session_id = :session_id
        ORDER BY dm.created_at ASC
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
                "status": row.status,
                "expertId": row.expert_id,
                "userId": row.user_id,
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


async def send_message(
    db: AsyncSession,
    session_id: str,
    user_id: str,
    content: str,
    generate_ai_reply: bool = True,
) -> dict:
    """Send a message to a discussion session (hybrid mode).

    Synchronously saves user message, asynchronously generates AI expert replies.

    Args:
        db: Database session
        session_id: Discussion session ID
        user_id: Current user ID
        content: Message content
        generate_ai_reply: Whether to generate AI expert replies (async)

    Returns:
        Dict with:
            - userMessage: Saved user message dict
            - aiReplies: List of expert response dicts (may be incomplete if async)
            - status: "success" or "partial" (if AI generation still pending)
    """
    # 1. Sync: Save user message
    user_message = await save_message(
        db,
        session_id=session_id,
        role="participant",
        content=content,
        user_id=user_id,
    )

    await logger.ainfo(
        "user_message_saved",
        session_id=session_id,
        user_id=user_id,
        message_id=user_message["id"],
    )

    # 2. Update session status to "discussing"
    await update_session_status(db, session_id, "discussing")

    # 3. Async: Generate AI expert replies (fire and forget for hybrid mode)
    ai_replies = []
    if generate_ai_reply:
        # Get session context and experts
        context = await get_session_context(db, session_id)
        if context:
            experts = await get_session_experts(db, session_id)

            # Generate responses from all assigned experts concurrently
            if experts:
                tasks = [
                    _generate_and_save_expert_response(
                        db, session_id, expert, context, content
                    )
                    for expert in experts
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, dict):
                        ai_replies.append(result)
                    elif isinstance(result, Exception):
                        await logger.aerror(
                            "expert_response_error",
                            session_id=session_id,
                            error=str(result),
                        )

    return {
        "code": 0,
        "data": {
            "userMessage": user_message,
            "aiReplies": ai_replies,
            "status": "success" if generate_ai_reply else "pending",
            "sessionId": session_id,
        },
    }


async def _generate_and_save_expert_response(
    db: AsyncSession, session_id: str, expert: dict, context: dict, user_message: str
) -> dict | None:
    """Helper: Generate and save expert response.

    Args:
        db: Database session
        session_id: Discussion session ID
        expert: Expert dict with id, name, role, stance, systemPrompt
        context: Session context
        user_message: The user message to respond to

    Returns:
        Saved expert message dict or None if generation failed
    """
    try:
        response_content = await generate_expert_response(
            expert_name=expert["name"],
            expert_role=expert["role"],
            expert_stance=expert["stance"],
            system_prompt=expert.get("systemPrompt"),
            session_context=context,
            user_message=user_message,
        )

        if response_content:
            expert_message = await save_message(
                db,
                session_id=session_id,
                role="expert",
                content=response_content,
                expert_id=expert["id"],
            )
            await logger.ainfo(
                "expert_response_saved",
                session_id=session_id,
                expert_id=expert["id"],
                message_id=expert_message["id"],
            )
            return expert_message
        else:
            await logger.awarn(
                "expert_response_generation_failed",
                session_id=session_id,
                expert_id=expert["id"],
            )
            return None

    except Exception as e:
        await logger.aerror(
            "expert_response_save_error",
            session_id=session_id,
            expert_id=expert["id"],
            error=str(e),
        )
        return None
