"""Fact Report Repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..repository.model.fact_report import FactReportORM


class FactReportRepository:
    """Fact Report 数据访问层."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, report_data: dict) -> FactReportORM:
        """创建新的 fact report."""
        report = FactReportORM(**report_data)
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get_by_id(self, report_id: UUID) -> FactReportORM | None:
        """根据 ID 获取 report."""
        result = await self.session.execute(
            select(FactReportORM).where(FactReportORM.id == report_id)
        )
        return result.scalar_one_or_none()

    async def get_by_topic(self, topic_id: UUID) -> list[FactReportORM]:
        """获取话题的所有 reports."""
        result = await self.session.execute(
            select(FactReportORM)
            .where(FactReportORM.topic_id == topic_id)
            .order_by(FactReportORM.created_at.desc())
        )
        return result.scalars().all()

    async def update_status(
        self, report_id: UUID, status: str, report_data: dict | None = None
    ) -> FactReportORM | None:
        """更新 report 状态和结果."""
        report = await self.get_by_id(report_id)
        if not report:
            return None

        report.status = status
        if report_data:
            report.report = report_data.get("report", report.report)
            report.search_iterations = report_data.get("iterations")
            report.sources = report_data.get("sources")
            report.credibility_distribution = report_data.get("credibility_dist")
            report.total_tokens = report_data.get("total_tokens")
            report.execution_time_ms = report_data.get("execution_time_ms")

        await self.session.commit()
        await self.session.refresh(report)
        return report
