import { toNextJsHandler } from 'better-auth/next-js';

import { getAuth } from '@/core/auth';
import { isCloudflareWorker } from '@/shared/lib/env';
import { enforceMinIntervalRateLimit } from '@/shared/lib/rate-limit';

function maybeRateLimitGetSession(request: Request): Response | null {
  const url = new URL(request.url);
  // better-auth session endpoint is served under this catch-all route.
  if (isCloudflareWorker() || !url.pathname.endsWith('/api/auth/get-session')) {
    return null;
  }

  const intervalMs =
    Number(process.env.AUTH_GET_SESSION_MIN_INTERVAL_MS) ||
    // default: 800ms (enough to stop request storms but still responsive)
    800;

  // Derive a rate-limit key from the request (IP or fallback to endpoint)
  const ip =
    request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ||
    request.headers.get('x-real-ip') ||
    'unknown';
  const key = `auth-get-session:${ip}`;
  const result = enforceMinIntervalRateLimit(key, intervalMs);

  if (!result.success) {
    return new Response(JSON.stringify({ error: 'Too many requests' }), {
      status: 429,
      headers: {
        'Content-Type': 'application/json',
        ...(result.retryAfter
          ? { 'Retry-After': String(Math.ceil(result.retryAfter / 1000)) }
          : {}),
      },
    });
  }

  return null;
}

export async function POST(request: Request) {
  const limited = maybeRateLimitGetSession(request);
  if (limited) {
    return limited;
  }

  const auth = await getAuth();
  const handler = toNextJsHandler(auth.handler);
  return handler.POST(request);
}

export async function GET(request: Request) {
  const limited = maybeRateLimitGetSession(request);
  if (limited) {
    return limited;
  }

  const auth = await getAuth();
  const handler = toNextJsHandler(auth.handler);
  return handler.GET(request);
}
