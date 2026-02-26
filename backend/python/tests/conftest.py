"""
共享测试 fixture。

运行前确保：
    1. PostgreSQL 已启动: brew services start postgresql@16
    2. Redis 已启动: brew services start redis
    3. wenexus_dev 数据库已创建
"""
import asyncio
import sys
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# 将 src 目录加入 Python path，使 wenexus 包可被 import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建一个 session 级别的事件循环。"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    异步 HTTP 测试客户端。

    使用方式:
        async def test_something(client: AsyncClient):
            response = await client.get("/health")
            assert response.status_code == 200
    """
    from wenexus.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[None, None]:
    """
    数据库 session fixture（集成测试用）。

    TODO: 实现事务回滚模式，每个测试运行在一个事务中，测试结束后回滚。
    """
    # from wenexus.db import async_session
    # async with async_session() as session:
    #     yield session
    #     await session.rollback()
    yield None
