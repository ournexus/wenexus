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

Follow these commit message conventions based on 69 analyzed commits.

### Commit Style: Conventional Commits

### Prefixes Used

- `feat`
- `docs`
- `fix`
- `chore`

### Message Guidelines

- Average message length: ~57 characters
- Keep first line concise and descriptive
- Use imperative mood ("Add feature" not "Added feature")


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
test: 创建认证系统集成测试和文档
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
- `frontend/packages/types/src/*`
- `frontend/packages/ui/src/*`
- `frontend/packages/utils/src/*`
- `**/*.test.*`
- `**/api/**`

**Example commit sequence**:
```
feat(docs): add module documentation enforcement system
docs: add knowledge engineering best practices
Merge pull request #16 from ournexus/refactor/monorepo-restructure
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

### Add Or Update Bmad Skill Or Workflow

Adds or updates BMAD (autonomous development) skills, workflows, or manifests for the BMAD agent framework.

**Frequency**: ~2 times per month

**Steps**:
1. Add or update files under .claude/skills/ or _bmad/bmm/workflows/ or _bmad/core/workflows/
2. Update manifest/config files (e.g., _bmad/_config/skill-manifest.csv, _bmad/_config/workflow-manifest.csv)
3. Optionally update .gitignore or .markdownlintignore to track/exclude new skill/workflow files
4. Document or reference new/changed skills or workflows

**Files typically involved**:
- `.claude/skills/*`
- `_bmad/bmm/workflows/*`
- `_bmad/core/workflows/*`
- `_bmad/_config/skill-manifest.csv`
- `_bmad/_config/workflow-manifest.csv`
- `.gitignore`
- `.markdownlintignore`

**Example commit sequence**:
```
Add or update files under .claude/skills/ or _bmad/bmm/workflows/ or _bmad/core/workflows/
Update manifest/config files (e.g., _bmad/_config/skill-manifest.csv, _bmad/_config/workflow-manifest.csv)
Optionally update .gitignore or .markdownlintignore to track/exclude new skill/workflow files
Document or reference new/changed skills or workflows
```

### Feature Development With Backend Layered Architecture

Implements a new backend feature or API endpoint using a layered architecture (repository, service, facade), with corresponding integration tests and documentation.

**Frequency**: ~2 times per month

**Steps**:
1. Add or update repository layer (e.g., repository/feature.py) for DB access
2. Add or update service layer (e.g., service/feature.py) for business logic
3. Add or update facade layer (e.g., facade/feature.py) for API endpoint
4. Add or update FastAPI main.py if new endpoints are registered
5. Add or update integration tests (tests/integration/facade/ or tests/integration/service/)
6. Add or update technical documentation (docs/technical/develop/...)

**Files typically involved**:
- `backend/python/src/wenexus/repository/*.py`
- `backend/python/src/wenexus/service/*.py`
- `backend/python/src/wenexus/facade/*.py`
- `backend/python/src/wenexus/main.py`
- `backend/python/tests/integration/facade/*.py`
- `backend/python/tests/integration/service/*.py`
- `docs/technical/develop/*`

**Example commit sequence**:
```
Add or update repository layer (e.g., repository/feature.py) for DB access
Add or update service layer (e.g., service/feature.py) for business logic
Add or update facade layer (e.g., facade/feature.py) for API endpoint
Add or update FastAPI main.py if new endpoints are registered
Add or update integration tests (tests/integration/facade/ or tests/integration/service/)
Add or update technical documentation (docs/technical/develop/...)
```

### Add Or Update E2e Tests And E2e Workflow

Adds or updates end-to-end (E2E) Playwright tests and related workflow/command files, including test environment setup and CI integration.

**Frequency**: ~2 times per month

**Steps**:
1. Add or update Playwright test files (e.g., tests/auth/*.spec.ts)
2. Update or create E2E test environment config (.env.test, playwright.config.ts)
3. Add or update E2E workflow/command files (.claude/commands/e2e-test.md or .windsurf/workflows/e2e-test.md)
4. Update CI/CD config for E2E (e.g., .github/workflows/ci-cd.yml, database setup scripts)
5. Update documentation for E2E test strategy or fixes

**Files typically involved**:
- `frontend/packages/e2e/tests/**/*.spec.ts`
- `frontend/packages/e2e/fixtures/*.ts`
- `frontend/packages/e2e/playwright.config.ts`
- `frontend/packages/e2e/.env.test`
- `.claude/commands/e2e-test.md`
- `.windsurf/workflows/e2e-test.md`
- `.github/workflows/ci-cd.yml`
- `docs/technical/260310-e2e-timeout-fix.md`
- `docs/technical/250310-e2e-logout-auth-state-fix.md`

**Example commit sequence**:
```
Add or update Playwright test files (e.g., tests/auth/*.spec.ts)
Update or create E2E test environment config (.env.test, playwright.config.ts)
Add or update E2E workflow/command files (.claude/commands/e2e-test.md or .windsurf/workflows/e2e-test.md)
Update CI/CD config for E2E (e.g., .github/workflows/ci-cd.yml, database setup scripts)
Update documentation for E2E test strategy or fixes
```

### Monorepo Or Project Structure Refactor

Performs a large-scale refactor or restructure of the monorepo, including moving directories, updating .gitignore, and reorganizing documentation or code.

**Frequency**: ~1 times per month

**Steps**:
1. Move or reorganize major directories (e.g., frontend/, backend/, docs/)
2. Update .gitignore, .husky, or other root config files
3. Update documentation to reflect new structure
4. Update CI/CD config if needed

**Files typically involved**:
- `.gitignore`
- `docs/**`
- `frontend/**`
- `backend/**`
- `.husky/**`
- `.github/workflows/ci-cd.yml`

**Example commit sequence**:
```
Move or reorganize major directories (e.g., frontend/, backend/, docs/)
Update .gitignore, .husky, or other root config files
Update documentation to reflect new structure
Update CI/CD config if needed
```

### Add Or Update Documentation With Planning Artifacts

Adds or updates planning and specification documents such as PRD, architecture, epics, UX specs, and implementation readiness reports.

**Frequency**: ~2 times per month

**Steps**:
1. Add or update PRD, product brief, or planning markdown files
2. Add or update architecture, epics, UX specification docs
3. Add implementation readiness or progress reports

**Files typically involved**:
- `docs/bmad/planning-artifacts/*.md`
- `docs/technical/deployment/*.md`
- `docs/technical/develop/**/*.md`

**Example commit sequence**:
```
Add or update PRD, product brief, or planning markdown files
Add or update architecture, epics, UX specification docs
Add implementation readiness or progress reports
```

### Address Pr Code Review Feedback

Addresses code review feedback from PRs, often fixing bugs, improving type safety, or refactoring per reviewer suggestions.

**Frequency**: ~2 times per month

**Steps**:
1. Edit files mentioned in PR review comments
2. Fix bugs, refactor code, or improve type safety
3. Update related documentation or comments
4. Mention PR number or reviewer in commit message

**Files typically involved**:
- `frontend/apps/web/src/**`
- `backend/python/src/wenexus/**`
- `docs/**`

**Example commit sequence**:
```
Edit files mentioned in PR review comments
Fix bugs, refactor code, or improve type safety
Update related documentation or comments
Mention PR number or reviewer in commit message
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
