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

## 🔁 日常开发

**后端 + Cloudflare Tunnel 已开机自启**，无需手动操作。

```bash
./scripts/dev.sh           # 全栈：数据库 + 后端(--reload) + Tunnel + 前端 Workers 预览
./scripts/dev.sh frontend  # 仅前端 Workers 预览（http://localhost:8787）
./scripts/dev.sh stop      # 停止所有
```

**改了后端代码：**

```bash
# 开发中（dev.sh 已有 --reload，保存自动生效）
# 或快速重启 LaunchAgent：
launchctl stop com.wenexus.backend && launchctl start com.wenexus.backend
```

**改了前端代码推到线上：**

```
git push origin develop   →  自动 CI/CD → staging
develop → main PR 合并    →  自动 CI/CD → production
```

> 后端运行在本机，git push 不影响后端，重启服务即生效。
> 一次性配置状态 → [deployment-plan.md §8 部署检查清单](./deployment-plan.md)

---

## 🔮 未来待做

| 事项 | 文档 | 说明 |
|------|------|------|
| Bundle 优化 | [bundle-analysis.md](./bundle-analysis.md) | Lucide 按需引入（~400K）、移除未用 Stripe（~500K） |

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
