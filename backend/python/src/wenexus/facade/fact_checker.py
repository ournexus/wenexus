"""Fact Checker API Facade.

Depends: fastapi, service.agent.fact_checker, model.agent
Consumers: main (router inclusion)
"""

from fastapi import APIRouter, HTTPException, status

from wenexus.facade.model.req.fact_checker import FactCheckRequest
from wenexus.facade.model.res.fact_checker import FactCheckResponse
from wenexus.model.agent import AgentTaskInput
from wenexus.service.agent.fact_checker.agent import FactCheckerAgent
from wenexus.service.agent.fact_checker.providers.mock import MockSearchProvider

router = APIRouter(prefix="/fact-check", tags=["fact-check"])


@router.post("", response_model=FactCheckResponse)
async def create_fact_check(request: FactCheckRequest) -> FactCheckResponse:
    """为话题创建事实核查报告."""
    try:
        agent = FactCheckerAgent(search_provider=MockSearchProvider())
        task_input = AgentTaskInput(
            agent_name="fact_checker",
            params={
                "topic_id": request.topic_id,
                "topic_title": request.topic_title,
                "topic_description": request.topic_description,
            },
        )
        output = await agent.run(task_input)

        if output.status == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fact check failed: {output.error}",
            )

        result: dict[str, object] = output.result
        return FactCheckResponse(
            report_id=request.topic_id,
            status="completed",
            topic_title=str(result.get("topic_title", "")),
            summary=str(result.get("summary", "")),
            facts_count=int(result.get("facts_count", 0)),  # type: ignore[call-overload]
            sources_count=int(result.get("sources_count", 0)),  # type: ignore[call-overload]
            credibility_distribution=dict(result.get("credibility_distribution") or {}),  # type: ignore[call-overload]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fact check failed: {str(e)}",
        ) from e
