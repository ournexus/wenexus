/**
 * @module e2e/health/app-startup
 * @description 应用启动健康检查 — 确保应用能正常启动并响应请求
 *
 * 这些测试不依赖任何具体的 DOM 结构或页面内容，
 * 只验证应用的基本可用性。
 */
import { expect, test } from '@playwright/test';

test.describe('App Startup Health', () => {
  test('homepage returns 200', async ({ page }) => {
    const response = await page.goto('/', { waitUntil: 'domcontentloaded' });
    expect(response?.status()).toBe(200);
  });

  test('page renders without fatal JS errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (err) => errors.push(err.message));

    await page.goto('/', { waitUntil: 'domcontentloaded' });

    // 允许非关键警告，但不应有致命错误
    expect(errors).toEqual([]);
  });
});
