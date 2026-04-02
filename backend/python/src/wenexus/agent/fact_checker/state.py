"""Fact Checker State."""

from dataclasses import dataclass, field

from typing_extensions import TypedDict


@dataclass
class Source:
    title: str
    url: str
    snippet: str
    source_type: str = "web"
    credibility: str = "uncertain"


@dataclass
class Fact:
    content: str
    claim: str
    source: Source
    credibility: str = "uncertain"


@dataclass
class FactReport:
    topic_title: str
    summary: str = ""
    facts: list[Fact] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)

    def to_dict(self):
        return {
            "topic": self.topic_title,
            "summary": self.summary,
            "facts": len(self.facts),
        }


class FactCheckState(TypedDict):
    topic_id: str | None
    topic_title: str
    topic_description: str | None
    current_iteration: int
    max_iterations: int
    should_continue: bool
    search_queries: list[str]
    search_results: list[Source]
    search_iterations: list
    extracted_facts: list[Fact]
    final_report: FactReport | None
    status: str
    error: str | None
    total_tokens: int
    start_time: float | None
    end_time: float | None
