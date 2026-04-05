# 外部依赖与服务配置清单

> 凡涉及密钥的配置，**不要写入版本控制**。本地用 `.env.*`，生产用 Wrangler secrets / GitHub Environment Secrets。

---

## 0. 状态速览

| 依赖 / 配置 | 本地开发 | Staging | Production | 配置方式 |
|-------------|---------|---------|------------|---------|
| PostgreSQL（Supabase） | ✅ 本地 Docker/Homebrew | ✅ Supabase | ✅ Supabase | `.env.*` / Wrangler secret |
| Redis | ✅ 本地 | ❌ 未配置 | ❌ 未配置 | `.env.*` / 需 Upstash |
| `AUTH_SECRET` | ✅ | ✅ | ✅ | Wrangler secret |
| `OPENROUTER_API_KEY` | ✅ | ✅ | ✅ | Wrangler secret |
| `PYTHON_BACKEND_URL` | ✅ | ✅ `api.aispeeds.me` | ✅ `api.aispeeds.me` | Wrangler secret |
| `FRONTEND_URLS`（后端 CORS） | ✅ | ✅ | ✅ | `.env.*` |
| Google / GitHub OAuth | ❌ | ❌ | ❌ | Admin Panel |
| Resend（邮件） | ❌ | ❌ | ❌ | Admin Panel |
| Cloudflare R2（存储） | ❌ | ❌ | ❌ | Admin Panel |
| Stripe / PayPal / Creem | ❌ | ❌ | ❌ | Admin Panel |
| AI（Replicate / Fal / Gemini / Kie） | ❌ | ❌ | ❌ | Admin Panel |

---

## 1. 基础设施配置（环境变量 / Secrets）

> **配置位置说明**
>
> | 环境 | 前端配置文件 | 后端配置文件 |
> |------|------------|------------|
> | 本地开发 | `frontend/apps/web/.env.development` | `backend/python/.env.development` |
> | Workers 本地预览 | `frontend/apps/web/.dev.vars` | — |
> | Staging / Production | Wrangler secrets + `wrangler.toml [vars]` | 机器上 `.env.production` |
> | CI/CD | GitHub Environment Secrets | — |

---

### 1.1 PostgreSQL 数据库 ✅

前端 (Drizzle ORM) 和 Python 后端 (SQLAlchemy) 共享同一数据库。

**本地开发**（Docker / Homebrew 自动创建）：

| 变量名 | 本地示例值 |
|--------|-----------|
| 前端 `DATABASE_URL` | `postgresql://wenexus:wenexus_dev_pwd@localhost:5432/wenexus_dev` |
| 前端 `DATABASE_PROVIDER` | `postgresql` |
| 前端 `DB_SINGLETON_ENABLED` | `true` |
| 前端 `DB_MAX_CONNECTIONS` | `1` |
| Python `DATABASE_URL` | `postgresql+asyncpg://wenexus:wenexus_dev_pwd@localhost:5432/wenexus_dev` |

**生产环境**（Supabase Transaction Pooler，格式不同）：

```
# 前端 Wrangler secret
postgresql://postgres.<project>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres?pgbouncer=true

# Python 后端 .env.production（asyncpg 不兼容 pgbouncer，用 Session Pooler port 5432）
postgresql+asyncpg://postgres.<project>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
```

**初始化**（首次部署后执行一次）：

```bash
cd frontend/apps/web
pnpm db:push    # 推送 schema
pnpm rbac:init  # 初始化 RBAC 角色
```

---

### 1.2 Redis ✅（本地）/ ❌（生产待配置）

Python 后端用于缓存和会话管理。

