# WeNexus 部署方案全景

> 当前架构：前端 → Cloudflare Workers，后端 → 本地机器（Cloudflare Tunnel），数据库 → Supabase。
> CI/CD 通过 GitHub Actions 自动触发，`develop` → staging，`main` → production。

---

## 1. 整体架构

```
用户浏览器
    │
    ▼
Cloudflare Workers  (前端 Next.js via OpenNext)
    │  PYTHON_BACKEND_URL
    ▼
Cloudflare Tunnel ──► 本地机器 :8000  (FastAPI)
                          │
                          ├── Supabase PostgreSQL  (云数据库)
                          └── Upstash Redis        (云 Redis)
```

| 层 | 服务 | 说明 |
|----|------|------|
| 前端 | Cloudflare Workers | Next.js via OpenNext，静态资源走 Cloudflare Assets |
| 后端 | 本地机器 + Cloudflare Tunnel | FastAPI，无需开放防火墙端口 |
| 数据库 | Supabase (Transaction Pooler) | 公网可访问，Workers 和本地后端均可连接 |
| 缓存 | Upstash Redis | 公网可访问，无需本地 Redis |
| 部署 | GitHub Actions | push to `develop` → staging；push to `main` → production |

---

## 2. 环境变量策略

### 变量分层

| 变量类型 | 存放位置 | 说明 |
|----------|----------|------|
| 公开配置（`NEXT_PUBLIC_*`、`DATABASE_PROVIDER`） | `wrangler.toml [vars]` | 明文提交，无敏感信息 |
| 运行时 secrets（`DATABASE_URL`、`AUTH_SECRET`、`PYTHON_BACKEND_URL`） | Cloudflare Workers Secrets | 通过 `wrangler secret put` 或 CI/CD 设置，**不提交到 git** |
| 本地开发 | `.env.development`（gitignored） | 本地 Docker PG + Upstash Redis，仅本机使用 |
| 本地 CF Workers 预览 | `.dev.vars`（gitignored） | `pnpm cf:preview` 时使用，替代 Wrangler secrets |

### 敏感变量清单

需要在 Cloudflare Dashboard 或 CI/CD 中设置：

```bash
# 数据库（Supabase Transaction Pooler 连接串）
wrangler secret put DATABASE_URL

# Auth 签名密钥（openssl rand -base64 32）
wrangler secret put AUTH_SECRET

# Python 后端公网地址（Cloudflare Tunnel 固定域名）
wrangler secret put PYTHON_BACKEND_URL
```

> ⚠️ **绝不**将真实 secrets 写入 `wrangler.toml` 的 `[vars]` 块，也不要在非 gitignored 文件中存放。

---

## 3. 数据库：Supabase

项目已切换到 **Supabase** 作为生产数据库，本地开发继续使用 Docker PostgreSQL。

### Supabase 连接串说明

Supabase 提供两种连接方式，根据场景选择：

| 模式 | 端口 | 适用场景 | 连接串格式 |
|------|------|----------|-----------|
| **Transaction Pooler** | 5432 | Serverless / Cloudflare Workers | `postgresql://postgres.[ref]:[pwd]@aws-*.pooler.supabase.com:5432/postgres?sslmode=require` |
| **Direct Connection** | 5432 | 长连接服务（FastAPI）、迁移 | `postgresql://postgres:[pwd]@db.[ref].supabase.co:5432/postgres` |

- **Cloudflare Workers** 使用 Transaction Pooler（短连接友好）
- **Python FastAPI 后端** 使用 Direct Connection（asyncpg 长连接）
- **迁移**（`pnpm db:push`）使用 Direct Connection

### 运行数据库迁移

```bash
cd frontend/apps/web
# 在 .env.production 中临时填入 Supabase Direct Connection URL，然后：
pnpm db:push
pnpm rbac:init
```

### 本地开发

本地保持 Docker PostgreSQL（`localhost:5432`），不影响生产数据：

```bash
docker compose up -d postgres
```

---

## 4. 后端：本地机器 + Cloudflare Tunnel

FastAPI 后端在本地机器运行，通过 Cloudflare Tunnel 对外暴露固定 HTTPS URL。

### 4.1 首次配置（仅做一次）

```bash
# 安装 cloudflared
brew install cloudflared

# 登录 Cloudflare 账号
cloudflared tunnel login

# 创建命名 Tunnel
cloudflared tunnel create wenexus-backend
# 输出：Created tunnel wenexus-backend with id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

创建 `~/.cloudflared/config.yml`：

```yaml
tunnel: wenexus-backend
credentials-file: ~/.cloudflared/<TUNNEL-UUID>.json

ingress:
  - hostname: api.wenexus.com    # 替换为你的域名
    service: http://localhost:8000
  - service: http_status:404
```

绑定 DNS（需要在 Cloudflare 管理该域名）：

```bash
cloudflared tunnel route dns wenexus-backend api.wenexus.com
```

### 4.2 日常启动

```bash
# 1. 启动后端
cd backend/python
uv run uvicorn src.wenexus.main:app --host 0.0.0.0 --port 8000 --reload

# 2. 启动 Tunnel（新终端）
cloudflared tunnel run wenexus-backend
```

固定域名后，`PYTHON_BACKEND_URL` 永远是 `https://api.wenexus.com`，无需每次重启后更新 secret。

### 4.3 后端 CORS 配置

后端通过环境变量 `FRONTEND_URLS`（逗号分隔）控制允许的来源，在 `.env.development` 或生产环境变量中设置：

```bash
# 本地开发（仅本机前端）
FRONTEND_URLS=http://localhost:3000

# 生产（本机开发 + Cloudflare Workers 默认域名 + 自定义域名）
FRONTEND_URLS=http://localhost:3000,https://wenexus-web.yihuimbin.workers.dev,https://wenexus.com
```

