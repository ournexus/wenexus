"""
app.discovery - Discovery 域应用编排层。

编排 repository 完成业务用例。

Depends: repository.discovery
Consumers: facade.discovery
"""

from sqlalchemy.ext.asyncio import AsyncSession

from wenexus.repository.discovery import count_public_topics, find_public_topics


async def get_feed(db: AsyncSession, page: int = 1, limit: int = 20) -> dict:
    """获取发现页 Feed 数据。"""
    total = await count_public_topics(db)
    topics = await find_public_topics(db, page=page, limit=limit)

    cards = [
        {
            "topic": topic,
            "expertCount": topic.get("expertCount", 0),
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


async def list_topics(db: AsyncSession, page: int = 1, limit: int = 20) -> dict:
    """获取公开话题列表。"""
    total = await count_public_topics(db)
    topics = await find_public_topics(db, page=page, limit=limit)

    return {
        "code": 0,
        "data": {
            "topics": topics,
            "total": total,
            "page": page,
            "limit": limit,
        },
    }
