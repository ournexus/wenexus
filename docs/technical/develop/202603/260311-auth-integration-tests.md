# 认证系统集成测试实现

> 实现日期：2026-03-11
> 涉及文件：`backend/python/tests/integration/facade/test_auth_endpoints.py`
> 参考文档：
>
> - `docs/technical/develop/202603/260308-auth-system-design.md`
> - `docs/technical/develop/202603/260311-reverse-proxy-setup.md`

## 一、测试目标

通过集成测试验证：

1. **认证依赖层** 正确从 Cookie 提取 token 并验证
2. **Cookie 传递机制** 在反向代理下工作正确
3. **异常流程处理** 无效token/过期token/无token 的正确响应
4. **UserInfo 数据结构** 映射正确

## 二、测试架构

### 2.1 测试分层

```
单元测试 (tests/unit/)
  ├─ config/test_settings.py         ✅ 已通过
  ├─ facade/test_deps.py             ✅ 已通过（Cookie提取）
  └─ service/test_auth.py            ✅ 已通过（业务逻辑）

集成测试 (tests/integration/)
  ├─ repository/test_auth_schema.py  ✅ 已通过（SQL兼容性）
  └─ facade/test_auth_endpoints.py   🔄 新增（端到端流程）
```

### 2.2 测试环境隔离

每个测试：

1. 创建独立的数据库连接（使用 `NullPool` 避免复用）
2. 创建测试用户和 session 数据
3. 创建测试 FastAPI 应用（dependency overrides）
4. 执行测试后自动清理数据

```python
@pytest_asyncio.fixture(scope="function")
async def async_db() -> AsyncSession:
    """真实数据库连接，每个测试独立"""
    engine = create_async_engine(
        "postgresql+asyncpg://wenexus:wenexus_dev_pwd@localhost:5432/wenexus_dev",
        echo=False,
        poolclass=NullPool,  # 禁用连接复用
    )
```

## 三、测试覆盖范围

### 3.1 认证流程测试 (`TestAuthenticationFlow`)

| 测试 | 场景 | 预期 |
|------|------|------|
| `test_protected_endpoint_with_valid_token` | 有效 token 访问受保护端点 | 200 + 用户信息 |
| `test_protected_endpoint_without_token` | 无 token 访问受保护端点 | 401 Unauthorized |
| `test_protected_endpoint_with_invalid_token` | 无效 token 访问受保护端点 | 401 Unauthorized |
| `test_protected_endpoint_with_expired_token` | 过期 token 访问受保护端点 | 401 Unauthorized |
| `test_public_endpoint_without_token` | 无 token 访问公开端点 | 200 + is_authenticated=False |
| `test_public_endpoint_with_valid_token` | 有效 token 访问公开端点 | 200 + 用户信息 |
| `test_public_endpoint_with_invalid_token` | 无效 token 访问公开端点 | 200 + is_authenticated=False |

**核心验证**：

- `get_current_user` 依赖：无 token → 401 异常
- `get_optional_user` 依赖：无 token → 返回 None（不异常）

### 3.2 Cookie 传递机制测试 (`TestCookieTransmission`)

| 测试 | 验证 |
|------|------|
| `test_cookie_name_must_match_exactly` | Cookie 名称精确匹配 `better-auth.session_token` |
| `test_cookie_name_is_case_sensitive` | Cookie 名称区分大小写 |
| `test_multiple_cookies_extraction` | 多 Cookie 场景下正确提取目标 token |

**关键发现**：

- `facade/deps.py` 中的 `get_session_token` 必须准确使用 Cookie 名称
- 错误的名称或大小写都会导致 token 无法提取（当作无 token 处理）

### 3.3 UserInfo 数据结构测试 (`TestUserInfoDataStructure`)

| 测试 | 验证 |
|------|------|
| `test_user_info_all_fields_present` | UserInfo 包含所有5个字段 |
| `test_user_info_email_verified_is_boolean` | email_verified 字段为 bool 类型 |
| `test_user_info_with_null_image` | image 字段可为 NULL |

**数据映射验证**：

- `email_verified`：从 DB 的 timestamp 转换为 bool
- `image`：支持 NULL 值
- 所有字段类型与 `util/schema.py` 中的 `UserInfo` dataclass 一致

## 四、测试数据准备

### 4.1 测试用户创建

```python
async def _setup_test_user(db: AsyncSession, user_id: str, is_expired: bool = False):
    """创建测试用户和session数据"""
    # 1. 清理旧数据
    # 2. 创建用户记录
    # 3. 创建 session 记录
    #    - expires_at: 有效期1小时或已过期
    #    - updated_at: 当前时间
    #    - ip_address, user_agent: 测试值
```

**关键细节**：

| 字段 | 值 | 说明 |
|------|-----|------|
| `id` | test-user-{suffix} | 测试用户唯一标识 |
| `token` | test-session-token-{suffix} | 唯一的 session token |
| `expires_at` | now() ± 1 hour | 有效或过期 |
| `email_verified` | Boolean | True for valid, False for expired |
| `image` | NULL | 测试 NULL 值处理 |

### 4.2 数据库表映射

**实际表结构** (Snake case)：

```sql
CREATE TABLE "session" (
    id TEXT PRIMARY KEY,
    token TEXT UNIQUE,  -- 用于认证查询
    user_id TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    ip_address TEXT,
    user_agent TEXT
);

CREATE TABLE "user" (
    id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    email_verified BOOLEAN,
    image TEXT
);
```

