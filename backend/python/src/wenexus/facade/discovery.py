"""
facade.discovery - Discovery 域 API 端点。

薄 HTTP 适配层：解析请求参数，委托 app 层处理，返回响应。

Depends: fastapi, app.discovery
Consumers: main (router inclusion)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from wenexus.app.discovery import get_feed, list_topics
from wenexus.repository.db import get_db

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.get("/feed")
async def get_feed_endpoint(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict:
    """获取发现页 Feed 数据。"""
    return await get_feed(db, page=page, limit=limit)


@router.get("/topics")
async def get_topics_endpoint(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict:
    """获取公开话题列表。"""
    return await list_topics(db, page=page, limit=limit)
