"""
util.schema - 跨层共享的数据传输对象 (DTO)。

UserInfo 被 facade、service、repository 三层使用，
放在 util 层避免任何反向依赖。

Depends: (none)
Consumers: facade.deps, service.auth, repository.auth
"""

from dataclasses import dataclass


@dataclass
class UserInfo:
    """认证用户信息，从 better-auth session 表查询得到。"""

    id: str
    name: str
    email: str
    image: str | None
    email_verified: bool
