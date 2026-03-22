"""
repository.roundtable - Roundtable 域数据库操作。

处理: discussion_session, discussion_message, expert 的查询和写入。

Depends: sqlalchemy, uuid
Consumers: service.roundtable, app.roundtable
"""

import json
import uuid
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------------------------------------------------------
# Expert queries
# ---------------------------------------------------------------------------


async def count_experts(db: AsyncSession, status: str = "active") -> int:
    """获取指定状态的专家总数。"""
    result = await db.execute(
        text("SELECT COUNT(*) FROM expert WHERE status = :status"),
        {"status": status},
    )
    return result.scalar() or 0


async def find_experts(
    db: AsyncSession, status: str = "active", page: int = 1, limit: int = 20
) -> list[dict]:
    """分页查询专家列表。

    Returns:
        专家字典列表 (id, name, role, avatar, stance, description, isBuiltin, status, createdAt)
    """
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

    return [
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
        for row in result
    ]


async def get_session_experts(db: AsyncSession, session_id: str) -> list[dict]:
    """获取讨论会话分配的专家列表。

    Returns:
        专家字典列表 (id, name, role, stance, systemPrompt)
    """
    result = await db.execute(
        text(
            """
        SELECT e.id, e.name, e.role, e.stance, e.system_prompt
        FROM expert e
        WHERE e.id = ANY(
            SELECT jsonb_array_elements(ds.expert_ids)::text
            FROM discussion_session ds
            WHERE ds.id = :session_id
        )
    """
        ),
        {"session_id": session_id},
    )

    return [
        {
            "id": row.id,
            "name": row.name,
            "role": row.role,
            "stance": row.stance,
            "systemPrompt": row.system_prompt,
        }
        for row in result
    ]


# ---------------------------------------------------------------------------
# Session queries
# ---------------------------------------------------------------------------


async def count_user_sessions(db: AsyncSession, user_id: str) -> int:
    """获取用户的讨论会话总数。"""
    result = await db.execute(
        text("SELECT COUNT(*) FROM discussion_session WHERE user_id = :user_id"),
        {"user_id": user_id},
    )
    return result.scalar() or 0


async def find_sessions(
    db: AsyncSession, user_id: str, page: int = 1, limit: int = 20
) -> list[dict]:
    """分页查询用户的讨论会话列表。"""
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

    return [
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
        for row in result
    ]


async def find_session_by_id(db: AsyncSession, session_id: str) -> dict | None:
    """根据 ID 查询讨论会话详情（含 topic 信息）。"""
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

    expert_ids = _parse_expert_ids(row.expert_ids)

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


async def get_session_context(db: AsyncSession, session_id: str) -> dict | None:
    """获取会话上下文（含 topic 信息和最近消息）。"""
    session_result = await db.execute(
        text(
            """
        SELECT ds.id, ds.topic_id, ds.status, ds.mode, ds.consensus_level,
               ds.expert_ids, t.title as topic_title, t.description as topic_desc,
               t.type as topic_type
        FROM discussion_session ds
        JOIN topic t ON ds.topic_id = t.id
        WHERE ds.id = :session_id
    """
        ),
        {"session_id": session_id},
    )

    session_row = session_result.first()
    if not session_row:
        return None

    messages_result = await db.execute(
        text(
            """
        SELECT dm.role, dm.content, dm.created_at
        FROM discussion_message dm
        WHERE dm.session_id = :session_id
        ORDER BY dm.created_at DESC
        LIMIT 10
    """
        ),
        {"session_id": session_id},
    )

    messages = [
        {
            "role": row.role,
            "content": row.content,
            "createdAt": row.created_at.isoformat() if row.created_at else None,
        }
        for row in messages_result
    ]

    expert_ids = _parse_expert_ids(session_row.expert_ids)

    return {
        "id": session_row.id,
        "topicId": session_row.topic_id,
        "topicTitle": session_row.topic_title,
        "topicDescription": session_row.topic_desc,
        "topicType": session_row.topic_type,
        "status": session_row.status,
        "mode": session_row.mode,
        "consensusLevel": session_row.consensus_level,
        "expertIds": expert_ids,
        "recentMessages": list(reversed(messages)),
    }


async def topic_exists(db: AsyncSession, topic_id: str) -> bool:
    """检查话题是否存在。"""
    result = await db.execute(
        text("SELECT id FROM topic WHERE id = :topic_id"),
        {"topic_id": topic_id},
    )
    return result.first() is not None


async def insert_session(
    db: AsyncSession,
    topic_id: str,
    user_id: str,
    mode: str = "autopilot",
    is_private: bool = False,
    expert_ids: list[str] | None = None,
) -> str:
    """插入新的讨论会话，返回会话 ID。"""
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
    return session_id


async def update_session_status(
    db: AsyncSession, session_id: str, new_status: str
) -> bool:
    """更新讨论会话状态。"""
    await db.execute(
        text(
            """
        UPDATE discussion_session
        SET status = :status, updated_at = NOW()
        WHERE id = :session_id
    """
        ),
        {"session_id": session_id, "status": new_status},
    )
    await db.commit()
    return True


# ---------------------------------------------------------------------------
# Message queries
# ---------------------------------------------------------------------------


async def count_session_messages(db: AsyncSession, session_id: str) -> int:
    """获取会话消息总数。"""
    result = await db.execute(
        text("SELECT COUNT(*) FROM discussion_message WHERE session_id = :session_id"),
        {"session_id": session_id},
    )
    return result.scalar() or 0


async def find_messages(
    db: AsyncSession, session_id: str, page: int = 1, limit: int = 50
) -> list[dict]:
    """分页查询讨论会话的消息列表。"""
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

    return [
        {
            "id": row.id,
            "role": row.role,
            "content": row.content,
            "status": row.status,
            "expertId": row.expert_id,
            "userId": row.user_id,
            "createdAt": row.created_at.isoformat() if row.created_at else None,
        }
        for row in result
    ]


async def save_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    content: str,
    user_id: str | None = None,
    expert_id: str | None = None,
    citations: dict | None = None,
) -> dict:
    """保存消息到 discussion_message 表。"""
    message_id = str(uuid.uuid4())
    citations_json = json.dumps(citations or [])

    result = await db.execute(
        text(
            """
        INSERT INTO discussion_message (
            id, session_id, user_id, expert_id, role, content,
            citations, status, metadata, created_at, updated_at
        )
        VALUES (
            :id, :session_id, :user_id, :expert_id, :role, :content,
            CAST(:citations AS jsonb), :status, NULL, NOW(), NOW()
        )
        RETURNING id, created_at
    """
        ),
        {
            "id": message_id,
            "session_id": session_id,
            "user_id": user_id,
            "expert_id": expert_id,
            "role": role,
            "content": content,
            "citations": citations_json,
            "status": "active",
        },
    )
    await db.commit()

    row = result.first()
    created_at = row.created_at.isoformat() if row and row.created_at else None

    return {
        "id": message_id,
        "sessionId": session_id,
        "userId": user_id,
        "expertId": expert_id,
        "role": role,
        "content": content,
        "citations": citations or [],
        "status": "active",
        "createdAt": created_at,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _parse_expert_ids(raw: object) -> list[Any]:
    """安全解析 expert_ids JSON 字段。"""
    if not raw:
        return []
    try:
        if isinstance(raw, str):
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, list) else []
        if isinstance(raw, list):
            return raw
        return []
    except (json.JSONDecodeError, TypeError):
        return []
