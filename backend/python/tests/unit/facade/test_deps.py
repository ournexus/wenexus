"""Tests for facade.deps: session token extraction and auth dependencies."""

from fastapi import Depends, FastAPI
from starlette.testclient import TestClient

from wenexus.facade.deps import get_session_token


def _make_app() -> FastAPI:
    """创建一个最小的 FastAPI 应用，用于测试 auth 依赖。"""
    app = FastAPI()

    @app.get("/test-token")
    async def test_token(token: str | None = Depends(get_session_token)):
        return {"token": token}

    return app


class TestGetSessionToken:
    """测试 get_session_token 从 Request cookie 中提取 better-auth session token。"""

    def test_returns_token_when_cookie_present(self) -> None:
        """有 better-auth.session_token cookie 时，返回 token 值。"""
        app = _make_app()
        client = TestClient(app)
        response = client.get(
            "/test-token",
            cookies={"better-auth.session_token": "abc123"},
        )
        assert response.status_code == 200
        assert response.json()["token"] == "abc123"

    def test_returns_none_when_no_cookie(self) -> None:
        """没有 cookie 时，返回 None。"""
        app = _make_app()
        client = TestClient(app)
        response = client.get("/test-token")
        assert response.status_code == 200
        assert response.json()["token"] is None

    def test_returns_none_when_wrong_cookie_name(self) -> None:
        """cookie 名称不对时，返回 None。"""
        app = _make_app()
        client = TestClient(app)
        response = client.get(
            "/test-token",
            cookies={"some-other-cookie": "abc123"},
        )
        assert response.status_code == 200
        assert response.json()["token"] is None
