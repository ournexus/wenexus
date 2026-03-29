"""
facade.deps - 共享 HTTP 依赖注入。

只处理 HTTP 关注点：cookie 提取、FastAPI Depends、HTTPException。
不包含业务逻辑或数据库查询。

Depends: fastapi, service.auth, repository.db, util.schema
Consumers: facade 路由模块 (roundtable, deliverable)
"""

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

_CODE_TO_STATUS: dict[int, int] = {
    400: status.HTTP_400_BAD_REQUEST,
    403: status.HTTP_403_FORBIDDEN,
    404: status.HTTP_404_NOT_FOUND,
    409: status.HTTP_409_CONFLICT,
    422: status.HTTP_422_UNPROCESSABLE_ENTITY,
}


def raise_if_error(result: dict) -> dict:
    """如果 app 层返回错误码，转换为对应 HTTP 异常；否则原样返回。"""
    code = result.get("code", 0)
    if code != 0:
        http_status = _CODE_TO_STATUS.get(code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise HTTPException(
            status_code=http_status, detail=result.get("message", "Error")
        )
    return result


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
