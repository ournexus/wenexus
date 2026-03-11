"""
service.auth - 认证业务逻辑。

认证决策和会话管理，不接触 HTTP 也不写 SQL。

Depends: repository.auth, util.schema
Consumers: facade.deps
"""

from sqlalchemy.ext.asyncio import AsyncSession

from wenexus.repository.auth import delete_session, query_user_by_token
from wenexus.util.schema import UserInfo


async def authenticate(db: AsyncSession, token: str) -> UserInfo | None:
    """验证 session token，返回用户信息或 None（token 无效/过期）。"""
    return await query_user_by_token(db, token)


async def revoke_session(db: AsyncSession, session_id: str) -> None:
    """撤销指定的 session。"""
    await delete_session(db, session_id)
