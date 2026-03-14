"""
service.discovery - Discovery 域服务层。

实现 topic 和 feed 的业务逻辑，包括查询、过滤、排序等。

Depends: repository.discovery, util.schema
Consumers: facade.discovery
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def count_public_topics(db: AsyncSession) -> int:
    """获取公开活跃话题总数。"""
    result = await db.execute(
        text("""
            SELECT COUNT(*) FROM topic
            WHERE visibility = 'public' AND status = 'active'
        """)
    )
    return result.scalar() or 0


async def get_public_topics(
    db: AsyncSession, page: int = 1, limit: int = 20
) -> list[dict]:
    """获取公开话题列表。"""
    offset = (page - 1) * limit

    # 从数据库获取公开话题
    result = await db.execute(
        text(
            """
        SELECT id, title, description, type, status, consensus_level,
               participant_count, tags, created_at
        FROM topic
        WHERE visibility = 'public' AND status = 'active'
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
    """
        ),
        {"limit": limit, "offset": offset},
    )

    topics = []
    for row in result:
        topics.append(
            {
                "id": row.id,
                "title": row.title,
                "description": row.description,
                "type": row.type,
                "status": row.status,
                "consensusLevel": row.consensus_level or 0,
                "participantCount": row.participant_count or 0,
                "tags": row.tags,
                "createdAt": row.created_at.isoformat() if row.created_at else None,
            }
        )

    return topics
