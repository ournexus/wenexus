"""Run-related Pydantic models."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class StreamMode(str, Enum):
    """Stream mode options matching SDK StreamMode type."""

    VALUES = "values"
    MESSAGES = "messages"
    MESSAGES_TUPLE = "messages-tuple"
    UPDATES = "updates"
    EVENTS = "events"
    DEBUG = "debug"
    TASKS = "tasks"
    CHECKPOINTS = "checkpoints"
    CUSTOM = "custom"


class EventType(str, Enum):
    """SSE event types matching SDK stream event types."""

    METADATA = "metadata"
    VALUES = "values"
    MESSAGES = "messages"
    UPDATES = "updates"
    EVENTS = "events"
    DEBUG = "debug"
    TASKS = "tasks"
    CHECKPOINTS = "checkpoints"
    CUSTOM = "custom"
    FEEDBACK = "feedback"
    END = "end"
    ERROR = "error"


class RunStreamRequest(BaseModel):
    """Request model for streaming runs."""

    assistant_id: str
    input: dict | None = None
    stream_mode: list[str] = Field(default_factory=lambda: ["updates"])
    stream_subgraphs: bool = False
    config: dict | None = None
    metadata: dict | None = None
    interrupt_before: list[str] | None = None
    interrupt_after: list[str] | None = None
    multitask_strategy: str | None = None

    @field_validator("stream_mode", mode="before")
    @classmethod
    def coerce_stream_mode(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            return [v]
        return v


class StreamEvent(BaseModel):
    """Stream event model."""

    event: str
    data: Any
    run_id: str | None = None
