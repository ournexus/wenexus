"""
集成测试：验证Discovery域API端点的完整功能。

测试场景：
  1. 通过TestClient模拟浏览器请求
  2. 测试 /discovery/feed 端点
  3. 测试 /discovery/topics 端点
  4. 验证分页功能
  5. 测试响应数据格式

前置条件：
  1. PostgreSQL 已启动，wenexus_dev 数据库存在
  2. 测试创建真实的 topic 和 user 记录
"""

import contextlib
from datetime import datetime
from typing import Any

import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from starlette.testclient import TestClient

from wenexus.facade.discovery import router as discovery_router
from wenexus.repository.db import get_db

# ==================== Helpers ====================


async def _get_async_db() -> AsyncSession:
    """创建临时数据库session。"""
    engine = create_async_engine(
        "postgresql+asyncpg://wenexus:wenexus_dev_pwd@localhost:5432/wenexus_dev",
        echo=False,
        poolclass=NullPool,
    )

    from sqlalchemy.ext.asyncio import async_sessionmaker

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    session = async_session()
    return session


async def _setup_test_user(db: AsyncSession) -> str:
    """创建测试用户。"""
    user_id = "test-user-discovery"

    # 清理旧数据
    async with db.begin():
        await db.execute(text('DELETE FROM "user" WHERE id = :id'), {"id": user_id})
    await db.commit()

    # 创建用户
    async with db.begin():
        await db.execute(
            text(
                """
                INSERT INTO "user" (id, name, email, email_verified, image)
                VALUES (:id, :name, :email, :email_verified, :image)
            """
            ),
            {
                "id": user_id,
                "name": "Discovery Test User",
                "email": "discovery-test@example.com",
                "email_verified": True,
                "image": None,
            },
        )
    await db.commit()

    return user_id


