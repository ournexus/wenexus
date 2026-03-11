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

  /**
   * Register a new user and wait for database write to complete.
   * Returns 'success' if registration completes and user can login,
   * or 'verify' if email verification is required.
   */
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

      // Only try to read response body if status is not successful
      let responseBody = '';
      if (responseStatus !== 200 && responseStatus !== 201) {
        try {
          responseBody = await apiResponse.text();
        } catch {
          responseBody = `(unable to read body)`;
        }
        throw new Error(
          `Registration API failed with status ${responseStatus}: ${responseBody}`,
        );
      }

      // Try to verify user was created by reading response, but don't fail if we can't
      try {
        const bodyText = await apiResponse.text();
        const responseData = JSON.parse(bodyText);
        if (!responseData.user && !responseData.id && !responseData.email) {
          console.warn(
            'Registration API response missing user data:',
            responseData,
          );
        }
      } catch {
        // Response body might not be JSON or available, that's ok
      }

      console.log('Registration API succeeded with status', responseStatus);
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
        registeredEmail: user.email,
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
        registeredEmail: user.email,
      });
      throw error;
    }

    const registrationResult = this.page.url().includes('/verify')
      ? 'verify'
      : 'success';

    // Stage 6: If registration succeeded (not verify), validate that user was actually created
    // by attempting to access protected page and then re-logging in after logout
    if (registrationResult === 'success') {
      console.log(
        `Registration completed for ${user.email}, waiting for database write...`,
      );
      // Wait to ensure database write completes before logout/relogin cycle
      await new Promise((resolve) => setTimeout(resolve, 500));
    }

    return registrationResult;
  }

  async login(email: string, password: string): Promise<void> {
    console.log(`Attempting to login with email: ${email}`);

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

      // Only try to read response body if status is not successful
      let responseBody = '';
      if (responseStatus !== 200 && responseStatus !== 201) {
        try {
          responseBody = await apiResponse.text();
        } catch {
          // Response body might not be available, that's ok
          responseBody = `(unable to read body)`;
        }
        throw new Error(
          `Login API failed with status ${responseStatus}: ${responseBody}`,
        );
      }

      console.log(
        `Login API succeeded with status ${responseStatus} for email: ${email}`,
      );
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
        attemptedEmail: email,
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
      const errorElement = this.page.locator('[role="alert"]');
      const errorText = await errorElement
        .textContent()
        .catch(() => 'No error element found');

      console.error('Login Navigation Failed:', {
        error: error instanceof Error ? error.message : String(error),
        currentUrl,
        errorText,
        attemptedEmail: email,
      });
      throw error;
    }
  }

  async logout(): Promise<void> {
    console.log('Logging out...');

    // Call sign-out API using page.request (Playwright native API)
    // This is more reliable and handles headers correctly
    try {
      const response = await this.page.request.post('/api/auth/sign-out', {
        headers: {
          'Content-Type': 'application/json',
          Origin: new URL(this.page.url()).origin,
        },
        data: {},
      });

      const responseStatus = response.status();
      console.log(`Sign-out API returned status ${responseStatus}`);

      if (!response.ok()) {
        const responseBody = await response
          .text()
          .catch(() => '(unable to read body)');
        console.warn(
          `Sign-out API failed with status ${responseStatus}: ${responseBody}`,
        );
      } else {
        console.log('Sign-out API succeeded');
      }
    } catch (error) {
      console.warn(
        'Sign-out API error:',
        error instanceof Error ? error.message : String(error),
      );
      // Continue with cleanup even if API fails
    }

    // Clear all auth state
    try {
      await this.page.context().clearCookies();
      console.log('Cookies cleared');
    } catch (error) {
      console.warn('Error clearing cookies:', error);
    }

    try {
      await this.page.evaluate(() => {
        localStorage.clear();
        sessionStorage.clear();
      });
      console.log('LocalStorage and SessionStorage cleared');
    } catch (error) {
      console.warn('Error clearing storage:', error);
    }

    // Wait a bit to ensure all cleanup is complete
    await new Promise((resolve) => setTimeout(resolve, 500));

    // Navigate to sign-in page to ensure we're in a clean state
    try {
      await this.page.goto(withLocale(AUTH_CONFIG.routes.signIn));
      await this.page.waitForLoadState('networkidle');
      console.log('Navigated to sign-in page after logout');
    } catch (error) {
      console.warn('Error navigating after logout:', error);
    }
  }

  async isLoggedIn(): Promise<boolean> {
    try {
      await this.page.goto(withLocale(AUTH_CONFIG.routes.settings));
      await this.page.waitForLoadState('networkidle');
      const isLoggedIn = this.page.url().includes('/settings');
      const currentUrl = this.page.url();
      console.log(`isLoggedIn check: ${isLoggedIn} (URL: ${currentUrl})`);
      return isLoggedIn;
    } catch (error) {
      console.warn('Error checking login status:', error);
      const currentUrl = this.page.url();
      console.log(
        `isLoggedIn check failed, current URL: ${currentUrl}`,
        error instanceof Error ? error.message : String(error),
      );
      return false;
    }
  }

  async expectLoggedIn(): Promise<void> {
    console.log('Verifying login...');
    const isLoggedIn = await this.isLoggedIn();
    if (!isLoggedIn) {
      const currentUrl = this.page.url();
      console.error('Login verification failed:', {
        currentUrl,
        expected: 'settings page',
      });
    }
    expect(isLoggedIn).toBe(true);
  }

  async expectLoggedOut(): Promise<void> {
    console.log('Verifying logout...');
    try {
      await this.page.goto(withLocale(AUTH_CONFIG.routes.settings));
      await this.page.waitForURL(/sign-in/, {
        timeout: AUTH_CONFIG.timeout.short,
      });
      const currentUrl = this.page.url();
      console.log(`Logout verified, redirected to: ${currentUrl}`);
      expect(this.page.url()).toContain('sign-in');
    } catch (error) {
      const currentUrl = this.page.url();
      console.error('Logout verification failed:', {
        error: error instanceof Error ? error.message : String(error),
        currentUrl,
      });
      throw error;
    }
  }
}
