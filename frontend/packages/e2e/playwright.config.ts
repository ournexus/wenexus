import { config } from 'dotenv';
import path from 'path';
import { defineConfig, devices } from '@playwright/test';

config({ path: path.resolve(__dirname, '../../apps/web/.env.development') });

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {
    baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    navigationTimeout: process.env.CI ? 30_000 : 15_000,
    actionTimeout: process.env.CI ? 15_000 : 10_000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // 禁用 webServer：在开发环境中手动启动服务
  // 运行前需要：
  // 1. pnpm dev --filter @wenexus/web (或在 frontend 目录运行 pnpm dev)
  // 2. Python 后端也需要启动
  // webServer: { ... }
});
