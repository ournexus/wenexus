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

### 2.2 Cookie 跨域传递：反向代理方案

浏览器的 Cookie 受同源策略约束。Next.js 和 FastAPI 运行在不同端口上，Cookie 默认不会跨端口发送。通过反向代理将两个服务统一到同一域名下解决此问题：

**部署环境**（Nginx/Caddy）：

```
wenexus.com/           → Next.js (port 3000)
wenexus.com/api/py/    → FastAPI (port 8000)
```

**开发环境**（Next.js rewrites 代理）：

```javascript
// next.config.js
async rewrites() {
  return [
    {
      source: '/api/py/:path*',
      destination: 'http://localhost:8000/api/py/:path*',
    },
  ];
}
```

开发时前端请求 `localhost:3000/api/py/*`，由 Next.js 代理转发到 FastAPI。Cookie 的 Domain 和 Path 天然匹配，无需 CORS 配置。

### 2.3 认证流程

```
Browser                    Next.js (better-auth)           Python FastAPI
  │                              │                              │
  │──── sign in ────────────────▶│                              │
  │◀─── Set-Cookie: ────────────│                              │
  │     better-auth.session_token│                              │
  │                              │                              │
  │──── /api/py/* ─────────────▶│──── proxy ──────────────────▶│
  │     Cookie 自动携带          │                    ┌────────┤
  │     (同域，无跨域问题)       │                    │ SELECT  │
  │                              │                    │ session │
  │                              │                    │ + user  │
  │                              │                    └────────┤
  │◀──── response ──────────────│◀────────────────────────────│
```

### 2.4 实现设计

**分层结构**：认证功能按项目分层架构拆分为四个模块：

| 模块 | 文件 | 职责 |
|------|------|------|
| `util.schema` | `util/schema.py` | `UserInfo` DTO，跨层共享 |
| `repository.auth` | `repository/auth.py` | 纯 SQL 查询，读取 session/user 表 |
| `service.auth` | `service/auth.py` | 认证业务逻辑，不接触 HTTP 也不写 SQL |
| `facade.deps` | `facade/deps.py` | HTTP 依赖注入，Cookie 提取、HTTPException |

**Session 验证查询**（`repository/auth.py`）：

```sql
SELECT u.id, u.name, u.email, u.image, u."emailVerified"
FROM "session" s
JOIN "user" u ON s."userId" = u.id
WHERE s.token = :token
  AND s."expiresAt" > NOW()
```

> 注意：better-auth 使用 camelCase 列名（如 `"expiresAt"`、`"userId"`），
> 需用双引号引用以保留大小写。`"emailVerified"` 是 timestamp 类型，
> Python 端通过 `is not None` 转换为 `bool`。

**数据传输对象**（`util/schema.py`）：

```python
@dataclass
class UserInfo:
    """认证用户信息，从 better-auth session 表查询得到。"""
    id: str
    name: str
    email: str
    image: str | None
    email_verified: bool
```

**Repository 层**（`repository/auth.py`）：

```python
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
        email_verified=row.emailVerified is not None,
    )
```

**Facade 层依赖注入**（`facade/deps.py`）：

```python
async def get_session_token(request: Request) -> str | None:
    """从 Cookie 中提取 better-auth session token。"""
    return request.cookies.get("better-auth.session_token")

async def get_current_user(
    token: str | None = Depends(get_session_token),
    db: AsyncSession = Depends(get_db),
) -> UserInfo:
    """要求认证的依赖：无有效 session 时抛出 401。"""
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, ...)
    user = await authenticate(db, token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, ...)
    return user

async def get_optional_user(
    token: str | None = Depends(get_session_token),
    db: AsyncSession = Depends(get_db),
) -> UserInfo | None:
    """可选认证的依赖：无有效 session 时返回 None 而非抛异常。"""
    if token is None:
        return None
    return await authenticate(db, token)
```

**Session 吊销**（`service/auth.py` → `repository/auth.py`）：

```python
# repository/auth.py
async def delete_session(db: AsyncSession, session_id: str) -> None:
    """删除指定的 session 记录。"""
    await db.execute(text('DELETE FROM "session" WHERE id = :session_id'), {"session_id": session_id})
    await db.commit()

# service/auth.py
async def revoke_session(db: AsyncSession, session_id: str) -> None:
    """撤销指定的 session。"""
    await delete_session(db, session_id)
```