**注意**：数据库使用 snake_case，但之前的设计文档曾错误地引用了 camelCase 列名。正确的映射：

| 设计文档 | 数据库实际 | 说明 |
|---------|----------|------|
| `expiresAt` | `expires_at` | session 过期时间 |
| `userId` | `user_id` | session 所属用户 |
| `emailVerified` | `email_verified` | 邮箱验证状态 |

## 五、测试端点实现

### 5.1 受保护端点

```python
@app.get("/test/protected")
async def protected_endpoint(user: UserInfo = Depends(get_current_user)) -> dict:
    """需要认证的端点"""
    return {"message": "Protected endpoint", "user": {...}}
```

**行为**：

- 无效 token → 依赖注入层抛 401 HTTPException
- 有效 token → 获取 UserInfo 对象，返回 200

### 5.2 公开端点

```python
@app.get("/test/public")
async def public_endpoint(user: UserInfo | None = Depends(get_optional_user)) -> dict:
    """可选认证的端点"""
    if user is None:
        return {"message": "Public endpoint (no user)", "is_authenticated": False}
    return {"message": "Public endpoint (with user)", "is_authenticated": True, "user": {...}}
```

**行为**：

- 无 token 或无效 token → user=None，返回 200 + is_authenticated=False
- 有效 token → 返回 200 + is_authenticated=True + 用户信息

## 六、验证结果总结

### 6.1 通过的测试

**单元测试**：11 passed

```
config: 2 passed
facade/deps: 3 passed （Cookie提取、依赖注入）
service/auth: 4 passed （业务逻辑）
main: 2 passed
```

**集成测试（Schema）**：7 passed, 1 skipped

```
repository/test_auth_schema.py: 验证 SQL 与 Drizzle schema 兼容
```

**集成测试（端点）**：13 passed

```
TestAuthenticationFlow: 7 passed
TestCookieTransmission: 3 passed
TestUserInfoDataStructure: 3 passed
```

### 6.2 测试覆盖率

| 组件 | 覆盖 |
|------|------|
| Cookie 提取 | ✅ 单元测试 + 集成测试 |
| 必须认证依赖 | ✅ 单元测试 + 集成测试 |
| 可选认证依赖 | ✅ 单元测试 + 集成测试 |
| Session 查询 | ✅ 集成测试 (schema兼容性) |
| 反向代理 Cookie 传递 | ✅ 功能验证完成 |
| 异常流程（无token/过期token） | ✅ 集成测试 |

## 七、认证系统完整性检查

### 7.1 架构分层验证

```
✅ facade/deps.py        HTTP依赖注入层 - 提取Cookie、处理异常
✅ service/auth.py       业务逻辑层 - authenticate() 函数
✅ repository/auth.py    数据访问层 - SQL查询 (JOIN session+user)
✅ util/schema.py        跨层DTO - UserInfo dataclass
✅ 反向代理配置         Next.js rewrites + CORS 中间件
```

### 7.2 关键流程验证

```
Browser 请求 /api/py/v1/xxx (含 better-auth.session_token Cookie)
    ↓
Next.js 代理 → /api/v1/xxx
    ↓
FastAPI 路由
    ├─ @Depends(get_current_user)
    ├─ └─ get_session_token(request) 从 Cookie 提取 token
    ├─ └─ authenticate(db, token) 查询 session+user
    ├─ └─ 返回 UserInfo 或抛 401
    ↓
处理业务逻辑
    ↓
返回响应
```

## 八、后续优化方向

### 8.1 性能优化

- [ ] Session 查询缓存（TTL 30s，减少 DB 查询）
- [ ] 批量 token 验证（支持多认证场景）
- [ ] Connection pool 配置优化

### 8.2 安全加固

- [ ] Token 轮转机制（session 定期更新）
- [ ] 异常登录检测（IP/UA 变更告警）
- [ ] Session 锁定机制（防止并发使用）

### 8.3 功能扩展

- [ ] 多设备登录管理（查看/撤销其他设备）
- [ ] 登出所有设备功能
- [ ] 登录历史记录

## 九、关键文件清单

| 文件 | 用途 |
|------|------|
| `backend/python/tests/integration/facade/test_auth_endpoints.py` | 认证端点集成测试 |
| `backend/python/tests/integration/repository/test_auth_schema.py` | SQL schema 兼容性测试 |
| `backend/python/tests/unit/facade/test_deps.py` | Cookie 提取单元测试 |
| `backend/python/tests/unit/service/test_auth.py` | 业务逻辑单元测试 |
| `backend/python/src/wenexus/facade/deps.py` | HTTP 依赖注入实现 |
| `backend/python/src/wenexus/service/auth.py` | 认证业务逻辑 |
| `backend/python/src/wenexus/repository/auth.py` | 数据库查询 |
| `frontend/apps/web/next.config.mjs` | 反向代理配置 |

## 十、故障排查

### 常见问题

| 问题 | 排查 |
|------|------|
| 测试失败：Task attached to different loop | async fixture 与 pytest-asyncio 交互问题，使用 `NullPool` 和独立数据库连接 |
| 数据库约束错误 | 确保 INSERT 语句包含所有 NOT NULL 列（如 `updated_at`） |
| 列名不匹配 | 数据库使用 snake_case（`email_verified`），不是 camelCase |

---

**相关文档**：

- `docs/technical/develop/202603/260308-auth-system-design.md` - 认证系统总体设计
- `docs/technical/develop/202603/260311-reverse-proxy-setup.md` - 反向代理配置
- `progress.md` - 项目进度跟踪
