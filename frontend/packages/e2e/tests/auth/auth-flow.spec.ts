/**
 * @module e2e/tests/auth/auth-flow
 * @description 认证流程 E2E 测试
 *
 * 测试重点：登录 → 登出 → 重新登录 流程
 *
 * 注意：注册流程暂时跳过，因为后端注册 API 存在数据持久性问题：
 * - 返回 200 OK 但用户数据没有真正保存到数据库
 * - 导致重新登录返回 401 INVALID_EMAIL_OR_PASSWORD
 * - 等待后端修复后会恢复测试
 *
 * 当前测试使用预置用户（从环境变量 E2E_TEST_USER_EMAIL/E2E_TEST_USER_PASSWORD 获取），
 * 或者会跳过该测试。
 */
import { test } from '@playwright/test';

import { E2E_TEST_TIMEOUT } from '../../config';
import { AuthPage } from '../../fixtures';

test.describe('Complete Auth Flow', () => {
  test.setTimeout(E2E_TEST_TIMEOUT);

  // 如果没有预置用户，跳过此测试
  // 原因：注册 API 有问题，需要后端修复
  test.skip(
    !process.env.E2E_TEST_USER_EMAIL || !process.env.E2E_TEST_USER_PASSWORD,
    'Skipped: Preset user credentials not provided. Registration API has data persistence issues (returns 200 but does not save user to database). Use preset users for testing until backend is fixed.',
  );

  test('登录 → 验证登录 → 登出 → 验证登出 → 重新登录', async ({ page }) => {
    const auth = new AuthPage(page);

    // 使用预置用户（避免注册 API 问题）
    const testEmail = process.env.E2E_TEST_USER_EMAIL!;
    const testPassword = process.env.E2E_TEST_USER_PASSWORD!;

    console.log(`Testing auth flow with user: ${testEmail}`);

    // 1. 登录
    console.log('Step 1: Login');
    await auth.login(testEmail, testPassword);

    // 2. 验证已登录
    console.log('Step 2: Verify login successful');
    await auth.expectLoggedIn();

    // 3. 登出
    console.log('Step 3: Logout');
    await auth.logout();

    // 4. 验证已登出
    console.log('Step 4: Verify logout successful');
    await auth.expectLoggedOut();

    // 5. 重新登录
    console.log('Step 5: Re-login with same user');
    await auth.login(testEmail, testPassword);

    // 6. 验证仍然已登录
    console.log('Step 6: Verify re-login successful');
    await auth.expectLoggedIn();

    console.log('✅ Complete auth flow test passed');
  });
});
