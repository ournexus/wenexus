"""
model.fact_report - Fact Check 领域模型。

Entity / Value Object / Domain Primitive 定义。
Entity 只包含业务行为，序列化交给 repository mapper 或 facade DTO 转换器。

Depends: model.base
Consumers: service.agent.fact_checker, app.fact_checker, facade.fact_checker, repository.fact_report
"""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .base import CredibilityLevel, SourceType, VerificationStatus

# ── Value Objects (不可变，按值比较) ──


@dataclass(frozen=True)
class Source:
    """事实来源（VO）。"""

    title: str
    url: str
    snippet: str
    source_type: SourceType = SourceType.WEB
    published_date: str | None = None
    credibility: CredibilityLevel = CredibilityLevel.UNCERTAIN


@dataclass(frozen=True)
class Fact:
    """提取的事实（VO）。"""

    content: str
    claim: str
    source: Source
    credibility: CredibilityLevel = CredibilityLevel.UNCERTAIN
    verification_status: VerificationStatus = VerificationStatus.PENDING
    notes: str = ""


@dataclass(frozen=True)
class CoverageAnalysis:
    """覆盖度分析（VO）。"""

    total_dimensions: int
    covered_dimensions: int
    coverage_score: float  # 0.0 ~ 1.0
    missing_dimensions: tuple[str, ...] = ()
    recommendation: str = ""


@dataclass(frozen=True)
class SearchIteration:
    """单次搜索迭代记录（VO）。"""

    iteration: int
    query: str
    results_count: int
    key_findings: tuple[str, ...] = ()


# ── Entity (有 ID，有生命周期) ──


@dataclass
class FactReport:
    """事实报告（Entity）— 有唯一标识，有生命周期。

    序列化方法不在 Entity 上，由 repository mapper 或 facade DTO 负责。
    Entity 通过方法管理内部状态，避免贫血模型。
    """

    id: UUID = field(default_factory=uuid4)
    topic_title: str = ""
    summary: str = ""
    facts: list[Fact] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    coverage_analysis: CoverageAnalysis | None = None
    credibility_distribution: dict[str, int] = field(default_factory=dict)

    def add_fact(self, fact: Fact) -> None:
        """添加事实并更新可信度分布。"""
        self.facts.append(fact)
        level = fact.credibility.value
        self.credibility_distribution[level] = (
            self.credibility_distribution.get(level, 0) + 1
        )

    def add_source(self, source: Source) -> None:
        """添加来源。"""
        self.sources.append(source)
