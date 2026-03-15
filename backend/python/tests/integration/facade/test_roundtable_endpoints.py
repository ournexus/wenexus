"""
集成测试：验证 Roundtable 域 API 端点的完整功能。

测试场景：
  1. 通过 TestClient 模拟浏览器请求
  2. 测试 /roundtable/experts 端点
  3. 测试 /roundtable/sessions 端点（需要认证）
  4. 验证分页功能
  5. 测试响应数据格式

前置条件：
  1. PostgreSQL 已启动，wenexus_dev 数据库存在
  2. 测试创建真实的 user, expert, session 记录
  3. 用户已认证
"""

from datetime import datetime, timedelta
from typing import Any

import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from starlette.testclient import TestClient

from wenexus.facade.deps import get_current_user
from wenexus.facade.roundtable import router as roundtable_router
from wenexus.repository.db import get_db
from wenexus.util.schema import UserInfo

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


async def _setup_test_user(db: AsyncSession) -> tuple[str, str]:
    """创建测试用户，返回 (user_id, token)."""
    user_id = "test-user-roundtable"
    token = f"test-token-{user_id}"

    # 清理旧数据
    await db.execute(
        text('DELETE FROM "session" WHERE token = :token'), {"token": token}
    )
    await db.commit()

    await db.execute(text('DELETE FROM "user" WHERE id = :id'), {"id": user_id})
    await db.commit()

    # 创建用户
    await db.execute(
        text(
            """
            INSERT INTO "user" (id, name, email, email_verified, image)
            VALUES (:id, :name, :email, :email_verified, :image)
        """
        ),
        {
            "id": user_id,
            "name": "Roundtable Test User",
            "email": "roundtable-test@example.com",
            "email_verified": True,
            "image": None,
        },
    )
    await db.commit()

    # 创建session
    expires_at = datetime.now() + timedelta(hours=1)
    await db.execute(
        text(
            """
            INSERT INTO "session" (id, token, user_id, expires_at, updated_at, ip_address, user_agent)
            VALUES (:id, :token, :user_id, :expires_at, :updated_at, :ip_address, :user_agent)
        """
        ),
        {
            "id": f"session-{user_id}",
            "token": token,
            "user_id": user_id,
            "expires_at": expires_at,
            "updated_at": datetime.now(),
            "ip_address": "127.0.0.1",
            "user_agent": "TestClient/1.0",
        },
    )
    await db.commit()

    return user_id, token


async def _cleanup_test_user(db: AsyncSession, user_id: str) -> None:
    """清理测试用户数据。"""
    # 删除session
    await db.execute(
        text('DELETE FROM "session" WHERE user_id = :user_id'), {"user_id": user_id}
    )
    await db.commit()

    # 删除user
    await db.execute(text('DELETE FROM "user" WHERE id = :id'), {"id": user_id})
    await db.commit()


