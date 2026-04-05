```markdown
# wenexus Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill documents the core development patterns, coding conventions, and workflows for the `wenexus` TypeScript codebase. It is designed to help contributors quickly understand how to structure code, write commits, add new components, and extend the repository following established conventions. No major framework is used; the project emphasizes modular, convention-driven TypeScript development.

## Coding Conventions

### File Naming
- Use **camelCase** for file names.
  - Example: `userProfile.ts`, `dataFetcher.test.ts`

### Import Style
- Use **relative imports** for all internal modules.
  - Example:
    ```typescript
    import { fetchData } from './dataFetcher';
    ```

### Export Style
- Use **named exports** instead of default exports.
  - Example:
    ```typescript
    // Good
    export function fetchData() { ... }

    // Bad
    export default function fetchData() { ... }
    ```

### Commit Messages
- Follow **conventional commit** format.
- Use the `feat` prefix for new features.
  - Example:  
    ```
    feat: add user authentication to profile module
    ```

## Workflows

### add-ecc-bundle-component
**Trigger:** When you want to extend the ECC bundle with a new capability, configuration, or documentation for wenexus-conventions.  
**Command:** `/add-ecc-bundle-component`

1. **Create a new file** in the relevant subdirectory, such as:
    - `.claude/skills/wenexus/`
    - `.agents/skills/wenexus/`
    - `.codex/agents/`
2. **Name the file** according to the component type:
    - For skills: `SKILL.md`
    - For agent configs: `.yaml`, `.toml`, `.json`
    - For documentation: `.md`
3. **Commit the new file** with a standardized commit message referencing the ECC bundle.
    - Example:
      ```
      feat: add SKILL.md for new ECC bundle component
      ```
4. **Example Directory Structure:**
    ```
    .claude/
      skills/
        wenexus/
          SKILL.md
      ecc-tools.json
      identity.json
      commands/
        add-ecc-bundle-component.md
    .codex/
      agents/
        explorer.toml
        reviewer.toml
        docs-researcher.toml
      config.toml
      AGENTS.md
    ```
5. **Push your changes** and open a pull request if required.

## Testing Patterns

- **Test files** use the pattern `*.test.*` (e.g., `userProfile.test.ts`).
- The specific testing framework is not detected, but tests are colocated with source files or in test directories.
- **Example Test File:**
    ```typescript
    // userProfile.test.ts
    import { getUserProfile } from './userProfile';

    describe('getUserProfile', () => {
      it('returns user data for valid ID', () => {
        // test implementation
      });
    });
    ```

## Commands

| Command                   | Purpose                                                      |
|---------------------------|--------------------------------------------------------------|
| /add-ecc-bundle-component | Add a new component/configuration to the ECC bundle workflow |

```