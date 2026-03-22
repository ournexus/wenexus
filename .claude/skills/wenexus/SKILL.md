---
name: wenexus-conventions
description: Development conventions and patterns for wenexus. TypeScript project with conventional commits.
---

# Wenexus Conventions

> Generated from [ournexus/wenexus](https://github.com/ournexus/wenexus) on 2026-03-22

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

Follow these commit message conventions based on 72 analyzed commits.

### Commit Style: Conventional Commits

### Prefixes Used

- `feat`
- `fix`
- `docs`
- `chore`
- `refactor`

### Message Guidelines

- Average message length: ~58 characters
- Keep first line concise and descriptive
- Use imperative mood ("Add feature" not "Added feature")


*Commit message example*

```text
fix(ci): resolve mypy errors and skip flaky signup E2E test in CI
```

*Commit message example*

```text
refactor(python): enforce layered architecture (facade → app → service → repository)
```

*Commit message example*

```text
feat(e2e): add signup flow test and PR comment handler command
```

*Commit message example*

```text
docs(bmad): complete PRD and add architecture, epics, UX spec
```

*Commit message example*

```text
chore: add .wrangler and .dev.vars to gitignore, fix CLAUDE.md typo
```

*Commit message example*

```text
fix(ci): resolve test-python-backend lint errors and test-frontend E2E failures
```

*Commit message example*

```text
feat(db): add initial schema migration
```

*Commit message example*

```text
docs(deployment): add deployment plan, tunnel guide, and bundle analysis
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

**Frequency**: ~21 times per month

**Steps**:
1. Add feature implementation
2. Add tests for feature
3. Update documentation

**Files typically involved**:
- `frontend/apps/web/*`
- `frontend/apps/web/scripts/*`
- `frontend/apps/web/src/app/[locale]/(admin)/admin/ai-tasks/*`
- `**/*.test.*`
- `**/api/**`

**Example commit sequence**:
```
docs: add BMAD development practices and theory documents
Merge pull request #17 from ournexus/refactor/monorepo-restructure
feat(frontend): integrate ShipAny template as web app foundation (#18)
```

### Refactoring

Code refactoring and cleanup workflow

**Frequency**: ~7 times per month

**Steps**:
1. Ensure tests pass before refactor
2. Refactor code structure
3. Verify tests still pass

**Files typically involved**:
- `src/**/*`

**Example commit sequence**:
```
feat(frontend): integrate ShipAny template as web app foundation (#18)
feat: domain architecture + local dev environment setup (#19)
fix(ci): resolve CI pipeline failures (#20)
```

### Backend Layered Feature Development

Implements a new backend feature or refactors an existing one using the layered architecture (facade → app → service → repository), often with associated integration tests and documentation.

**Frequency**: ~2 times per month

**Steps**:
1. Create or update repository layer file (e.g., repository/feature.py) for SQL/data access.
2. Create or update service layer file (e.g., service/feature.py) for business logic.
3. Create or update app layer file (e.g., app/feature.py) for orchestration/auth checks.
4. Update facade layer file (e.g., facade/feature.py) to expose API endpoints.
5. Update or add integration tests mirroring the source layout.
6. Update technical documentation to reflect changes.

**Files typically involved**:
- `backend/python/src/wenexus/repository/*.py`
- `backend/python/src/wenexus/service/*.py`
- `backend/python/src/wenexus/app/*.py`
- `backend/python/src/wenexus/facade/*.py`
- `backend/python/tests/integration/**/*.py`
- `docs/technical/develop/**/*.md`

**Example commit sequence**:
```
Create or update repository layer file (e.g., repository/feature.py) for SQL/data access.
Create or update service layer file (e.g., service/feature.py) for business logic.
Create or update app layer file (e.g., app/feature.py) for orchestration/auth checks.
Update facade layer file (e.g., facade/feature.py) to expose API endpoints.
Update or add integration tests mirroring the source layout.
Update technical documentation to reflect changes.
```

### End To End Auth Flow Testing And Ci Hardening

Adds or fixes end-to-end (E2E) authentication flow tests, including Playwright config, CI pipeline steps, and supporting scripts for reliable test execution in both local and CI environments.

**Frequency**: ~2 times per month

**Steps**:
1. Add or update Playwright E2E test files for auth flows (register, login, logout, re-login).
2. Update Playwright config (timeouts, webServer, env vars) for CI compatibility.
3. Add or update scripts to initialize database state for E2E tests.
4. Update CI workflow to run E2E tests, ensure DB is ready, and install browser dependencies.
5. Document test strategy, issues, or fixes in technical docs.

**Files typically involved**:
- `frontend/packages/e2e/tests/auth/*.spec.ts`
- `frontend/packages/e2e/playwright.config.ts`
- `frontend/packages/e2e/.env.test`
- `frontend/apps/web/scripts/init-db-e2e.ts`
- `.github/workflows/ci-cd.yml`
- `docs/technical/fix/*.md`
- `docs/technical/develop/**/*.md`

**Example commit sequence**:
```
Add or update Playwright E2E test files for auth flows (register, login, logout, re-login).
Update Playwright config (timeouts, webServer, env vars) for CI compatibility.
Add or update scripts to initialize database state for E2E tests.
Update CI workflow to run E2E tests, ensure DB is ready, and install browser dependencies.
Document test strategy, issues, or fixes in technical docs.
```

### Monorepo Structure And Documentation Reorganization

Reorganizes the monorepo's code and documentation structure, including moving, renaming, or consolidating files, updating .gitignore, and enforcing documentation rules.

**Frequency**: ~2 times per month

**Steps**:
1. Move or reorganize documentation files and directories.
2. Update or add documentation governance rules (e.g., CLAUDE.md, enforced checklist).
3. Update .gitignore and other config files to reflect new structure.
4. Remove obsolete or duplicate files.
5. Update references in code or docs to match new paths.

**Files typically involved**:
- `docs/**/*.md`
- `.gitignore`
- `CLAUDE.md`
- `.claude/hookify.check-docs-before-stop.local.md`
- `frontend/apps/web/package.json`
- `frontend/apps/web/next.config.mjs`

**Example commit sequence**:
```
Move or reorganize documentation files and directories.
Update or add documentation governance rules (e.g., CLAUDE.md, enforced checklist).
Update .gitignore and other config files to reflect new structure.
Remove obsolete or duplicate files.
Update references in code or docs to match new paths.
```

### Ci Pipeline Fix And Hardening

Fixes or improves CI/CD pipeline reliability, especially for multi-language monorepo setups, including dependency upgrades, environment setup, and test/lint/build steps.

**Frequency**: ~2 times per month

**Steps**:
1. Edit .github/workflows/ci-cd.yml to fix or enhance steps.
2. Update environment setup (e.g., database, browsers, Node/Python versions).
3. Pin or upgrade CI dependencies and actions.
4. Add or fix scripts for setup/teardown.
5. Document changes or root causes in technical docs.

**Files typically involved**:
- `.github/workflows/ci-cd.yml`
- `scripts/dev.sh`
- `frontend/pnpm-lock.yaml`
- `docs/technical/fix/*.md`
- `docs/technical/develop/**/*.md`

**Example commit sequence**:
```
Edit .github/workflows/ci-cd.yml to fix or enhance steps.
Update environment setup (e.g., database, browsers, Node/Python versions).
Pin or upgrade CI dependencies and actions.
Add or fix scripts for setup/teardown.
Document changes or root causes in technical docs.
```

### Bmad Framework Skills And Workflows Sync

Synchronizes, upgrades, or migrates BMAD (autonomous agent) framework skills, workflows, and configuration files, including tracking in version control and updating manifests.

**Frequency**: ~2 times per month

**Steps**:
1. Add, update, or migrate .claude/skills/ and related workflow files.
2. Update BMAD manifest/configuration CSV/YAML files.
3. Track skills and workflows in version control (remove from .gitignore, add to .markdownlintignore).
4. Document new/changed workflows or commands.
5. Optionally, migrate workflows from other systems (e.g., Windsurf → Claude Code).

**Files typically involved**:
- `.claude/skills/**/*`
- `.claude/commands/*.md`
- `.markdownlintignore`
- `.gitignore`
- `_bmad/_config/*.csv`
- `_bmad/_config/*.yaml`
- `_bmad/bmm/**/*`

**Example commit sequence**:
```
Add, update, or migrate .claude/skills/ and related workflow files.
Update BMAD manifest/configuration CSV/YAML files.
Track skills and workflows in version control (remove from .gitignore, add to .markdownlintignore).
Document new/changed workflows or commands.
Optionally, migrate workflows from other systems (e.g., Windsurf → Claude Code).
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
