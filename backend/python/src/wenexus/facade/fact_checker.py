"""Fact Checker API Facade."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from wenexus.agent.fact_checker.harness.harness import FactCheckerHarness
from wenexus.agent.fact_checker.providers.mock import MockSearchProvider

router = APIRouter(prefix="/fact-check", tags=["fact-check"])


class FactCheckRequest(BaseModel):
    topic_id: str = Field(..., description="话题ID")
    topic_title: str = Field(..., description="话题标题")
    topic_description: str | None = Field(None, description="话题描述")


class FactCheckResponse(BaseModel):
    report_id: str = Field(..., description="报告ID")
    status: str = Field(..., description="状态: pending/completed/error")
    topic_title: str
    summary: str
    facts_count: int
    sources_count: int
    credibility_distribution: dict


@router.post("", response_model=FactCheckResponse)
async def create_fact_check(request: FactCheckRequest):
    """为话题创建事实核查报告.

    调用 FactChecker Harness 执行多轮搜索和事实提取.
    """
    try:
        harness = FactCheckerHarness(search_provider=MockSearchProvider())
        report = await harness.run(
            topic_title=request.topic_title,
            topic_description=request.topic_description,
            topic_id=request.topic_id,
        )

        return FactCheckResponse(
            report_id=request.topic_id,  # 简化用 topic_id
            status="completed",
            topic_title=report.topic_title,
            summary=report.summary,
            facts_count=len(report.facts),
            sources_count=len(report.sources),
            credibility_distribution=report.credibility_distribution,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fact check failed: {str(e)}",
        )
