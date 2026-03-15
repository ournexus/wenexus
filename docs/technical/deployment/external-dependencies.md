# 外部依赖与服务配置清单

项目运行所需的全部外部服务依赖。分为**必需**（项目无法启动）和**可选**（按需启用）两级。

---

## 1. 必需依赖（项目启动必备）

### 1.1 PostgreSQL 数据库

前端 (Next.js / Drizzle ORM) 和后端 (Python / SQLAlchemy) 共享同一数据库。

| 项目 | 值 |
|------|------|
| 镜像 | `postgres:16` |
| 本地端口 | `5432` |
| 数据库名 | `wenexus_dev` |
| 用户/密码 | `wenexus` / `wenexus_dev_pwd` |

**启动方式**：

```bash
docker compose up -d postgres
```

**环境变量**：

| 服务 | 变量名 | 示例值 |
|------|--------|--------|
| Frontend (.env) | `DATABASE_URL` | `postgresql://wenexus:wenexus_dev_pwd@localhost:5432/wenexus_dev` |
| Frontend (.env) | `DATABASE_PROVIDER` | `postgresql` |
| Python (.env) | `DATABASE_URL` | `postgresql+asyncpg://wenexus:wenexus_dev_pwd@localhost:5432/wenexus_dev` |

**初始化**：

```bash
cd frontend/apps/web
pnpm db:push        # 推送 schema 到数据库
pnpm db:migrate     # 运行迁移
pnpm rbac:init      # 初始化 RBAC 角色
```

### 1.2 Redis

Python 后端用于缓存和会话管理。

| 项目 | 值 |
|------|------|
| 镜像 | `redis:7` |
| 本地端口 | `6379` |

**启动方式**：

```bash
docker compose up -d redis
```

**环境变量**：

| 服务 | 变量名 | 示例值 |
|------|--------|--------|
| Python (.env) | `REDIS_URL` | `redis://localhost:6379/0` |

### 1.3 AUTH_SECRET

Next.js 认证系统 (better-auth) 所需的密钥。

```bash
# 生成方式
openssl rand -base64 32
```

| 服务 | 变量名 | 说明 |
|------|--------|------|
| Frontend (.env) | `AUTH_SECRET` | 认证签名密钥，必须设置 |

---

## 2. 可选依赖（按功能需求启用）

> 以下服务通过**管理后台** (`/admin/settings`) 动态配置，存储在数据库中。
> 部分也可通过 `.env` 文件设置。

### 2.1 AI 服务

#### OpenRouter（LLM 对话 / 文本生成）

前端和 Python 后端均使用，兼容 OpenAI API 格式。

| 配置项 | Admin 设置名 | 说明 |
|--------|-------------|------|
| API Key | `openrouter_api_key` | OpenRouter API 密钥 (`sk-or-xxx`) |
| Base URL | `openrouter_base_url` | 默认 `https://openrouter.ai/api/v1`，可替换为任意 OpenAI 兼容 API |

> **需要用户提供**：OpenRouter API Key（或兼容的 API Key）

#### Replicate（图像/视频/音乐生成）

| 配置项 | Admin 设置名 | 说明 |
|--------|-------------|------|
| API Token | `replicate_api_token` | Replicate API Token (`r8_xxx`) |
| Custom Storage | `replicate_custom_storage` | 是否用自定义存储保存生成文件 |

#### Fal（图像/视频生成）

| 配置项 | Admin 设置名 | 说明 |
|--------|-------------|------|
| API Key | `fal_api_key` | Fal API Key (`fal_xxx`) |
| Custom Storage | `fal_custom_storage` | 是否用自定义存储保存生成文件 |

#### Gemini（Google AI 图像生成）

| 配置项 | Admin 设置名 | 说明 |
|--------|-------------|------|
| API Key | `gemini_api_key` | Google Gemini API Key (`AIza...`) |

#### Kie（音乐/图像/视频生成）

| 配置项 | Admin 设置名 | 说明 |
|--------|-------------|------|
| API Key | `kie_api_key` | Kie API Key |
| Custom Storage | `kie_custom_storage` | 是否用自定义存储保存生成文件 |

---

### 2.2 支付服务

#### Stripe

| 配置项 | Admin 设置名 | 说明 |
|--------|-------------|------|
| Publishable Key | `stripe_publishable_key` | 公钥 (`pk_xxx`) |
| Secret Key | `stripe_secret_key` | 密钥 (`sk_xxx`) |
| Signing Secret | `stripe_signing_secret` | Webhook 签名密钥 (`whsec_xxx`) |
| Payment Methods | `stripe_payment_methods` | 支付方式：card / wechat_pay / alipay |
| Promotion Codes | `stripe_promotion_codes` | 产品 ID 到促销码的 JSON 映射 |

#### PayPal

| 配置项 | Admin 设置名 | 说明 |
|--------|-------------|------|
| Client ID | `paypal_client_id` | PayPal Client ID |
| Client Secret | `paypal_client_secret` | PayPal Client Secret |
| Webhook ID | `paypal_webhook_id` | Webhook 验证用 |
| Environment | `paypal_environment` | `sandbox` 或 `production` |

#### Creem

| 配置项 | Admin 设置名 | 说明 |
|--------|-------------|------|
| API Key | `creem_api_key` | Creem API Key |
| Signing Secret | `creem_signing_secret` | Webhook 签名密钥 |
| Product IDs | `creem_product_ids` | 产品 ID 映射 JSON |
| Environment | `creem_environment` | `sandbox` 或 `production` |

