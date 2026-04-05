"""Fact Checker 请求模型。"""

from pydantic import BaseModel, Field


class FactCheckRequest(BaseModel):
    """CQE: CreateFactCheck Command."""

    topic_id: str = Field(..., description="话题ID")
    topic_title: str = Field(..., description="话题标题")
    topic_description: str | None = Field(None, description="话题描述")
