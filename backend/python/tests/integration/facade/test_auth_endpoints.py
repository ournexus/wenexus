"""
集成测试：验证认证系统的完整Cookie传递和依赖注入流程。

测试场景：
  1. 通过TestClient模拟浏览器请求
  2. 测试 get_current_user 依赖（需要认证）
  3. 测试 get_optional_user 依赖（可选认证）
  4. 验证Cookie自动传递机制
  5. 测试异常流程（无token、无效token、过期token）

前置条件：
  1. PostgreSQL 已启动，wenexus_dev 数据库存在
  2. 测试创建真实的 user 和 session 记录
"""

from datetime import datetime, timedelta
from typing import Any

import pytest
import pytest_asyncio
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from starlette.testclient import TestClient

from wenexus.facade.deps import get_current_user, get_optional_user
from wenexus.repository.db import get_db
from wenexus.util.schema import UserInfo

# ==================== Fixtures ====================


@pytest_asyncio.fixture(scope="function")
async def async_db() -> AsyncSession:
    """创建真实数据库session，用于测试数据准备和验证。"""
    engine = create_async_engine(
        "postgresql+asyncpg://wenexus:wenexus_dev_pwd@localhost:5432/wenexus_dev",
        echo=False,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1, "Database connection failed"

    from sqlalchemy.ext.asyncio import async_sessionmaker

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


async def _setup_test_user(
    db: AsyncSession, user_id: str, is_expired: bool = False
) -> dict[str, Any]:
    """创建测试用户和session数据。"""
    token = f"test-session-token-{user_id}"

    # 清理旧数据
    async with db.begin():
        await db.execute(
            text('DELETE FROM "session" WHERE token = :token'), {"token": token}
        )
    await db.commit()

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
                "name": "Test User",
                "email": f"{user_id}@example.com",
                "email_verified": True,
                "image": None,
            },
        )
    await db.commit()

    # 创建session
    # 转换为本地时间（不带timezone）以匹配PostgreSQL时间戳列
    if is_expired:
        expires_at = datetime.now() - timedelta(hours=1)
    else:
        expires_at = datetime.now() + timedelta(hours=1)

    async with db.begin():
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

    return {
        "user_id": user_id,
        "token": token,
        "expires_at": expires_at,
    }


async def _cleanup_test_user(db: AsyncSession, user_id: str) -> None:
    """清理测试用户数据。"""
    async with db.begin():
        await db.execute(
            text('DELETE FROM "session" WHERE user_id = :user_id'), {"user_id": user_id}
        )
    await db.commit()

    async with db.begin():
        await db.execute(text('DELETE FROM "user" WHERE id = :id'), {"id": user_id})
    await db.commit()


@pytest_asyncio.fixture(scope="function")
async def test_user_data(async_db: AsyncSession) -> dict[str, Any]:
    """创建有效用户数据。"""
    user_id = "test-user-valid"
    data = await _setup_test_user(async_db, user_id)
    yield data
    # 清理
    try:
        await _cleanup_test_user(async_db, user_id)
    except Exception:
        pass


@pytest_asyncio.fixture(scope="function")
async def test_expired_token(async_db: AsyncSession) -> dict[str, Any]:
    """创建已过期token数据。"""
    user_id = "test-user-expired"
    data = await _setup_test_user(async_db, user_id, is_expired=True)
    yield data
    # 清理
    try:
        await _cleanup_test_user(async_db, user_id)
    except Exception:
        pass


