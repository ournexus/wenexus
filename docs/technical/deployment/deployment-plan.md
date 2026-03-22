# WeNexus 部署方案全景

> 本文档梳理"前端部署到 Cloudflare Workers + 后端本地机器暴露"这套混合部署方案的完整流程、注意事项与操作步骤。

---

## 1. 整体架构

```
用户浏览器
    │
    ▼
Cloudflare Workers (前端 Next.js via OpenNext)
    │  PYTHON_BACKEND_URL
    ▼
Cloudflare Tunnel ──► 本地机器 :8000 (FastAPI)
                          │
                          ▼
                    本地 PostgreSQL :5432
                    本地 Redis      :6379
```

**说明：**

- 前端 Next.js 运行在 Cloudflare Workers 的 edge 网络上，静态资源由 Cloudflare Assets 托管（免费、无限）。
- 后端 FastAPI 运行在本地机器，通过 **Cloudflare Tunnel**（`cloudflared`）将本地端口安全暴露到公网，无需开放防火墙端口。
- 数据库（PostgreSQL/Redis）在本地 Docker 容器中运行，仅供本地后端访问，不直接对外暴露。

---

## 2. Cloudflare Workers 付费方案说明

### 为什么需要付费方案

当前项目前端 bundle gzip 约 **4.5 MiB**，超出免费计划 3 MiB 的 Worker 脚本上限，**必须升级到付费计划**才能部署。

| 计划 | Worker 脚本大小（gzip） | 费用 | 请求配额 |
|------|------------------------|------|----------|
| **Workers Free** | 3 MiB | 免费 | 10万次/天 |
| **Workers Paid** | **10 MiB** | **$5/月起** | 1000万次/月（含） |

本项目 bundle 约 4.5 MiB，Workers Paid 计划（10 MiB 上限）**完全够用**，不存在无法部署的情况。

### 如何开通 Workers Paid

这个付费方案不在普通的"个人/企业套餐"里，而是单独的 Workers 开发者平台订阅：

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 顶部导航选择你的账户
3. 左侧菜单 → **Workers & Pages**
4. 页面右侧找到 **Usage Model** 或 **Subscription** → 点击 **Upgrade to Paid**
5. 按提示完成付款（$5/月，包含 10M 次请求）

> **提示**：如果在 Workers & Pages 主页没找到订阅入口，也可以直接访问：
> `https://dash.cloudflare.com/<你的账户ID>/workers/plans`

---

## 3. 前端部署步骤

### 3.1 前置准备

```bash
# 安装 wrangler CLI（已在 devDependencies 中，无需全局安装）
cd frontend/apps/web
pnpm install

# 登录 Cloudflare（会弹出浏览器授权）
pnpm exec wrangler login
```

### 3.2 配置 Secrets

以下 secrets 必须在部署前配置好，否则运行时会报错：

```bash
# 数据库连接（必须是公网可访问的云数据库，本地 localhost 无效）
# 推荐：Neon (neon.tech) 或 Supabase 的 PostgreSQL
pnpm exec wrangler secret put DATABASE_URL

# 认证密钥
pnpm exec wrangler secret put AUTH_SECRET
# 生成方式：openssl rand -base64 32

# Python 后端地址（见第4节，使用 Cloudflare Tunnel 获取的公网 URL）
pnpm exec wrangler secret put PYTHON_BACKEND_URL
```

