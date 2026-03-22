"""
service.roundtable - Roundtable 域服务层。

实现讨论会话的业务逻辑：消息发送、AI 专家回复生成。
纯数据访问已下沉到 repository.roundtable。

Depends: repository.roundtable, util.llm
Consumers: app.roundtable
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


async def send_message(
    db: AsyncSession,
    session_id: str,
    user_id: str,
    content: str,
    generate_ai_reply: bool = True,
) -> dict:
    """发送消息到讨论会话（混合模式）。

    同步保存用户消息，异步生成 AI 专家回复。

    Returns:
        包含 userMessage, aiReplies, status 的响应字典
    """
    # 1. 保存用户消息
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

    # 2. 更新会话状态为 "discussing"
    await update_session_status(db, session_id, "discussing")

    # 3. 生成 AI 专家回复
    ai_replies = []
    if generate_ai_reply:
        context = await get_session_context(db, session_id)
        if context:
            experts = await get_session_experts(db, session_id)
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
    """生成并保存专家回复。"""
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