**路由使用示例**：

```python
@router.get("/api/py/v1/profile")
async def get_profile(user: UserInfo = Depends(get_current_user)):
    """需要登录的端点。"""
    return {"user": user}

@router.get("/api/py/v1/feed")
async def get_feed(user: UserInfo | None = Depends(get_optional_user)):
    """公开端点，登录用户有个性化内容。"""
    return {"personalized": user is not None}
```

### 2.5 Session 续期策略

**设计决策**：Python 端不负责 session 续期。

理由：better-auth 在 Next.js 侧自动续期 session（每次 `getSession` 调用时更新 `expiresAt`）。前端 SPA 通过 `client.ts` 中的节流 fetch 定期调用 Next.js session 端点，已覆盖续期需求。当前产品形态下不存在"只访问 Python API 而不访问前端"的场景。

### 2.6 数据库 Schema 注意事项

- Python 端使用 `text()` 原生 SQL 查询 session 表，不定义 ORM 模型（避免与 Drizzle schema 维护两套）
- 如果前端配置了非 `public` schema（通过 `db_schema` 配置），Python 端查询需加 schema 前缀：`{schema}.session`
- Session token 字段有 unique 索引，查询性能不是问题
- 基线阶段不加 session 验证缓存；后续如有性能瓶颈，可引入 `cachetools.TTLCache`（TTL 30s）做进程内缓存

**Schema 兼容性保障**：通过集成测试验证 Python 端 SQL 与实际表结构一致：

```python
# tests/test_auth_schema.py
async def test_session_query_matches_schema(db):
    """确保 auth 查询与实际 schema 兼容，Drizzle 迁移后此测试会检测到不兼容变更。"""
    result = await db.execute(text("""
        SELECT u.id, u.name, u.email, u.image, u."emailVerified"
        FROM "session" s JOIN "user" u ON s."userId" = u.id
        LIMIT 0
    """))
    assert set(result.keys()) == {"id", "name", "email", "image", "emailVerified"}
```

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

**CSRF 防护**：流程中的 `state` 参数由 better-auth 框架自动生成、存储和验证，无需手动处理。

### 3.2 实现方式：Generic OAuth Plugin

