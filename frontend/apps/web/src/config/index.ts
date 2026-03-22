/**
 * @module config
 * @description Application configuration loaded from environment variables
 * @consumers core/*, shared/*, domains/*, app/*
 */
import packageJson from '../../package.json';

// Note: Environment variables are loaded via dotenv-cli in package.json scripts.
// Next.js automatically loads .env files in the runtime, so no manual loading is needed here.

export type ConfigMap = Record<string, string>;

// Mapping from config key → [env var name, fallback value].
// In Cloudflare Workers, secrets (DATABASE_URL, AUTH_SECRET, etc.) are only
// populated into process.env inside the request context (via populateProcessEnv).
// A static object would capture empty strings at module-init time.
// The Proxy below defers reads to the actual process.env on every access.
const ENV_KEY_MAP: Record<string, [env: string, fallback: string]> = {
  app_url: ['NEXT_PUBLIC_APP_URL', 'http://localhost:3000'],
  app_name: ['NEXT_PUBLIC_APP_NAME', 'ShipAny App'],
  app_description: ['NEXT_PUBLIC_APP_DESCRIPTION', ''],
  app_logo: ['NEXT_PUBLIC_APP_LOGO', '/logo.png'],
  app_favicon: ['NEXT_PUBLIC_APP_FAVICON', '/favicon.ico'],
  app_preview_image: ['NEXT_PUBLIC_APP_PREVIEW_IMAGE', '/preview.png'],
  theme: ['NEXT_PUBLIC_THEME', 'default'],
  appearance: ['NEXT_PUBLIC_APPEARANCE', 'system'],
  locale: ['NEXT_PUBLIC_DEFAULT_LOCALE', 'en'],
  database_url: ['DATABASE_URL', ''],
  database_auth_token: ['DATABASE_AUTH_TOKEN', ''],
  database_provider: ['DATABASE_PROVIDER', 'postgresql'],
  db_schema_file: ['DB_SCHEMA_FILE', './src/config/db/schema.ts'],
  // PostgreSQL schema name (e.g. 'web'). Default: 'public'
  db_schema: ['DB_SCHEMA', 'public'],
  // Drizzle migrations journal table name (avoid conflicts across projects)
  db_migrations_table: ['DB_MIGRATIONS_TABLE', '__drizzle_migrations'],
  // Drizzle migrations journal schema (default in drizzle-kit is 'drizzle')
  // We keep 'public' as template default for stability on fresh Supabase DBs.
  db_migrations_schema: ['DB_MIGRATIONS_SCHEMA', 'drizzle'],
  // Output folder for drizzle-kit generated migrations
  db_migrations_out: ['DB_MIGRATIONS_OUT', './src/config/db/migrations'],
  db_singleton_enabled: ['DB_SINGLETON_ENABLED', 'false'],
  db_max_connections: ['DB_MAX_CONNECTIONS', '1'],
  auth_secret: ['AUTH_SECRET', ''], // openssl rand -base64 32
  python_backend_url: ['PYTHON_BACKEND_URL', 'http://localhost:8000'],
  locale_detect_enabled: ['NEXT_PUBLIC_LOCALE_DETECT_ENABLED', 'false'],
};

// Special keys that need multi-env or static resolution.
const SPECIAL_KEYS: Record<string, () => string> = {
  auth_url: () => process.env.AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || '',
  version: () => packageJson.version,
};

export const envConfigs: ConfigMap = new Proxy({} as ConfigMap, {
  get(_, key: string) {
    if (key in SPECIAL_KEYS) return SPECIAL_KEYS[key]();
    const mapping = ENV_KEY_MAP[key];
    if (mapping) return process.env[mapping[0]] || mapping[1];
    return '';
  },
  ownKeys() {
    return [...Object.keys(ENV_KEY_MAP), ...Object.keys(SPECIAL_KEYS)];
  },
  getOwnPropertyDescriptor(_, key: string) {
    if (key in ENV_KEY_MAP || key in SPECIAL_KEYS) {
      return { configurable: true, enumerable: true, writable: false };
    }
    return undefined;
  },
  has(_, key: string) {
    return key in ENV_KEY_MAP || key in SPECIAL_KEYS;
  },
});
