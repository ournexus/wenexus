```markdown
# wenexus Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill teaches you the core development patterns, coding conventions, and workflows used in the `wenexus` repository. The codebase is primarily TypeScript (with a Python backend), and follows clear architectural layering, conventional commits, and robust testing and documentation practices. You'll learn how to add features, endpoints, tests, and documentation efficiently, and how to maintain consistency with existing code and processes.

---

## Coding Conventions

### File Naming

- Use **camelCase** for file names.
  - Example: `seedDomain.ts`, `initDbE2e.ts`

### Import Style

- Use **import aliases** for modules.
  - Example:
    ```typescript
    import apiClient from '@/utils/apiClient'
    ```

### Export Style

- Use **default exports** for modules.
  - Example:
    ```typescript
    export default function handler(req, res) {
      // ...
    }
    ```

### Commit Messages

- Follow **Conventional Commits**:
  - Prefixes: `feat`, `fix`, `docs`, `chore`
  - Example: `feat: add expert count endpoint for Discovery domain`

---

## Workflows

### Add API Endpoint with Layered Backend

**Trigger:** When you need to add a new backend API endpoint for a domain (e.g., Discovery, Roundtable, Fact Checker).  
**Command:** `/new-api-endpoint`

1. **Create or update facade file** to define the API route  
   _Example: `facade/roundtable.py`_
2. **Implement orchestration/business logic** in `app/`  
   _Example: `app/roundtable.py`_
3. **Add or update service logic** in `service/`  
   _Example: `service/roundtable.py`_
4. **Add or update SQL/data access** in `repository/`  
   _Example: `repository/roundtable.py`_
5. **Update or create integration tests**  
   _Example: `tests/integration/service/test_roundtable.py`_
6. **Update documentation**  
   _Example: `docs/technical/develop/roundtable.md`_
7. **Update progress tracking**  
   _Edit: `progress.md`_

---

### Feature Development with Tests and Docs

**Trigger:** When implementing a new business feature or domain logic (e.g., Fact Checker Agent, Discovery expert count).  
**Command:** `/feature-dev`

1. **Implement core feature logic** (may span multiple layers/modules).
2. **Add or update configuration/settings files** as needed.
3. **Write or update tests** (unit, integration, or E2E).
4. **Document the implementation** (technical docs, architecture, or planning artifacts).
5. **Update progress tracking** (`progress.md`).

---

### Deployment Pipeline and Config Update

**Trigger:** When changing deployment targets, environment variables, or CI/CD steps (e.g., Cloudflare Workers, Supabase, GitHub Actions).  
**Command:** `/update-deploy-config`

1. **Edit deployment config files**  
   _Examples: `wrangler.toml`, `scripts/dev.sh`_
2. **Update CI/CD workflow files**  
   _Example: `.github/workflows/ci-cd.yml`_
3. **Update deployment documentation**  
   _Example: `docs/technical/deployment/README.md`_
4. **Update environment variable templates**  
   _Examples: `.env.example`_
5. **Update progress tracking** (`progress.md`).

---

### E2E Test Infrastructure Improvement

**Trigger:** When fixing, enhancing, or refactoring E2E tests and their CI/CD integration.  
**Command:** `/e2e-fix`

1. **Edit or refactor E2E test files**  
   _Examples: `frontend/packages/e2e/**/*.ts`_
2. **Adjust test configs** (timeouts, waits, login flows).
3. **Update CI/CD workflow** to run or skip E2E tests.
4. **Add/update scripts** for DB init or environment setup.
5. **Document fixes or test strategies**.
6. **Update progress tracking** (`progress.md`).

---

### Documentation and Progress Tracking Update

**Trigger:** When documenting new features, updating architecture, or marking progress.  
**Command:** `/doc-update`

1. **Edit/add technical documentation**  
   _Examples: `docs/technical/`, `docs/bmad/`_
2. **Update planning artifacts**  
   _Examples: `sprint-status.yaml`, architecture docs_
3. **Update progress tracking** (`progress.md`).

---

## Testing Patterns

- **Framework:** Playwright for E2E and integration tests.
- **Test file pattern:** `*.spec.ts`
- **Location:**  
  - E2E: `frontend/packages/e2e/`
  - Backend integration: `backend/python/tests/integration/`
- **Typical test example:**
  ```typescript
  // example.spec.ts
  import { test, expect } from '@playwright/test';

  test('should display expert count', async ({ page }) => {
    await page.goto('/discovery');
    const count = await page.textContent('.expert-count');
    expect(Number(count)).toBeGreaterThan(0);
  });
  ```

---

## Commands

| Command              | Purpose                                                        |
|----------------------|----------------------------------------------------------------|
| /new-api-endpoint    | Add a new backend API endpoint with layered architecture       |
| /feature-dev         | Implement a new feature with tests and documentation           |
| /update-deploy-config| Update deployment pipeline, CI/CD, and related configuration   |
| /e2e-fix             | Improve E2E test infrastructure and integration                |
| /doc-update          | Update technical documentation and progress tracking           |
```
