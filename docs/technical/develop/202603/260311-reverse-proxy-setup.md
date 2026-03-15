# 反向代理配置与 Cookie 同域传递实现

> 实现日期：2026-03-11
> 涉及文件：`frontend/apps/web/next.config.mjs`
> 参考文档：`docs/technical/develop/202603/260308-auth-system-design.md` §2.2

## 一、需求回顾

根据认证系统设计（§2.2），Next.js 前端和 Python FastAPI 后端运行在不同的端口上（3000 vs 8000）。浏览器的同源策略（SOP）默认不允许跨端口的 Cookie 传递，因此需要通过反向代理统一域名。

### 1.1 开发环境方案

开发环境采用 **Next.js rewrites** 代理方案：

```
Browser                Next.js (localhost:3000)      Python Backend (localhost:8000)
   │                         │                                │
   │── /api/py/v1/* ────────→│                                │
   │                         │── /api/v1/* ─────────────────→│
   │                         │                     DB查询      │
   │◀─── 响应 ───────────────│◀──────────────────────────────│
   │    (自动包含Cookie)
```

**关键特性**：

- 浏览器的所有请求仍然发送到 `localhost:3000`
- Cookie 的 Domain 和 Path 天然匹配 `localhost:3000`
- 无需 CORS 配置，完全规避跨域问题
- 中间件自动转发 Cookie（包括 `better-auth.session_token`）

## 二、实现细节

### 2.1 路由映射设计

**路由层级约定**：

| 层级 | 说明 |
|------|------|
| `/api/py/` | Next.js 代理层前缀（标记请求转发到 Python） |
| `/api/v1/` | Python 后端 API 版本号 |
| `/roundtable`, `/deliverable` | 领域路由 |

**完整请求路径示例**：

```
前端请求：    GET /api/py/v1/roundtable/sessions
    ↓ (Next.js rewrites)
代理到：     GET http://localhost:8000/api/v1/roundtable/sessions
```

### 2.2 rewrites 配置实现

**文件**：`frontend/apps/web/next.config.mjs`

```javascript
async rewrites() {
  return [
    {
      // Rewrite /api/py/v1/* to Python backend /api/v1/*
      // 这允许请求保持在 localhost:3000 域名内，
      // 保留 Cookie 域名匹配，无需 CORS。
      // 参考：docs/technical/develop/202603/260311-reverse-proxy-setup.md
      source: '/api/py/v1/:path*',
      destination: `${process.env.PYTHON_BACKEND_URL || 'http://localhost:8000'}/api/v1/:path*`,
    },
  ];
}
```

**关键设计决策**：

1. **source 路径**：`/api/py/v1/:path*`
   - 明确指定前端访问的路径
   - `/api/py/` 是代理层标记，后端无感知
   - `/v1/` 与后端 API 版本对应

2. **destination 路径处理**：
   - 去掉 `/api/py/` 前缀（只有Next.js才需要）
   - 保留 `/api/v1/:path*`（这是Python后端的真实路由）

3. **环境变量**：
   - `PYTHON_BACKEND_URL`：从 `.env.development` 读取（默认 `http://localhost:8000`）
   - 支持配置 Cloudflare Tunnel 等远程后端

### 2.3 环境配置

**文件**：`frontend/apps/web/.env.development`

```bash
PYTHON_BACKEND_URL = "http://localhost:8000"
```

**生产部署注意**：在 Nginx/Caddy 等真实反向代理环境中，应配置类似的路由规则：

```nginx
# Nginx example
location /api/py/v1/ {
    rewrite ^/api/py/v1/(.*)$ /api/v1/$1 break;
    proxy_pass http://python-backend:8000;
    proxy_set_header Cookie $http_cookie;
}
```

## 三、Cookie 传递机制

### 3.1 自动传递流程

当浏览器请求 `/api/py/v1/roundtable/sessions` 时：

1. **浏览器**发送请求，自动包含 Cookie：

   ```
   GET /api/py/v1/roundtable/sessions HTTP/1.1
   Cookie: better-auth.session_token=xxx; ...
   ```

2. **Next.js 服务器**接收请求并代理：

   ```
   GET http://localhost:8000/api/v1/roundtable/sessions HTTP/1.1
   Cookie: better-auth.session_token=xxx; ...
   ```

