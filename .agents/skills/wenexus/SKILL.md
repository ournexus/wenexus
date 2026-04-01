```markdown
# wenexus Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill teaches the core development patterns, coding conventions, and workflows used in the `wenexus` repository. The codebase is primarily TypeScript, with a Python backend and a focus on clean, layered architecture, robust end-to-end testing, and clear documentation. The repository uses conventional commits, Playwright for E2E testing, and supports autonomous agent (BMAD) workflows.

## Coding Conventions

- **File Naming:**  
  Use kebab-case for all file names.  
  _Example:_  
  ```
  user-profile.ts
  roundtable-service.ts
  ```

- **Import Style:**  
  Use aliased imports for clarity and maintainability.  
  _Example:_  
  ```typescript
  import { fetchUser } from '@/services/user-service';
  ```

- **Export Style:**  
  Use default exports for modules.  
  _Example:_  
  ```typescript
  const UserService = { ... };
  export default UserService;
  ```

- **Commit Messages:**  
  Follow [Conventional Commits](https://www.conventionalcommits.org/).  
  Prefixes: `feat`, `fix`, `docs`, `chore`  
  _Example:_  
  ```
  feat: add roundtable API endpoint for session creation
  fix: correct user role assignment logic
  docs: update architecture diagram in planning artifacts
  chore: bump dependency versions
  ```

## Workflows

### Feature API Endpoint Development
**Trigger:** When adding or expanding an API endpoint for a domain (e.g., Roundtable, Discovery)  
**Command:** `/new-api-endpoint`

1. Create or update the endpoint in the facade layer (e.g., `facade/roundtable.py`).
2. Implement business logic in the `app`, `service`, or `repository` layers as needed.
3. Update or create models to support the new endpoint.
4. Add or update integration/unit tests to cover the new functionality.
5. Update `progress.md` to reflect the new feature.

_Code Example (Python, facade layer):_
```python
# backend/python/src/wenexus/facade/roundtable.py
def create_roundtable(request):
    return app.create_roundtable(request)
```

### Backend Layered Architecture Refactor
**Trigger:** When improving separation of concerns or addressing technical debt in backend structure  
**Command:** `/refactor-backend-layers`

1. Move SQL queries from the service layer to the repository layer.
2. Introduce or update the app orchestration layer for business logic coordination.
3. Adjust imports and dependencies to match the new structure.
4. Update tests to reflect the new layout.
5. Update architecture documentation (`docs/bmad/planning-artifacts/architecture.md`).

_Code Example (Moving query from service to repository):_
```python
# Before: service/roundtable.py
def get_active_sessions():
    return db.query("SELECT * FROM sessions WHERE active = TRUE")

# After: repository/roundtable.py
def get_active_sessions():
    return db.query("SELECT * FROM sessions WHERE active = TRUE")

# service/roundtable.py now calls the repository function
def get_active_sessions():
    return repository.get_active_sessions()
```

### E2E Test Infrastructure Update
**Trigger:** When adding, migrating, or improving E2E test infrastructure  
**Command:** `/add-e2e-test`

1. Add or update Playwright config and test files (e.g., `*.spec.ts`).
2. Move or refactor E2E test packages as needed (e.g., `apps/web/e2e` → `packages/e2e`).
3. Update CI/CD workflow to run or skip E2E tests as appropriate.
4. Add scripts for DB initialization or test setup.
5. Document test strategy or fixes in the appropriate docs.

_Code Example (Playwright test):_
```typescript
// frontend/packages/e2e/roundtable.spec.ts
import { test, expect } from '@playwright/test';

test('should create a new roundtable session', async ({ page }) => {
  await page.goto('/roundtable');
  await page.click('button#create-session');
  await expect(page).toHaveURL(/.*session/);
});
```

### Deployment Pipeline and Config Update
**Trigger:** When changing deployment targets, environment variables, or CI/CD steps  
**Command:** `/update-deployment`

1. Edit `wrangler.toml` and/or deployment scripts as needed.
2. Update `.env.example` or `backend/python/.env.example` with new variables.
3. Modify CI/CD workflow YAML files.
4. Update deployment documentation in `docs/technical/deployment/`.
5. Test deployment in staging or production environments.

### Documentation Structure and Progress Update
**Trigger:** When recording new progress, reorganizing docs, or adding planning artifacts  
**Command:** `/update-progress`

1. Edit or add files in `docs/bmad/planning-artifacts` or `docs/technical`.
2. Update `progress.md` with completed features or changes.
3. Reorganize documentation directories or move files as needed.
4. Add or update BMAD/PRD/architecture/epics/UX docs.

### BMAD Skill and Workflow Management
**Trigger:** When introducing new BMAD (autonomous agent) skills, updating workflows, or sharing agent configurations  
**Command:** `/add-bmad-skill`

1. Add or update files in `.claude/skills/` or `.claude/commands/`.
2. Track or untrack BMAD skills in version control as appropriate.
3. Update `.gitignore` or `.markdownlintignore` if necessary.
4. Document new skills or workflows for team visibility.

## Testing Patterns

- **Framework:** Playwright is used for end-to-end (E2E) testing.
- **File Pattern:** E2E test files are named with the `.spec.ts` suffix.
- **Location:** E2E tests are typically located in `frontend/packages/e2e/`.
- **Test Example:**
  ```typescript
  // frontend/packages/e2e/user-login.spec.ts
  import { test, expect } from '@playwright/test';

  test('user can log in', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });
  ```

## Commands

| Command              | Purpose                                                      |
|----------------------|--------------------------------------------------------------|
| /new-api-endpoint    | Start a new API endpoint or expand an existing one           |
| /refactor-backend-layers | Refactor backend code to improve layered architecture     |
| /add-e2e-test        | Add or update E2E test infrastructure or scripts             |
| /update-deployment   | Update deployment pipeline, config, or environment variables |
| /update-progress     | Update documentation structure or progress tracking          |
| /add-bmad-skill      | Add or update BMAD skills, workflows, or agent configs       |
```
