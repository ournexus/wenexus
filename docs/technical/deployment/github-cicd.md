# GitHub Actions CI/CD 配置指南

WeNexus 使用 GitHub Actions 自动化测试和部署。配置文件：`.github/workflows/ci-cd.yml`。

---

## 1. 分支策略

| 分支 | 用途 | 自动触发 |
|------|------|---------|
| `feature/*` | 功能开发 | 无（仅 PR 检查） |
| `develop` | 集成测试 / staging | `deploy-staging` |
| `main` | 生产 | `deploy-production` |

开发流程：`feature/* → develop (PR) → main (PR)`

---

## 2. GitHub Secrets 配置

进入仓库 **Settings → Secrets and variables → Actions** 配置以下内容。

### 2.1 Repository Secrets（所有环境共用）

| Secret 名称 | 获取方式 |
|-------------|---------|
| `CLOUDFLARE_API_TOKEN` | Cloudflare Dashboard → My Profile → API Tokens → Create Token → 使用 **Edit Cloudflare Workers** 模板 |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare Dashboard → Workers & Pages → 右侧 Account ID |

**Cloudflare API Token 权限要求：**

- `Account` → `Cloudflare Workers Scripts` → `Edit`
- `Zone` → `Workers Routes` → `Edit`（如果使用自定义域名）

### 2.2 Environment Secrets

在仓库 **Settings → Environments** 分别创建 `staging` 和 `production` 两个 Environment，然后各自添加以下 Secrets：

**`staging` Environment：**

| Secret 名称 | 值 |
|-------------|---|
| `STAGING_AUTH_SECRET` | `openssl rand -base64 32` 生成 |
| `STAGING_DATABASE_URL` | Supabase staging 项目的 Transaction Pooler URL |
| `STAGING_PYTHON_BACKEND_URL` | `https://api.your-domain.com`（Cloudflare Tunnel 固定域名） |

**`production` Environment：**

| Secret 名称 | 值 |
|-------------|---|
| `PROD_AUTH_SECRET` | `openssl rand -base64 32` 生成（与 staging 不同） |
| `PROD_DATABASE_URL` | Supabase 生产项目的 Transaction Pooler URL |
| `PROD_PYTHON_BACKEND_URL` | `https://api.your-domain.com`（同 staging 或不同子域） |

> 建议为 `production` Environment 开启 **Required reviewers**（Settings → Environments → production → Protection rules），防止误操作直接触发生产部署。

---

## 3. CI/CD Jobs 说明

### 测试 Jobs（并行，所有分支均触发）

| Job | 说明 |
|-----|------|
| `test-frontend` | pnpm lint + typecheck + 单元测试 |
| `test-e2e` | Playwright E2E，使用临时 CI PostgreSQL 服务容器 |
| `test-python-backend` | ruff check/format + mypy + pytest unit tests |
| `test-java-backend` | mvn test + mvn package |
| `security-scan` | Trivy 漏洞扫描，结果上传到 GitHub Security 面板 |

### 部署 Jobs

部署 Job 在所有测试 Job 通过后才运行：

```yaml
needs: [test-frontend, test-e2e, test-java-backend, test-python-backend, security-scan]
```

**部署流程（staging / production 相同）：**

1. `pnpm cf:build` — OpenNext 构建，生成 `.open-next/` 产物
2. `wrangler secret put` — 将 GitHub Secrets 同步到 Cloudflare Workers Secrets
3. `wrangler deploy --env <staging|production>` — 上传 Worker 脚本到 Cloudflare

> **为什么分两步（build 再 deploy）？**
> `pnpm cf:deploy` 等价于 build + deploy 合并执行，但分开写可以在 build 失败时更早发现问题，
> 也让 secret 注入步骤更清晰可见。

---

## 4. Wrangler Secrets 在 CI 中的工作方式

Cloudflare Workers Secrets 存储在 Cloudflare 侧，与代码部署分离。

CI/CD 中每次部署前会执行：

```bash
echo "$SECRET_VALUE" | pnpm exec wrangler secret put SECRET_NAME --env <env>
```

这会**覆盖**已有的同名 secret，所以：

- 首次部署会创建 secret
- 后续部署会用 GitHub Secrets 中的值更新 secret
- 如果 GitHub Secret 没有变化，Cloudflare 侧的值也不会变（Wrangler 会检测到相同值，跳过更新）

`CLOUDFLARE_API_TOKEN` 和 `CLOUDFLARE_ACCOUNT_ID` 由 Wrangler CLI 自动从环境变量中读取，不需要显式传入命令行参数。

---

## 5. 手动触发部署

如果需要在不推送代码的情况下重新部署（例如只更新了 Secrets），可以：

**方法 A：通过 GitHub Actions 界面**

1. 进入仓库 **Actions** 面板
2. 选择 **CI/CD Pipeline** workflow
3. 点击 **Run workflow** → 选择分支 → 运行

**方法 B：本地手动部署**

```bash
cd frontend/apps/web

# 更新 secrets
echo "new-value" | pnpm exec wrangler secret put DATABASE_URL --env production

# 仅部署（无需重新构建，如果 Worker 代码未变）
pnpm exec wrangler deploy --env production
```

---

## 6. 常见问题

### CI 部署失败：`Authentication error`

原因：`CLOUDFLARE_API_TOKEN` 未配置或已过期。

检查：

1. GitHub Settings → Secrets → 确认 `CLOUDFLARE_API_TOKEN` 存在
2. Cloudflare Dashboard → API Tokens → 确认 Token 未被撤销
3. Token 权限是否包含 `Workers Scripts:Edit`

### CI 部署失败：`Could not route to environment`

原因：`wrangler.toml` 中未定义对应的 `[env.staging]` 或 `[env.production]`。

检查 `frontend/apps/web/wrangler.toml` 中是否有：

```toml
[env.staging]
name = "wenexus-web-staging"

[env.production]
name = "wenexus-web-production"
```

### E2E 测试失败：数据库连接超时

原因：`test-e2e` Job 使用 GitHub Actions 的 Service Container 启动临时 PostgreSQL，偶尔启动慢。

解决：检查 Job 中 `postgres` service 的 `health-check` 配置是否正确（已在 `ci-cd.yml` 中配置）。

### `wrangler secret put` 卡住

Cloudflare API 偶尔响应慢，等待 30 秒以上是正常的。若超时，重新触发 CI 即可。