---

### 2.3 邮件服务

#### Resend

用于发送验证邮件、通知邮件等。

| 配置项 | Admin 设置名 | 说明 |
|--------|-------------|------|
| API Key | `resend_api_key` | Resend API Key |
| Sender Email | `resend_sender_email` | 发件人地址，如 `WeNexus <no-reply@mail.wenexus.com>` |

---

### 2.4 对象存储

#### Cloudflare R2

用于用户上传文件、AI 生成文件存储。

| 配置项 | Admin 设置名 | 说明 |
|--------|-------------|------|
| Access Key | `r2_access_key` | Cloudflare R2 Access Key ID |
| Secret Key | `r2_secret_key` | Cloudflare R2 Secret Access Key |
| Bucket Name | `r2_bucket_name` | 存储桶名称 |
| Upload Path | `r2_upload_path` | 上传路径前缀，默认 `uploads` |
| Endpoint | `r2_endpoint` | `https://<account-id>.r2.cloudflarestorage.com` |
| Domain | `r2_domain` | 自定义公开访问域名 |

> 代码也支持 **AWS S3** 作为存储后端（`S3Provider`），但管理后台目前只暴露 R2 配置。

---

### 2.5 OAuth 社交登录

#### Google OAuth

| 配置项 | Admin 设置名 | 说明 |
|--------|-------------|------|
| Client ID | `google_client_id` | Google OAuth Client ID |
| Client Secret | `google_client_secret` | Google OAuth Client Secret |
| One Tap | `google_one_tap_enabled` | 是否启用 Google One Tap 登录 |

#### GitHub OAuth

| 配置项 | Admin 设置名 | 说明 |
|--------|-------------|------|
| Client ID | `github_client_id` | GitHub OAuth Client ID |
| Client Secret | `github_client_secret` | GitHub OAuth Client Secret |

---

### 2.6 数据分析

| 服务 | 配置项 | 说明 |
|------|--------|------|
| Google Analytics | `google_analytics_id` | GA Tracking ID |
| Microsoft Clarity | `clarity_id` | Clarity Project ID |
| Plausible | `plausible_domain` + `plausible_src` | 自托管或 SaaS |
| OpenPanel | `openpanel_client_id` | OpenPanel Client ID |
| Vercel Analytics | `vercel_analytics_enabled` | 仅 Vercel 部署时可用 |

---

### 2.7 客服系统

| 服务 | 配置项 | 说明 |
|------|--------|------|
| Crisp | `crisp_website_id` | Crisp 在线客服 Widget ID |
| Tawk | `tawk_property_id` + `tawk_widget_id` | Tawk.to 在线客服 |

---

### 2.8 广告

| 服务 | 配置项 | 说明 |
|------|--------|------|
| Google AdSense | `adsense_code` | AdSense 代码 (`ca-pub-xxx`) |

---

### 2.9 联盟营销

| 服务 | 配置项 | 说明 |
|------|--------|------|
| Affonso | `affonso_id` + `affonso_cookie_duration` | Affonso 联盟 ID |
| PromoteKit | `promotekit_id` | PromoteKit 联盟 ID |

---

## 3. 本地开发快速启动

### 最小启动配置

只需以下步骤即可在本地运行项目：

```bash
# 1. 启动基础设施
docker compose up -d                    # 启动 PostgreSQL + Redis

# 2. 前端
cd frontend/apps/web
cp .env.example .env.development        # 复制并编辑环境变量
pnpm install
pnpm db:push                            # 初始化数据库 schema
pnpm dev                                # 启动前端 http://localhost:3000

# 3. Python 后端
cd backend/python
cp .env.example .env.development        # 复制并编辑环境变量
uv sync --dev
uv run uvicorn src.main:app --reload    # 启动后端 http://localhost:8000
```

### 环境变量文件

| 文件 | 位置 | 用途 |
|------|------|------|
| `.env.development` | `frontend/apps/web/` | 前端环境变量 |
| `.env.development` | `backend/python/` | Python 后端环境变量 |
| `docker-compose.yml` | 项目根目录 | PostgreSQL + Redis 容器 |

### 需要用户手动提供的配置

以下配置无法自动生成，需要从对应服务商获取：

| 优先级 | 配置 | 获取方式 |
|--------|------|----------|
| **必需** | PostgreSQL + Redis | `docker compose up -d` 自动创建 |
| **必需** | `AUTH_SECRET` | `openssl rand -base64 32` 自动生成 |
| 推荐 | `OPENROUTER_API_KEY` | [openrouter.ai](https://openrouter.ai) 注册获取 |
| 可选 | Stripe / PayPal / Creem 密钥 | 对应平台开发者后台 |
| 可选 | Google / GitHub OAuth | 对应平台开发者控制台 |
| 可选 | Resend API Key | [resend.com](https://resend.com) |
| 可选 | Cloudflare R2 密钥 | Cloudflare Dashboard |
| 可选 | AI 服务密钥 | 各 AI 平台开发者控制台 |

---

## 4. 运行时版本要求

| 依赖 | 版本 |
|------|------|
| Node.js | >= 18 |
| Python | >= 3.11 |
| Java | 17 |
| pnpm | 最新版 |
| uv | 最新版 |
| Maven | >= 3.8 |
| Docker | 最新版 |
