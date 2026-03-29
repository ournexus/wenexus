# 部署文档索引

WeNexus 部署相关文档汇总。

## 当前部署架构

```
前端  → Cloudflare Workers (Next.js via OpenNext)
后端  → 本地机器 via Cloudflare Tunnel（固定域名）
数据库 → Supabase (Transaction Pooler)
缓存  → Upstash Redis
CI/CD → GitHub Actions (develop → staging, main → production)
```

## 文档列表

| 文档 | 说明 |
|------|------|
| [deployment-plan.md](./deployment-plan.md) | **部署方案全景**（架构、环境变量策略、检查清单） |
| [github-cicd.md](./github-cicd.md) | **GitHub Actions CI/CD 配置**（Secrets 设置、Jobs 说明、常见问题） |
| [cloudflare-workers.md](./cloudflare-workers.md) | Cloudflare Workers 部署命令、bundle 大小、付费方案 |
| [backend-local-tunnel.md](./backend-local-tunnel.md) | Cloudflare Tunnel 详细配置（固定域名方案） |
| [external-dependencies.md](./external-dependencies.md) | 所有外部服务依赖清单（数据库、AI、支付、邮件等） |

## 快速导航

- 首次部署？→ 从 [deployment-plan.md](./deployment-plan.md) 开始
- 配置 GitHub CI/CD？→ [github-cicd.md](./github-cicd.md)
- 如何暴露本地后端？→ [backend-local-tunnel.md](./backend-local-tunnel.md)
- Workers 付费方案怎么开通？→ [cloudflare-workers.md](./cloudflare-workers.md)
- 需要哪些 API Key？→ [external-dependencies.md](./external-dependencies.md)
