---
name: wenexus-conventions
description: Development conventions and patterns for wenexus. TypeScript project with conventional commits.
---

# Wenexus Conventions

> Generated from [ournexus/wenexus](https://github.com/ournexus/wenexus) on 2026-03-23

## Overview

This skill teaches Claude the development patterns and conventions used in wenexus.

## Tech Stack

- **Primary Language**: TypeScript
- **Architecture**: feature-based module organization
- **Test Location**: mixed
- **Test Framework**: playwright

## When to Use This Skill

Activate this skill when:
- Making changes to this repository
- Adding new features following established patterns
- Writing tests that match project conventions
- Creating commits with proper message format

## Commit Conventions

Follow these commit message conventions based on 43 analyzed commits.

### Commit Style: Conventional Commits

### Prefixes Used

- `feat`
- `docs`
- `fix`
- `refactor`

### Message Guidelines

- Average message length: ~60 characters
- Keep first line concise and descriptive
- Use imperative mood ("Add feature" not "Added feature")


*Commit message example*

```text
fix: improve E2E test reliability by replacing URL checks and hard delays
```

*Commit message example*

```text
docs: add E2E test code logic analysis and improvement recommendations
```

*Commit message example*

```text
feat: Cloudflare Workers deployment, BMAD planning, and initial schema (#31)
```

*Commit message example*

```text
refactor: monorepo restructure with frontend, backend layering, and docs reorganization (#26)
```

*Commit message example*

```text
fix: disable email verification for local testing and update E2E signup tests
```

*Commit message example*

```text
docs: update progress.md with PR #31 completion summary
```

*Commit message example*

```text
Refactor/monorepo restructure (#30)
```

*Commit message example*

```text
feat: dev toolchain, roundtable, and docs restructuring (#29)
```

## Architecture

### Project Structure: Single Package

This project uses **feature-based** module organization.

### Configuration Files

- `.github/workflows/ci-cd.yml`
- `docker-compose.yml`
- `frontend/apps/admin/package.json`
- `frontend/apps/mobile/package.json`
- `frontend/apps/web/next.config.mjs`
- `frontend/apps/web/package.json`
- `frontend/apps/web/tsconfig.json`
- `frontend/apps/web/wrangler.toml`
- `frontend/package.json`
- `frontend/packages/e2e/package.json`
- `frontend/packages/e2e/playwright.config.ts`
- `frontend/packages/e2e/tsconfig.json`
- `frontend/packages/shared/package.json`
- `frontend/packages/types/package.json`
- `frontend/packages/types/tsconfig.json`
- `frontend/packages/ui/package.json`
- `frontend/packages/ui/tsconfig.json`
- `frontend/packages/utils/package.json`
- `frontend/packages/utils/tsconfig.json`
- `frontend/tsconfig.json`
- `package.json`

### Guidelines

- Group related code by feature/domain
- Each feature folder should be self-contained
- Shared utilities go in a common/shared folder

## Code Style

### Language: TypeScript

### Naming Conventions

| Element | Convention |
|---------|------------|
| Files | kebab-case |
| Functions | camelCase |
| Classes | PascalCase |
| Constants | SCREAMING_SNAKE_CASE |

### Import Style: Path Aliases (@/, ~/)

### Export Style: Default Exports


*Preferred import style*

```typescript
// Use path aliases for imports
import { Button } from '@/components/Button'
import { useAuth } from '@/hooks/useAuth'
import { api } from '@/lib/api'
```

*Preferred export style*

```typescript
// Use default exports for main component/function
export default function UserProfile() { ... }
```

## Testing

### Test Framework: playwright

### File Pattern: `*.spec.ts`

### Test Types

- **Unit tests**: Test individual functions and components in isolation
- **Integration tests**: Test interactions between multiple components/services
- **E2e tests**: Test complete user flows through the application

### Coverage

This project has coverage reporting configured. Aim for 80%+ coverage.


## Error Handling

### Error Handling Style: Try-Catch Blocks


*Standard error handling pattern*

```typescript
try {
  const result = await riskyOperation()
  return result
} catch (error) {
  console.error('Operation failed:', error)
  throw new Error('User-friendly message')
}
```

## Common Workflows

These workflows were detected from analyzing commit patterns.

### Database Migration

Database schema changes with migration files

**Frequency**: ~3 times per month

**Steps**:
1. Create migration file
2. Update schema definitions
3. Generate/update types

**Files typically involved**:
- `**/schema.*`
- `**/types.ts`
- `migrations/*`

**Example commit sequence**:
```
feat(frontend): integrate ShipAny template as web app foundation (#18)
feat: domain architecture + local dev environment setup (#19)
fix(ci): resolve CI pipeline failures (#20)
```

### Feature Development

Standard feature implementation workflow

**Frequency**: ~20 times per month

**Steps**:
1. Add feature implementation
2. Add tests for feature
3. Update documentation

**Files typically involved**:
- `frontend/packages/types/src/*`
- `frontend/packages/ui/src/*`
- `frontend/packages/utils/src/*`
- `**/*.test.*`
- `**/api/**`

**Example commit sequence**:
```
feat: Initialize WeNexus monorepo with comprehensive project structure
feat: Setup comprehensive precommit hooks and development tools
docs: Add Claude.md
```

### Refactoring

Code refactoring and cleanup workflow

**Frequency**: ~8 times per month

**Steps**:
1. Ensure tests pass before refactor
2. Refactor code structure
3. Verify tests still pass

**Files typically involved**:
- `src/**/*`

**Example commit sequence**:
```
feat(tools): implement intelligent code quality system with auto-fix
docs: add initial CHANGELOG.md for version 1.0.0
feat: add Claude commands and documentation structure
```

### Feature Api Endpoint Development

Implements a new API endpoint, including backend logic, route registration, and associated tests and documentation.

**Frequency**: ~2 times per month

**Steps**:
1. Create or update backend API route file (e.g., facade/ or api/ directory).
2. Implement business logic in service/ and/or repository/ layer.
3. Add or update integration/unit tests for the endpoint.
4. Update or add technical documentation describing the endpoint and flow.
5. Update progress or planning artifacts to reflect completion.

**Files typically involved**:
- `backend/python/src/wenexus/facade/*.py`
- `backend/python/src/wenexus/service/*.py`
- `backend/python/src/wenexus/repository/*.py`
- `backend/python/tests/integration/**/*.py`
- `docs/technical/develop/**/*.md`
- `progress.md`

**Example commit sequence**:
```
Create or update backend API route file (e.g., facade/ or api/ directory).
Implement business logic in service/ and/or repository/ layer.
Add or update integration/unit tests for the endpoint.
Update or add technical documentation describing the endpoint and flow.
Update progress or planning artifacts to reflect completion.
```

### E2e Test Workflow

Adds or improves end-to-end (E2E) tests, including test code, configuration, and reliability fixes.

**Frequency**: ~2 times per month

**Steps**:
1. Add or update test files in packages/e2e/tests/ or apps/web/e2e/.
2. Modify or add fixtures, config files, or test utilities.
3. Update CI/CD workflow to ensure tests run and pass.
4. Document test logic, issues, or fixes in technical docs.
5. Optionally, update scripts for database/test environment setup.

**Files typically involved**:
- `frontend/packages/e2e/tests/**/*.spec.ts`
- `frontend/packages/e2e/fixtures/**/*.ts`
- `frontend/packages/e2e/playwright.config.ts`
- `frontend/apps/web/scripts/init-db-e2e.ts`
- `.github/workflows/ci-cd.yml`
- `docs/technical/**/*.md`

**Example commit sequence**:
```
Add or update test files in packages/e2e/tests/ or apps/web/e2e/.
Modify or add fixtures, config files, or test utilities.
Update CI/CD workflow to ensure tests run and pass.
Document test logic, issues, or fixes in technical docs.
Optionally, update scripts for database/test environment setup.
```

### Backend Layered Architecture Refactor

Refactors backend code to enforce or improve layered architecture (facade → app → service → repository), often splitting logic and updating imports.

**Frequency**: ~1 times per month

**Steps**:
1. Move business logic from service/ to repository/ or app/ layer.
2. Create or update app/ layer as orchestration between facade and service.
3. Update imports in facade/ to use app/ instead of service/.
4. Update or add tests to match new structure.
5. Update architecture documentation to reflect changes.

**Files typically involved**:
- `backend/python/src/wenexus/app/**/*.py`
- `backend/python/src/wenexus/service/**/*.py`
- `backend/python/src/wenexus/repository/**/*.py`
- `backend/python/src/wenexus/facade/**/*.py`
- `backend/python/tests/integration/**/*.py`
- `docs/bmad/planning-artifacts/architecture.md`

**Example commit sequence**:
```
Move business logic from service/ to repository/ or app/ layer.
Create or update app/ layer as orchestration between facade and service.
Update imports in facade/ to use app/ instead of service/.
Update or add tests to match new structure.
Update architecture documentation to reflect changes.
```

### Documentation Structure Reorganization

Reorganizes documentation directories, enforces documentation rules, and updates or consolidates docs.

**Frequency**: ~2 times per month

**Steps**:
1. Move or remove outdated documentation files.
2. Update documentation governance rules (e.g., CLAUDE.md).
3. Add or update hook/check scripts for documentation enforcement.
4. Update planning artifacts or technical docs as needed.

**Files typically involved**:
- `docs/**/*.md`
- `CLAUDE.md`
- `.claude/hookify.check-docs-before-stop.local.md`

**Example commit sequence**:
```
Move or remove outdated documentation files.
Update documentation governance rules (e.g., CLAUDE.md).
Add or update hook/check scripts for documentation enforcement.
Update planning artifacts or technical docs as needed.
```

### Ci Cd Pipeline And Devops Fix

Updates CI/CD workflow files, fixes pipeline issues, or adds new steps for testing, security, or deployment.

**Frequency**: ~2 times per month

**Steps**:
1. Edit .github/workflows/ci-cd.yml to add, fix, or update jobs.
2. Update scripts or config files for test, build, or deployment steps.
3. Add or update documentation for pipeline changes.
4. Optionally, update .gitignore or other infra files.

**Files typically involved**:
- `.github/workflows/ci-cd.yml`
- `frontend/apps/web/scripts/init-db-e2e.ts`
- `.gitignore`
- `docs/technical/**/*.md`

**Example commit sequence**:
```
Edit .github/workflows/ci-cd.yml to add, fix, or update jobs.
Update scripts or config files for test, build, or deployment steps.
Add or update documentation for pipeline changes.
Optionally, update .gitignore or other infra files.
```

### Bmad Planning Artifact Workflow

Creates or updates BMAD (autonomous development) planning artifacts such as PRD, architecture, epics, and UX specs.

**Frequency**: ~1 times per month

**Steps**:
1. Add or update PRD, architecture, epics, UX design, or readiness report in docs/bmad/planning-artifacts/.
2. Optionally, update product brief or MVP scope.
3. Update progress.md to reflect planning status.

**Files typically involved**:
- `docs/bmad/planning-artifacts/*.md`
- `progress.md`

**Example commit sequence**:
```
Add or update PRD, architecture, epics, UX design, or readiness report in docs/bmad/planning-artifacts/.
Optionally, update product brief or MVP scope.
Update progress.md to reflect planning status.
```


## Best Practices

Based on analysis of the codebase, follow these practices:

### Do

- Use conventional commit format (feat:, fix:, etc.)
- Keep feature code co-located in feature folders
- Write tests using playwright
- Follow *.spec.ts naming pattern
- Use kebab-case for file names
- Prefer default exports

### Don't

- Don't use long relative imports (use aliases)
- Don't write vague commit messages
- Don't skip tests for new features
- Don't deviate from established patterns without discussion

---

*This skill was auto-generated by [ECC Tools](https://ecc.tools). Review and customize as needed for your team.*
