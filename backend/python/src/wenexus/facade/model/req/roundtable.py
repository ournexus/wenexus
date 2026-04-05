"""Roundtable 请求模型。"""

from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    """Request body for sending a message to a discussion session."""

    content: str
    generate_ai_reply: bool = True


class CreateSessionRequest(BaseModel):
    """Request body for creating a new discussion session."""

    topic_id: str
    mode: str = "autopilot"
    is_private: bool = False
    expert_ids: list[str] | None = None


class UpdateSessionRequest(BaseModel):
    """Request body for updating a discussion session."""

    mode: str | None = None
    is_private: bool | None = None
