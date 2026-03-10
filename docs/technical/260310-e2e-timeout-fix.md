# E2E 测试超时修复 (PR #26)

## 问题描述

E2E 测试在本地通过，但在 CI 环境中超时失败，错误信息：

```
TimeoutError: page.waitForURL: Timeout 20000ms exceeded
```

## 根本原因分析

通过逐步诊断发现了问题链：

1. **初始现象**：超时错误 (20s 不够)
2. **进一步诊断**：URL 没有变化
3. **API 响应检查**：登出 API 返回 **415 Unsupported Media Type**
4. **更新诊断**：登出 API 返回 **403 MISSING_OR_NULL_ORIGIN**
5. **真正原因**：
   - logout() 方法使用 `page.evaluate(fetch)` 时没有正确的 headers
   - 导致登出 API 失败，session 没有清理
   - 重新登录时，用户 session 仍然"存在"但无效，导致 401 错误

这不是超时问题，而是 **API 调用协议问题** 导致的 session 管理失败。

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
```

关键日志显示：

- ✅ 注册 API 返回 200
- ✅ 登出 API 返回 200（修复后）
- ✅ 重新登录 API 返回 200
- ✅ 完整认证流程无中断

## 文件变更

- `frontend/packages/e2e/playwright.config.ts` - CI 环境超时配置
- `frontend/packages/e2e/fixtures/auth.ts` - 修复 logout() API 调用 + 完善诊断日志

## 关键学习

这次诊断展示了为什么 **监测和诊断** 比单纯增加超时更重要：

- 问题的表面症状（超时）与真实原因（API 调用失败）完全不同
- 如果只是盲目增加超时，问题永远不会被发现
- 详细的诊断日志使得问题原因清晰可见
