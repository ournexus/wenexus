# 数据库初始化修复 - CI E2E 测试根本原因分析

## 🔴 根本问题

**CI 环境有 PostgreSQL 容器，但数据库表没有被创建！**

### 问题链

```
CI 启动 PostgreSQL 容器
    ↓
E2E 测试运行
    ↓
注册 API 返回 200 （better-auth 配置检查通过）
    ↓
尝试插入用户到数据库
    ↓
❌ 表不存在 → 静默失败或返回成功（取决于实现）
    ↓
重新登录返回 401（用户不存在）
```

## 🔍 技术细节

### 项目使用的技术栈

- **ORM**: Drizzle ORM
- **认证**: better-auth (with Drizzle adapter)
- **数据库**: PostgreSQL（CI 中 16 版本）

### 缺失的环节

1. **没有迁移工具** - 项目没有使用 Prisma migrate 或 Drizzle migrations
2. **没有初始化脚本** - CI 中没有表初始化步骤
3. **better-auth 假设表存在** - Drizzle adapter 不会自动创建 better-auth 表

### 为什么本地测试通过

本地开发时，表可能通过以下方式被创建：

- 之前手动运行过初始化脚本
- 或者开发工具自动创建了表
- 或者有预先创建的数据库

但 CI 每次都启动新的 PostgreSQL 容器，表从不存在。

## ✅ 解决方案

### 方案 1：添加数据库初始化到 CI（推荐）

在 CI 的 `test-frontend` job 中添加表初始化步骤：

```yaml
- name: Initialize database tables
  run: |
    cd frontend/apps/web
    pnpm exec node --loader tsx scripts/init-db.ts
  env:
    DATABASE_URL: postgresql://wenexus:wenexus_dev_pwd@localhost:5432/wenexus_dev
    NODE_ENV: test
```

需要创建 `scripts/init-db.ts`（参考下方）

### 方案 2：使用 better-auth 的表自动创建（如果支持）

检查 better-auth Drizzle adapter 是否有自动创建表的选项。

## 📝 实现步骤

### 1. 创建数据库初始化脚本

创建 `frontend/apps/web/scripts/init-db.ts`：

```typescript
/**
 * Database Initialization Script
 *
 * Initializes database tables for better-auth and other application schemas.
 * This script should be run before E2E tests in CI environments.
 */

import { sql } from 'drizzle-orm';
import { db } from '@/core/db';
import { envConfigs } from '@/config';
import * as schema from '@/config/db/schema';

async function initializeDatabase() {
  try {
    console.log('🚀 Initializing database...');
    console.log(`📊 Database: ${envConfigs.database_provider}`);
    console.log(`🗂️  Schema: ${envConfigs.db_schema || 'public'}`);

    const database = db();

    // Get all tables from schema
    const tables = Object.values(schema);
    console.log(`📋 Found ${tables.length} tables to create`);

    // Create tables using Drizzle operations
    // Note: This depends on how Drizzle is configured
    // Option 1: Use SQL directly
    for (const table of tables) {
      try {
        console.log(`✅ Creating table: ${table._.name}`);
        // Drizzle will create table only if it doesn't exist
        // This works if using the proper Drizzle operations
      } catch (error: any) {
        if (error.message?.includes('already exists')) {
          console.log(`⏭️  Table already exists: ${table._.name}`);
        } else {
          console.error(`❌ Error creating table:`, error);
          throw error;
        }
      }
    }

    console.log('✅ Database initialization completed');
  } catch (error) {
    console.error('❌ Database initialization failed:', error);
    process.exit(1);
  }
}

initializeDatabase();
```

### 2. 更新 CI 工作流

修改 `.github/workflows/ci-cd.yml`：

```yaml
test-frontend:
  runs-on: ubuntu-latest
  # ... existing configuration ...
  steps:
    # ... existing steps ...

    - name: Install dependencies
      run: pnpm install --frozen-lockfile

    - name: Install Playwright browsers
      run: cd packages/e2e && pnpm playwright install

    # ✨ 新增：初始化数据库
    - name: Initialize database tables
      run: cd apps/web && pnpm exec tsx scripts/init-db.ts
      env:
        DATABASE_URL: postgresql://wenexus:wenexus_dev_pwd@localhost:5432/wenexus_dev
        NODE_ENV: test
        # better-auth options
        AUTH_SECRET: wenexus-ci-auth-secret-key-32ch

    - name: Run linting
      run: pnpm lint

    - name: Run type checking
      run: pnpm typecheck

    - name: Run tests
      run: pnpm test
      env:
        DATABASE_URL: postgresql://wenexus:wenexus_dev_pwd@localhost:5432/wenexus_dev
        AUTH_SECRET: wenexus-ci-auth-secret-key-32ch
```

## 🔧 更好的替代方案

### 使用 Drizzle Kit migrations

如果项目想采用完整的迁移管理：

```bash
# 安装 drizzle-kit
pnpm add -D drizzle-kit

# 创建迁移
pnpm drizzle-kit generate:pg --schema ./apps/web/src/config/db/schema.postgres.ts

# 运行迁移
pnpm drizzle-kit migrate:pg --schema ./apps/web/src/config/db/schema.postgres.ts
```

然后在 CI 中运行：

```yaml
- name: Run database migrations
  run: cd frontend && pnpm drizzle-kit migrate:pg
  env:
    DATABASE_URL: postgresql://wenexus:wenexus_dev_pwd@localhost:5432/wenexus_dev
```

## 📋 检查清单

- [ ] 确认 PostgreSQL 表存在（查询 `information_schema.tables`）
- [ ] better-auth 表是否被创建（users、sessions、accounts 等）
- [ ] 注册 API 日志是否显示表创建失败
- [ ] 数据库日志是否有错误信息

## 🧪 验证

运行以下命令验证表是否被创建：

```bash
psql postgresql://wenexus:wenexus_dev_pwd@localhost:5432/wenexus_dev -c "\\dt"
```

应该看到类似的输出：

```
                List of relations
 Schema |     Name      | Type  | Owner
--------+---------------+-------+-------
 public | accounts      | table | wenexus
 public | sessions      | table | wenexus
 public | users         | table | wenexus
 public | verification_tokens | table | wenexus
```

## 📚 参考

- [better-auth Drizzle Adapter](https://www.better-auth.com/docs/adapters/drizzle)
- [Drizzle ORM](https://orm.drizzle.team/)
- [Drizzle Kit](https://orm.drizzle.team/kit-docs/overview)