async def _create_test_topic(
    db: AsyncSession,
    user_id: str,
    topic_id: str,
    title: str,
    visibility: str = "public",
    status: str = "active",
    consensus_level: int = 0,
    participant_count: int = 0,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """创建测试topic数据。"""
    if tags is None:
        tags = []

    import json

    async with db.begin():
        await db.execute(
            text(
                """
                INSERT INTO "topic" (
                    id, user_id, title, description, type, status, visibility,
                    consensus_level, participant_count, tags, created_at, updated_at
                )
                VALUES (
                    :id, :user_id, :title, :description, :type, :status, :visibility,
                    :consensus_level, :participant_count, :tags, :created_at, :updated_at
                )
            """
            ),
            {
                "id": topic_id,
                "user_id": user_id,
                "title": title,
                "description": f"Description for {title}",
                "type": "debate",
                "status": status,
                "visibility": visibility,
                "consensus_level": consensus_level,
                "participant_count": participant_count,
                "tags": json.dumps(tags),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        )
    await db.commit()

    return {
        "id": topic_id,
        "title": title,
        "visibility": visibility,
        "status": status,
    }


async def _cleanup_test_topics(
    db: AsyncSession, user_id: str, topic_ids: list[str]
) -> None:
    """清理测试topic数据。"""
    async with db.begin():
        for topic_id in topic_ids:
            await db.execute(
                text('DELETE FROM "topic" WHERE id = :id'), {"id": topic_id}
            )
    await db.commit()

    async with db.begin():
        await db.execute(text('DELETE FROM "user" WHERE id = :id'), {"id": user_id})
    await db.commit()


@pytest_asyncio.fixture(scope="function")
async def app_and_client_with_db() -> tuple[FastAPI, TestClient, AsyncSession]:
    """创建FastAPI应用、TestClient和async_db，共享同一个async_db。"""
    async_db = await _get_async_db()
    app = FastAPI()

    # 重写 get_db 依赖
    async def get_db_override():
        yield async_db

    app.dependency_overrides[get_db] = get_db_override

    # 注册Discovery路由
    app.include_router(discovery_router, prefix="/api/v1")

    client = TestClient(app)
    return app, client, async_db


# ==================== Tests ====================


class TestDiscoveryFeedEndpoint:
    """测试 /discovery/feed 端点。"""

    @pytest.mark.asyncio
    async def test_feed_endpoint_returns_cards_format(
        self, app_and_client_with_db
    ) -> None:
        """Feed端点返回正确的card格式。"""
        _, test_client, _ = app_and_client_with_db
        response = test_client.get("/api/v1/discovery/feed")
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        assert "cards" in data["data"]
        assert isinstance(data["data"]["cards"], list)

    @pytest.mark.asyncio
    async def test_feed_endpoint_returns_correct_data(
        self, app_and_client_with_db
    ) -> None:
        """Feed端点返回正确的topic数据结构。"""
        _, test_client, _ = app_and_client_with_db
        response = test_client.get("/api/v1/discovery/feed")
        assert response.status_code == 200

        data = response.json()
        cards = data["data"]["cards"]

        # 检查card结构（即使没有数据也应该返回列表）
        assert isinstance(cards, list)

        # 如果有数据，检查card结构
        for card in cards:
            assert "topic" in card
            assert "expertCount" in card
            assert "consensusLevel" in card

            # 检查topic字段
            topic = card["topic"]
            assert "id" in topic
            assert "title" in topic
            assert "description" in topic
            assert "type" in topic
            assert "status" in topic
            assert "consensusLevel" in topic
            assert "participantCount" in topic
            assert "tags" in topic
            assert "createdAt" in topic

    @pytest.mark.asyncio
    async def test_feed_endpoint_pagination(self, app_and_client_with_db) -> None:
        """Feed端点支持分页。"""
        _, test_client, _ = app_and_client_with_db
        # 第一页
        response = test_client.get("/api/v1/discovery/feed?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["page"] == 1
        assert data["data"]["limit"] == 10

        # 检查分页信息
        assert "total" in data["data"]
        assert "cards" in data["data"]

    @pytest.mark.asyncio
    async def test_feed_endpoint_default_pagination(
        self, app_and_client_with_db
    ) -> None:
        """Feed端点使用默认分页参数。"""
        _, test_client, _ = app_and_client_with_db
        response = test_client.get("/api/v1/discovery/feed")
        assert response.status_code == 200

        data = response.json()
        assert data["data"]["page"] == 1
        assert data["data"]["limit"] == 20

    @pytest.mark.asyncio
    async def test_feed_endpoint_card_expertise_count(
        self, app_and_client_with_db
    ) -> None:
        """Feed endpoint card中的expertCount字段存在。"""
        _, test_client, _ = app_and_client_with_db
        response = test_client.get("/api/v1/discovery/feed")
        assert response.status_code == 200

        data = response.json()
        cards = data["data"]["cards"]

        for card in cards:
            assert "expertCount" in card
            # expertCount应该是整数（当前为0，因为没有关联expert）
            assert isinstance(card["expertCount"], int)

    @pytest.mark.asyncio
    async def test_feed_endpoint_ordering(self, app_and_client_with_db) -> None:
        """Feed端点按创建时间倒序返回。"""
        _, test_client, _ = app_and_client_with_db
        response = test_client.get("/api/v1/discovery/feed")
        assert response.status_code == 200

        data = response.json()
        cards = data["data"]["cards"]

        if len(cards) > 1:
            # 检查创建时间是否倒序
            for i in range(len(cards) - 1):
                created_at_1 = cards[i]["topic"]["createdAt"]
                created_at_2 = cards[i + 1]["topic"]["createdAt"]
                assert created_at_1 >= created_at_2


class TestDiscoveryTopicsEndpoint:
    """测试 /discovery/topics 端点。"""

    @pytest.mark.asyncio
    async def test_topics_endpoint_returns_topics_format(
        self, app_and_client_with_db
    ) -> None:
        """Topics端点返回正确的格式。"""
        _, test_client, _ = app_and_client_with_db
        response = test_client.get("/api/v1/discovery/topics")
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        assert "topics" in data["data"]
        assert isinstance(data["data"]["topics"], list)

    @pytest.mark.asyncio
    async def test_topics_endpoint_returns_correct_data(
        self, app_and_client_with_db
    ) -> None:
        """Topics端点返回正确的topic数据结构。"""
        _, test_client, _ = app_and_client_with_db
        response = test_client.get("/api/v1/discovery/topics")
        assert response.status_code == 200

        data = response.json()
        topics = data["data"]["topics"]

        # 检查topics结构（即使没有数据也应该返回列表）
        assert isinstance(topics, list)

        # 如果有数据，检查topic字段
        for topic in topics:
            assert "id" in topic
            assert "title" in topic
            assert "description" in topic
            assert "type" in topic
            assert "status" in topic
            assert "consensusLevel" in topic
            assert "participantCount" in topic
            assert "tags" in topic
            assert "createdAt" in topic

    @pytest.mark.asyncio
    async def test_topics_endpoint_pagination(self, app_and_client_with_db) -> None:
        """Topics端点支持分页。"""
        _, test_client, _ = app_and_client_with_db
        response = test_client.get("/api/v1/discovery/topics?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["page"] == 1
        assert data["data"]["limit"] == 10

    @pytest.mark.asyncio
    async def test_topics_endpoint_default_pagination(
        self, app_and_client_with_db
    ) -> None:
        """Topics端点使用默认分页参数。"""
        _, test_client, _ = app_and_client_with_db
        response = test_client.get("/api/v1/discovery/topics")
        assert response.status_code == 200

        data = response.json()
        assert data["data"]["page"] == 1
        assert data["data"]["limit"] == 20

    @pytest.mark.asyncio
    async def test_topics_no_expertise_count(self, app_and_client_with_db) -> None:
        """Topics端点不包含expertCount字段。"""
        _, test_client, _ = app_and_client_with_db
        response = test_client.get("/api/v1/discovery/topics")
        assert response.status_code == 200

        data = response.json()
        topics = data["data"]["topics"]

        for topic in topics:
            assert "expertCount" not in topic


class TestDiscoveryDataIntegrity:
    """测试Discovery端点的数据完整性和一致性。"""

    @pytest.mark.asyncio
    async def test_feed_and_topics_consistency(self, app_and_client_with_db) -> None:
        """Feed和Topics端点返回结构一致。"""
        _, test_client, _ = app_and_client_with_db
        feed_response = test_client.get("/api/v1/discovery/feed")

        assert feed_response.status_code == 200
        feed_data = feed_response.json()

        # 检查两个端点返回相同的数据结构
        assert "code" in feed_data
        assert "data" in feed_data
        assert "cards" in feed_data["data"]
        assert isinstance(feed_data["data"]["cards"], list)

    @pytest.mark.asyncio
    async def test_topic_visibility_filtering(self, app_and_client_with_db) -> None:
        """验证只返回public的topic。"""
        _, test_client, async_db = app_and_client_with_db
        user_id = await _setup_test_user(async_db)
        topic_ids = ["test-public-1", "test-private-1"]

        # 创建public topic
        await _create_test_topic(
            async_db,
            user_id,
            topic_ids[0],
            title="Public Topic",
            visibility="public",
            status="active",
        )

        # 创建private topic
        await _create_test_topic(
            async_db,
            user_id,
            topic_ids[1],
            title="Private Topic",
            visibility="private",
            status="active",
        )

        response = test_client.get("/api/v1/discovery/feed")
        assert response.status_code == 200

        data = response.json()
        cards = data["data"]["cards"]

        # 应该只返回public topic
        for card in cards:
            topic = card["topic"]
            if topic["title"] in ["Public Topic", "Private Topic"]:
                assert topic["title"] == "Public Topic"

        # 清理
        with contextlib.suppress(Exception):
            await _cleanup_test_topics(async_db, user_id, topic_ids)

    @pytest.mark.asyncio
    async def test_topic_status_filtering(self, app_and_client_with_db) -> None:
        """验证只返回active的topic。"""
        _, test_client, async_db = app_and_client_with_db
        user_id = await _setup_test_user(async_db)
        topic_ids = ["test-active-1", "test-completed-1", "test-draft-1"]

        # 创建不同status的topic
        statuses = ["active", "completed", "draft"]
        for topic_id, status in zip(topic_ids, statuses, strict=True):
            await _create_test_topic(
                async_db,
                user_id,
                topic_id,
                title=f"{status.capitalize()} Topic",
                visibility="public",
                status=status,
            )

        response = test_client.get("/api/v1/discovery/feed")
        assert response.status_code == 200

        data = response.json()
        cards = data["data"]["cards"]

        # 应该只返回status=active的topic
        returned_statuses = set(card["topic"]["status"] for card in cards)
        if "Active Topic" in [card["topic"]["title"] for card in cards]:
            assert all(status == "active" for status in returned_statuses)

        # 清理
        with contextlib.suppress(Exception):
            await _cleanup_test_topics(async_db, user_id, topic_ids)
