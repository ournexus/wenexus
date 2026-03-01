/**
 * @module e2e/health/api-routes
 * @description API 路由健康检查 — 确保关键 API 端点可达且不崩溃
 *
 * 使用 HTTP request context（不经过浏览器页面），直接检查 API 状态码。
 */
import { expect, test } from '@playwright/test';

test.describe('API Routes Health', () => {
  // dev 模式下首次请求需要编译路由，超时设长一些
  test.setTimeout(60_000);

  test('GET /api/config/get-configs does not return 500', async ({
    request,
  }) => {
    const response = await request.get('/api/config/get-configs');
    expect(response.status()).not.toBe(500);
  });

  test('auth session endpoint is reachable', async ({ request }) => {
    const response = await request.get('/api/auth/get-session');
    expect(response.status()).not.toBe(404);
  });

  // 将每个域路由拆分为独立测试，避免串行编译导致单测超时
  const domainRoutes = [
    '/api/domains/discovery/feed',
    '/api/domains/discovery/topics',
    '/api/domains/roundtable/sessions',
    '/api/domains/identity/preferences',
  ];

  for (const path of domainRoutes) {
    test(`${path} is registered (not 404)`, async ({ request }) => {
      const response = await request.get(path);
      expect(
        response.status(),
        `${path} should be registered (not 404)`
      ).not.toBe(404);
    });
  }
});
