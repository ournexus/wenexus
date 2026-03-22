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

Follow these commit message conventions based on 70 analyzed commits.

### Commit Style: Conventional Commits

### Prefixes Used

- `feat`
- `docs`
- `fix`
- `chore`
- `refactor`

### Message Guidelines

- Average message length: ~57 characters
- Keep first line concise and descriptive
- Use imperative mood ("Add feature" not "Added feature")


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
fix(web): resolve Cloudflare Workers runtime issues
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
feat: merge main into feature/dev_0315
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

**Frequency**: ~2 times per month

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
docs: add knowledge engineering best practices
Merge pull request #16 from ournexus/refactor/monorepo-restructure
docs: add BMAD development practices and theory documents
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

### Backend Layered Feature Development

Implements or refactors a backend feature using a strict layered architecture (facade → app → service → repository), with tests and documentation.

**Frequency**: ~2 times per month

**Steps**:
1. Move or create SQL queries in repository/*.py
2. Implement business logic in service/*.py
3. Add orchestration/auth/session logic in app/*.py (if present)
4. Expose endpoints in facade/*.py
5. Update or add tests in tests/integration/(facade|service|repository)/*.py
6. Update or add technical documentation in docs/technical/develop/ or similar

**Files typically involved**:
- `backend/python/src/wenexus/facade/*.py`
- `backend/python/src/wenexus/app/*.py`
- `backend/python/src/wenexus/service/*.py`
- `backend/python/src/wenexus/repository/*.py`
- `backend/python/tests/integration/**/*.py`
- `docs/technical/develop/**/*.md`

**Example commit sequence**:
```
Move or create SQL queries in repository/*.py
Implement business logic in service/*.py
Add orchestration/auth/session logic in app/*.py (if present)
Expose endpoints in facade/*.py
Update or add tests in tests/integration/(facade|service|repository)/*.py
Update or add technical documentation in docs/technical/develop/ or similar
```

### Api Endpoint With Integration Tests

Implements a new API endpoint (usually in Python backend), adds corresponding integration tests, and documents the flow.

**Frequency**: ~2 times per month

**Steps**:
1. Add endpoint to facade/*.py (FastAPI route)
2. Implement supporting logic in service/*.py and repository/*.py
3. Add or update integration tests in tests/integration/facade/*.py
4. Document API and flow in docs/technical/develop/ or similar
5. Update progress.md if tracking

**Files typically involved**:
- `backend/python/src/wenexus/facade/*.py`
- `backend/python/src/wenexus/service/*.py`
- `backend/python/src/wenexus/repository/*.py`
- `backend/python/tests/integration/facade/*.py`
- `docs/technical/develop/**/*.md`
- `progress.md`

**Example commit sequence**:
```
Add endpoint to facade/*.py (FastAPI route)
Implement supporting logic in service/*.py and repository/*.py
Add or update integration tests in tests/integration/facade/*.py
Document API and flow in docs/technical/develop/ or similar
Update progress.md if tracking
```

### E2e Auth Flow Test Development

Adds or improves end-to-end authentication/signup/login/logout tests using Playwright, with supporting config and documentation.

**Frequency**: ~2 times per month

**Steps**:
1. Add or update Playwright test files in tests/auth/*.spec.ts
2. Update or add fixtures in fixtures/*.ts
3. Adjust Playwright config/playwright.config.ts as needed
4. Update .env.test or related E2E environment config
5. Document test strategy or fixes in docs/technical/
6. Update or add Claude Code commands for E2E test running

**Files typically involved**:
- `frontend/packages/e2e/tests/auth/*.spec.ts`
- `frontend/packages/e2e/fixtures/*.ts`
- `frontend/packages/e2e/playwright.config.ts`
- `frontend/packages/e2e/.env.test`
- `docs/technical/**/*.md`
- `.claude/commands/e2e-test.md`

**Example commit sequence**:
```
Add or update Playwright test files in tests/auth/*.spec.ts
Update or add fixtures in fixtures/*.ts
Adjust Playwright config/playwright.config.ts as needed
Update .env.test or related E2E environment config
Document test strategy or fixes in docs/technical/
Update or add Claude Code commands for E2E test running
```

### Bm Ad Skills And Workflows Synchronization

Adds, migrates, or synchronizes BMAD (autonomous agent) skills, workflows, and supporting manifests/configs for the project.

**Frequency**: ~2 times per month

**Steps**:
1. Add or update .claude/skills/ and .claude/commands/ files
2. Update or add _bmad/_config/*.csv, *.yaml, *.md (manifests, config, templates)
3. Add or update workflow/skill files in _bmad/bmm/ or _bmad/core/
4. Update .gitignore and .markdownlintignore as needed to track skills
5. Document or update BMAD-related docs

**Files typically involved**:
- `.claude/skills/**/*`
- `.claude/commands/**/*`
- `_bmad/_config/**/*`
- `_bmad/bmm/**/*`
- `_bmad/core/**/*`
- `.gitignore`
- `.markdownlintignore`

**Example commit sequence**:
```
Add or update .claude/skills/ and .claude/commands/ files
Update or add _bmad/_config/*.csv, *.yaml, *.md (manifests, config, templates)
Add or update workflow/skill files in _bmad/bmm/ or _bmad/core/
Update .gitignore and .markdownlintignore as needed to track skills
Document or update BMAD-related docs
```

### Monorepo Structure And Docs Reorganization

Performs a broad monorepo restructure, including moving documentation, updating .gitignore, and aligning config files.

**Frequency**: ~2 times per month

**Steps**:
1. Move or consolidate docs across docs/prd/, docs/theory/, docs/technical/, etc.
2. Update .gitignore and other root config files
3. Remove or archive obsolete files
4. Add or update documentation governance rules (e.g., CLAUDE.md)
5. Update or add technical debt registry or architecture docs

**Files typically involved**:
- `docs/**/*.md`
- `.gitignore`
- `CLAUDE.md`
- `docs/changelog/CHANGELOG.md`
- `docs/prd/**/*`
- `docs/theory/**/*`
- `docs/technical/**/*`

**Example commit sequence**:
```
Move or consolidate docs across docs/prd/, docs/theory/, docs/technical/, etc.
Update .gitignore and other root config files
Remove or archive obsolete files
Add or update documentation governance rules (e.g., CLAUDE.md)
Update or add technical debt registry or architecture docs
```

### Cloudflare Workers Deployment Pipeline Update

Implements or updates Cloudflare Workers deployment for the Next.js frontend, including CI/CD, OpenNext config, and wrangler settings.

**Frequency**: ~2 times per month

**Steps**:
1. Update or add .github/workflows/ci-cd.yml for deployment steps
2. Add or update frontend/apps/web/open-next.config.ts and wrangler.toml
3. Patch dependencies as needed for Workers compatibility
4. Update .gitignore to exclude deployment artifacts
5. Document deployment plan or fixes in docs/technical/deployment/

**Files typically involved**:
- `.github/workflows/ci-cd.yml`
- `frontend/apps/web/open-next.config.ts`
- `frontend/apps/web/wrangler.toml`
- `frontend/patches/*.patch`
- `.gitignore`
- `docs/technical/deployment/**/*.md`

**Example commit sequence**:
```
Update or add .github/workflows/ci-cd.yml for deployment steps
Add or update frontend/apps/web/open-next.config.ts and wrangler.toml
Patch dependencies as needed for Workers compatibility
Update .gitignore to exclude deployment artifacts
Document deployment plan or fixes in docs/technical/deployment/
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
