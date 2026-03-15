# Cloudflare Workers 部署指南

WeNexus 前端使用 [OpenNext Cloudflare](https://opennext.js.org/cloudflare) 将 Next.js 应用部署到 Cloudflare Workers。

## 前置要求

- Node.js 20+
- pnpm 9+
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/) (`pnpm add -g wrangler`)
- Cloudflare 账号（**需要 Workers 付费计划**，bundle gzip 约 4.5 MiB，超出免费计划 3 MiB 限制）

## 环境变量与 Secrets

### `wrangler.toml` 中的公开变量

`wrangler.toml` 已包含非敏感变量，无需额外配置：

```toml
[vars]
NEXT_PUBLIC_APP_NAME = "WeNexus"
NEXT_PUBLIC_THEME = "default"
NEXT_PUBLIC_APPEARANCE = "system"
DATABASE_PROVIDER = "postgresql"
```

### 需要手动配置的 Secrets

通过 `wrangler secret put` 或 Cloudflare Dashboard 配置以下敏感变量：

```bash
# 数据库连接（PostgreSQL / Neon / Supabase 等）
pnpm exec wrangler secret put DATABASE_URL

# Auth 密钥（openssl rand -base64 32 生成）
pnpm exec wrangler secret put AUTH_SECRET

# Python 后端地址
pnpm exec wrangler secret put PYTHON_BACKEND_URL
```

## 部署命令

在 `frontend/apps/web` 目录下执行：

```bash
# 完整构建并部署（推荐）
pnpm cf:deploy

# 仅构建，不部署
pnpm cf:build

# 本地预览 Cloudflare Workers 环境
pnpm cf:preview
```

`cf:deploy` 等价于：

```bash
opennextjs-cloudflare build && opennextjs-cloudflare deploy
```

## 多环境部署

`wrangler.toml` 中已定义 `staging` 和 `production` 环境：

```bash
# 部署到 staging
pnpm exec wrangler deploy --env staging

# 部署到 production
pnpm exec wrangler deploy --env production
```

## Bundle 大小说明

| 指标 | 当前值 | 限制 |
|------|--------|------|
| 未压缩大小 | ~23 MiB | 无硬性限制 |
| gzip 大小 | ~4.5 MiB | 免费计划 3 MiB / 付费计划 10 MiB |

大型依赖（shiki、micromark、@mdx-js/mdx 等）已在 esbuild 打包阶段通过 stub 排除，
具体配置见 `patches/@opennextjs__cloudflare@1.17.0.patch`。

## 构建产物

```
.open-next/
├── worker.js               # Wrangler 入口（引用 server-functions）
├── assets/                 # 静态资源（上传为 Cloudflare Assets）
├── server-functions/
│   └── default/
│       └── apps/web/
│           └── handler.mjs # Worker 脚本主体
└── middleware/
    └── handler.mjs         # Edge middleware
```

## 常见问题

### `Your Worker exceeded the size limit`

Worker bundle gzip 超出计划限制。解决方案：

1. 升级到 Workers 付费计划（$5/月，10 MiB 限制）
2. 检查是否有新的大型依赖被引入，在 `bundle-server.js` patch 中追加 stub

### `No matching export` 构建错误

stub 模块缺少某个 named export。在 patch 文件中 `empty.js` shim 里补充对应的 no-op export。

### 上传卡住不动

Cloudflare API 处理大文件较慢，等待 3-5 分钟是正常的。若长时间无响应，检查网络或重试。
