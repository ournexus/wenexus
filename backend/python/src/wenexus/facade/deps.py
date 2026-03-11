"""
facade.deps - 共享 HTTP 依赖注入。

只处理 HTTP 关注点：cookie 提取、FastAPI Depends、HTTPException。
不包含业务逻辑或数据库查询。

Depends: fastapi, service.auth, repository.db, util.schema
Consumers: facade 路由模块 (roundtable, deliverable)
"""

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from wenexus.repository.db import get_db
from wenexus.service.auth import authenticate
from wenexus.util.schema import UserInfo


async def get_session_token(request: Request) -> str | None:
    """从 Cookie 中提取 better-auth session token。"""
    return request.cookies.get("better-auth.session_token")


async def get_current_user(
    token: str | None = Depends(get_session_token),
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> UserInfo:
    """要求认证的依赖：无有效 session 时抛出 401。"""
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    user = await authenticate(db, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )
    return user


async def get_optional_user(
    token: str | None = Depends(get_session_token),
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> UserInfo | None:
    """可选认证的依赖：无有效 session 时返回 None 而非抛异常。"""
    if token is None:
        return None
    return await authenticate(db, token)
