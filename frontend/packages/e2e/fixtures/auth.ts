/**
 * @module e2e/fixtures/auth
 * @description 认证测试的 Page Object 和辅助工具
 */
import { expect, Page } from '@playwright/test';

// ========== 常量 ==========
export const AUTH_CONFIG = {
  locale: 'en',
  timeout: {
    short: 10_000,
    medium: 15_000,
    long: 20_000,
  },
  routes: {
    signIn: '/sign-in',
    signUp: '/sign-up',
    settings: '/settings',
  },
} as const;

// ========== 类型 ==========
export interface TestUser {
  name: string;
  email: string;
  password: string;
}

// ========== 工具函数 ==========
export const generateTestUser = (): TestUser => ({
  name: `Test User ${Date.now()}`,
  email: `test-${Date.now()}@example.com`,
  password: 'Test123!@#',
});

export const withLocale = (path: string) => `/${AUTH_CONFIG.locale}${path}`;

const isHomePage = (pathname: string): boolean =>
  pathname === '/' ||
  pathname === `/${AUTH_CONFIG.locale}` ||
  pathname === `/${AUTH_CONFIG.locale}/`;

// ========== Page Object ==========
export class AuthPage {
  constructor(private page: Page) {}

  async register(user: TestUser): Promise<'success' | 'verify'> {
    await this.page.goto(withLocale(AUTH_CONFIG.routes.signUp));
    await this.page.waitForLoadState('networkidle');

    const nameInput = this.page.locator('#name');
    await expect(nameInput).toBeVisible({ timeout: AUTH_CONFIG.timeout.short });

    await nameInput.fill(user.name);
    await this.page.locator('#email').fill(user.email);
    await this.page.locator('#password').fill(user.password);
    await this.page.locator('button[type="submit"]').click();

    await this.page.waitForURL(
      (url) => isHomePage(url.pathname) || url.pathname.includes('/verify'),
      { timeout: AUTH_CONFIG.timeout.long },
    );

    return this.page.url().includes('/verify') ? 'verify' : 'success';
  }

  async login(email: string, password: string): Promise<void> {
    await this.page.goto(withLocale(AUTH_CONFIG.routes.signIn));
    await this.page.waitForLoadState('networkidle');

    await this.page.locator('#email').fill(email);
    await this.page.locator('#password').fill(password);
    await this.page.locator('button[type="submit"]').click();

    await this.page.waitForURL((url) => !url.pathname.includes('/sign-in'), {
      timeout: AUTH_CONFIG.timeout.long,
    });
  }

  async logout(): Promise<void> {
    // Call sign-out API and wait for it to complete
    await this.page.evaluate(() =>
      fetch('/api/auth/sign-out', { method: 'POST' }).then(() => true),
    );

    // Clear all auth state
    await this.page.context().clearCookies();
    await this.page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });

    // Navigate to home to ensure we're in a clean state
    await this.page.goto(withLocale(AUTH_CONFIG.routes.signIn));
    await this.page.waitForLoadState('networkidle');
  }

  async isLoggedIn(): Promise<boolean> {
    await this.page.goto(withLocale(AUTH_CONFIG.routes.settings));
    await this.page.waitForLoadState('networkidle');
    return this.page.url().includes('/settings');
  }

  async expectLoggedIn(): Promise<void> {
    expect(await this.isLoggedIn()).toBe(true);
  }

  async expectLoggedOut(): Promise<void> {
    await this.page.goto(withLocale(AUTH_CONFIG.routes.settings));
    await this.page.waitForURL(/sign-in/, {
      timeout: AUTH_CONFIG.timeout.short,
    });
    expect(this.page.url()).toContain('sign-in');
  }
}
