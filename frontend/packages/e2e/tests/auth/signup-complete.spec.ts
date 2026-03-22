/**
 * @module e2e/tests/auth/signup-complete
 * @description 完整注册流程 E2E 测试
 *
 * 测试场景：
 * 1. 访问注册页面
 * 2. 填写注册表单（邮箱 + 密码）
 * 3. 提交注册
 * 4. 验证注册成功（跳转到首页或仪表板）
 * 5. 验证用户已登录状态
 * 6. 登出
 * 7. 使用注册的账号重新登录
 */
import { expect, test } from '@playwright/test';

import { AuthPage } from '../../fixtures';

test.describe('完整注册流程', () => {
  test.setTimeout(60_000);

  test('注册新用户 → 验证登录 → 登出 → 重新登录', async ({ page }) => {
    const auth = new AuthPage(page);

    // 生成唯一测试邮箱（避免重复）
    const timestamp = Date.now();
    const testEmail = `test-${timestamp}@wenexus-e2e.test`;
    const testPassword = 'TestPassword123!';

    console.log(`Testing signup with email: ${testEmail}`);

    // 1. 访问注册页面
    console.log('Step 1: Navigate to signup page');
    await page.goto('/sign-up');
    await page.waitForLoadState('networkidle');

    // 2. 填写注册表单
    console.log('Step 2: Fill signup form');
    const emailInput = page.locator('#email');
    const passwordInput = page.locator('#password');
    const submitButton = page.locator('button[type="submit"]');

    await expect(emailInput).toBeVisible({ timeout: 10_000 });
    await emailInput.fill(testEmail);
    await passwordInput.fill(testPassword);

    // 3. 提交注册
    console.log('Step 3: Submit signup form');
    await submitButton.click();

    // 4. 等待页面跳转（注册成功后应跳转到首页或仪表板）
    console.log('Step 4: Wait for redirect after signup');
    await page.waitForURL((url) => !url.pathname.includes('sign-up'), {
      timeout: 15_000,
    });

    // 5. 验证已登录（检查是否有用户菜单或登出按钮）
    console.log('Step 5: Verify user is logged in');
    await auth.expectLoggedIn();

    // 6. 登出
    console.log('Step 6: Logout');
    await auth.logout();

    // 7. 验证已登出
    console.log('Step 7: Verify logout successful');
    await auth.expectLoggedOut();

    // 8. 使用刚注册的账号重新登录
    console.log('Step 8: Re-login with registered account');
    await auth.login(testEmail, testPassword);

    // 9. 验证重新登录成功
    console.log('Step 9: Verify re-login successful');
    await auth.expectLoggedIn();

    console.log('✅ Complete signup flow test passed');
  });

  test('注册页面表单验证', async ({ page }) => {
    console.log('Testing signup form validation');

    await page.goto('/sign-up');
    await page.waitForLoadState('networkidle');

    const emailInput = page.locator('#email');
    const passwordInput = page.locator('#password');
    const submitButton = page.locator('button[type="submit"]');

    await expect(emailInput).toBeVisible({ timeout: 10_000 });

    // 测试空表单提交
    console.log('Test 1: Empty form submission');
    await submitButton.click();
    await page.waitForTimeout(1000);
    expect(page.url()).toContain('sign-up'); // 应该停留在注册页

    // 测试无效邮箱
    console.log('Test 2: Invalid email format');
    await emailInput.fill('invalid-email');
    await passwordInput.fill('ValidPassword123!');
    await submitButton.click();
    await page.waitForTimeout(1000);
    expect(page.url()).toContain('sign-up');

    // 测试弱密码（如果有密码强度验证）
    console.log('Test 3: Weak password');
    await emailInput.fill('valid@email.com');
    await passwordInput.fill('123');
    await submitButton.click();
    await page.waitForTimeout(1000);
    expect(page.url()).toContain('sign-up');

    console.log('✅ Form validation test passed');
  });
});