> ⚠️ **重要**：`DATABASE_URL` 必须指向公网可访问的数据库。
> Workers 运行在 Cloudflare 边缘节点，**无法访问你本地的 `localhost:5432`**。
> 详见 [数据库方案](#5-数据库方案) 一节。

### 3.3 构建并部署

```bash
cd frontend/apps/web

# 一键构建 + 部署
pnpm cf:deploy
```

等价命令：

```bash
opennextjs-cloudflare build && opennextjs-cloudflare deploy
```

### 3.4 部署到 staging / production 环境

`wrangler.toml` 中已预定义了两个环境：

```bash
# staging 环境
pnpm exec wrangler deploy --env staging

# production 环境
pnpm exec wrangler deploy --env production
```

### 3.5 本地预览 Workers 环境

```bash
pnpm cf:preview
```

此命令会在本地模拟 Workers 运行时，方便在部署前验证。

---

## 4. 后端本地暴露方案

详细步骤见 [backend-local-tunnel.md](./backend-local-tunnel.md)，此处列出核心流程。

### 推荐方案：Cloudflare Tunnel（免费）

```bash
# 1. 安装 cloudflared
brew install cloudflared

# 2. 登录 Cloudflare（仅首次需要）
cloudflared tunnel login

# 3. 创建 tunnel（仅首次，会生成一个 UUID）
cloudflared tunnel create wenexus-backend

# 4. 启动本地后端
cd backend/python
uv run uvicorn src.wenexus.main:app --host 0.0.0.0 --port 8000

# 5. 暴露本地端口（快速临时模式，无需额外配置）
cloudflared tunnel --url http://localhost:8000

# 控制台会打印类似：
# https://xxxx-xxxx-xxxx.trycloudflare.com → localhost:8000
```

将打印的公网 URL 设置为 `PYTHON_BACKEND_URL` secret：

```bash
pnpm exec wrangler secret put PYTHON_BACKEND_URL
# 输入：https://xxxx-xxxx-xxxx.trycloudflare.com
```

> **临时 URL 说明**：`trycloudflare.com` 的 URL 每次重启会变化。
> 若需要固定 URL，需绑定自定义域名（见 [backend-local-tunnel.md](./backend-local-tunnel.md)）。

---

## 5. 数据库方案

Workers 运行在 Cloudflare 边缘，**无法连接本地 PostgreSQL**，需要使用云数据库。

### 推荐：Neon（免费额度充足）

1. 注册 [neon.tech](https://neon.tech)
2. 创建项目，获取 connection string：

   ```
   postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

3. 运行数据库迁移：

   ```bash
   cd frontend/apps/web
   # 临时设置 DATABASE_URL 指向 Neon，然后：
   pnpm db:push
   pnpm rbac:init
   ```

4. 将 Neon 连接串配置为 Workers secret：

   ```bash
   pnpm exec wrangler secret put DATABASE_URL
   ```

### 备选：Supabase

1. 注册 [supabase.com](https://supabase.com)
2. 创建项目，使用 **Transaction Pooler** 连接串（适合 serverless 场景）
3. 步骤同 Neon

### 本地开发与线上数据库并存

本地开发时继续使用 `.env.development` 中的 `localhost:5432`，Workers secret 中使用云数据库，互不干扰。

---

## 6. 后端 CORS 配置

后端 FastAPI 需要允许来自 Workers 域名的跨域请求。编辑 `backend/python/src/wenexus/main.py`（或 CORS 配置处），将前端 Workers 域名加入允许列表：

```python
# 允许 Workers 域名（staging 和 production 都需要加）
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://wenexus-web.workers.dev",           # Workers 默认域名
    "https://wenexus-web-staging.workers.dev",   # staging
    "https://wenexus.com",                        # 自定义域名（如已配置）
]
```

---

## 7. 当前 Bundle 大小优化现状

项目已通过以下方式将 bundle 从 ~23 MiB 压缩到 ~4.5 MiB（gzip）：

| 优化措施 | 文件位置 | 节省量 |
|---------|---------|--------|
| Shiki 语言/主题 bundle stub | `patches/@opennextjs__cloudflare@1.17.0.patch` + `next.config.mjs` | ~10 MiB |
| Prettier / yaml / acorn stub | 同上 | ~3 MiB |
| DB 连接数限制（`DB_MAX_CONNECTIONS=1`） | `wrangler.toml` | 稳定性优化 |

当前 4.5 MiB gzip 在 Workers Paid 计划的 10 MiB 限制范围内，**无需进一步优化即可部署**。

若 bundle 持续增大，检查新增的大型依赖并在 `patches/@opennextjs__cloudflare@1.17.0.patch` 中追加 stub。

---

## 8. 部署检查清单

### 首次部署

- [ ] Cloudflare 账号已升级为 **Workers Paid** 计划
- [ ] `wrangler login` 登录成功
- [ ] 云数据库（Neon/Supabase）已创建并完成 schema 初始化
- [ ] `wrangler secret put DATABASE_URL` 已配置（云数据库）
- [ ] `wrangler secret put AUTH_SECRET` 已配置
- [ ] 本地后端通过 Cloudflare Tunnel 已暴露并获得公网 URL
- [ ] `wrangler secret put PYTHON_BACKEND_URL` 已配置
- [ ] 后端 CORS 配置已包含 Workers 域名
- [ ] `pnpm cf:deploy` 构建部署成功

### 日常重启后（Tunnel URL 变化时）

- [ ] 重新启动本地后端：`uv run uvicorn src.wenexus.main:app --port 8000`
- [ ] 重新启动 Cloudflare Tunnel：`cloudflared tunnel --url http://localhost:8000`
- [ ] 更新 Workers secret：`pnpm exec wrangler secret put PYTHON_BACKEND_URL`
- [ ] 重新部署 Worker（使 secret 生效）：`pnpm cf:deploy`

> **避免每次更新的方法**：为 Cloudflare Tunnel 绑定自定义域名（固定 URL），详见 [backend-local-tunnel.md](./backend-local-tunnel.md)。

---

## 9. 相关文档

| 文档 | 说明 |
|------|------|
| [cloudflare-workers.md](./cloudflare-workers.md) | Workers 部署命令、bundle 大小、常见问题 |
| [backend-local-tunnel.md](./backend-local-tunnel.md) | Cloudflare Tunnel 详细配置（含固定域名） |
| [external-dependencies.md](./external-dependencies.md) | 所有外部服务依赖清单 |
