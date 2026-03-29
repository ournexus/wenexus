# 微信登录接入技术方案

> 本文档合并自 `260308-auth-system-design.md § 三` 的调研结论与初版方案草稿，
> 作为微信登录的唯一权威设计文档。

---

## 一、平台选型与约束

### 1.1 微信 Web 登录方式对比

| 方式 | 平台 | 场景 | Scope |
|------|------|------|-------|
| 网页扫码登录 | 微信开放平台 · 网站应用 | PC / Web | `snsapi_login` |
| 公众号网页授权 | 微信公众平台 · 公众号 | 微信内浏览器 H5 | `snsapi_base` / `snsapi_userinfo` |

**当前项目选择：网站应用扫码登录**（用户用手机扫 PC 上的二维码）。

前提条件：

- 在 [微信开放平台](https://open.weixin.qq.com) 注册并**完成审核**网站应用（~7 个工作日）
- 配置授权回调域名（仅填域名，不含路径）：`your-domain.com`
- 本地开发需公网可达的域名（ngrok / Cloudflare Tunnel），微信不允许 `localhost`

### 1.2 与 Google / GitHub OAuth 的关键差异

| 对比点 | Google / GitHub | 微信 |
|--------|-----------------|------|
| 应用注册 | 无需审核，即时生效 | 人工审核 ~7 天 |
| OAuth 标准合规 | 标准 OAuth 2.0 | **非标准**：token 端点用 `appid`/`secret`，非 `client_id`/`client_secret` |
| 用户唯一标识 | email | `openid`（无 email） |
| 用户信息 | 直接从 token 响应获取 | 需额外请求 `/sns/userinfo`，且需 `access_token` + `openid` 双参数 |
| Token 有效期 | 长期 | `access_token` 2 小时，`refresh_token` 30 天 |

### 1.3 实现方案选择：Generic OAuth Plugin

**不使用** `socialProviders.wechat`（better-auth 内置方式），原因：

- 微信 token 端点不接受标准 `client_id` / `client_secret` 参数，必须用 `appid` / `secret`
- 微信 userinfo 接口需要 `openid` 参数（从 token 响应中取），标准流程无法自动传递
- Generic OAuth Plugin 提供 `getToken` / `getUserInfo` / `refreshAccessToken` 自定义钩子，
  可精确控制每个非标准步骤

---

## 二、数据流

### 2.1 完整 OAuth 流程

```
Browser                    Next.js (better-auth)              微信开放平台
   │                              │                               │
   │── 点击"微信登录" ────────────▶│                               │
   │◀─ redirect ─────────────────│                               │
   │   open.weixin.qq.com/        │                               │
   │   connect/qrconnect?         │                               │
   │   appid=APPID&               │                               │
   │   redirect_uri=callback_url& │                               │
   │   scope=snsapi_login&        │                               │
   │   state=STATE                │                               │
   │                              │                               │
   │   [显示扫码页面]              │                               │
   │── 用户手机扫码确认 ───────────────────────────────────────────▶│
   │◀─ redirect to callback ─────────────────────────────────────│
   │   ?code=CODE&state=STATE     │                               │
   │                              │                               │
   │──────────────────────────────▶│                               │
   │                              │── GET /sns/oauth2/access_token▶│
   │                              │   ?appid=&secret=&code=       │
   │                              │◀─ { access_token, openid,     │
   │                              │      refresh_token, unionid } ─│
   │                              │── GET /sns/userinfo ──────────▶│
   │                              │   ?access_token=&openid=      │
   │                              │◀─ { openid, unionid,          │
   │                              │      nickname, headimgurl } ───│
   │                              │                               │
   │                              │  upsert user + account 表     │
   │                              │  grantRoleForNewUser()        │
   │                              │  grantCreditsForNewUser()     │
   │                              │  创建 session                  │
   │                              │  Set-Cookie: session_token    │
   │◀─ 302 redirect to callbackURL│                               │
```

**CSRF 防护**：`state` 参数由 better-auth 自动生成、存储和验证。

### 2.2 新用户 vs 已有用户判断（better-auth Generic OAuth 内部）

```
微信回调 → getUserInfo 返回 id = unionid || openid
                    │
                    ▼
        查 account 表
        WHERE providerId = 'wechat'
          AND accountId  = id
                    │
          ┌─────────┴─────────┐
        存在                不存在
          │                   │
          ▼                   ▼
      取已有 user         尝试按 email 匹配 user
          │               （微信无 email，此步跳过）
          │                   │
          │               新建 user 记录
          │               email = wx_{unionid|openid}@wechat.placeholder
          │                   │
          └─────────┬─────────┘
                    │
              创建/更新 account 记录
              创建 session
```

---

## 三、数据结构

### 3.1 `account` 表（微信登录记录）

```
id                    = "uuid-xxx"
accountId             = "oXxxx..."   ← unionid（优先）或 openid
providerId            = "wechat"
userId                = "uuid-user-xxx"
accessToken           = "ACCESS_TOKEN"              ← 有效期 2 小时
refreshToken          = "REFRESH_TOKEN"             ← 有效期 30 天
accessTokenExpiresAt  = 2026-03-29 17:xx:xx
refreshTokenExpiresAt = 2026-04-28 xx:xx:xx
scope                 = "snsapi_login"
idToken               = null
password              = null
```

### 3.2 `user` 表（纯微信注册用户）

```
id            = "uuid-user-xxx"
name          = "微信昵称"                        ← profile.nickname
email         = "wx_oXxxx@wechat.placeholder"    ← 确定性占位（见 3.4 节）
emailVerified = false
image         = "https://thirdwx.qlogo.cn/..."   ← profile.headimgurl
utmSource     = ""
ip            = "用户 IP"
locale        = "zh"
```

### 3.3 微信 Profile 类型（新增类型定义）

```typescript
// src/core/auth/types.ts（新文件或追加到现有 types）

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

### 3.4 Placeholder Email 策略

**背景**：`user.email` 字段为 `notNull().unique()`，微信不返回 email。

**方案**：在 `getUserInfo` 钩子中主动构造确定性占位 email：

```
wx_{unionid || openid}@wechat.placeholder
```

- 优先用 `unionid`（同一用户在同一开放平台下跨应用唯一），fallback 到 `openid`
- 前缀 `wx_` + 域名 `wechat.placeholder` 确保不与任何真实邮箱冲突
- **无需修改 schema**，`notNull().unique()` 约束依然成立

**邮件发送防护**：所有触发邮件发送的逻辑（验证邮件、通知等）需过滤占位邮箱：

```typescript
if (user.email?.endsWith('@wechat.placeholder')) return;
```

**Python 侧影响**：`UserInfo.email` 会是占位字符串而非 null，Python 侧无需改动 schema，
但业务逻辑中若依赖 email 做展示或发送，需同样检查 `@wechat.placeholder` 后缀。

### 3.5 配置键

| 配置键 | 类型 | 说明 | 公开（publicSettingNames）|
|--------|------|------|--------------------------|
| `wechat_auth_enabled` | `switch` | 前端展示微信登录按钮 | ✅ 是 |
| `wechat_app_id` | `text` | 微信开放平台 AppID | ❌ 否（服务端独用）|
| `wechat_app_secret` | `password` | 微信开放平台 AppSecret | ❌ 否（敏感）|

> Google/GitHub 使用 `*_client_id` / `*_client_secret` 命名，
> 微信对应字段官方叫 AppID / AppSecret，使用 `wechat_app_id` / `wechat_app_secret`
> 与微信文档术语保持一致，避免混淆。

---

## 四、核心实现代码

### 4.1 Generic OAuth Plugin 配置

```typescript
// src/core/auth/config.ts — getAuthOptions() 的 plugins 数组

import { genericOAuth } from 'better-auth/plugins/generic-oauth';

// 在 getAuthOptions() 中，plugins 数组追加：
if (configs.wechat_app_id && configs.wechat_app_secret) {
  plugins.push(
    genericOAuth({
      providerId: 'wechat',
      clientId: configs.wechat_app_id,
      clientSecret: configs.wechat_app_secret,
      authorizationUrl: 'https://open.weixin.qq.com/connect/qrconnect',
      tokenUrl: 'https://api.weixin.qq.com/sns/oauth2/access_token',
      userInfoUrl: 'https://api.weixin.qq.com/sns/userinfo',
      scopes: ['snsapi_login'],
      redirectURI: `${envConfigs.app_url}/api/auth/callback/wechat`,

      // 微信 token 端点用 appid/secret，不是标准 client_id/client_secret
      getToken: async ({ code }) => {
        const url = new URL('https://api.weixin.qq.com/sns/oauth2/access_token');
        url.searchParams.set('appid', configs.wechat_app_id!);
        url.searchParams.set('secret', configs.wechat_app_secret!);
        url.searchParams.set('code', code);
        url.searchParams.set('grant_type', 'authorization_code');
        const res = await fetch(url);
        const data = await res.json();
        return {
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          accessTokenExpiresAt: new Date(Date.now() + data.expires_in * 1000),
          raw: data, // 保留 openid、unionid 等微信特有字段
        };
      },

      // 微信 userinfo 需要 access_token + openid 双参数
      getUserInfo: async (tokens) => {
        const openid = (tokens.raw as Record<string, string>)?.openid || '';
        const url = new URL('https://api.weixin.qq.com/sns/userinfo');
        url.searchParams.set('access_token', tokens.accessToken!);
        url.searchParams.set('openid', openid);
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

      // access_token 2 小时过期，支持刷新
      refreshAccessToken: async (refreshToken) => {
        const url = new URL('https://api.weixin.qq.com/sns/oauth2/refresh_token');
        url.searchParams.set('appid', configs.wechat_app_id!);
        url.searchParams.set('grant_type', 'refresh_token');
        url.searchParams.set('refresh_token', refreshToken);
        const res = await fetch(url);
        const data = await res.json();
        return {
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          accessTokenExpiresAt: new Date(Date.now() + data.expires_in * 1000),
        };
      },

      // 授权 URL 微信需要 appid 参数（better-auth 会附加 client_id，微信忽略未知参数）
      authorizationUrlParams: {
        appid: configs.wechat_app_id!,
      },
    })
  );
}
```

### 4.2 前端触发登录

客户端调用方式与 Google/GitHub 完全一致：

```typescript
// social-providers.tsx
await signIn.social({ provider: 'wechat', callbackURL: callbackUrl });
```

### 4.3 账号关联（已有账号绑定微信）

better-auth 内置端点，无需额外开发：

| 端点 | 用途 |
|------|------|
| `POST /api/auth/link-social` | 已登录用户绑定微信 |
| `POST /api/auth/unlink-account` | 解除微信绑定 |
| `GET /api/auth/list-accounts` | 查看已绑定的所有 provider |

用户流程：

1. **首次微信登录** → 自动创建账号（placeholder email）
2. **已登录用户** → 设置页调用 `/link-social` 绑定微信到已有账号
3. **引导补充邮箱** → 检测到 `@wechat.placeholder` 后前端可提示用户补充真实邮箱

---

## 五、改动文件清单

| 文件 | 改动内容 | 状态 |
|------|----------|------|
| `src/core/auth/config.ts` | ~~`getSocialProviders()` wechat 分支~~ → 改用 `genericOAuth` plugin | ⚠️ 需修正（已有错误改动）|
| `src/core/auth/types.ts` | 新增 `WeChatProfile` 接口定义 | 待实施 |
| `src/shared/services/settings.ts` | 新增 `wechat_auth` 设置组 + 3 字段；`publicSettingNames` 追加 `wechat_auth_enabled` | 待实施 |
| `src/shared/blocks/sign/social-providers.tsx` | 增加微信按钮（条件：`wechat_auth_enabled === 'true'`） | 待实施 |
| `src/shared/blocks/sign/sign-in.tsx` | 增加 `isWechatAuthEnabled` 判断 | 待实施 |
| `src/shared/blocks/sign/sign-in-form.tsx` | 同上 | 待实施 |
| `src/config/locale/messages/en/admin/settings.json` | 新增 `"wechat_auth": "WeChat Auth"` | 待实施 |
| `src/config/locale/messages/zh/admin/settings.json` | 新增 `"wechat_auth": "微信认证"` | 待实施 |
| `src/config/locale/messages/en/common.json` | 新增 `"wechat_sign_in_title": "Sign in with WeChat"` | 待实施 |
| `src/config/locale/messages/zh/common.json` | 新增 `"wechat_sign_in_title": "使用微信登录"` | 待实施 |

> **⚠️ config.ts 已有错误改动**：之前误用了 `socialProviders.wechat`（内置方式）
> 并采用了错误的配置键名（`wechat_client_id` / `wechat_client_secret`）。
> 实施时需先还原，再按本方案改用 `genericOAuth` + `wechat_app_id` / `wechat_app_secret`。

### 5.1 settings.ts 新增内容（详细结构）

```typescript
// settingGroups 中追加（紧跟 github_auth 之后）
{
  name: 'wechat_auth',
  title: t('groups.wechat_auth'),
  description: 'custom your wechat auth settings',
  tab: 'auth',
},

// settings 字段中追加（紧跟 github_client_secret 之后）
{ name: 'wechat_auth_enabled', title: 'Auth Enabled', type: 'switch', value: 'false', group: 'wechat_auth', tab: 'auth' },
{ name: 'wechat_app_id',       title: 'WeChat AppID',     type: 'text',     placeholder: 'wx...', group: 'wechat_auth', tab: 'auth' },
{ name: 'wechat_app_secret',   title: 'WeChat AppSecret', type: 'password', placeholder: '',       group: 'wechat_auth', tab: 'auth' },

// publicSettingNames 追加
'wechat_auth_enabled',
```

---

## 六、环境变量（实施参考）

```bash
# .env.development / .env.production
WECHAT_AUTH_ENABLED=true
WECHAT_APP_ID=wxxxxxxxxxxxxxxxxxxx        # 微信开放平台 AppID
WECHAT_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxx # 微信开放平台 AppSecret
```

`getAllConfigs()` 会将大写 env key 自动映射到小写配置键，与 Google/GitHub 处理一致。

---

## 七、无需修改的部分

- **数据库 Schema**：`account` 表原生支持多 provider，无需新增字段或 migration
- **`user` 表**：占位 email 策略保持 `notNull().unique()` 约束不变
- **Python 后端**：session 验证逻辑（`repository/auth.py`）对 provider 无感知，无需改动；
  业务层若展示 email，需检查 `@wechat.placeholder` 后缀
