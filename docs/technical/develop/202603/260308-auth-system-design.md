# WeNexus 用户登录体系技术设计

## 一、现有认证体系现状

### 1.1 技术栈

- **认证框架**：[better-auth](https://www.better-auth.com/) — TypeScript-first 的全栈认证库
- **数据库适配**：Drizzle ORM + PostgreSQL（通过 `drizzleAdapter` 桥接）
- **运行环境**：Next.js App Router（服务端 + 客户端双模式）

### 1.2 已支持的认证方式

| 方式 | 状态 | 配置项 |
|------|------|--------|
| Email/Password | 已实现 | `email_auth_enabled`、`email_verification_enabled` |
| Google OAuth | 已实现 | `google_client_id`、`google_client_secret` |
| GitHub OAuth | 已实现 | `github_client_id`、`github_client_secret` |
| Google One Tap | 已实现 | `google_client_id`、`google_one_tap_enabled` |

- Email 验证可选开启，需配合 Resend API（`resend_api_key`）
- 验证邮件发送有服务端去重（60s 内同一邮箱不重复发送）
- One Tap 作为 better-auth plugin 在客户端加载（`oneTapClient`）

### 1.3 RBAC 权限体系

**4 个预定义角色**：

| 角色 | 用途 |
|------|------|
| `super_admin` | 超级管理员，拥有所有权限 |
| `admin` | 管理员 |
| `editor` | 编辑者 |
| `viewer` | 只读查看者 |

**权限通配机制**（层级匹配）：

```
权限码格式：{domain}.{resource}.{action}
示例：admin.posts.edit

匹配规则（按优先级）：
1. 精确匹配：admin.posts.edit
2. 层级通配：admin.posts.* → admin.*
3. 全局通配：* （super_admin 拥有）
```

新用户注册时自动通过 `grantRoleForNewUser()` 分配默认角色。

### 1.4 Credits 系统

- 新用户注册后自动授予初始积分（可配置）
- 配置项：`initial_credits_enabled`、`initial_credits_amount`、`initial_credits_valid_days`
- 交易类型：`grant`（授予）/ `consume`（消耗）
- 交易场景：`payment` / `subscription` / `renewal` / `gift` / `reward`
- 新用户初始积分场景为 `gift`

### 1.5 数据库表结构

认证相关的核心表（定义于 `schema.postgres.ts`）：

| 表名 | 用途 | 关键字段 |
|------|------|----------|
| `user` | 用户主表 | id, name, email, emailVerified, image, utmSource, ip, locale |
| `session` | 会话管理 | id, token (unique), expiresAt, userId, ipAddress, userAgent |
| `account` | OAuth 账号关联 | providerId, accountId, userId, accessToken, refreshToken, password |
| `verification` | 邮箱验证码 | identifier, value, expiresAt |
| `role` | 角色定义 | name (unique), title, status |
| `permission` | 权限定义 | code (unique), resource, action |
| `role_permission` | 角色-权限关联 | roleId, permissionId |
| `user_role` | 用户-角色关联 | userId, roleId, expiresAt |
| `apikey` | API Key | userId, key, title, status |
| `credit` | 积分流水 | userId, transactionType, credits, remainingCredits, expiresAt |

### 1.6 中间件路由保护

Next.js middleware（`src/middleware.ts`）对以下路径强制要求 session cookie：

- `/admin/*` — 管理后台
- `/settings/*` — 用户设置
- `/activity/*` — 用户活动

未登录用户被重定向到 `/sign-in?callbackUrl={原路径}`。

中间件仅做轻量级 cookie 存在检查，完整的 RBAC 权限校验在页面/API 层通过 `requirePermission()` 执行。

### 1.7 关键文件索引

```
frontend/apps/web/src/
├── core/auth/
│   ├── config.ts          # Auth 配置：providers、plugins、databaseHooks
│   ├── client.ts          # 客户端 Auth：createAuthClient、session 节流
│   └── index.ts           # 服务端 Auth 实例：getAuth()
├── config/db/
│   └── schema.postgres.ts # 全量数据库 Schema（含认证表）
├── middleware.ts           # 路由保护中间件
└── shared/
    ├── services/rbac.ts   # RBAC：角色定义、权限通配匹配、grantRoleForNewUser
    └── models/credit.ts   # Credits：授予/消耗逻辑、grantCreditsForNewUser
```

## 二、Python 后端认证集成方案

### 2.1 方案选型：共享数据库 Session 验证

**选择理由**：

- 基线阶段 Next.js 和 Python FastAPI 共享同一个 PostgreSQL 数据库
- Python 直接读取 better-auth 写入的 `session` 表验证请求
- 零额外基础设施依赖（无需 Redis、JWT 签名密钥同步等）
- Python 后端已有 SQLAlchemy + asyncpg 依赖（见 `pyproject.toml`）

**不选 JWT 的原因**：better-auth 默认使用 session-based 认证（不是 JWT），强行引入 JWT 需要在 Next.js 侧额外配置 token 签发，增加复杂度。

### 2.2 认证流程

```
Browser                    Next.js (better-auth)           Python FastAPI
  │                              │                              │
  │──── sign in ────────────────▶│                              │
  │◀─── Set-Cookie: ────────────│                              │
  │     better-auth.session_token│                              │
  │                              │                              │
  │──── API request ─────────────────────────────────────────▶│
  │     Cookie: better-auth.session_token                      │
  │                              │                    ┌────────┤
  │                              │                    │ SELECT  │
  │                              │                    │ session │
  │                              │                    │ + user  │
  │                              │                    └────────┤
  │◀──── response ───────────────────────────────────────────│
```

### 2.3 实现设计

**Session 验证查询**：

```sql
SELECT
  s.id AS session_id,
  s.user_id,
  s.expires_at,
  u.name,
  u.email,
  u.image,
  u.email_verified
FROM session s
JOIN "user" u ON u.id = s.user_id
WHERE s.token = :token
  AND s.expires_at > NOW()
LIMIT 1;
```

**FastAPI 依赖注入**：

```python
# src/core/auth.py

from fastapi import Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

async def get_session_token(request: Request) -> str | None:
    """从 Cookie 中提取 better-auth session token。"""
    return request.cookies.get("better-auth.session_token")

async def get_current_user(
    token: str | None = Depends(get_session_token),
    db: AsyncSession = Depends(get_db),
) -> UserInfo:
    """验证 session 并返回用户信息。必须登录。"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.execute(
        text("""
            SELECT s.user_id, u.name, u.email, u.image, u.email_verified
            FROM session s JOIN "user" u ON u.id = s.user_id
            WHERE s.token = :token AND s.expires_at > NOW()
            LIMIT 1
        """),
        {"token": token},
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return UserInfo(
        id=row.user_id,
        name=row.name,
        email=row.email,
        image=row.image,
        email_verified=row.email_verified,
    )

async def get_optional_user(
    token: str | None = Depends(get_session_token),
    db: AsyncSession = Depends(get_db),
) -> UserInfo | None:
    """可选认证：未登录返回 None，不抛异常。"""
    if not token:
        return None
    # ... 同上查询逻辑，无结果返回 None
```

**路由使用示例**：

```python
@router.get("/api/v1/profile")
async def get_profile(user: UserInfo = Depends(get_current_user)):
    """需要登录的端点。"""
    return {"user": user}

@router.get("/api/v1/feed")
async def get_feed(user: UserInfo | None = Depends(get_optional_user)):
    """公开端点，登录用户有个性化内容。"""
    return {"personalized": user is not None}
```

### 2.4 数据库 Schema 注意事项

- Python 端使用 `text()` 原生 SQL 查询 session 表，不定义 ORM 模型（避免与 Drizzle schema 维护两套）
- 如果前端配置了非 `public` schema（通过 `db_schema` 配置），Python 端查询需加 schema 前缀：`{schema}.session`
- Session token 字段有 unique 索引，查询性能不是问题

## 三、微信登录集成方案

### 3.1 微信开放平台 OAuth2.0 流程

微信 Web 扫码登录遵循标准 OAuth2.0 授权码流程：

```
Browser                    WeNexus Server              微信开放平台
  │                              │                         │
  │── 点击"微信登录" ──────────▶│                         │
  │◀─ redirect ─────────────────│                         │
  │   open.weixin.qq.com/       │                         │
  │   connect/qrconnect         │                         │
  │                              │                         │
  │── 用户扫码确认 ──────────────────────────────────────▶│
  │◀─ redirect callback ────────────────────────────────│
  │   ?code=xxx&state=yyy        │                         │
  │                              │                         │
  │──────────────────────────▶│── code 换 access_token ──▶│
  │                              │◀─ access_token + openid ─│
  │                              │── 获取用户信息 ──────────▶│
  │                              │◀─ nickname, avatar ──────│
  │◀─ 登录成功，Set-Cookie ─────│                         │
```

### 3.2 better-auth 自定义社交 Provider

在 `getSocialProviders()` 中新增 wechat provider：

```typescript
// frontend/apps/web/src/core/auth/config.ts — getSocialProviders()

if (configs.wechat_app_id && configs.wechat_app_secret) {
  providers.wechat = {
    clientId: configs.wechat_app_id,
    clientSecret: configs.wechat_app_secret,
    // 微信 OAuth 端点
    authorizationUrl: "https://open.weixin.qq.com/connect/qrconnect",
    tokenUrl: "https://api.weixin.qq.com/sns/oauth2/access_token",
    userInfoUrl: "https://api.weixin.qq.com/sns/userinfo",
    // 微信特殊参数映射
    redirectURI: `${envConfigs.app_url}/api/auth/callback/wechat`,
    scopes: ["snsapi_login"],
    // 微信返回字段映射到 better-auth user
    mapProfileToUser: (profile: any) => ({
      name: profile.nickname,
      image: profile.headimgurl,
      // 微信无 email，使用 openid 作为唯一标识
      email: `${profile.openid}@wechat.placeholder`,
    }),
  };
}
```

### 3.3 配置项

| 配置项 | 来源 | 说明 |
|--------|------|------|
| `wechat_app_id` | 微信开放平台 → 网站应用 → AppID | 应用唯一标识 |
| `wechat_app_secret` | 微信开放平台 → 网站应用 → AppSecret | 应用密钥 |

前置条件：在 [微信开放平台](https://open.weixin.qq.com/) 注册网站应用，完成审核，配置回调域名。

### 3.4 数据库复用

微信登录复用现有 `account` 表：

| 字段 | 值 |
|------|-----|
| `providerId` | `'wechat'` |
| `accountId` | 微信 openid |
| `accessToken` | 微信 access_token |
| `refreshToken` | 微信 refresh_token |

一个用户可同时绑定多个 provider（Google + GitHub + WeChat），通过 `account.userId` 关联到同一个 `user` 记录。

### 3.5 前端集成

客户端通过 `authClient.signIn.social({ provider: "wechat" })` 触发微信登录流程，与 Google/GitHub OAuth 使用方式一致。

## 四、与 Identity 域的映射关系

### 4.1 认证 vs 身份

认证（Authentication）是基础设施层，解决"你是谁"的问题。Identity 域是业务层，解决"你的社交画像是什么"的问题。

```
┌─────────────────────────────────────────────┐
│  Identity Domain (业务层)                     │
│  UserProfile 聚合根                           │
│  ├── backgroundSummary (职业背景)             │
│  ├── preferences (偏好设置)                   │
│  ├── socialLinks (社交链接)                   │
│  └── ... (未来扩展)                           │
├─────────────────────────────────────────────┤
│  Auth Infrastructure (基础设施层)              │
│  better-auth 管理的表                         │
│  ├── user (基础信息：name, email, image)      │
│  ├── session (会话)                           │
│  ├── account (OAuth 关联)                     │
│  └── user_role (角色)                         │
└─────────────────────────────────────────────┘
```

### 4.2 当前状态与扩展规划

**现在**：`user` 表是 UserProfile 聚合根的基础数据来源，提供 name、email、image 等基础字段。

**未来**：Identity 域实现时，新建 `user_profile` 表（或扩展字段），存储 backgroundSummary、preferences 等业务数据。通过 `user.id` 外键关联。

**原则**：不在 `user` 表上堆积业务字段。认证表由 better-auth 管理，业务扩展通过独立表实现。
