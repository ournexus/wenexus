"""
repository.roundtable - Roundtable domain database operations.

Handles: discussion_session, discussion_message, expert queries and mutations.

Depends: sqlalchemy, uuid
Consumers: service.roundtable
"""

import json
import uuid
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def save_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    content: str,
    user_id: str | None = None,
    expert_id: str | None = None,
    citations: dict | None = None,
) -> dict:
    """Save a message to discussion_message table.

    Args:
        db: Database session
        session_id: Discussion session ID
        role: Message role (user, expert, system, fact_checker, host, participant)
        content: Message content
        user_id: User ID (for user/host messages)
        expert_id: Expert ID (for expert messages)
        citations: Optional citations JSON

    Returns:
        Saved message dict with id, createdAt, etc.
    """
    message_id = str(uuid.uuid4())
    citations_json = json.dumps(citations or [])

    await db.execute(
        text(
            """
        INSERT INTO discussion_message (
            id, session_id, user_id, expert_id, role, content,
            citations, status, metadata, created_at, updated_at
        )
        VALUES (
            :id, :session_id, :user_id, :expert_id, :role, :content,
            CAST(:citations AS jsonb), :status, NULL, NOW(), NOW()
        )
    """
        ),
        {
            "id": message_id,
            "session_id": session_id,
            "user_id": user_id,
            "expert_id": expert_id,
            "role": role,
            "content": content,
            "citations": citations_json,
            "status": "active",
        },
    )
    await db.commit()

    return {
        "id": message_id,
        "sessionId": session_id,
        "userId": user_id,
        "expertId": expert_id,
        "role": role,
        "content": content,
        "citations": citations or [],
        "status": "active",
        "createdAt": datetime.now().isoformat(),
    }


async def get_session_experts(db: AsyncSession, session_id: str) -> list[dict]:
    """Get list of experts assigned to a discussion session.

    Args:
        db: Database session
        session_id: Discussion session ID

    Returns:
        List of expert dicts with id, name, role, stance, systemPrompt
    """
    result = await db.execute(
        text(
            """
        SELECT e.id, e.name, e.role, e.stance, e.system_prompt
        FROM expert e
        WHERE e.id = ANY(
            SELECT jsonb_array_elements(ds.expert_ids)::text
            FROM discussion_session ds
            WHERE ds.id = :session_id
        )
    """
        ),
        {"session_id": session_id},
    )

    experts = []
    for row in result:
        experts.append(
            {
                "id": row.id,
                "name": row.name,
                "role": row.role,
                "stance": row.stance,
                "systemPrompt": row.system_prompt,
            }
        )

    return experts


async def get_session_context(db: AsyncSession, session_id: str) -> dict | None:
    """Get session context including topic, mode, and recent messages.

    Args:
        db: Database session
        session_id: Discussion session ID

    Returns:
        Session context dict or None if not found
    """
    # Get session details
    session_result = await db.execute(
        text(
            """
        SELECT ds.id, ds.topic_id, ds.status, ds.mode, ds.consensus_level,
               ds.expert_ids, t.title as topic_title, t.description as topic_desc,
               t.type as topic_type
        FROM discussion_session ds
        JOIN topic t ON ds.topic_id = t.id
        WHERE ds.id = :session_id
    """
        ),
        {"session_id": session_id},
    )

    session_row = session_result.first()
    if not session_row:
        return None

    # Get recent messages (last 10)
    messages_result = await db.execute(
        text(
            """
        SELECT dm.role, dm.content, dm.created_at
        FROM discussion_message dm
        WHERE dm.session_id = :session_id
        ORDER BY dm.created_at DESC
        LIMIT 10
    """
        ),
        {"session_id": session_id},
    )

    messages = []
    for row in messages_result:
        messages.append(
            {
                "role": row.role,
                "content": row.content,
                "createdAt": row.created_at.isoformat() if row.created_at else None,
            }
        )

    # Parse expert IDs
    expert_ids = []
    if session_row.expert_ids:
        try:
            if isinstance(session_row.expert_ids, str):
                expert_ids = json.loads(session_row.expert_ids)
            elif isinstance(session_row.expert_ids, list):
                expert_ids = session_row.expert_ids
        except (json.JSONDecodeError, TypeError):
            expert_ids = []

    return {
        "id": session_row.id,
        "topicId": session_row.topic_id,
        "topicTitle": session_row.topic_title,
        "topicDescription": session_row.topic_desc,
        "topicType": session_row.topic_type,
        "status": session_row.status,
        "mode": session_row.mode,
        "consensusLevel": session_row.consensus_level,
        "expertIds": expert_ids,
        "recentMessages": list(reversed(messages)),
    }


async def update_session_status(
    db: AsyncSession, session_id: str, new_status: str
) -> bool:
    """Update discussion session status.

    Args:
        db: Database session
        session_id: Discussion session ID
        new_status: New status (discussing, concluding, completed, etc.)

    Returns:
        True if update successful
    """
    await db.execute(
        text(
            """
        UPDATE discussion_session
        SET status = :status, updated_at = NOW()
        WHERE id = :session_id
    """
        ),
        {"session_id": session_id, "status": new_status},
    )
    await db.commit()
    return True
