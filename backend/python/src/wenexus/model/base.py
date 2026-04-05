"""
model.base - 基础领域原语（Domain Primitive）。

自校验值对象，非法状态无法构造。
跨领域共享的枚举和 DP 定义。

Depends: (无)
Consumers: model.fact_report, model.agent, service, app, facade
"""

import re
from dataclasses import dataclass
from enum import StrEnum


class CredibilityLevel(StrEnum):
    """可信度等级。"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


class SourceType(StrEnum):
    """来源类型。"""

    WEB = "web"
    ACADEMIC = "academic"
    NEWS = "news"
    GOV = "gov"


class VerificationStatus(StrEnum):
    """验证状态。"""

    VERIFIED = "verified"
    PENDING = "pending"
    DISPUTED = "disputed"


class AgentStatus(StrEnum):
    """Agent 执行状态。"""

    PENDING = "pending"
    PLANNING = "planning"
    SEARCHING = "searching"
    EXTRACTING = "extracting"
    ANALYZING = "analyzing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    ERROR = "error"


_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.I,
)


@dataclass(frozen=True)
class TopicId:
    """话题 ID — UUID 格式自校验。"""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not _UUID_RE.match(self.value):
            raise ValueError(f"Invalid TopicId: {self.value}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SessionId:
    """会话 ID — UUID 格式自校验。"""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not _UUID_RE.match(self.value):
            raise ValueError(f"Invalid SessionId: {self.value}")

    def __str__(self) -> str:
        return self.value
