"""
util.llm - LLM provider integration (OpenRouter).

Handles: API calls to OpenRouter for generating expert responses.

Depends: httpx, config
Consumers: service.roundtable
"""

import httpx
import structlog

from wenexus.config import settings

logger = structlog.get_logger()


async def generate_expert_response(
    expert_name: str,
    expert_role: str,
    expert_stance: str,
    system_prompt: str | None,
    session_context: dict,
    user_message: str,
    model: str = "openrouter/auto",
) -> str | None:
    """Generate expert response using OpenRouter API.

    Args:
        expert_name: Expert name
        expert_role: Expert role (economist, technologist, etc.)
        expert_stance: Expert stance (supportive, critical, neutral, analytical)
        system_prompt: Custom system prompt for the expert
        session_context: Session context including topic, messages
        user_message: The user message to respond to
        model: Model to use (default: openrouter/auto for cost optimization)

    Returns:
        Generated response text or None if error
    """
    if not settings.openrouter_api_key:
        await logger.awarn("openrouter_api_key not configured")
        return None

    # Build system prompt
    if not system_prompt:
        system_prompt = f"""You are a {expert_role} expert with a {expert_stance} stance.
Your name is {expert_name}. Provide thoughtful, balanced responses that contribute to the discussion.
Consider the context of the topic: {session_context.get("topicTitle", "General Discussion")}
Focus on clarity, evidence-based reasoning, and constructive dialogue."""

    # Build conversation context from recent messages
    messages = []
    for msg in session_context.get("recentMessages", [])[-5:]:  # Last 5 messages
        messages.append(
            {
                "role": "user"
                if msg["role"] in ["user", "host", "participant"]
                else "assistant",
                "content": msg["content"],
            }
        )

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.openrouter_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "HTTP-Referer": settings.frontend_url,
                    "X-Title": "WeNexus",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        *messages,
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000,
                },
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("choices") and len(data["choices"]) > 0:
                    content: str = data["choices"][0]["message"]["content"]
                    return content
            else:
                await logger.aerror(
                    "openrouter_api_error",
                    status=response.status_code,
                    body=response.text,
                )
                return None

    except httpx.HTTPError as e:
        await logger.aerror("openrouter_http_error", error=str(e))
        return None
    except Exception as e:
        await logger.aerror("openrouter_unexpected_error", error=str(e))
        return None

    return None
