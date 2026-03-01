/**
 * @module e2e/health/page-routes
 * @description 页面路由健康检查 — 确保关键页面可访问、不白屏
 *
 * 使用 request context (HTTP) 检查页面状态码，避免浏览器渲染超时。
 * 使用 page.goto 检查首页实际渲染。
 * next-intl 配置 localePrefix='as-needed'，默认 locale(en) 不带前缀。
 */
import { expect, test } from '@playwright/test';

test.describe('Page Routes Health', () => {
  test.setTimeout(60_000);

  // 首页：应返回 200 且有内容（浏览器渲染）
  test('homepage returns 200 and renders', async ({ page }) => {
    const response = await page.goto('/', { waitUntil: 'domcontentloaded' });
    expect(response?.status()).toBe(200);

    const bodyText = await page.evaluate(() => document.body.innerText);
    expect(bodyText.trim().length).toBeGreaterThan(0);
  });

  test('/en returns 200', async ({ page }) => {
    const response = await page.goto('/en', {
      waitUntil: 'domcontentloaded',
    });
    expect(response?.status()).toBe(200);
  });

  // 关键页面路由：使用 HTTP request context 检查（不走浏览器渲染）
  // 只验证路由可达 + 不返回 500，不验证渲染
  const keyPages = ['/sign-in', '/sign-up', '/pricing', '/topic/create'];

  for (const path of keyPages) {
    test(`${path} responds without 500`, async ({ request }) => {
      const response = await request.get(path, {
        maxRedirects: 5,
        timeout: 30_000,
      });
      const status = response.status();
      expect(status, `${path} should not return 500`).not.toBe(500);
    });
  }
});
