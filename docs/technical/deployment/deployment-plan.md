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

FastAPI 在本地运行，通过 Cloudflare Tunnel 暴露固定域名 `https://api.aispeeds.me`。
后端（`com.wenexus.backend` LaunchAgent）和 Tunnel（`com.cloudflare.cloudflared` LaunchDaemon）均已设置**开机自启**。

首次配置步骤、CORS 设置、故障排查 → [backend-local-tunnel.md](./backend-local-tunnel.md)

---

## 5. 前端：Cloudflare Workers

Next.js 通过 OpenNext 部署到 Cloudflare Workers（Paid 计划 $5/月，已开通）。

| 场景 | 命令 |
|------|------|
| 本地预览（模拟线上） | `./scripts/dev.sh frontend`（读取 `.dev.vars`） |
| 手动部署 | `cd frontend/apps/web && pnpm cf:deploy` |
| CI/CD 自动部署 | push 到 `develop` / `main` 自动触发 |

部署命令详解、多环境配置、常见问题 → [cloudflare-workers.md](./cloudflare-workers.md)

---

## 6. CI/CD：GitHub Actions

`develop` push → staging 自动部署；`main` push → production 自动部署。所有 GitHub Secrets 已配置完成。

| 分支 | 目标环境 |
|------|----------|
| `develop` | `wenexus-web-staging.workers.dev` |
| `main` | `wenexus-web.yihuimbin.workers.dev` |

Secrets 配置方法、Jobs 说明、常见报错 → [github-cicd.md](./github-cicd.md)

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

- [x] Cloudflare Workers Paid 计划已开通
- [x] Supabase 项目已创建，schema 已初始化（`pnpm db:push && pnpm rbac:init`）
- [x] Cloudflare Tunnel 已创建并绑定固定域名（`api.aispeeds.me`）
- [x] `FRONTEND_URLS` 已在 `backend/python/.env.development` 中包含 Workers 域名
- [x] Wrangler secrets 已设置（`DATABASE_URL`、`AUTH_SECRET`、`PYTHON_BACKEND_URL`）
- [x] GitHub Repository Secrets 已配置（`CLOUDFLARE_API_TOKEN`、`CLOUDFLARE_ACCOUNT_ID`）
- [x] GitHub Environment Secrets 已配置（`staging` 和 `production` 各三个）
- [x] 推送 `develop` 分支触发 CI/CD，确认 staging 部署成功

### 日常开发

- 后端 + Tunnel 已**开机自启**，无需手动启动
- [ ] 本地预览前端：`./scripts/dev.sh frontend`（Workers 预览，`http://localhost:8787`）
- [ ] 功能开发在 feature 分支，PR 合并到 `develop` 自动触发 staging 部署
- [ ] `develop` → `main` PR 合并触发 production 部署