使用 better-auth 的 [Generic OAuth Plugin](https://www.better-auth.com/docs/plugins/generic-oauth) 接入微信，而非直接在 `socialProviders` 中硬编码。Generic OAuth Plugin 提供更完整的自定义能力（token 交换、token 刷新、类型安全的 profile 映射）。

**微信 Profile 类型定义**：

```typescript
// frontend/apps/web/src/core/auth/types.ts

interface WeChatProfile {
  openid: string;
  unionid?: string;
  nickname: string;
  headimgurl: string;
  sex: number;
  province: string;
  city: string;
  country: string;
  privilege: string[];
}
```

**Generic OAuth 配置**：

```typescript
// frontend/apps/web/src/core/auth/config.ts — plugins 数组

import { genericOAuth } from "better-auth/plugins/generic-oauth";

// 在 getAuthOptions() 的 plugins 数组中添加：
if (configs.wechat_app_id && configs.wechat_app_secret) {
  plugins.push(
    genericOAuth({
      providerId: "wechat",
      clientId: configs.wechat_app_id,
      clientSecret: configs.wechat_app_secret,
      authorizationUrl: "https://open.weixin.qq.com/connect/qrconnect",
      tokenUrl: "https://api.weixin.qq.com/sns/oauth2/access_token",
      userInfoUrl: "https://api.weixin.qq.com/sns/userinfo",
      scopes: ["snsapi_login"],
      redirectURI: `${envConfigs.app_url}/api/auth/callback/wechat`,

      // 微信 token 端点使用 appid/secret 而非标准 client_id/client_secret
      // 返回值的 raw 字段保存完整响应（含 openid/unionid），供 getUserInfo 使用
      getToken: async ({ code, redirectURI }) => {
        const url = new URL("https://api.weixin.qq.com/sns/oauth2/access_token");
        url.searchParams.set("appid", configs.wechat_app_id!);
        url.searchParams.set("secret", configs.wechat_app_secret!);
        url.searchParams.set("code", code);
        url.searchParams.set("grant_type", "authorization_code");
        const res = await fetch(url);
        const data = await res.json();
        return {
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          accessTokenExpiresAt: new Date(Date.now() + data.expires_in * 1000),
          raw: data, // 保留 openid、unionid 等微信特有字段
        };
      },

      // 微信 userinfo 需要 access_token + openid 两个参数
      // openid 从 getToken 返回的 raw 字段中获取
      getUserInfo: async (tokens) => {
        const openid = (tokens.raw as Record<string, string>)?.openid || "";
        const url = new URL("https://api.weixin.qq.com/sns/userinfo");
        url.searchParams.set("access_token", tokens.accessToken!);
        url.searchParams.set("openid", openid);
        const res = await fetch(url);
        const profile: WeChatProfile = await res.json();
        return {
          id: profile.unionid || profile.openid,
          name: profile.nickname,
          image: profile.headimgurl,
          email: `wx_${profile.unionid || profile.openid}@wechat.placeholder`,
          emailVerified: false,
          raw: profile,
        };
      },

      // 微信 access_token 2 小时过期，支持刷新
      refreshAccessToken: async (refreshToken) => {
        const url = new URL("https://api.weixin.qq.com/sns/oauth2/refresh_token");
        url.searchParams.set("appid", configs.wechat_app_id!);
        url.searchParams.set("grant_type", "refresh_token");
        url.searchParams.set("refresh_token", refreshToken);
        const res = await fetch(url);
        const data = await res.json();
        return {
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          accessTokenExpiresAt: new Date(Date.now() + data.expires_in * 1000),
        };
      },

      // 授权 URL 需要 appid 而非 client_id
      // 注意：better-auth 会自动附加 client_id 参数，微信端点会同时收到 client_id 和 appid
      // 微信服务器优先识别 appid，忽略未知的 client_id 参数（需实际验证）
      authorizationUrlParams: {
        appid: configs.wechat_app_id!,
      },
    })
  );
}
```

### 3.3 Placeholder Email 策略

**背景**：`user.email` 字段为 `notNull().unique()`，微信用户无 email。

**方案**：使用确定性格式的 placeholder email：

```
wx_{unionid|openid}@wechat.placeholder
```

- 优先使用 `unionid`（跨微信应用唯一），fallback 到 `openid`
- 前缀 `wx_` 避免与真实 email 格式冲突
- 域名 `wechat.placeholder` 不可能是真实邮箱域名

**邮件发送过滤**：所有发送邮件的逻辑中需检查 placeholder：

```typescript
// 邮件发送前
if (user.email.endsWith("@wechat.placeholder")) return;
```

**后续优化**：如果接入更多无 email 的 provider（手机号登录等），应评估将 `email` 改为 nullable 的可行性。

### 3.4 配置项

| 配置项 | 来源 | 说明 |
|--------|------|------|
| `wechat_app_id` | 微信开放平台 → 网站应用 → AppID | 应用唯一标识 |
| `wechat_app_secret` | 微信开放平台 → 网站应用 → AppSecret | 应用密钥 |

前置条件：在 [微信开放平台](https://open.weixin.qq.com/) 注册网站应用，完成审核，配置回调域名。

### 3.5 数据库复用

微信登录复用现有 `account` 表：

| 字段 | 值 |
|------|-----|
| `providerId` | `'wechat'` |
| `accountId` | 微信 unionid 或 openid |
| `accessToken` | 微信 access_token（2 小时有效） |
| `refreshToken` | 微信 refresh_token（30 天有效） |
| `accessTokenExpiresAt` | access_token 过期时间 |
| `refreshTokenExpiresAt` | refresh_token 过期时间 |

一个用户可同时绑定多个 provider（Google + GitHub + WeChat），通过 `account.userId` 关联到同一个 `user` 记录。

### 3.6 账号关联

better-auth 内置账号关联能力：

| 端点 | 用途 |
|------|------|
| `/link-social` | 已登录用户绑定新的 OAuth provider |
| `/unlink-account` | 解除某个 provider 的关联 |
| `/list-accounts` | 列出当前用户已关联的所有 provider |

**用户流程**：

1. **首次微信登录**：创建新账号（带 placeholder email）
2. **已登录用户绑定微信**：通过设置页调用 `/link-social`，将微信关联到已有账号
3. **引导补充信息**：微信登录后如果检测到 placeholder email，前端引导用户补充真实邮箱或关联已有账号

### 3.7 前端集成

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
