/**
 * @module e2e/tests/auth/auth-flow
 * @description 完整认证流程 E2E 测试
 */
import { test } from '@playwright/test';

import { AuthPage, generateTestUser } from '../../fixtures';

test.describe('Complete Auth Flow', () => {
  test.setTimeout(60_000);

  test('注册 → 验证登录 → 登出 → 重新登录', async ({ page }) => {
    const auth = new AuthPage(page);
    const user = generateTestUser();

    // 1. 注册
    const result = await auth.register(user);
    if (result === 'verify') {
      test.skip();
      return;
    }

    // 2. 验证已登录
    await auth.expectLoggedIn();

    // 3. 登出
    await auth.logout();

    // 4. 验证已登出
    await auth.expectLoggedOut();

    // 5. 重新登录
    await auth.login(user.email, user.password);
    await auth.expectLoggedIn();
  });
});
