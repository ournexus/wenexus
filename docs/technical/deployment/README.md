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

---

## ✅ 已完成（一次性配置，已生效）

| 文档 | 已完成的事项 |
|------|------------|
| [deployment-plan.md §4.1](./deployment-plan.md) | Cloudflare Tunnel 创建 + 绑定固定域名 `api.aispeeds.me` |
| [deployment-plan.md §5.1](./deployment-plan.md) | Cloudflare Workers Paid 计划已开通（$5/月） |
| [deployment-plan.md §3](./deployment-plan.md) | Supabase 项目创建，schema 初始化（`db:push` + `rbac:init`） |
| [deployment-plan.md §5.2](./deployment-plan.md) | Wrangler Secrets 已设置（`DATABASE_URL` / `AUTH_SECRET` / `PYTHON_BACKEND_URL`） |
| [github-cicd.md §2](./github-cicd.md) | GitHub Repository Secrets + Environment Secrets 已配置 |

---

## 🔁 每次开发都要做（日常启动）

**后端 + Cloudflare Tunnel 已开机自启**，通常无需手动操作。

主动开发时用一键脚本（支持热重载）：

```bash
./scripts/dev.sh           # 全栈：数据库 + 前端 + 后端(--reload) + Tunnel
./scripts/dev.sh frontend  # 仅前端：数据库 + 前端
./scripts/dev.sh stop      # 停止所有
```

**改了后端代码后让线上生效：**

```bash
# 方案 A（开发中）：dev.sh 已有热重载，保存文件自动生效
# 方案 B（快速重启 LaunchAgent）：
launchctl stop com.wenexus.backend && launchctl start com.wenexus.backend
```

**改了前端代码推到线上：**

```
git push origin develop   →  自动 CI/CD → staging
develop → main PR 合并    →  自动 CI/CD → production
```

> 后端运行在本机，git push 不影响后端，重启服务即生效。

---

## 🔮 未来待做

| 事项 | 文档 | 说明 |
|------|------|------|
| 确认 staging 部署成功 | [deployment-plan.md §8](./deployment-plan.md) | 推送 `develop` 触发 CI，验证 staging 正常 |
| Bundle 优化 | [bundle-analysis.md](./bundle-analysis.md) | Lucide 按需引入（~400K）、移除未用 Stripe（~500K） |
| ~~Cloudflare Tunnel 开机自启~~ | ~~backend-local-tunnel.md §2.5~~ | ✅ 已完成：`cloudflared service install` + `com.wenexus.backend` LaunchAgent |

---

## 📖 参考文档

| 文档 | 用途 |
|------|------|
| [deployment-plan.md](./deployment-plan.md) | 部署方案全景（架构图、环境变量策略、完整检查清单） |
| [github-cicd.md](./github-cicd.md) | GitHub Actions CI/CD 配置详解（Secrets、Jobs、常见报错） |
| [cloudflare-workers.md](./cloudflare-workers.md) | Workers 部署命令、bundle 大小、多环境、常见问题 |
| [backend-local-tunnel.md](./backend-local-tunnel.md) | Cloudflare Tunnel 详细配置（临时模式 vs 固定域名模式） |
| [bundle-analysis.md](./bundle-analysis.md) | Worker bundle 组成分析与优化方案 |
| [dependency/external-dependencies.md](./dependency/external-dependencies.md) | 所有外部服务依赖清单（数据库、AI、支付、邮件等） |
