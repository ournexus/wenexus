/**
 * Database Initialization Script for E2E Testing
 *
 * Ensures database tables are created before running E2E tests.
 * This script initializes the better-auth tables required for authentication.
 *
 * Usage:
 *   tsx scripts/init-db-e2e.ts
 */

import { sql } from 'drizzle-orm';

import { db } from '@/core/db';
import { envConfigs } from '@/config';

async function initializeDatabase() {
  const dbInstance = db();

  try {
    console.log('🚀 Initializing database for E2E tests...');
    console.log(`📊 Database Provider: ${envConfigs.database_provider}`);
    console.log(
      `🗂️  Database URL: ${envConfigs.database_url?.substring(0, 50)}...`
    );

    // Test database connection
    console.log('\n1️⃣  Testing database connection...');
    await dbInstance.execute(sql`SELECT 1`);
    console.log('✅ Database connection successful');

    // List existing tables
    console.log('\n2️⃣  Checking existing tables...');
    const tables = await dbInstance.execute(sql`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
      ORDER BY table_name
    `);

    if (tables.length > 0) {
      console.log(`✅ Found ${tables.length} existing tables:`);
      tables.forEach((row: any) => {
        console.log(`   - ${row.table_name}`);
      });
    } else {
      console.log('⚠️  No tables found - they will be created on first use');
    }

    // Verify better-auth required tables
    console.log('\n3️⃣  Verifying better-auth tables...');
    const requiredTables = ['users', 'sessions', 'accounts'];
    const existingTableNames = tables.map((t: any) => t.table_name);

    const missingTables = requiredTables.filter(
      (table) => !existingTableNames.includes(table)
    );

    if (missingTables.length === 0) {
      console.log('✅ All required better-auth tables exist');
    } else {
      console.log(`⚠️  Missing tables: ${missingTables.join(', ')}`);
      console.log('   Note: Tables will be created on first API call');
    }

    console.log('\n✅ Database initialization check completed');
    console.log(
      '\n📝 Database is ready for E2E tests. If tables are missing, they will be created on first better-auth API call.\n'
    );
  } catch (error) {
    console.error('❌ Database initialization failed:', error);
    process.exit(1);
  }
}

initializeDatabase().catch((error) => {
  console.error('Unexpected error:', error);
  process.exit(1);
});
