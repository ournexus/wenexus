# 后端本地暴露指南（Cloudflare Tunnel）

将本地机器的 FastAPI 后端安全暴露到公网，供 Cloudflare Workers 前端调用。

---

## 为什么需要 Tunnel

Cloudflare Workers 运行在 Cloudflare 边缘节点（全球分布式），**无法直接访问你的 `localhost:8000`**。
需要一个"隧道"将本地端口映射到一个公网可访问的 HTTPS URL。

**Cloudflare Tunnel vs ngrok 对比：**

| 特性 | Cloudflare Tunnel | ngrok 免费版 |
|------|:-----------------:|:------------:|
| 费用 | 免费 | 免费（随机 URL） |
| 固定 URL | ✅（绑定自定义域名） | ❌（每次随机） |
| 速度/延迟 | 低（Cloudflare 边缘） | 一般 |
| 需要账号 | Cloudflare 账号 | ngrok 账号 |
| 与 CF Workers 协同 | ✅ 原生 | 需要额外配置 CORS |

**推荐使用 Cloudflare Tunnel**，与前端 Workers 同在 Cloudflare 生态内，延迟更低，配置更简洁。

---

## 方案一：快速临时模式（开发调试用）

适合：快速测试，不需要固定 URL。每次重启 URL 会变化。

### 步骤

```bash
# 1. 安装 cloudflared（macOS）
brew install cloudflared

# 2. 启动本地后端
cd backend/python
uv run uvicorn src.wenexus.main:app --host 0.0.0.0 --port 8000 --reload

# 3. 新开一个终端，启动 Tunnel（无需登录，无需配置文件）
cloudflared tunnel --url http://localhost:8000
```

命令输出示例：

```
2024-01-01T00:00:00Z INF +--------------------------------------------------------------------------------------------+
2024-01-01T00:00:00Z INF |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable): |
2024-01-01T00:00:00Z INF |  https://liberal-accounts-whenever-existing.trycloudflare.com                            |
2024-01-01T00:00:00Z INF +--------------------------------------------------------------------------------------------+
```

### 更新 Workers Secret

将打印的 URL 更新到 Cloudflare Workers secret，然后重新部署：

```bash
cd frontend/apps/web

# 更新 secret
pnpm exec wrangler secret put PYTHON_BACKEND_URL
# 粘贴：https://liberal-accounts-whenever-existing.trycloudflare.com

# 重新部署（使 secret 生效）
pnpm cf:deploy
```

---

## 方案二：固定域名模式（生产推荐）

URL 固定不变，每次重启后端/Tunnel 无需重新更新 secret。

**前提**：需要在 Cloudflare 管理一个域名（如 `wenexus.com`）。

### 2.1 登录并创建 Tunnel

```bash
# 登录 Cloudflare（弹出浏览器授权）
cloudflared tunnel login

# 创建命名 Tunnel（只需创建一次）
cloudflared tunnel create wenexus-backend
# 输出：Created tunnel wenexus-backend with id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
# 同时在 ~/.cloudflared/ 下生成凭证文件
```

### 2.2 创建配置文件

创建 `~/.cloudflared/config.yml`：

```yaml
tunnel: wenexus-backend
credentials-file: /Users/mac/.cloudflared/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.json

ingress:
  - hostname: api.wenexus.com      # 替换为你的域名
    service: http://localhost:8000
  - service: http_status:404
```

> 将 `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` 替换为上一步输出的 Tunnel ID。
> 将 `api.wenexus.com` 替换为你实际的域名。

### 2.3 添加 DNS 记录

```bash
# 在 Cloudflare DNS 中创建 CNAME 记录，将子域名指向 Tunnel
cloudflared tunnel route dns wenexus-backend api.wenexus.com
```

### 2.4 启动 Tunnel

```bash
# 使用配置文件启动
cloudflared tunnel run wenexus-backend
```

启动后，`https://api.wenexus.com` 将固定转发到本地 `:8000`。

### 2.5 设置为系统服务（可选，开机自启）

```bash
# 安装为 macOS LaunchDaemon
sudo cloudflared service install
sudo launchctl start com.cloudflare.cloudflared
```

---

## 后端配置

### 确保后端监听所有接口

```bash
# 启动命令必须带 --host 0.0.0.0
uv run uvicorn src.wenexus.main:app --host 0.0.0.0 --port 8000
```

### CORS 配置

后端需要允许来自 Workers 域名的请求。找到 FastAPI 的 CORS 配置（通常在 `src/wenexus/main.py`），添加 Workers 域名：

```python
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "http://localhost:3000",                       # 本地前端开发
    "https://wenexus-web.workers.dev",             # Workers 默认域名
    "https://wenexus-web-staging.workers.dev",     # staging
    "https://wenexus.com",                         # 自定义域名
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 请求链路验证

部署完成后，验证完整链路：

```bash
# 1. 直接测试后端健康检查
curl https://xxxx.trycloudflare.com/api/v1/health
# 期望返回：{"status": "ok"}

# 2. 通过前端 Workers 代理测试
curl https://wenexus-web.workers.dev/api/py/v1/health
# 期望返回：{"status": "ok"}
```

> 前端 Workers 会将 `/api/py/v1/*` 的请求代理到 `PYTHON_BACKEND_URL/api/v1/*`，
> 配置见 `frontend/apps/web/next.config.mjs` 中的 `rewrites()`。

---

## 常见问题

### Tunnel 连接失败

```
ERR  failed to connect to the origin  error="dial tcp 127.0.0.1:8000: connect: connection refused"
```

原因：本地后端未启动。先启动后端再运行 Tunnel。

### 502 Bad Gateway

原因：Tunnel 连接到了后端，但后端请求处理出错。查看后端日志排查。

### CORS 错误

```
Access to fetch at 'https://xxxx.trycloudflare.com' from origin 'https://wenexus-web.workers.dev' 
has been blocked by CORS policy
```

原因：后端 CORS 配置未包含 Workers 域名。按上面的 [CORS 配置](#cors-配置) 更新。

### 临时 URL 每次变化

这是 `trycloudflare.com` 的设计。解决方案：使用 [方案二（固定域名模式）](#方案二固定域名模式生产推荐)。
