# E2E 测试超时修复 (PR #26)

## 问题描述

E2E 测试在本地通过，但在 CI 环境中超时失败，错误信息：

```
TimeoutError: page.waitForURL: Timeout 20000ms exceeded
```

**根本原因**：CI 环境资源受限导致响应较慢，20 秒超时不足以完成登录/注册流程。

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

### 3. 分阶段等待策略

改进 `auth.ts` 中的 `login()` 和 `register()` 方法，采用 4 阶段等待模式：

- **Stage 1**：导航并等待页面加载完成 (`waitForLoadState('networkidle')`)
- **Stage 2**：验证表单元素可见 (使用 `expect().toBeVisible()`)
- **Stage 3**：填写表单并提交
- **Stage 4**：等待导航完成

这种分段方式的好处：

- 提前检测问题（如表单加载失败）而非等到提交才超时
- 每个阶段使用适当的超时时间，避免单一超时过长
- 在 CI 中更容易定位问题位置

## 测试验证

本地环境测试结果：✅ 全部通过

```
6 passed (1.3m)
- 路由保护 (2 tests)
- 页面渲染 (2 tests)
- 错误处理 (1 test)
- 完整认证流程 (1 test)
```

## 文件变更

- `frontend/packages/e2e/playwright.config.ts` - CI 超时配置
- `frontend/packages/e2e/fixtures/auth.ts` - 分阶段等待策略
