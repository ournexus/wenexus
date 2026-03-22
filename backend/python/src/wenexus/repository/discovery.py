"""
repository.discovery - Discovery 域数据库操作。

处理: topic 表的查询。

Depends: sqlalchemy
Consumers: app.discovery
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


async def find_public_topics(
    db: AsyncSession, page: int = 1, limit: int = 20
) -> list[dict]:
    """分页查询公开话题列表。"""
    offset = (page - 1) * limit

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

    return [
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
        for row in result
    ]
