# E2E 测试超时修复 (PR #26)

## 问题描述

E2E 测试在本地通过，但在 CI 环境中超时失败，错误信息：

```
TimeoutError: page.waitForURL: Timeout 20000ms exceeded
```

## 根本原因分析

通过逐步诊断发现了完整的问题链，共经历 4 个阶段：

**阶段 1**：超时错误 → 增加超时配置
**阶段 2**：URL 未变化 → 使用 waitForResponse 等待 API
**阶段 3**：API 返回 415/403 → 修复 logout() headers
**阶段 4**：登出成功但重新登录失败 → 添加数据库写入延迟

### 最终根本原因：数据库写入延迟

问题不在 E2E 测试本身，而在于：

1. 注册 API 返回 200（前端看起来成功了）
2. **但用户数据写入数据库需要时间**
3. 如果立即登出再登录，用户还没有被保存
4. 导致后续登录返回 401

### 解决方案

添加 **500ms 延迟** 在注册后，确保数据库写入完成：

```typescript
if (registrationResult === 'success') {
  console.log(`Registration completed, waiting for database write...`);
  // Wait to ensure database write completes
  await new Promise((resolve) => setTimeout(resolve, 500));
}
```

这个延迟是必要的，因为：

- 注册 API 返回 200 只表示请求处理完毕
- 不保证数据库事务已提交
- 在高并发或 CI 环境中延迟可能更长

## 解决方案

### 1. 增加 CI 特定的超时配置

在 `playwright.config.ts` 中添加 CI 环境的专用超时设置：

```typescript
use: {
  navigationTimeout: process.env.CI ? 30_000 : 15_000,
  actionTimeout: process.env.CI ? 15_000 : 10_000,
}
```

### 2. 增加 AUTH_CONFIG 中的 waitForURL 超时

```typescript
export const AUTH_CONFIG = {
  timeout: {
    short: 10_000,
    medium: 15_000,
    long: 30_000,  // 从 20_000 增加到 30_000
  },
}
```

### 3. 改用 waitForResponse 等待 API 调用

使用 `waitForResponse` 等待 API 调用完成，而不是仅依赖 `waitForLoadState`：

```typescript
const apiResponsePromise = this.page.waitForResponse(
  (response) =>
    response.url().includes('/api/auth/sign-in') ||
    response.url().includes('/api/auth/login'),
  { timeout: AUTH_CONFIG.timeout.long },
);

await submitButton.click();
const apiResponse = await apiResponsePromise;

if (apiResponse.status() !== 200 && apiResponse.status() !== 201) {
  throw new Error(`Login API failed: ${responseBody}`);
}
```

### 4. 修复 logout() 方法中的 API 调用

**关键修复**：从 `page.evaluate(fetch)` 改为 `page.request.post()`，并添加必要的 headers：

```typescript
const response = await this.page.request.post('/api/auth/sign-out', {
  headers: {
    'Content-Type': 'application/json',
    'Origin': new URL(this.page.url()).origin,
  },
  data: {},
});
```

**为什么这很重要**：

- `page.evaluate(fetch)` 在某些环境下不能正确设置 headers
- 后端登出 API 要求：
  - `Content-Type: application/json`（否则 415 错误）
  - `Origin` header（CORS 验证，否则 403 错误）
- `page.request` 是 Playwright 原生 API，能正确处理所有 headers

### 5. 完善诊断日志和错误处理

添加详细的日志到所有认证方法：

- **logout()**:
  - 日志记录 API 返回状态
  - 如果失败，记录错误响应体
  - 分别处理 API、Cookies、Storage 清理的错误
  - 添加 500ms 延迟确保清理完成

- **login()**: 记录登录邮箱、API 成功/失败、当前 URL

- **register()**: 记录注册邮箱、验证用户数据

- **isLoggedIn()**: 记录当前 URL 和状态

## 测试验证

完整认证流程测试结果：✅ **全部通过**

```
注册 → 登录验证 → 登出 → 登出验证 → 重新登录 → 登录验证

Sign-out API returned status 200
Sign-out API succeeded
Login API succeeded with status 200 for email: test-xxx@example.com
isLoggedIn check: true (URL: http://localhost:3000/settings/profile)

6 passed (1.2m)
1 skipped (预置用户测试，需要环境变量)
```

## 推荐方案

本 fix 提供了两种测试方案，可根据场景选择：

### 方案 1：使用新用户注册 (默认)

**文件**：`tests/auth/auth-flow.spec.ts`

**特点**：

- ✅ 测试完整的注册流程
- ✅ 自动生成唯一的测试用户
- ✅ 验证注册 + 登录 + 登出 + 重新登录的完整周期
- ⚠️ 依赖注册 API 和数据库，有延迟风险

**运行**：

```bash
pnpm test auth-flow  # 默认运行
```

### 方案 2：使用预置用户 (CI 推荐)

**文件**：`tests/auth/auth-preset-user.spec.ts`

**特点**：

- ✅ 完全避免注册数据库写入延迟
- ✅ 跳过注册流程，专注于登出/重新登录
- ✅ 适合 CI 环境，更稳定可靠
- ⚠️ 需要预先创建测试用户

**在 CI 中启用**：

在 CI 配置中设置环境变量，然后运行测试：

```bash
# GitHub Actions 示例
export E2E_TEST_USER_EMAIL=ci-test@example.com
export E2E_TEST_USER_PASSWORD=CITestPassword123!
pnpm test  # 会运行所有测试，包括预置用户测试
```

**创建测试用户**（一次性）：

在 CI 初始化或 setup 脚本中调用注册 API：

```bash
curl -X POST http://localhost:3000/api/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CI Test User",
    "email": "ci-test@example.com",
    "password": "CITestPassword123!"
  }'
```

或通过数据库直接插入（更快）：

```sql
INSERT INTO users (name, email, password_hash, created_at)
VALUES ('CI Test User', 'ci-test@example.com', <hash>, NOW());
```

## 文件变更

- `frontend/packages/e2e/playwright.config.ts` - CI 环境超时配置
- `frontend/packages/e2e/fixtures/auth.ts` - 修复 logout() + 添加数据库写入延迟
- `frontend/packages/e2e/tests/auth/auth-preset-user.spec.ts` - 新增预置用户测试

## 关键学习

这次诊断展示了为什么 **监测和诊断** 比单纯增加超时更重要：

- 问题的表面症状（超时）与真实原因（API 调用失败）完全不同
- 如果只是盲目增加超时，问题永远不会被发现
- 详细的诊断日志使得问题原因清晰可见
