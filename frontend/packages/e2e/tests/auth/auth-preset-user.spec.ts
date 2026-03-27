/**
 * @module e2e/tests/auth/auth-preset-user
 * @description 使用预置用户的认证流程测试
 *
 * 这个测试使用预先在数据库中创建的用户，而不是通过注册创建新用户。
 * 这避免了注册流程中的数据库写入延迟问题。
 *
 * 前置条件：需要在测试环境中预先创建一个测试用户
 * 用户凭证通过环境变量提供：
 * - E2E_TEST_USER_EMAIL: 测试用户邮箱
 * - E2E_TEST_USER_PASSWORD: 测试用户密码
 *
 * 如果没有提供这些环境变量，测试会被跳过。
 */
import { test } from '@playwright/test';

import { AuthPage } from '../../fixtures';

test.describe('Auth Flow with Preset User', () => {
  test.setTimeout(120_000);

  // Skip this test if preset user credentials are not provided
  test.skip(
    !process.env.E2E_TEST_USER_EMAIL || !process.env.E2E_TEST_USER_PASSWORD,
    'Skipped: Preset user credentials not provided (E2E_TEST_USER_EMAIL, E2E_TEST_USER_PASSWORD)',
  );

  test('使用预置用户的认证流程：登录 → 验证登录 → 登出 → 验证登出 → 重新登录', async ({
    page,
  }) => {
    const auth = new AuthPage(page);

    // 从环境变量获取预置用户凭证
    const testEmail = process.env.E2E_TEST_USER_EMAIL!;
    const testPassword = process.env.E2E_TEST_USER_PASSWORD!;

    console.log(`Using preset user: ${testEmail}`);

    // 1. 登录预置用户
    await auth.login(testEmail, testPassword);
    console.log('Preset user login successful');

    // 2. 验证已登录
    await auth.expectLoggedIn();
    console.log('Login verification passed');

    // 3. 登出
    await auth.logout();
    console.log('Logout successful');

    // 4. 验证已登出
    await auth.expectLoggedOut();
    console.log('Logout verification passed');

    // 5. 重新登录
    await auth.login(testEmail, testPassword);
    console.log('Re-login successful');

    // 6. 验证仍然已登录
    await auth.expectLoggedIn();
    console.log('Re-login verification passed');
  });
});
