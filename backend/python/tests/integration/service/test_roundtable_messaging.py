"""
Integration tests for roundtable message sending functionality.

Tests hybrid mode: synchronous message save + asynchronous AI reply generation.
"""

import json
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from wenexus.config import settings
from wenexus.service.roundtable import send_message


@pytest.mark.asyncio
async def test_send_message_saves_user_message():
    """Test that user message is synchronously saved to database."""
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Setup: Create test data
        user_id = str(uuid.uuid4())
        topic_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())

        # Create user
        await session.execute(
            text(
                """
            INSERT INTO "user" (id, name, email, email_verified, created_at, updated_at)
            VALUES (:id, :name, :email, :email_verified, NOW(), NOW())
        """
            ),
            {
                "id": user_id,
                "name": "Test User",
                "email": f"test-{uuid.uuid4()}@example.com",
                "email_verified": True,
            },
        )

        # Create topic
        await session.execute(
            text(
                """
            INSERT INTO topic (id, user_id, title, description, type, status, visibility, created_at, updated_at)
            VALUES (:id, :user_id, :title, :description, :type, :status, :visibility, NOW(), NOW())
        """
            ),
            {
                "id": topic_id,
                "user_id": user_id,
                "title": "Test Topic",
                "description": "Test description",
                "type": "debate",
                "status": "active",
                "visibility": "public",
            },
        )

        # Create discussion session
        await session.execute(
            text(
                """
            INSERT INTO discussion_session (id, topic_id, user_id, status, mode, consensus_level,
                                           expert_ids, is_private, created_at, updated_at)
            VALUES (:id, :topic_id, :user_id, :status, :mode, :consensus_level,
                   :expert_ids, :is_private, NOW(), NOW())
        """
            ),
            {
                "id": session_id,
                "topic_id": topic_id,
                "user_id": user_id,
                "status": "initializing",
                "mode": "autopilot",
                "consensus_level": 0,
                "expert_ids": json.dumps([]),
                "is_private": False,
            },
        )
        await session.commit()

        # Test: Send message without AI generation (faster test)
        result = await send_message(
            session,
            session_id=session_id,
            user_id=user_id,
            content="What are your thoughts on this?",
            generate_ai_reply=False,
        )

        # Verify response structure
        assert result["code"] == 0
        assert "data" in result
        assert "userMessage" in result["data"]
        assert "aiReplies" in result["data"]
        assert result["data"]["sessionId"] == session_id

        # Verify user message details
        user_msg = result["data"]["userMessage"]
        assert user_msg["sessionId"] == session_id
        assert user_msg["userId"] == user_id
        assert user_msg["role"] == "participant"
        assert user_msg["content"] == "What are your thoughts on this?"

        # Verify message was saved to database
        saved_msg = await session.execute(
            text("SELECT * FROM discussion_message WHERE id = :id"),
            {"id": user_msg["id"]},
        )
        row = saved_msg.first()
        assert row is not None
        assert row.content == "What are your thoughts on this?"

        # Cleanup
        await session.execute(
            text("DELETE FROM discussion_message WHERE id = :id"),
            {"id": user_msg["id"]},
        )
        await session.execute(
            text("DELETE FROM discussion_session WHERE id = :id"), {"id": session_id}
        )
        await session.execute(
            text("DELETE FROM topic WHERE id = :id"), {"id": topic_id}
        )
        await session.execute(
            text('DELETE FROM "user" WHERE id = :id'), {"id": user_id}
        )
        await session.commit()

    await engine.dispose()


@pytest.mark.asyncio
async def test_send_message_updates_session_status():
    """Test that session status is updated to 'discussing' after message sent."""
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Setup
        user_id = str(uuid.uuid4())
        topic_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())

        # Create user and topic
        await session.execute(
            text(
                """
            INSERT INTO "user" (id, name, email, email_verified, created_at, updated_at)
            VALUES (:id, :name, :email, :email_verified, NOW(), NOW())
        """
            ),
            {
                "id": user_id,
                "name": "Test User 2",
                "email": f"test2-{uuid.uuid4()}@example.com",
                "email_verified": True,
            },
        )

        await session.execute(
            text(
                """
            INSERT INTO topic (id, user_id, title, description, type, status, visibility, created_at, updated_at)
            VALUES (:id, :user_id, :title, :description, :type, :status, :visibility, NOW(), NOW())
        """
            ),
            {
                "id": topic_id,
                "user_id": user_id,
                "title": "Test Topic 2",
                "description": "Test",
                "type": "brainstorm",
                "status": "active",
                "visibility": "public",
            },
        )

        # Create discussion session with 'initializing' status
        await session.execute(
            text(
                """
            INSERT INTO discussion_session (id, topic_id, user_id, status, mode, consensus_level,
                                           expert_ids, is_private, created_at, updated_at)
            VALUES (:id, :topic_id, :user_id, :status, :mode, :consensus_level,
                   :expert_ids, :is_private, NOW(), NOW())
        """
            ),
            {
                "id": session_id,
                "topic_id": topic_id,
                "user_id": user_id,
                "status": "initializing",
                "mode": "autopilot",
                "consensus_level": 0,
                "expert_ids": json.dumps([]),
                "is_private": False,
            },
        )
        await session.commit()

        # Test: Send message
        await send_message(
            session,
            session_id=session_id,
            user_id=user_id,
            content="Let's discuss this topic.",
            generate_ai_reply=False,
        )

        # Verify session status changed to 'discussing'
        status_result = await session.execute(
            text("SELECT status FROM discussion_session WHERE id = :id"),
            {"id": session_id},
        )
        status_row = status_result.first()
        assert status_row.status == "discussing"

        # Cleanup
        await session.execute(
            text("DELETE FROM discussion_message WHERE session_id = :id"),
            {"id": session_id},
        )
        await session.execute(
            text("DELETE FROM discussion_session WHERE id = :id"), {"id": session_id}
        )
        await session.execute(
            text("DELETE FROM topic WHERE id = :id"), {"id": topic_id}
        )
        await session.execute(
            text('DELETE FROM "user" WHERE id = :id'), {"id": user_id}
        )
        await session.commit()

    await engine.dispose()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
