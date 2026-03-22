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

Follow these commit message conventions based on 71 analyzed commits.

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
fix(ci): resolve test-python-backend lint errors and test-frontend E2E failures
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
feat(db): add initial schema migration
```

*Commit message example*

```text
docs(deployment): add deployment plan, tunnel guide, and bundle analysis
```

*Commit message example*

```text
fix(web): resolve Cloudflare Workers runtime issues
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
Merge pull request #16 from ournexus/refactor/monorepo-restructure
docs: add BMAD development practices and theory documents
Merge pull request #17 from ournexus/refactor/monorepo-restructure
```

### Add Or Update Api Endpoint

Implements a new API endpoint or updates an existing one, including backend logic, route registration, and tests.

**Frequency**: ~3 times per month

**Steps**:
1. Create or update a facade (API route) file in backend/python/src/wenexus/facade/
2. Implement or update corresponding service and/or repository logic in backend/python/src/wenexus/service/ and backend/python/src/wenexus/repository/
3. Update or add integration tests in backend/python/tests/integration/facade/ or backend/python/tests/integration/service/
4. Update or add documentation in docs/technical/develop/ or similar docs/technical/ directories

**Files typically involved**:
- `backend/python/src/wenexus/facade/*.py`
- `backend/python/src/wenexus/service/*.py`
- `backend/python/src/wenexus/repository/*.py`
- `backend/python/tests/integration/facade/*.py`
- `backend/python/tests/integration/service/*.py`
- `docs/technical/develop/**/*.md`

**Example commit sequence**:
```
Create or update a facade (API route) file in backend/python/src/wenexus/facade/
Implement or update corresponding service and/or repository logic in backend/python/src/wenexus/service/ and backend/python/src/wenexus/repository/
Update or add integration tests in backend/python/tests/integration/facade/ or backend/python/tests/integration/service/
Update or add documentation in docs/technical/develop/ or similar docs/technical/ directories
```

### Backend Layered Architecture Refactor

Refactors backend code to enforce or improve layered architecture (facade → app → service → repository), moving logic between layers and updating docs.

**Frequency**: ~2 times per month

**Steps**:
1. Move business logic from service to repository or app layer as appropriate
2. Create new app/ or repository/ modules if needed
3. Update imports in facade/ to use new structure
4. Remove or update redundant code
5. Update architecture documentation to reflect changes

**Files typically involved**:
- `backend/python/src/wenexus/app/*.py`
- `backend/python/src/wenexus/facade/*.py`
- `backend/python/src/wenexus/service/*.py`
- `backend/python/src/wenexus/repository/*.py`
- `docs/bmad/planning-artifacts/architecture.md`

**Example commit sequence**:
```
Move business logic from service to repository or app layer as appropriate
Create new app/ or repository/ modules if needed
Update imports in facade/ to use new structure
Remove or update redundant code
Update architecture documentation to reflect changes
```

### Add Or Update E2e Tests

Adds or updates end-to-end (E2E) tests for frontend flows, often with Playwright, and integrates with CI/CD.

**Frequency**: ~2 times per month

**Steps**:
1. Create or update E2E test files in frontend/packages/e2e/tests/ or frontend/apps/web/e2e/
2. Update or add fixtures or config in frontend/packages/e2e/fixtures/ or frontend/packages/e2e/playwright.config.ts
3. Update CI/CD workflow to ensure E2E tests run (e.g., .github/workflows/ci-cd.yml)
4. Update or add documentation for E2E test strategy

**Files typically involved**:
- `frontend/packages/e2e/tests/**/*.spec.ts`
- `frontend/packages/e2e/fixtures/*.ts`
- `frontend/packages/e2e/playwright.config.ts`
- `frontend/apps/web/e2e/**/*.spec.ts`
- `.github/workflows/ci-cd.yml`
- `docs/technical/**/*.md`

**Example commit sequence**:
```
Create or update E2E test files in frontend/packages/e2e/tests/ or frontend/apps/web/e2e/
Update or add fixtures or config in frontend/packages/e2e/fixtures/ or frontend/packages/e2e/playwright.config.ts
Update CI/CD workflow to ensure E2E tests run (e.g., .github/workflows/ci-cd.yml)
Update or add documentation for E2E test strategy
```

### Ci Cd Pipeline Fix Or Improvement

Fixes or improves the CI/CD pipeline, including adding steps, fixing environment issues, or integrating new tools.

**Frequency**: ~2 times per month

**Steps**:
1. Edit .github/workflows/ci-cd.yml to add/fix steps or environment variables
2. Add scripts or config files to support new pipeline steps
3. Document the change in a relevant markdown file

**Files typically involved**:
- `.github/workflows/ci-cd.yml`
- `frontend/apps/web/scripts/*.ts`
- `docs/technical/**/*.md`

**Example commit sequence**:
```
Edit .github/workflows/ci-cd.yml to add/fix steps or environment variables
Add scripts or config files to support new pipeline steps
Document the change in a relevant markdown file
```

### Documentation Structure Reorganization

Reorganizes documentation directories, moves or archives files, and updates documentation governance rules.

**Frequency**: ~2 times per month

**Steps**:
1. Move or archive markdown files between docs/ subdirectories
2. Update or add documentation guidelines (e.g., CLAUDE.md)
3. Update .gitignore or .markdownlintignore as needed

**Files typically involved**:
- `docs/**/*.md`
- `CLAUDE.md`
- `.gitignore`
- `.markdownlintignore`

**Example commit sequence**:
```
Move or archive markdown files between docs/ subdirectories
Update or add documentation guidelines (e.g., CLAUDE.md)
Update .gitignore or .markdownlintignore as needed
```

### Add Bmad Skill Or Workflow

Adds or updates BMAD (autonomous agent) skills, workflows, or configuration for the BMAD framework.

**Frequency**: ~2 times per month

**Steps**:
1. Add or update files in .claude/skills/ or _bmad/ directories
2. Update manifest/config files (e.g., skill-manifest.csv, workflow-manifest.csv)
3. Update .gitignore or .markdownlintignore to track new skills

**Files typically involved**:
- `.claude/skills/**/*`
- `_bmad/**/*`
- `.gitignore`
- `.markdownlintignore`

**Example commit sequence**:
```
Add or update files in .claude/skills/ or _bmad/ directories
Update manifest/config files (e.g., skill-manifest.csv, workflow-manifest.csv)
Update .gitignore or .markdownlintignore to track new skills
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
