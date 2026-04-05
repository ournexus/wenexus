"""Fact Checker 响应模型。"""

from pydantic import BaseModel, Field


class FactCheckResponse(BaseModel):
    """DTO: Fact Check 响应。"""

    report_id: str = Field(..., description="报告ID")
    status: str = Field(..., description="状态: pending/completed/error")
    topic_title: str
    summary: str
    facts_count: int
    sources_count: int
    credibility_distribution: dict
