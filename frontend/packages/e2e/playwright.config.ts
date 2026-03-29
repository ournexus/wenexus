import { config } from 'dotenv';
import path from 'path';

import { defineConfig, devices } from '@playwright/test';

config({
  path:
    process.env.DOTENV_PATH ||
    path.resolve(__dirname, '../../apps/web/.env.development'),
});

const isCI = !!process.env.CI;
const baseURL = process.env.E2E_BASE_URL ?? 'http://localhost:3000';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: isCI,
  retries: isCI ? 2 : 0,
  workers: isCI ? 1 : undefined,
  reporter: 'html',

  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    navigationTimeout: isCI ? 30_000 : 15_000,
    actionTimeout: isCI ? 15_000 : 10_000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // CI: 自动启动 Next.js dev server
  // 本地: 手动启动 (pnpm dev --filter @wenexus/web)
  ...(isCI
    ? {
        webServer: {
          command: 'pnpm dev',
          cwd: path.resolve(__dirname, '../../apps/web'),
          url: baseURL,
          reuseExistingServer: false,
          timeout: 120_000,
        },
      }
    : {}),
});
