"""
service.roundtable - Roundtable 域服务层。

实现讨论会话的业务逻辑：消息发送、AI 专家回复生成、Facilitator 合成。
纯数据访问已下沉到 repository.roundtable。

Depends: repository.roundtable, util.llm, agent.graph
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
    在 autopilot 模式下，专家回复后追加 Facilitator 合成消息。

    Returns:
        包含 userMessage, aiReplies, facilitatorMessage, status 的响应字典
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
    ai_replies: list[dict] = []
    context = None
    experts: list[dict] = []
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

    # 4. Facilitator 合成（autopilot 模式 + 有专家回复时）
    facilitator_message = None
    if (
        generate_ai_reply
        and ai_replies
        and context
        and context.get("mode") == "autopilot"
    ):
        facilitator_message = await _generate_facilitator_synthesis(
            db, session_id, context, experts, content, ai_replies
        )

    return {
        "code": 0,
        "data": {
            "userMessage": user_message,
            "aiReplies": ai_replies,
            "facilitatorMessage": facilitator_message,
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


async def _generate_facilitator_synthesis(
    db: AsyncSession,
    session_id: str,
    context: dict,
    experts: list[dict],
    user_message: str,
    expert_replies: list[dict],
) -> dict | None:
    """Invoke LangGraph facilitator agent and save synthesis message."""
    try:
        from wenexus.agent.graph import invoke_facilitator

        response_content = await invoke_facilitator(
            topic_title=context.get("topicTitle", "Discussion"),
            topic_description=context.get("topicDescription"),
            experts=experts,
            user_message=user_message,
            expert_replies=expert_replies,
            recent_messages=context.get("recentMessages"),
        )

        if response_content:
            facilitator_msg = await save_message(
                db,
                session_id=session_id,
                role="host",
                content=response_content,
            )
            await logger.ainfo(
                "facilitator_response_saved",
                session_id=session_id,
                message_id=facilitator_msg["id"],
            )
            return facilitator_msg

        await logger.awarn("facilitator_response_empty", session_id=session_id)

    except Exception as e:
        await logger.aerror(
            "facilitator_response_error",
            session_id=session_id,
            error=str(e),
        )

    return None
