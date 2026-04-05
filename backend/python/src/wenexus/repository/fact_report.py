"""Fact Report Repository — DO ↔ Entity 映射 + CRUD。

Depends: sqlalchemy, model.fact_report, repository.model.fact_report
Consumers: app.fact_checker
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from wenexus.model.base import CredibilityLevel, SourceType, VerificationStatus
from wenexus.model.fact_report import (
    Fact,
    FactReport,
    Source,
)

from .model.fact_report import FactReportORM


def entity_to_do(entity: FactReport, topic_id: UUID) -> dict:
    """FactReport Entity → DO 字段字典（用于创建 ORM 实例）。"""
    return {
        "id": entity.id,
        "topic_id": topic_id,
        "report": {
            "topic_title": entity.topic_title,
            "summary": entity.summary,
            "facts": [
                {
                    "content": f.content,
                    "claim": f.claim,
                    "source": {
                        "title": f.source.title,
                        "url": f.source.url,
                        "source_type": f.source.source_type.value,
                        "credibility": f.source.credibility.value,
                    },
                    "credibility": f.credibility.value,
                    "verification_status": f.verification_status.value,
                    "notes": f.notes,
                }
                for f in entity.facts
            ],
        },
        "sources": [
            {
                "title": s.title,
                "url": s.url,
                "snippet": s.snippet,
                "source_type": s.source_type.value,
            }
            for s in entity.sources
        ],
        "credibility_distribution": entity.credibility_distribution,
        "status": "completed",
        "iterations": len(entity.facts),
    }


def do_to_entity(orm: FactReportORM) -> FactReport:
    """FactReportORM DO → FactReport Entity。"""
    report_data = orm.report or {}
    facts_data = report_data.get("facts", [])

    facts = []
    sources = []
    for fd in facts_data:
        sd = fd.get("source", {})
        source = Source(
            title=sd.get("title", ""),
            url=sd.get("url", ""),
            snippet="",
            source_type=SourceType(sd.get("source_type", "web")),
            credibility=CredibilityLevel(sd.get("credibility", "uncertain")),
        )
        fact = Fact(
            content=fd.get("content", ""),
            claim=fd.get("claim", ""),
            source=source,
            credibility=CredibilityLevel(fd.get("credibility", "uncertain")),
            verification_status=VerificationStatus(
                fd.get("verification_status", "pending")
            ),
            notes=fd.get("notes", ""),
        )
        facts.append(fact)
        sources.append(source)

    cred_dist = orm.credibility_distribution or {}

    entity = FactReport(
        id=orm.id,
        topic_title=report_data.get("topic_title", ""),
        summary=report_data.get("summary", ""),
        coverage_analysis=None,
        credibility_distribution=cred_dist,
    )
    entity.facts = facts
    entity.sources = sources
    return entity


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
        return list(result.scalars().all())

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
            tokens = report_data.get("total_tokens")
            report.total_tokens = int(tokens) if tokens is not None else None  # type: ignore[assignment]
            exec_time = report_data.get("execution_time_ms")
            report.execution_time_ms = int(exec_time) if exec_time is not None else None  # type: ignore[assignment]

        await self.session.commit()
        await self.session.refresh(report)
        return report
