"""
repository.auth - 认证相关的数据库查询。

纯 SQL 查询层，不包含业务逻辑。
通过共享 PostgreSQL 读取 better-auth 写入的 session/user 表。

Depends: sqlalchemy, util.schema
Consumers: service.auth
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from wenexus.util.schema import UserInfo

_SESSION_QUERY = text("""
    SELECT u.id, u.name, u.email, u.image, u.email_verified
    FROM "session" s
    JOIN "user" u ON s.user_id = u.id
    WHERE s.token = :token
      AND s.expires_at > NOW()
""")

_DELETE_SESSION = text("""
    DELETE FROM "session" WHERE id = :session_id
""")


async def query_user_by_token(db: AsyncSession, token: str) -> UserInfo | None:
    """根据 session token 查询用户信息，token 过期则返回 None。"""
    result = await db.execute(_SESSION_QUERY, {"token": token})
    row = result.first()
    if row is None:
        return None
    return UserInfo(
        id=row.id,
        name=row.name,
        email=row.email,
        image=row.image,
        email_verified=row.email_verified if row.email_verified is not None else False,
    )


async def delete_session(db: AsyncSession, session_id: str) -> None:
    """删除指定的 session 记录。"""
    await db.execute(_DELETE_SESSION, {"session_id": session_id})
    await db.commit()
