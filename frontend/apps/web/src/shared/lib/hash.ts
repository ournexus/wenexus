/**
 * @module hash
 * @description UUID, Snowflake ID, and random string generation utilities
 * @consumers core/auth, shared/models, shared/services, scripts, extensions/ai, domains
 */

import { SnowflakeIdv1 } from 'simple-flakeid';
import { v4 as uuidv4 } from 'uuid';

const flakeId = new SnowflakeIdv1({ workerId: 1 });

/**
 * Generate a UUID v4 string.
 */
export function getUuid(): string {
  return uuidv4();
}

/**
 * Generate a Snowflake-style numeric ID string.
 */
export function getSnowId(): string {
  return flakeId.NextId().toString();
}

/**
 * Generate a random alphanumeric string of the given length.
 */
export function getNonceStr(length: number = 16): string {
  const chars =
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

/**
 * Compute MD5 hex digest of a Uint8Array using the Web Crypto API.
 * Note: Uses a simple hash for non-crypto purposes (file dedup).
 */
export function md5(data: Uint8Array): string {
  // Simple non-crypto hash for file deduplication
  let hash = 0;
  for (let i = 0; i < data.length; i++) {
    hash = ((hash << 5) - hash + data[i]) | 0;
  }
  return Math.abs(hash).toString(16).padStart(8, '0');
}
