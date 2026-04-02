"""Fact Report ORM Model."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class FactReportORM(Base):
    """fact_reports 表 ORM 模型."""

    __tablename__ = "fact_reports"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    topic_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id"), nullable=False
    )
    session_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roundtable_sessions.id"), nullable=True
    )

    # Deep Agents 输出
    report: Mapped[dict] = mapped_column(JSON, nullable=False)
    search_iterations: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sources: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    credibility_distribution: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # 执行元数据
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    iterations: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
