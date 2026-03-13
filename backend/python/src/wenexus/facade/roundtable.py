"""
facade.roundtable - Roundtable 域 API 端点。

Depends: fastapi, service.roundtable, repository.db
Consumers: main (router inclusion)
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from wenexus.facade.deps import get_current_user
from wenexus.repository.db import get_db
from wenexus.service.roundtable import (
    create_session,
    get_experts,
    get_session_detail,
    get_session_messages,
    get_sessions,
    send_message,
)
from wenexus.util.schema import UserInfo
from wenexus.util.websocket import ws_manager

router = APIRouter(prefix="/roundtable", tags=["roundtable"])


class SendMessageRequest(BaseModel):
    """Request body for sending a message to a discussion session."""

    content: str
    generate_ai_reply: bool = True


@router.get("/experts")
async def list_experts(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """获取专家列表。

    Args:
        page: 分页页码，从 1 开始
        limit: 每页数量，默认 20
        db: 数据库 session

    Returns:
        {
            "code": 0,
            "data": {
                "experts": [...],
                "total": 100,
                "page": 1,
                "limit": 20
            }
        }
    """
    # 获取符合条件的总记录数
    total_result = await db.execute(
        text("SELECT COUNT(*) as count FROM expert WHERE status = 'active'")
    )
    total = total_result.scalar() or 0

    experts = await get_experts(db, page=page, limit=limit)

    return {
        "code": 0,
        "data": {
            "experts": experts,
            "total": total,
            "page": page,
            "limit": limit,
        },
    }


@router.get("/sessions")
async def list_sessions(
    page: int = 1,
    limit: int = 20,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """获取用户的讨论会话列表。

    Args:
        page: 分页页码，从 1 开始
        limit: 每页数量，默认 20
        user: 当前用户
        db: 数据库 session

    Returns:
        {
            "code": 0,
            "data": {
                "sessions": [...],
                "total": 10,
                "page": 1,
                "limit": 20
            }
        }
    """
    # 获取符合条件的总记录数
    total_result = await db.execute(
        text(
            "SELECT COUNT(*) as count FROM discussion_session WHERE user_id = :user_id"
        ),
        {"user_id": user.id},
    )
    total = total_result.scalar() or 0

    sessions = await get_sessions(db, user_id=user.id, page=page, limit=limit)

    return {
        "code": 0,
        "data": {
            "sessions": sessions,
            "total": total,
            "page": page,
            "limit": limit,
        },
    }


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """获取讨论会话详情。

    Args:
        session_id: 会话 ID
        user: 当前用户
        db: 数据库 session

    Returns:
        {
            "code": 0,
            "data": {
                "id": "...",
                "topicId": "...",
                "status": "...",
                ...
            }
        }
    """
    session = await get_session_detail(db, session_id)

    if not session:
        return {
            "code": 404,
            "message": "Session not found",
        }

    # 验证用户权限
    if session["userId"] != user.id:
        return {
            "code": 403,
            "message": "Forbidden",
        }

    return {
        "code": 0,
        "data": session,
    }


@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: str,
    page: int = 1,
    limit: int = 50,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """获取讨论会话的消息列表。

    Args:
        session_id: 会话 ID
        page: 分页页码
        limit: 每页数量
        user: 当前用户
        db: 数据库 session

    Returns:
        {
            "code": 0,
            "data": {
                "messages": [...],
                "total": 100,
                "page": 1,
                "limit": 50
            }
        }
    """
    # 先验证用户有权访问此会话
    session = await get_session_detail(db, session_id)
    if not session:
        return {
            "code": 404,
            "message": "Session not found",
        }

    if session["userId"] != user.id:
        return {
            "code": 403,
            "message": "Forbidden",
        }

    # 获取符合条件的总记录数
    total_result = await db.execute(
        text(
            "SELECT COUNT(*) as count FROM discussion_message WHERE session_id = :session_id"
        ),
        {"session_id": session_id},
    )
    total = total_result.scalar() or 0

    messages = await get_session_messages(db, session_id, page=page, limit=limit)

    return {
        "code": 0,
        "data": {
            "messages": messages,
            "total": total,
            "page": page,
            "limit": limit,
        },
    }


@router.post("/sessions")
async def create_session_endpoint(
    topic_id: str,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """创建新的讨论会话。

    Args:
        topic_id: 话题 ID
        user: 当前用户
        db: 数据库 session

    Returns:
        {
            "code": 0,
            "data": {
                "id": "...",
                "topicId": "...",
                ...
            }
        }
    """
    session = await create_session(db, topic_id, user.id)

    if not session:
        return {
            "code": 404,
            "message": "Topic not found",
        }

    return {
        "code": 0,
        "data": session,
    }


@router.post("/sessions/{session_id}/messages")
async def send_message_endpoint(
    session_id: str,
    request: SendMessageRequest,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Send a message to a discussion session.

    Hybrid mode:
    - Synchronously saves user message
    - Asynchronously generates expert AI replies

    Args:
        session_id: Discussion session ID
        request: SendMessageRequest with content and generate_ai_reply flag
        user: Current user
        db: Database session

    Returns:
        {
            "code": 0,
            "data": {
                "userMessage": {...},
                "aiReplies": [...],
                "status": "success" or "pending",
                "sessionId": "..."
            }
        }
    """
    # Verify user owns this session
    session = await get_session_detail(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["userId"] != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Send message (hybrid mode)
    result = await send_message(
        db,
        session_id=session_id,
        user_id=user.id,
        content=request.content,
        generate_ai_reply=request.generate_ai_reply,
    )

    # Broadcast new message to WebSocket clients
    if result.get("data"):
        await ws_manager.broadcast(
            session_id,
            {
                "type": "new_message",
                "message": result["data"]["userMessage"],
            },
        )

    return result


@router.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(
    session_id: str,
    websocket: WebSocket,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """WebSocket endpoint for real-time session updates.

    Broadcasts new messages and session state changes to connected clients.

    Args:
        session_id: Discussion session ID
        websocket: WebSocket connection
        user: Current user
        db: Database session
    """
    # Verify user owns this session
    session = await get_session_detail(db, session_id)
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return

    if session["userId"] != user.id:
        await websocket.close(code=4003, reason="Forbidden")
        return

    # Accept connection
    await ws_manager.connect(session_id, websocket)

    # Send connection confirmation
    await websocket.send_json(
        {
            "type": "connected",
            "sessionId": session_id,
            "message": "Connected to discussion session",
        }
    )

    try:
        # Keep connection alive and handle incoming messages
        while True:
            # Wait for incoming message (or connection close)
            data = await websocket.receive_json()

            # Echo back or process incoming messages if needed
            # For now, just acknowledge
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        ws_manager.disconnect(session_id, websocket)
    except Exception as e:
        import structlog

        logger = structlog.get_logger()
        await logger.aerror(
            "websocket_error",
            session_id=session_id,
            error=str(e),
        )
        ws_manager.disconnect(session_id, websocket)
