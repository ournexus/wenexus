"""
app.roundtable - Roundtable 域应用编排层。

编排 repository 和 service 完成业务用例，处理权限检查和分页封装。

Depends: repository.roundtable, service.roundtable
Consumers: facade.roundtable
"""

from sqlalchemy.ext.asyncio import AsyncSession

from wenexus.repository.roundtable import (
    count_experts,
    count_session_messages,
    count_user_sessions,
    find_experts,
    find_message_by_id,
    find_messages,
    find_session_by_id,
    find_sessions,
    insert_session,
    soft_delete_message,
    topic_exists,
    update_session_fields,
    update_session_status,
)
from wenexus.service.roundtable import send_message as _send_message


async def list_experts(db: AsyncSession, page: int = 1, limit: int = 20) -> dict:
    """获取专家列表（含分页）。"""
    total = await count_experts(db)
    experts = await find_experts(db, page=page, limit=limit)
    return {
        "code": 0,
        "data": {
            "experts": experts,
            "total": total,
            "page": page,
            "limit": limit,
        },
    }


async def list_sessions(
    db: AsyncSession, user_id: str, page: int = 1, limit: int = 20
) -> dict:
    """获取用户的讨论会话列表（含分页）。"""
    total = await count_user_sessions(db, user_id)
    sessions = await find_sessions(db, user_id=user_id, page=page, limit=limit)
    return {
        "code": 0,
        "data": {
            "sessions": sessions,
            "total": total,
            "page": page,
            "limit": limit,
        },
    }


async def get_session_detail(db: AsyncSession, session_id: str, user_id: str) -> dict:
    """获取讨论会话详情（含权限检查）。"""
    session = await find_session_by_id(db, session_id)

    if not session:
        return {"code": 404, "message": "Session not found"}

    if session["userId"] != user_id:
        return {"code": 403, "message": "Forbidden"}

    return {"code": 0, "data": session}


async def list_messages(
    db: AsyncSession, session_id: str, user_id: str, page: int = 1, limit: int = 50
) -> dict:
    """获取讨论会话的消息列表（含权限检查）。"""
    session = await find_session_by_id(db, session_id)
    if not session:
        return {"code": 404, "message": "Session not found"}

    if session["userId"] != user_id:
        return {"code": 403, "message": "Forbidden"}

    total = await count_session_messages(db, session_id)
    messages = await find_messages(db, session_id, page=page, limit=limit)

    return {
        "code": 0,
        "data": {
            "messages": messages,
            "total": total,
            "page": page,
            "limit": limit,
        },
    }


async def create_session(
    db: AsyncSession,
    topic_id: str,
    user_id: str,
    mode: str = "autopilot",
    is_private: bool = False,
    expert_ids: list[str] | None = None,
) -> dict:
    """创建新的讨论会话。"""
    if not await topic_exists(db, topic_id):
        return {"code": 404, "message": "Topic not found"}

    session_id = await insert_session(
        db, topic_id, user_id, mode=mode, is_private=is_private, expert_ids=expert_ids
    )
    session = await find_session_by_id(db, session_id)
    return {"code": 0, "data": session}


async def send_message(
    db: AsyncSession,
    session_id: str,
    user_id: str,
    content: str,
    generate_ai_reply: bool = True,
) -> dict:
    """发送消息到讨论会话（含权限检查）。"""
    session = await find_session_by_id(db, session_id)
    if not session:
        return {"code": 404, "message": "Session not found"}

    if session["userId"] != user_id:
        return {"code": 403, "message": "Forbidden"}

    return await _send_message(
        db,
        session_id=session_id,
        user_id=user_id,
        content=content,
        generate_ai_reply=generate_ai_reply,
    )


async def update_session(
    db: AsyncSession,
    session_id: str,
    user_id: str,
    mode: str | None = None,
    is_private: bool | None = None,
) -> dict:
    """更新讨论会话设置（含权限检查）。"""
    session = await find_session_by_id(db, session_id)
    if not session:
        return {"code": 404, "message": "Session not found"}

    if session["userId"] != user_id:
        return {"code": 403, "message": "Forbidden"}

    await update_session_fields(db, session_id, mode=mode, is_private=is_private)
    updated = await find_session_by_id(db, session_id)
    return {"code": 0, "data": updated}


async def end_session(db: AsyncSession, session_id: str, user_id: str) -> dict:
    """结束讨论会话（含权限检查）。"""
    session = await find_session_by_id(db, session_id)
    if not session:
        return {"code": 404, "message": "Session not found"}

    if session["userId"] != user_id:
        return {"code": 403, "message": "Forbidden"}

    if session["status"] == "completed":
        return {"code": 409, "message": "Session already completed"}

    await update_session_status(db, session_id, "completed")
    updated = await find_session_by_id(db, session_id)
    return {"code": 0, "data": updated}


async def delete_message(
    db: AsyncSession, session_id: str, message_id: str, user_id: str
) -> dict:
    """删除讨论消息（含权限检查：仅消息作者或会话所有者可删）。"""
    session = await find_session_by_id(db, session_id)
    if not session:
        return {"code": 404, "message": "Session not found"}

    message = await find_message_by_id(db, message_id)
    if not message:
        return {"code": 404, "message": "Message not found"}

    if message["sessionId"] != session_id:
        return {"code": 404, "message": "Message not found"}

    if message["status"] == "deleted":
        return {"code": 409, "message": "Message already deleted"}

    is_session_owner = session["userId"] == user_id
    is_message_author = message.get("userId") == user_id
    if not (is_session_owner or is_message_author):
        return {"code": 403, "message": "Forbidden"}

    await soft_delete_message(db, message_id)
    return {"code": 0, "data": {"id": message_id, "status": "deleted"}}
