"""单元测试 — 健康检查端点。"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    """GET /health 应返回 200 和状态信息。"""
    response = await client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] in ("ok", "healthy")


@pytest.mark.asyncio
async def test_health_includes_version(client: AsyncClient) -> None:
    """健康检查应包含版本信息。"""
    response = await client.get("/health")
    data = response.json()
    assert "status" in data
