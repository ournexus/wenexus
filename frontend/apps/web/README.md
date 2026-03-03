# WeNexus Web

主 Web 应用，基于 Next.js，通过 OpenNext 部署到 Cloudflare Workers。

## 开发

```bash
pnpm install
cp .env.example .env.development  # 首次需配置环境变量
pnpm dev
```

## 部署

```bash
pnpm cf:preview   # 预览
pnpm cf:deploy    # 部署
```

## 环境变量配置

| 文件 | 用途 |
|------|------|
| `.env.example` | 变量模板 |
| `.env.development` | 本地开发（`next dev` 读取） |
| `wrangler.toml [vars]` | Cloudflare Workers 部署 |

`.env.development` 和 `wrangler.toml [vars]` 存在共享变量，修改时需同步更新。

敏感变量（`AUTH_SECRET`、`DATABASE_URL` 等）在 Workers 环境中通过 `wrangler secret put` 或 Cloudflare Dashboard 设置，不写入 `wrangler.toml`。