---

## 5. 前端：Cloudflare Workers

### 5.1 Cloudflare Workers Paid 计划

当前 bundle gzip ~5.3 MiB，**必须**使用 Workers Paid 计划（$5/月，10 MiB 上限）：

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. **Workers & Pages** → **Usage Model / Subscription** → **Upgrade to Paid**

### 5.2 手动部署（首次 / 紧急修复）

```bash
cd frontend/apps/web

# 登录 Cloudflare
pnpm exec wrangler login

# 设置 Secrets（仅首次或更换密钥时）
pnpm exec wrangler secret put DATABASE_URL        # Supabase Transaction Pooler URL
pnpm exec wrangler secret put AUTH_SECRET         # openssl rand -base64 32
pnpm exec wrangler secret put PYTHON_BACKEND_URL  # https://api.your-domain.com

# 构建并部署（默认环境）
pnpm cf:deploy
```

### 5.3 本地 Workers 预览

```bash
# 在 .dev.vars 中填入 Supabase URL 和 AUTH_SECRET，然后：
pnpm cf:preview
```

---

## 6. CI/CD：GitHub Actions

详细说明见 [github-cicd.md](./github-cicd.md)，此处列出核心流程。

### 分支 → 环境映射

| 分支 | 触发 Job | 目标环境 |
|------|---------|---------|
| `develop` | `deploy-staging` | `wenexus-web-staging.workers.dev` |
| `main` | `deploy-production` | `wenexus-web.yihuimbin.workers.dev`（或自定义域名） |

### 必须在 GitHub 配置的 Secrets

在 **Settings → Secrets and variables → Actions** 中添加：

**Repository Secrets（两个环境共用）：**

| Secret | 说明 |
|--------|------|
| `CLOUDFLARE_API_TOKEN` | Cloudflare API Token（需要 `Workers Scripts:Edit` 权限） |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare 账户 ID |

**Environment Secrets — `staging`：**

| Secret | 说明 |
|--------|------|
| `STAGING_AUTH_SECRET` | staging 环境 Auth 密钥 |
| `STAGING_DATABASE_URL` | Supabase Transaction Pooler URL（staging 项目） |
| `STAGING_PYTHON_BACKEND_URL` | 后端 Tunnel URL（固定域名） |

**Environment Secrets — `production`：**

| Secret | 说明 |
|--------|------|
| `PROD_AUTH_SECRET` | 生产 Auth 密钥 |
| `PROD_DATABASE_URL` | Supabase Transaction Pooler URL（生产项目） |
| `PROD_PYTHON_BACKEND_URL` | 后端 Tunnel URL（固定域名） |

### CI/CD 流程

```
push to develop / main
    │
    ├── test-frontend   (lint + typecheck + unit tests)
    ├── test-e2e        (Playwright, 使用临时 CI Postgres)
    ├── test-python-backend (ruff + mypy + pytest)
    ├── test-java-backend
    └── security-scan (Trivy)
            │
            ▼ (all pass)
    deploy-staging (develop) / deploy-production (main)
        ├── Build: opennextjs-cloudflare build
        ├── Secrets: wrangler secret put (DATABASE_URL / AUTH_SECRET / PYTHON_BACKEND_URL)
        └── Deploy: wrangler deploy --env <staging|production>
```

---

## 7. Bundle 大小说明

| 指标 | 当前值 | Workers Paid 限制 |
|------|--------|-------------------|
| gzip 大小 | ~5.3 MiB | 10 MiB |

优化措施（已应用）：

| 措施 | 位置 |
|------|------|
| Shiki / Prettier / yaml / acorn stub | `patches/@opennextjs__cloudflare@1.17.0.patch` |
| `DB_MAX_CONNECTIONS=1` | `wrangler.toml [vars]` |

---

## 8. 部署检查清单

### 首次部署

- [ ] Cloudflare Workers Paid 计划已开通
- [ ] Supabase 项目已创建，schema 已初始化（`pnpm db:push && pnpm rbac:init`）
- [ ] Cloudflare Tunnel 已创建并绑定固定域名（`api.your-domain.com`）
- [ ] `FRONTEND_URLS` 已在 `backend/python/.env.development` 中包含 Workers 域名
- [ ] Wrangler secrets 已设置（`DATABASE_URL`、`AUTH_SECRET`、`PYTHON_BACKEND_URL`）
- [ ] GitHub Repository Secrets 已配置（`CLOUDFLARE_API_TOKEN`、`CLOUDFLARE_ACCOUNT_ID`）
- [ ] GitHub Environment Secrets 已配置（`staging` 和 `production` 各三个）
- [ ] 推送 `develop` 分支触发 CI/CD，确认 staging 部署成功

### 日常开发

- [ ] 本地启动后端：`uv run uvicorn src.wenexus.main:app --port 8000 --reload`
- [ ] 本地启动 Tunnel：`cloudflared tunnel run wenexus-backend`（固定域名，无需更新 secret）
- [ ] 功能开发在 feature 分支，PR 合并到 `develop` 自动触发 staging 部署
- [ ] `develop` → `main` PR 合并触发 production 部署

---

## 9. 相关文档

| 文档 | 说明 |
|------|------|
| [github-cicd.md](./github-cicd.md) | GitHub Actions CI/CD 详细配置指南 |
| [cloudflare-workers.md](./cloudflare-workers.md) | Workers 部署命令、bundle 大小、常见问题 |
| [backend-local-tunnel.md](./backend-local-tunnel.md) | Cloudflare Tunnel 详细配置（含固定域名） |
| [external-dependencies.md](./external-dependencies.md) | 所有外部服务依赖清单 |
