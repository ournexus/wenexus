/**
 * Database Initialization Script for E2E Testing
 *
 * Pushes Drizzle schema to the database, ensuring all tables exist
 * before running E2E tests.
 *
 * Usage:
 *   DATABASE_URL=... tsx scripts/init-db-e2e.ts
 */

import { execSync } from 'child_process';
import { sql } from 'drizzle-orm';

import { db } from '@/core/db';
import { envConfigs } from '@/config';

async function initializeDatabase() {
  const dbUrl = envConfigs.database_url;
  if (!dbUrl) {
    console.error('❌ DATABASE_URL is not set');
    process.exit(1);
  }

  console.log('🚀 Initializing database for E2E tests...');
  console.log(`📊 Database Provider: ${envConfigs.database_provider}`);
  console.log(`🗂️  Database URL: ${dbUrl.substring(0, 50)}...`);

  // 1. Push Drizzle schema (creates/updates tables)
  console.log('\n1️⃣  Pushing Drizzle schema to database...');
  try {
    execSync('npx drizzle-kit push --config=src/core/db/config.ts --force', {
      stdio: 'inherit',
      cwd: process.cwd(),
      env: { ...process.env },
    });
    console.log('✅ Schema push completed');
  } catch {
    console.error('❌ Schema push failed');
    process.exit(1);
  }

  // 2. Verify database connection and tables
  console.log('\n2️⃣  Verifying database tables...');
  const dbInstance = db();

  try {
    await dbInstance.execute(sql`SELECT 1`);
    console.log('✅ Database connection successful');

    const tables = await dbInstance.execute(sql`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
      ORDER BY table_name
    `);

    console.log(`✅ Found ${tables.length} tables:`);
    tables.forEach((row: any) => {
      console.log(`   - ${row.table_name}`);
    });

    // Verify auth tables exist
    const existingNames = tables.map((t: any) => t.table_name);
    const requiredAuth = ['user', 'session', 'account'];
    const missing = requiredAuth.filter((t) => !existingNames.includes(t));

    if (missing.length > 0) {
      console.warn(`⚠️  Missing auth tables: ${missing.join(', ')}`);
    } else {
      console.log('✅ All required auth tables exist');
    }
  } catch (error) {
    console.error('❌ Database verification failed:', error);
    process.exit(1);
  }

  console.log('\n✅ Database ready for E2E tests\n');
}

initializeDatabase().catch((error) => {
  console.error('Unexpected error:', error);
  process.exit(1);
});
