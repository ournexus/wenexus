# E2E 测试超时修复 (PR #26)

## 问题描述

E2E 测试在本地通过，但在 CI 环境中超时失败，错误信息：

```
TimeoutError: page.waitForURL: Timeout 20000ms exceeded
```

**根本原因分析**：

1. 初期认为只是超时时间不足（CI 环境资源较慢）
2. 后发现真正原因是登录后 **URL 没有变化**，而不仅仅是时间问题
3. 原因：未等待 API 调用完成就检查 URL 变化

## 解决方案

### 1. 增加 CI 特定的超时配置

在 `playwright.config.ts` 中添加 CI 环境的专用超时设置：

```typescript
use: {
  navigationTimeout: process.env.CI ? 30_000 : 15_000,  // 导航超时：CI 30s，本地 15s
  actionTimeout: process.env.CI ? 15_000 : 10_000,      // 操作超时：CI 15s，本地 10s
}
```

这样 CI 环境获得 50% 的额外时间用于导航操作，本地开发仍保持快速反馈。

### 2. 增加 AUTH_CONFIG 中的 waitForURL 超时

由于 `waitForURL` 调用使用的是 `AUTH_CONFIG.timeout.long` 而不是全局的 `navigationTimeout`，需要同时增加这个值：

```typescript
export const AUTH_CONFIG = {
  timeout: {
    short: 10_000,
    medium: 15_000,
    long: 30_000,  // 从 20_000 增加到 30_000
  },
  // ...
}
```

### 3. 改用 waitForResponse 等待 API 调用

关键修改：在 `login()` 和 `register()` 方法中，使用 `waitForResponse` 等待 API 调用完成，而不是仅依赖 `waitForLoadState`：

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
  throw new Error(`Login API failed: ${await apiResponse.text()}`);
}
```

**好处**：

- 确保 API 请求确实完成，而不是假设网络空闲就代表登录成功
- 能立即检测 API 失败（如 401 未授权、500 服务器错误等）

### 4. 添加诊断错误处理

为 API 失败和导航超时添加详细的诊断信息：

```typescript
try {
  const apiResponse = await apiResponsePromise;
  // ... 检查响应
} catch (error) {
  const currentUrl = this.page.url();
  const errorText = await this.page
    .locator('[role="alert"]')
    .textContent()
    .catch(() => 'No error element found');

  console.error('Login API Response Error:', {
    error: error.message,
    currentUrl,
    errorText,  // 服务器返回的错误信息
  });
  throw error;
}
```

当 CI 中测试失败时，将输出：

- 当前 URL（检查页面是否正确重定向）
- 服务器返回的错误信息（如表单验证失败、认证错误等）
- 完整的错误堆栈

## 测试验证

本地环境测试结果：✅ 全部通过

```
6 passed (1.2m)
- 路由保护 (2 tests)
- 页面渲染 (2 tests)
- 错误处理 (1 test)
- 完整认证流程 (1 test)
```

## 文件变更

- `frontend/packages/e2e/playwright.config.ts` - CI 环境超时配置
- `frontend/packages/e2e/fixtures/auth.ts` - 改用 waitForResponse + 诊断错误处理
