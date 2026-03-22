# 部署文档索引

WeNexus 部署相关文档汇总。

## 文档列表

| 文档 | 说明 |
|------|------|
| [deployment-plan.md](./deployment-plan.md) | **部署方案全景**（从零开始的完整指南，推荐首先阅读） |
| [cloudflare-workers.md](./cloudflare-workers.md) | Cloudflare Workers 部署命令、bundle 大小、付费方案、常见问题 |
| [backend-local-tunnel.md](./backend-local-tunnel.md) | 后端本地暴露方案（Cloudflare Tunnel 详细配置） |
| [external-dependencies.md](./external-dependencies.md) | 所有外部服务依赖清单（数据库、AI、支付、邮件等） |

## 当前部署架构

```
前端  → Cloudflare Workers (Next.js via OpenNext)
后端  → 本地机器 via Cloudflare Tunnel
数据库 → 云数据库（Neon / Supabase）
存储  → Cloudflare R2（可选）
```

## 快速导航

- 首次部署？→ 阅读 [deployment-plan.md](./deployment-plan.md)
- Workers 付费方案怎么开通？→ [cloudflare-workers.md#workers-paid-计划开通方式](./cloudflare-workers.md#workers-paid-计划开通方式)
- 如何暴露本地后端？→ [backend-local-tunnel.md](./backend-local-tunnel.md)
- 需要哪些 API Key？→ [external-dependencies.md](./external-dependencies.md)
