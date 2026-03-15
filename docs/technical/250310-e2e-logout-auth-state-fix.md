# E2E 测试修复：logout 认证状态清除问题

**日期**: 2026-03-10
**关联 PR**: #26
**修复类型**: Bug Fix

## 问题描述

E2E 测试 `auth-flow.spec.ts` 在测试登出后重新登录时超时失败：

```
TimeoutError: page.waitForURL: Timeout 20000ms exceeded.
```

问题出现在第二次登录（登出后重新登录）的表单提交阶段。表单提交后，页面应该从 `/sign-in` 重定向到主页，但超过 20 秒仍未发生重定向。

## 根本原因

`logout()` 方法存在两个关键问题：

### 1. **Fetch 异步操作未正确等待**

```typescript
// ❌ 问题代码
await this.page.evaluate(() =>
  fetch('/api/auth/sign-out', { method: 'POST' }),
);
```

虽然看起来在 `await` 中，但 `fetch` 返回的 Promise 没有显式返回，可能导致异步操作未完全等待。

### 2. **仅清除 cookies，忽视其他认证状态**

原始代码只清除了 cookies：

```typescript
await this.page.context().clearCookies();
```

但应用可能在 `localStorage` 或 `sessionStorage` 中存储认证令牌。登出时这些状态未清除，导致：

- 第二次登录时，页面仍然持有旧的认证状态
- 表单提交时出现状态冲突
- 服务器可能因为检测到已认证状态而拒绝重定向

## 解决方案

改进 `logout()` 方法的三个方面：

```typescript
async logout(): Promise<void> {
  // 1. 明确等待 Fetch 完成
  await this.page.evaluate(() =>
    fetch('/api/auth/sign-out', { method: 'POST' }).then(() => true),
  );

  // 2. 清除所有认证状态
  await this.page.context().clearCookies();
  await this.page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });

  // 3. 导航到 sign-in 页面确保页面状态清洁
  await this.page.goto(withLocale(AUTH_CONFIG.routes.signIn));
  await this.page.waitForLoadState('networkidle');
}
```

### 改进点

1. **Fetch 保证等待** - 添加 `.then(() => true)` 确保异步完成
2. **全面清除认证状态** - 不仅清除 cookies，还清除所有本地存储
3. **导航重置** - 显式导航到 sign-in 页面确保 DOM 和页面状态完全清洁
4. **网络稳定等待** - `waitForLoadState('networkidle')` 确保所有网络操作完成

## 验证

修复后测试通过：

```bash
# ✅ 测试通过
[1/1] Complete Auth Flow › 注册 → 验证登录 → 登出 → 重新登录
  1 passed (1.2m)
```

## 相关依赖

- 修复文件: `frontend/packages/e2e/fixtures/auth.ts`
- 测试文件: `frontend/packages/e2e/tests/auth/auth-flow.spec.ts`

## 学习点

在 E2E 测试中处理认证状态需要清除所有层级的存储：

- HTTP Cookies (认证会话)
- Local Storage (令牌存储)
- Session Storage (临时状态)
- Page State (DOM、JavaScript 上下文)

仅清除其中一个会导致状态不一致，影响后续操作的可靠性。
