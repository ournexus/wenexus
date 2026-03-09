/**
 * @module e2e/tests/auth/auth-basic
 * @description 认证系统基础 E2E 测试 - 页面渲染和路由保护
 */
import { expect, test } from '@playwright/test';

import { AUTH_CONFIG, withLocale } from '../../fixtures';

const { timeout } = AUTH_CONFIG;

test.describe('路由保护', () => {
  const protectedRoutes = ['/admin', '/settings'];

  for (const route of protectedRoutes) {
    test(`未登录访问 ${route} 应重定向到登录页`, async ({ page }) => {
      await page.goto(withLocale(route));
      await page.waitForURL(/sign-in/, { timeout: timeout.short });

      expect(page.url()).toContain('sign-in');
      expect(page.url()).toContain('callbackUrl');
    });
  }
});

test.describe('页面渲染', () => {
  const authPages = [
    { path: '/sign-in', name: '登录页' },
    { path: '/sign-up', name: '注册页' },
  ];

  for (const { path, name } of authPages) {
    test(`${name}正确渲染`, async ({ page }) => {
      await page.goto(withLocale(path));
      await page.waitForLoadState('networkidle');

      const emailInput = page.locator('#email');
      await expect(emailInput).toBeVisible({ timeout: timeout.short });
    });
  }
});

test.describe('错误处理', () => {
  test('无效凭证不跳转', async ({ page }) => {
    await page.goto(withLocale('/sign-in'));
    await page.waitForLoadState('networkidle');

    const emailInput = page.locator('#email');
    await expect(emailInput).toBeVisible({ timeout: timeout.short });

    await emailInput.fill('wrong@example.com');
    await page.locator('#password').fill('wrongpassword');
    await page.locator('button[type="submit"]').click();

    await page.waitForLoadState('networkidle');
    expect(page.url()).toContain('sign-in');
  });
});