@pytest_asyncio.fixture(scope="function")
async def app_with_test_endpoints(async_db: AsyncSession) -> FastAPI:
    """
    创建FastAPI应用，包含测试认证端点。

    这些端点专门用于测试认证依赖的行为。
    """
    app = FastAPI()

    # 重写 get_db 依赖，使其返回测试用的 async_db
    async def get_db_override():
        yield async_db

    app.dependency_overrides[get_db] = get_db_override

    # 测试端点：需要认证
    @app.get("/test/protected")
    async def protected_endpoint(
        user: UserInfo = Depends(get_current_user),
    ) -> dict[str, Any]:
        """需要认证的端点。"""
        return {
            "message": "Protected endpoint",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "image": user.image,
                "email_verified": user.email_verified,
            },
        }

    # 测试端点：可选认证
    @app.get("/test/public")
    async def public_endpoint(
        user: UserInfo | None = Depends(get_optional_user),
    ) -> dict[str, Any]:
        """可选认证的端点。"""
        if user is None:
            return {"message": "Public endpoint (no user)", "is_authenticated": False}
        return {
            "message": "Public endpoint (with user)",
            "is_authenticated": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "image": user.image,
                "email_verified": user.email_verified,
            },
        }

    return app


@pytest.fixture(scope="function")
def test_client(app_with_test_endpoints) -> TestClient:
    """创建FastAPI TestClient，用于发送HTTP请求。"""
    return TestClient(app_with_test_endpoints)


# ==================== Helper for creating app with db ====================


@pytest.fixture(scope="function")
async def app_and_client_with_db(async_db: AsyncSession) -> tuple[FastAPI, TestClient]:
    """创建FastAPI应用和TestClient，共享同一个async_db。"""
    app = FastAPI()

    # 重写 get_db 依赖
    async def get_db_override():
        yield async_db

    app.dependency_overrides[get_db] = get_db_override

    @app.get("/test/protected")
    async def protected_endpoint(
        user: UserInfo = Depends(get_current_user),
    ) -> dict[str, Any]:
        """需要认证的端点。"""
        return {
            "message": "Protected endpoint",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "image": user.image,
                "email_verified": user.email_verified,
            },
        }

    @app.get("/test/public")
    async def public_endpoint(
        user: UserInfo | None = Depends(get_optional_user),
    ) -> dict[str, Any]:
        """可选认证的端点。"""
        if user is None:
            return {"message": "Public endpoint (no user)", "is_authenticated": False}
        return {
            "message": "Public endpoint (with user)",
            "is_authenticated": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "image": user.image,
                "email_verified": user.email_verified,
            },
        }

    client = TestClient(app)
    return app, client


# ==================== Tests ====================