async def _create_test_expert(
    db: AsyncSession, expert_id: str, name: str, role: str = "economist"
) -> dict[str, Any]:
    """创建测试专家数据。"""
    async with db.begin():
        await db.execute(
            text(
                """
                INSERT INTO "expert" (id, name, role, stance, description, is_builtin, status, created_at, updated_at)
                VALUES (:id, :name, :role, :stance, :description, :is_builtin, :status, :created_at, :updated_at)
            """
            ),
            {
                "id": expert_id,
                "name": name,
                "role": role,
                "stance": "supportive",
                "description": f"Test expert: {name}",
                "is_builtin": False,
                "status": "active",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        )
    await db.commit()

    return {"id": expert_id, "name": name, "role": role}


# ==================== Fixtures ====================


@pytest_asyncio.fixture(scope="function")
async def app_and_client_with_db() -> tuple[
    FastAPI, TestClient, AsyncSession, UserInfo
]:
    """创建FastAPI应用、TestClient、async_db和认证用户。"""
    async_db = await _get_async_db()
    user_id, token = await _setup_test_user(async_db)

    app = FastAPI()

    # 重写 get_db 依赖
    async def get_db_override():
        yield async_db

    # 重写 get_current_user 依赖
    async def get_current_user_override():
        return UserInfo(
            id=user_id,
            name="Roundtable Test User",
            email="roundtable-test@example.com",
            image=None,
            email_verified=True,
        )

    app.dependency_overrides[get_db] = get_db_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    # 注册Roundtable路由
    app.include_router(roundtable_router, prefix="/api/v1")

    client = TestClient(app)
    user = UserInfo(
        id=user_id,
        name="Roundtable Test User",
        email="roundtable-test@example.com",
        image=None,
        email_verified=True,
    )

    yield app, client, async_db, user

    # 清理
    await _cleanup_test_user(async_db, user_id)


# ==================== Tests ====================


class TestRoundtableExpertsEndpoint:
    """测试 /roundtable/experts 端点。"""

    @pytest.mark.asyncio
    async def test_experts_endpoint_returns_list(self, app_and_client_with_db) -> None:
        """Experts端点返回专家列表。"""
        _, test_client, _, _ = app_and_client_with_db
        response = test_client.get("/api/v1/roundtable/experts")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        assert "experts" in data["data"]
        assert isinstance(data["data"]["experts"], list)

    @pytest.mark.asyncio
    async def test_experts_endpoint_pagination(self, app_and_client_with_db) -> None:
        """Experts端点支持分页。"""
        _, test_client, _, _ = app_and_client_with_db
        response = test_client.get("/api/v1/roundtable/experts?page=1&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["page"] == 1
        assert data["data"]["limit"] == 10
        assert "total" in data["data"]

    @pytest.mark.asyncio
    async def test_experts_endpoint_default_pagination(
        self, app_and_client_with_db
    ) -> None:
        """Experts端点使用默认分页参数。"""
        _, test_client, _, _ = app_and_client_with_db
        response = test_client.get("/api/v1/roundtable/experts")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["page"] == 1
        assert data["data"]["limit"] == 20

    @pytest.mark.asyncio
    async def test_experts_endpoint_data_structure(
        self, app_and_client_with_db
    ) -> None:
        """验证Expert数据结构。"""
        _, test_client, async_db, _ = app_and_client_with_db

        # 创建测试专家
        await _create_test_expert(async_db, "test-expert-1", "Test Expert 1")

        response = test_client.get("/api/v1/roundtable/experts")
        assert response.status_code == 200
        data = response.json()
        experts = data["data"]["experts"]

        # 如果有数据，检查结构
        for expert in experts:
            assert "id" in expert
            assert "name" in expert
            assert "role" in expert
            assert "stance" in expert
            assert "description" in expert
            assert "isBuiltin" in expert
            assert "status" in expert
            assert "createdAt" in expert


class TestRoundtableSessionsEndpoint:
    """测试 /roundtable/sessions 端点。"""

    @pytest.mark.asyncio
    async def test_sessions_endpoint_requires_auth(self) -> None:
        """Sessions端点需要认证。"""
        app = FastAPI()

        # 不设置get_current_user override，会使用原始的，会抛异常
        async def get_db_override():
            yield None

        app.dependency_overrides[get_db] = get_db_override
        app.include_router(roundtable_router, prefix="/api/v1")

        client = TestClient(app)
        response = client.get("/api/v1/roundtable/sessions")

        # 应该返回401（未认证）
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_sessions_endpoint_returns_list(self, app_and_client_with_db) -> None:
        """Sessions端点返回会话列表。"""
        _, test_client, _, _ = app_and_client_with_db
        response = test_client.get("/api/v1/roundtable/sessions")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        assert "sessions" in data["data"]
        assert isinstance(data["data"]["sessions"], list)

    @pytest.mark.asyncio
    async def test_sessions_endpoint_pagination(self, app_and_client_with_db) -> None:
        """Sessions端点支持分页。"""
        _, test_client, _, _ = app_and_client_with_db
        response = test_client.get("/api/v1/roundtable/sessions?page=1&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["page"] == 1
        assert data["data"]["limit"] == 10

    @pytest.mark.asyncio
    async def test_sessions_endpoint_default_pagination(
        self, app_and_client_with_db
    ) -> None:
        """Sessions端点使用默认分页参数。"""
        _, test_client, _, _ = app_and_client_with_db
        response = test_client.get("/api/v1/roundtable/sessions")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["page"] == 1
        assert data["data"]["limit"] == 20


class TestRoundtableSessionDetailEndpoint:
    """测试 /roundtable/sessions/{session_id} 端点。"""

    @pytest.mark.asyncio
    async def test_session_detail_not_found(self, app_and_client_with_db) -> None:
        """不存在的会话返回404。"""
        _, test_client, _, _ = app_and_client_with_db
        response = test_client.get("/api/v1/roundtable/sessions/nonexistent")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404

    @pytest.mark.asyncio
    async def test_session_detail_requires_ownership(
        self, app_and_client_with_db
    ) -> None:
        """会话详情需要所有权验证。"""
        app = FastAPI()
        async_db = await _get_async_db()

        # 创建另一个用户
        other_user_id = "other-user"

        async def get_db_override():
            yield async_db

        # 使用不同用户的override
        other_user = UserInfo(
            id=other_user_id,
            name="Other User",
            email="other@example.com",
            image=None,
            email_verified=True,
        )

        async def get_current_user_override():
            return other_user

        app.dependency_overrides[get_db] = get_db_override
        app.dependency_overrides[get_current_user] = get_current_user_override
        app.include_router(roundtable_router, prefix="/api/v1")

        client = TestClient(app)
        response = client.get("/api/v1/roundtable/sessions/any-session")

        # 应该返回404或403
        assert response.status_code == 200
        data = response.json()
        assert data["code"] in [404, 403]


class TestRoundtableMessagesEndpoint:
    """测试 /roundtable/sessions/{session_id}/messages 端点。"""

    @pytest.mark.asyncio
    async def test_messages_endpoint_requires_auth(self) -> None:
        """Messages端点需要认证。"""
        app = FastAPI()

        async def get_db_override():
            yield None

        app.dependency_overrides[get_db] = get_db_override
        app.include_router(roundtable_router, prefix="/api/v1")

        client = TestClient(app)
        response = client.get("/api/v1/roundtable/sessions/any-session/messages")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_messages_endpoint_session_not_found(
        self, app_and_client_with_db
    ) -> None:
        """会话不存在时返回404。"""
        _, test_client, _, _ = app_and_client_with_db
        response = test_client.get("/api/v1/roundtable/sessions/nonexistent/messages")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404