3. **Python FastAPI**收到请求：

   ```python
   # 在 facade/deps.py 中
   async def get_session_token(request: Request) -> str | None:
       return request.cookies.get("better-auth.session_token")
   ```

4. **验证流程**：
   - `facade/deps.py` 从 Cookie 提取 token
   - `service/auth.py` 调用 `authenticate()`
   - `repository/auth.py` 执行 SQL 查询验证 token

### 3.2 Python 后端 CORS 配置

**文件**：`backend/python/src/wenexus/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],  # http://localhost:3000
    allow_credentials=True,  # 允许跨域 Cookie
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**说明**：

- 在开发环境中，CORS 配置**不是必需的**（因为请求是 server-to-server）
- 但配置它增加了灵活性，支持直接访问后端的场景（如调试、移动应用）

## 四、集成测试验证

### 4.1 反向代理测试

**验证命令**：

```bash
# 通过前端代理请求后端 API
curl -s http://localhost:3000/api/py/v1/roundtable/sessions | jq

# 预期输出
{
  "sessions": [],
  "total": 0
}
```

### 4.2 集成测试

**文件**：`backend/python/tests/integration/repository/test_auth_schema.py`

测试覆盖：

- ✅ session 和 user 表的列结构兼容性
- ✅ SELECT 查询语法正确性
- ✅ JOIN 查询字段名匹配
- ✅ UserInfo dataclass 映射
- ✅ NULL 值处理

**运行结果**：

```
7 passed, 1 skipped in 0.48s
```

## 五、生产部署注意

### 5.1 Nginx 反向代理示例

```nginx
upstream python_backend {
    server localhost:8000;
}

upstream next_frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name wenexus.com;

    # 前端应用
    location / {
        proxy_pass http://next_frontend;
    }

    # Python API 代理
    location /api/py/v1/ {
        rewrite ^/api/py/v1/(.*)$ /api/v1/$1 break;
        proxy_pass http://python_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cookie_path / /;  # 保留 Cookie 路径
    }
}
```

### 5.2 Caddy 配置示例

```caddy
wenexus.com {
    route /api/py/v1/* {
        uri strip_prefix /api/py
        reverse_proxy localhost:8000
    }

    route /* {
        reverse_proxy localhost:3000
    }
}
```

## 六、故障排查

### 6.1 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Cookie 未传递 | 代理 source/destination 路径不匹配 | 检查 next.config.mjs 的 rewrites 配置 |
| 401 Unauthorized | 后端无法从 Cookie 读取 token | 检查 `facade/deps.py` 的 Cookie 名称 |
| CORS 错误 | 生产环境未配置反向代理 | 确保 Nginx/Caddy 配置正确 |
| 路由 404 | 前端请求路径与后端路由不匹配 | 确保 source/destination 转换正确 |

### 6.2 调试建议

1. **检查 Network 请求**：

   ```bash
   curl -v http://localhost:3000/api/py/v1/roundtable/sessions
   ```

2. **查看 Cookie 传递**：

   ```bash
   curl -b "better-auth.session_token=test-token" \
        http://localhost:3000/api/py/v1/roundtable/sessions
   ```

3. **查看后端日志**：

   ```bash
   # Python 后端会输出请求日志
   INFO:     127.0.0.1:xxxx - "GET /api/v1/roundtable/sessions HTTP/1.1" 200 OK
   ```

## 七、验证清单

- [x] next.config.mjs rewrites 配置正确
- [x] 前端代理请求测试通过
- [x] Python 后端集成测试通过（7 passed, 1 skipped）
- [x] 单元测试全部通过（11 passed）
- [x] 前端 lint 和 typecheck 通过
- [x] 环境变量 `PYTHON_BACKEND_URL` 配置完整
- [x] CORS 中间件配置完整

## 八、后续工作

1. **认证集成测试**：需要创建真实用户和 session，验证 Cookie 传递的完整流程
2. **生产部署验证**：在 Nginx/Caddy 环境中验证反向代理
3. **性能优化**：如有必要，考虑在代理层添加缓存或连接池

---

**相关文档**：

- `docs/technical/develop/202603/260308-auth-system-design.md` - 认证系统设计
- `docs/prd/domain-architecture.md` - 域架构设计
