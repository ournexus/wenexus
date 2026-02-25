/**
 * Cookie utilities for client and server contexts.
 */

export function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
  return match ? decodeURIComponent(match[2]) : null;
}

export function setCookie(
  name: string,
  value: string,
  options: { days?: number; path?: string } = {}
): void {
  if (typeof document === 'undefined') return;
  const { days = 365, path = '/' } = options;
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${encodeURIComponent(value)};expires=${expires};path=${path}`;
}

export function getCookieFromCtx(ctx: {
  headers?: { cookie?: string };
}): (name: string) => string | null {
  const cookieHeader = ctx?.headers?.cookie ?? '';
  return (name: string) => {
    const match = cookieHeader.match(new RegExp(`(^| )${name}=([^;]+)`));
    return match ? decodeURIComponent(match[2]) : null;
  };
}

export function getHeaderValue(
  headers: Headers | Record<string, string | string[] | undefined>,
  key: string
): string | null {
  if (headers instanceof Headers) {
    return headers.get(key);
  }
  const val = headers[key];
  return typeof val === 'string' ? val : (val?.[0] ?? null);
}

export function guessLocaleFromAcceptLanguage(header: string): string {
  if (!header) return 'en';
  const first = header.split(',')[0]?.trim();
  const lang = first?.split(';')[0]?.split('-')[0]?.toLowerCase();
  return lang || 'en';
}