class TestAuthenticationFlow:
    """测试完整的认证流程和Cookie传递。"""

    @pytest.mark.asyncio
    async def test_protected_endpoint_with_valid_token(
        self,
        async_db: AsyncSession,
        app_and_client_with_db,
        test_user_data: dict[str, Any],
    ) -> None:
        """使用有效token访问受保护端点。"""
        _, test_client = app_and_client_with_db
        token = test_user_data["token"]
        user_id = test_user_data["user_id"]

        response = test_client.get(
            "/test/protected",
            cookies={"better-auth.session_token": token},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Protected endpoint"
        assert data["user"]["id"] == user_id
        assert data["user"]["name"] == "Test User"
        assert data["user"]["email_verified"] is True

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(
        self,
        app_and_client_with_db,
    ) -> None:
        """无token访问受保护端点返回401。"""
        _, test_client = app_and_client_with_db
        response = test_client.get("/test/protected")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_endpoint_with_invalid_token(
        self,
        app_and_client_with_db,
    ) -> None:
        """使用无效token访问受保护端点返回401。"""
        _, test_client = app_and_client_with_db
        response = test_client.get(
            "/test/protected",
            cookies={"better-auth.session_token": "invalid-token-xyz"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_endpoint_with_expired_token(
        self,
        app_and_client_with_db,
        test_expired_token: dict[str, Any],
    ) -> None:
        """使用过期token访问受保护端点返回401。"""
        _, test_client = app_and_client_with_db
        token = test_expired_token["token"]
        response = test_client.get(
            "/test/protected",
            cookies={"better-auth.session_token": token},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_public_endpoint_without_token(
        self,
        app_and_client_with_db,
    ) -> None:
        """无token访问公开端点返回user为None。"""
        _, test_client = app_and_client_with_db
        response = test_client.get("/test/public")
        assert response.status_code == 200
        data = response.json()
        assert data["is_authenticated"] is False

    @pytest.mark.asyncio
    async def test_public_endpoint_with_valid_token(
        self,
        app_and_client_with_db,
        test_user_data: dict[str, Any],
    ) -> None:
        """使用有效token访问公开端点返回用户信息。"""
        _, test_client = app_and_client_with_db
        token = test_user_data["token"]
        user_id = test_user_data["user_id"]

        response = test_client.get(
            "/test/public",
            cookies={"better-auth.session_token": token},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_authenticated"] is True
        assert data["user"]["id"] == user_id

    @pytest.mark.asyncio
    async def test_public_endpoint_with_invalid_token(
        self,
        app_and_client_with_db,
    ) -> None:
        """使用无效token访问公开端点返回None而非异常。"""
        _, test_client = app_and_client_with_db
        response = test_client.get(
            "/test/public",
            cookies={"better-auth.session_token": "invalid-token-xyz"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_authenticated"] is False


class TestCookieTransmission:
    """测试Cookie传递机制。"""

    @pytest.mark.asyncio
    async def test_cookie_name_must_match_exactly(
        self,
        app_and_client_with_db,
        test_user_data: dict[str, Any],
    ) -> None:
        """Cookie名称必须准确匹配 'better-auth.session_token'。"""
        _, test_client = app_and_client_with_db
        token = test_user_data["token"]

        response = test_client.get(
            "/test/protected",
            cookies={"session_token": token},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_cookie_name_is_case_sensitive(
        self,
        app_and_client_with_db,
        test_user_data: dict[str, Any],
    ) -> None:
        """Cookie名称区分大小写。"""
        _, test_client = app_and_client_with_db
        token = test_user_data["token"]

        response = test_client.get(
            "/test/protected",
            cookies={"Better-Auth.Session_Token": token},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_multiple_cookies_extraction(
        self,
        app_and_client_with_db,
        test_user_data: dict[str, Any],
    ) -> None:
        """在多个Cookie中正确提取session token。"""
        _, test_client = app_and_client_with_db
        token = test_user_data["token"]
        user_id = test_user_data["user_id"]

        response = test_client.get(
            "/test/protected",
            cookies={
                "other_cookie": "some_value",
                "better-auth.session_token": token,
                "another_cookie": "another_value",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["id"] == user_id


class TestUserInfoDataStructure:
    """测试UserInfo数据结构的正确性。"""

    @pytest.mark.asyncio
    async def test_user_info_all_fields_present(
        self,
        app_and_client_with_db,
        test_user_data: dict[str, Any],
    ) -> None:
        """UserInfo包含所有必要字段。"""
        _, test_client = app_and_client_with_db
        token = test_user_data["token"]

        response = test_client.get(
            "/test/protected",
            cookies={"better-auth.session_token": token},
        )

        assert response.status_code == 200
        user = response.json()["user"]

        assert "id" in user
        assert "name" in user
        assert "email" in user
        assert "image" in user
        assert "email_verified" in user

    @pytest.mark.asyncio
    async def test_user_info_email_verified_is_boolean(
        self,
        app_and_client_with_db,
        test_user_data: dict[str, Any],
    ) -> None:
        """email_verified字段是boolean类型。"""
        _, test_client = app_and_client_with_db
        token = test_user_data["token"]

        response = test_client.get(
            "/test/protected",
            cookies={"better-auth.session_token": token},
        )

        assert response.status_code == 200
        user = response.json()["user"]
        assert isinstance(user["email_verified"], bool)

    @pytest.mark.asyncio
    async def test_user_info_with_null_image(
        self,
        app_and_client_with_db,
        test_user_data: dict[str, Any],
    ) -> None:
        """image字段可以为null。"""
        _, test_client = app_and_client_with_db
        token = test_user_data["token"]

        response = test_client.get(
            "/test/protected",
            cookies={"better-auth.session_token": token},
        )

        assert response.status_code == 200
        user = response.json()["user"]
        assert user["image"] is None
