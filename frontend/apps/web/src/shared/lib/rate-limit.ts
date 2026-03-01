/**
 * Rate limiting utilities.
 */

const lastRequestMap = new Map<string, number>();

export function enforceMinIntervalRateLimit(
  key: string,
  intervalMs: number = 1000
): { success: boolean; retryAfter?: number } {
  const now = Date.now();
  const last = lastRequestMap.get(key);

  if (last && now - last < intervalMs) {
    return { success: false, retryAfter: intervalMs - (now - last) };
  }

  lastRequestMap.set(key, now);
  return { success: true };
}
