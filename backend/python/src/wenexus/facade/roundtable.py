"""
facade.roundtable - Roundtable 域 API 端点。

薄 HTTP 适配层：解析请求参数，委托 app 层处理，返回响应。

Depends: fastapi, app.roundtable, repository.roundtable (仅 find_session_by_id 用于 WebSocket)
Consumers: main (router inclusion)
"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from wenexus.app.roundtable import (
    create_session,
    get_session_detail,
    list_experts,
    list_messages,
    list_sessions,
    send_message,
)
from wenexus.facade.deps import get_current_user, raise_if_error
from wenexus.repository.db import get_db
from wenexus.repository.roundtable import find_session_by_id
from wenexus.util.schema import UserInfo
from wenexus.util.websocket import ws_manager

router = APIRouter(prefix="/roundtable", tags=["roundtable"])


class SendMessageRequest(BaseModel):
    """Request body for sending a message to a discussion session."""

    content: str
    generate_ai_reply: bool = True


class CreateSessionRequest(BaseModel):
    """Request body for creating a new discussion session."""

    topic_id: str
    mode: str = "autopilot"
    is_private: bool = False
    expert_ids: list[str] | None = None


@router.get("/experts")
async def list_experts_endpoint(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict:
    """获取专家列表。"""
    return await list_experts(db, page=page, limit=limit)


@router.get("/sessions")
async def list_sessions_endpoint(
    page: int = 1,
    limit: int = 20,
    user: UserInfo = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict:
    """获取用户的讨论会话列表。"""
    return await list_sessions(db, user_id=user.id, page=page, limit=limit)


@router.get("/sessions/{session_id}")
async def get_session_endpoint(
    session_id: str,
    user: UserInfo = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict:
    """获取讨论会话详情。"""
    result = await get_session_detail(db, session_id=session_id, user_id=user.id)
    return raise_if_error(result)


@router.get("/sessions/{session_id}/messages")
async def get_messages_endpoint(
    session_id: str,
    page: int = 1,
    limit: int = 50,
    user: UserInfo = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict:
    """获取讨论会话的消息列表。"""
    result = await list_messages(
        db, session_id=session_id, user_id=user.id, page=page, limit=limit
    )
    return raise_if_error(result)


@router.post("/sessions")
async def create_session_endpoint(
    request: CreateSessionRequest,
    user: UserInfo = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict:
    """创建新的讨论会话。"""
    result = await create_session(
        db,
        topic_id=request.topic_id,
        user_id=user.id,
        mode=request.mode,
        is_private=request.is_private,
        expert_ids=request.expert_ids,
    )
    return raise_if_error(result)


@router.post("/sessions/{session_id}/messages")
async def send_message_endpoint(
    session_id: str,
    request: SendMessageRequest,
    user: UserInfo = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict:
    """发送消息到讨论会话。"""
    result = await send_message(
        db,
        session_id=session_id,
        user_id=user.id,
        content=request.content,
        generate_ai_reply=request.generate_ai_reply,
    )
    result = raise_if_error(result)

    # 广播新消息到 WebSocket 客户端
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
    user: UserInfo = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> None:
    """WebSocket 端点：讨论会话实时更新。"""
    session = await find_session_by_id(db, session_id)
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return

    if session["userId"] != user.id:
        await websocket.close(code=4003, reason="Forbidden")
        return

    await ws_manager.connect(session_id, websocket)

    await websocket.send_json(
        {
            "type": "connected",
            "sessionId": session_id,
            "message": "Connected to discussion session",
        }
    )

    try:
        while True:
            data = await websocket.receive_json()
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
