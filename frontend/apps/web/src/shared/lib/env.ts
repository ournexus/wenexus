/**
 * Environment detection utilities.
 */

export function isCloudflareWorker(): boolean {
  try {
    return (
      typeof (globalThis as any).caches !== 'undefined' &&
      typeof (globalThis as any).caches.default !== 'undefined'
    );
  } catch {
    return false;
  }
}
