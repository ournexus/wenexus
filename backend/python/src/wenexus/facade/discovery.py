"""
facade.discovery - Discovery 域 API 端点。

Depends: fastapi, service.discovery, repository.db
Consumers: main (router inclusion)
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from wenexus.repository.db import get_db
from wenexus.service.discovery import get_public_topics

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.get("/feed")
async def get_feed(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """获取发现页 Feed 数据。

    Args:
        page: 分页页码，从 1 开始
        limit: 每页数量，默认 20
        db: 数据库 session

    Returns:
        {
            "code": 0,
            "data": {
                "cards": [
                    {
                        "topic": {...},
                        "expertCount": 0,
                        "consensusLevel": 0
                    },
                    ...
                ],
                "total": 100,
                "page": 1,
                "limit": 20
            }
        }
    """
    # 获取符合条件的总记录数
    total_result = await db.execute(
        text("""
            SELECT COUNT(*) as count
            FROM topic
            WHERE visibility = 'public' AND status = 'active'
        """)
    )
    total = total_result.scalar() or 0

    topics = await get_public_topics(db, page=page, limit=limit)

    # 转换为前端期望的格式
    cards = [
        {
            "topic": topic,
            "expertCount": 0,  # TODO: 从 roundtable 域获取
            "consensusLevel": topic.get("consensusLevel", 0),
        }
        for topic in topics
    ]

    return {
        "code": 0,
        "data": {
            "cards": cards,
            "total": total,
            "page": page,
            "limit": limit,
        },
    }


@router.get("/topics")
async def get_topics(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """获取公开话题列表。

    这是更基础的端点，不包含 feed 的额外信息。

    Args:
        page: 分页页码
        limit: 每页数量
        db: 数据库 session

    Returns:
        {
            "code": 0,
            "data": {
                "topics": [...],
                "total": 100,
                "page": 1,
                "limit": 20
            }
        }
    """
    # 获取符合条件的总记录数
    total_result = await db.execute(
        text("""
            SELECT COUNT(*) as count
            FROM topic
            WHERE visibility = 'public' AND status = 'active'
        """)
    )
    total = total_result.scalar() or 0

    topics = await get_public_topics(db, page=page, limit=limit)

    return {
        "code": 0,
        "data": {
            "topics": topics,
            "total": total,
            "page": page,
            "limit": limit,
        },
    }