| 变量名 | 本地值 | 生产建议 |
|--------|--------|---------|
| Python `REDIS_URL` | `redis://localhost:6379/0` | [Upstash](https://upstash.com) 免费套餐 `rediss://...` |

> **生产环境 Redis 尚未配置**。如果后端功能依赖 Redis，上线前需在 `.env.production` 设置 Upstash 或其他 Redis 服务的连接串。

---

### 1.3 前端环境变量 ✅

**`frontend/apps/web/.env.development`**（本地开发，gitignored）：

| 变量名 | 说明 |
|--------|------|
| `NEXT_PUBLIC_APP_URL` | `http://localhost:3000` |
| `NEXT_PUBLIC_APP_NAME` | `WeNexus` |
| `NEXT_PUBLIC_THEME` | `default` |
| `NEXT_PUBLIC_APPEARANCE` | `system` |
| `DATABASE_URL` | 本地 PostgreSQL |
| `DATABASE_PROVIDER` | `postgresql` |
| `DB_SINGLETON_ENABLED` | `true` |
| `DB_MAX_CONNECTIONS` | `1` |
| `AUTH_SECRET` | `openssl rand -base64 32` 生成 |
| `PYTHON_BACKEND_URL` | `http://localhost:8000` |
| `NEXT_PUBLIC_WEBSOCKET_BASE_URL` | `ws://localhost:8000`（可留空，由 host 推导） |
| `OPENROUTER_API_KEY` | OpenRouter API Key |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` |

**`frontend/apps/web/.dev.vars`**（Workers 本地预览专用，gitignored）：

| 变量名 | 说明 |
|--------|------|
| `DATABASE_URL` | Supabase 连接串（Workers 预览需要真实 DB） |
| `AUTH_SECRET` | 与 `.env.development` 相同 |

**`frontend/apps/web/wrangler.toml [vars]`**（公开变量，已提交版本控制）：

| 变量名 | 说明 |
|--------|------|
| `NEXT_PUBLIC_APP_URL` | 各环境 Workers URL |
| `NEXT_PUBLIC_APP_NAME` | `WeNexus` |
| `NEXT_PUBLIC_THEME` | `default` |
| `NEXT_PUBLIC_APPEARANCE` | `system` |
| `DATABASE_PROVIDER` | `postgresql` |
| `DB_SINGLETON_ENABLED` | `true` |
| `DB_MAX_CONNECTIONS` | `1` |

---

### 1.4 Python 后端环境变量 ✅

**`backend/python/.env.development`**（本地，gitignored）：

| 变量名 | 示例值 | 说明 |
|--------|--------|------|
| `APP_ENV` | `development` | 控制加载哪个 `.env.*` 文件 |
| `APP_PORT` | `8000` | 后端监听端口 |
| `DATABASE_URL` | `postgresql+asyncpg://...` | 本地 PostgreSQL |
| `REDIS_URL` | `redis://localhost:6379/0` | 本地 Redis |
| `OPENROUTER_API_KEY` | `sk-or-xxx` | OpenRouter API Key |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | 可替换为兼容 API |
| `FRONTEND_URLS` | `http://localhost:3000,https://wenexus-web.yihuimbin.workers.dev` | CORS 允许源，逗号分隔 |

**`backend/python/.env.production`**（生产机器，gitignored）：

| 变量名 | 值 |
|--------|-----|
| `APP_ENV` | `production` |
| `DATABASE_URL` | Supabase Session Pooler（asyncpg 格式） |
| `REDIS_URL` | Upstash Redis URL（待配置） |
| `OPENROUTER_API_KEY` | 同开发环境或专用 key |
| `FRONTEND_URLS` | `https://wenexus-web-staging.yihuimbin.workers.dev,https://wenexus-web-production.yihuimbin.workers.dev` |

---

### 1.5 Wrangler Secrets ✅

通过 `wrangler secret put <NAME>` 或 Cloudflare Dashboard 设置，**不出现在代码中**：

| Secret 名 | 用途 | 当前状态 |
|-----------|------|---------|
| `AUTH_SECRET` | better-auth 签名密钥 | ✅ 已设置 |
| `DATABASE_URL` | Supabase 连接串 | ✅ 已设置 |
| `PYTHON_BACKEND_URL` | `https://api.aispeeds.me` | ✅ 已设置 |
| `OPENROUTER_API_KEY` | OpenRouter API Key | ✅ 已设置 |

---

### 1.6 GitHub CI/CD Secrets ✅

**Repository Secrets**（所有环境共用）：

| Secret 名 | 当前状态 |
|-----------|---------|
| `CLOUDFLARE_API_TOKEN` | ✅ 已设置 |
| `CLOUDFLARE_ACCOUNT_ID` | ✅ 已设置 |

**Environment Secrets**（`staging` 和 `production` 各自独立）：

| Secret 名 | 说明 | 当前状态 |
|-----------|------|---------|
| `STAGING_AUTH_SECRET` / `PROD_AUTH_SECRET` | Auth 密钥 | ✅ 已设置 |
| `STAGING_DATABASE_URL` / `PROD_DATABASE_URL` | Supabase URL | ✅ 已设置 |
| `STAGING_PYTHON_BACKEND_URL` / `PROD_PYTHON_BACKEND_URL` | `https://api.aispeeds.me` | ✅ 已设置 |

---

## 2. 功能配置（Admin Panel `/admin/settings`，按需启用）

> 以下配置均通过管理后台动态写入数据库，无需修改代码或重新部署。

---

### 2.1 认证 ❌（未配置）

#### Google OAuth

| Admin 设置名 | 说明 | 获取方式 |
|-------------|------|---------|
| `google_auth_enabled` | 开关 | — |
| `google_client_id` | Client ID | [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Credentials |
| `google_client_secret` | Client Secret | 同上 |
| `google_one_tap_enabled` | 一键登录 | — |

#### GitHub OAuth

| Admin 设置名 | 说明 | 获取方式 |
|-------------|------|---------|
| `github_auth_enabled` | 开关 | — |
| `github_client_id` | Client ID | GitHub → Settings → Developer settings → OAuth Apps |
| `github_client_secret` | Client Secret | 同上 |

> Callback URL 设为：`https://wenexus-web-production.yihuimbin.workers.dev/api/auth/callback/<provider>`

---

### 2.2 邮件 ❌（未配置）

| Admin 设置名 | 说明 | 获取方式 |
|-------------|------|---------|
| `resend_api_key` | Resend API Key | [resend.com](https://resend.com) |
| `resend_sender_email` | 发件人 | 如 `WeNexus <no-reply@mail.wenexus.com>` |

> 开启邮件验证还需在 Admin → Auth 中打开 `email_verification_enabled`。

---

### 2.3 对象存储 ❌（未配置）

用于用户上传文件、AI 生成文件持久化。

| Admin 设置名 | 说明 |
|-------------|------|
| `r2_access_key` | Cloudflare R2 Access Key ID |
| `r2_secret_key` | Cloudflare R2 Secret Access Key |
| `r2_bucket_name` | 存储桶名称 |
| `r2_upload_path` | 上传路径前缀（默认 `uploads`） |
| `r2_endpoint` | `https://<account-id>.r2.cloudflarestorage.com` |
| `r2_domain` | 自定义公开访问域名 |

> Cloudflare Dashboard → R2 → 创建 Bucket → Manage R2 API Tokens 获取密钥。

---

### 2.4 支付 ❌（未配置）

先在 Admin → Payment → Basic 选择默认支付商，再填对应密钥。

#### Stripe

| Admin 设置名 | 说明 |
|-------------|------|
| `stripe_enabled` | 开关 |
| `stripe_publishable_key` | `pk_xxx` |
| `stripe_secret_key` | `sk_xxx` |
| `stripe_signing_secret` | Webhook 签名密钥 `whsec_xxx` |
| `stripe_payment_methods` | `card` / `wechat_pay` / `alipay` |
| `stripe_promotion_codes` | 产品 ID → 促销码 JSON |
| `stripe_allow_promotion_codes` | 是否允许用户输入自定义促销码 |

#### PayPal

| Admin 设置名 | 说明 |
|-------------|------|
| `paypal_enabled` | 开关 |
| `paypal_client_id` | Client ID |
| `paypal_client_secret` | Client Secret |
| `paypal_webhook_id` | Webhook ID |
| `paypal_environment` | `sandbox` / `production` |

#### Creem

| Admin 设置名 | 说明 |
|-------------|------|
| `creem_enabled` | 开关 |
| `creem_api_key` | API Key |
| `creem_signing_secret` | Webhook 签名密钥 |
| `creem_product_ids` | 产品 ID 映射 JSON |
| `creem_environment` | `sandbox` / `production` |

---

### 2.5 AI 服务（OpenRouter 已配置，其余未配置）

#### OpenRouter ✅（LLM 对话，前端 + 后端均使用）

| Admin 设置名 | 说明 |
|-------------|------|
| `openrouter_api_key` | `sk-or-xxx`（已通过 Wrangler secret 设置） |
| `openrouter_base_url` | 默认 `https://openrouter.ai/api/v1`，支持任意 OpenAI 兼容 API |

#### Replicate ❌（图像/视频/音乐生成）

| Admin 设置名 | 说明 |
|-------------|------|
| `replicate_api_token` | `r8_xxx` |
| `replicate_custom_storage` | 是否用 R2 保存生成文件 |

#### Fal ❌（图像/视频生成）

| Admin 设置名 | 说明 |
|-------------|------|
| `fal_api_key` | `fal_xxx` |
| `fal_custom_storage` | 是否用 R2 保存生成文件 |

#### Gemini ❌（Google 图像生成）

| Admin 设置名 | 说明 |
|-------------|------|
| `gemini_api_key` | `AIza...` |

#### Kie ❌（音乐/图像/视频生成）

| Admin 设置名 | 说明 |
|-------------|------|
| `kie_api_key` | Kie API Key |
| `kie_custom_storage` | 是否用 R2 保存生成文件 |

---

### 2.6 数据分析 ❌（未配置）

| Admin 设置名 | 服务 | 说明 |
|-------------|------|------|
| `google_analytics_id` | Google Analytics | GA4 Tracking ID（`G-xxx`） |
| `clarity_id` | Microsoft Clarity | Project ID |
| `plausible_domain` + `plausible_src` | Plausible | 自托管或 SaaS |
| `openpanel_client_id` | OpenPanel | Client ID |
| `vercel_analytics_enabled` | Vercel Analytics | 仅 Vercel 部署可用，当前 Workers 部署无效 |

---

### 2.7 客服 ❌（未配置）

| Admin 设置名 | 服务 | 说明 |
|-------------|------|------|
| `crisp_website_id` | Crisp | Website ID |
| `tawk_property_id` + `tawk_widget_id` | Tawk.to | Property ID + Widget ID |

---

### 2.8 广告 ❌（未配置）

| Admin 设置名 | 服务 | 说明 |
|-------------|------|------|
| `adsense_code` | Google AdSense | `ca-pub-xxx` |

---

### 2.9 联盟营销 ❌（未配置）

| Admin 设置名 | 服务 | 说明 |
|-------------|------|------|
| `affonso_id` + `affonso_cookie_duration` | Affonso | Program ID + Cookie 有效期（天） |
| `promotekit_id` | PromoteKit | Program ID |

---

## 3. 一键本地启动

```bash
./scripts/dev.sh           # 全栈：数据库 + 后端 + Tunnel + 前端 Workers 预览
./scripts/dev.sh frontend  # 仅前端：数据库 + 前端 Workers 预览
./scripts/dev.sh stop      # 停止后台服务
```

前端访问：`http://localhost:8787`（Workers 预览）
后端 API：`http://localhost:8000/docs`（本地）/ `https://api.aispeeds.me/docs`（公网）

---

## 4. 运行时版本要求

| 依赖 | 版本 |
|------|------|
| Node.js | >= 20 |
| Python | >= 3.14 |
| Java | 17 |
| pnpm | >= 9 |
| uv | 最新版 |
| Maven | >= 3.8 |
| Docker | 最新版 |
