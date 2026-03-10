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
    long: 30_000,
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
    // Stage 1: Navigate and wait for page to be interactive
    await this.page.goto(withLocale(AUTH_CONFIG.routes.signUp));
    await this.page.waitForLoadState('networkidle');

    // Stage 2: Wait for form fields to be visible and ready
    const nameInput = this.page.locator('#name');
    await expect(nameInput).toBeVisible({ timeout: AUTH_CONFIG.timeout.short });
    await expect(this.page.locator('#email')).toBeVisible({
      timeout: AUTH_CONFIG.timeout.short,
    });
    await expect(this.page.locator('#password')).toBeVisible({
      timeout: AUTH_CONFIG.timeout.short,
    });

    // Stage 3: Fill form and submit
    await nameInput.fill(user.name);
    await this.page.locator('#email').fill(user.email);
    await this.page.locator('#password').fill(user.password);

    // Stage 4: Wait for registration API response before checking URL
    const submitButton = this.page.locator('button[type="submit"]');
    const apiResponsePromise = this.page.waitForResponse(
      (response) =>
        response.url().includes('/api/auth/sign-up') ||
        response.url().includes('/api/auth/register'),
      { timeout: AUTH_CONFIG.timeout.long },
    );

    await submitButton.click();

    try {
      const apiResponse = await apiResponsePromise;
      const responseStatus = apiResponse.status();

      if (responseStatus !== 200 && responseStatus !== 201) {
        const responseBody = await apiResponse.text();
        throw new Error(
          `Registration API failed with status ${responseStatus}: ${responseBody}`,
        );
      }
    } catch (error) {
      // Capture diagnostic information on API failure
      const currentUrl = this.page.url();
      const errorElement = this.page.locator('[role="alert"]');
      const errorText = await errorElement
        .textContent()
        .catch(() => 'No error element found');

      console.error('Registration API Response Error:', {
        error: error instanceof Error ? error.message : String(error),
        currentUrl,
        errorText,
      });
      throw error;
    }

    // Stage 5: Wait for navigation to complete (home or verify page)
    try {
      await this.page.waitForURL(
        (url) => isHomePage(url.pathname) || url.pathname.includes('/verify'),
        { timeout: AUTH_CONFIG.timeout.long },
      );
    } catch (error) {
      // Capture diagnostic information on navigation failure
      const currentUrl = this.page.url();
      const errorElement = this.page.locator('[role="alert"]');
      const errorText = await errorElement
        .textContent()
        .catch(() => 'No error element found');

      console.error('Registration Navigation Failed:', {
        error: error instanceof Error ? error.message : String(error),
        currentUrl,
        errorText,
      });
      throw error;
    }

    return this.page.url().includes('/verify') ? 'verify' : 'success';
  }

  async login(email: string, password: string): Promise<void> {
    // Stage 1: Navigate and wait for page to be interactive
    await this.page.goto(withLocale(AUTH_CONFIG.routes.signIn));
    await this.page.waitForLoadState('networkidle');

    // Stage 2: Wait for form fields to be visible and ready
    await expect(this.page.locator('#email')).toBeVisible({
      timeout: AUTH_CONFIG.timeout.short,
    });
    await expect(this.page.locator('#password')).toBeVisible({
      timeout: AUTH_CONFIG.timeout.short,
    });

    // Stage 3: Fill form and submit
    await this.page.locator('#email').fill(email);
    await this.page.locator('#password').fill(password);

    // Stage 4: Wait for login API response before checking URL
    const submitButton = this.page.locator('button[type="submit"]');
    const apiResponsePromise = this.page.waitForResponse(
      (response) =>
        response.url().includes('/api/auth/sign-in') ||
        response.url().includes('/api/auth/login'),
      { timeout: AUTH_CONFIG.timeout.long },
    );

    await submitButton.click();

    try {
      const apiResponse = await apiResponsePromise;
      const responseStatus = apiResponse.status();

      if (responseStatus !== 200 && responseStatus !== 201) {
        const responseBody = await apiResponse.text();
        throw new Error(
          `Login API failed with status ${responseStatus}: ${responseBody}`,
        );
      }
    } catch (error) {
      // Capture diagnostic information on API failure
      const currentUrl = this.page.url();
      const errorElement = this.page.locator('[role="alert"]');
      const errorText = await errorElement
        .textContent()
        .catch(() => 'No error element found');

      console.error('Login API Response Error:', {
        error: error instanceof Error ? error.message : String(error),
        currentUrl,
        errorText,
      });
      throw error;
    }

    // Stage 5: Wait for navigation away from sign-in page
    try {
      await this.page.waitForURL((url) => !url.pathname.includes('/sign-in'), {
        timeout: AUTH_CONFIG.timeout.long,
      });
    } catch (error) {
      // Capture diagnostic information on navigation failure
      const currentUrl = this.page.url();
      const pageContent = await this.page
        .content()
        .catch(() => 'Unable to read page');
      const errorElement = this.page.locator('[role="alert"]');
      const errorText = await errorElement
        .textContent()
        .catch(() => 'No error element found');

      console.error('Login Navigation Failed:', {
        error: error instanceof Error ? error.message : String(error),
        currentUrl,
        errorText,
        pageContentLength: pageContent?.length || 0,
      });
      throw error;
    }
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
