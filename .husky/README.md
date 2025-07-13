# Husky Configuration for WeNexus Git Hooks

This directory contains Git hooks managed by Husky to ensure code quality and consistency.

## Available Hooks

### Pre-commit

- Runs pre-commit hooks on staged files
- Formats code with Prettier
- Lints code with ESLint
- Checks for common issues
- Validates brand consistency

### Commit-msg

- Validates commit message format using Conventional Commits
- Ensures proper commit structure and types

## Setup

The hooks are automatically installed when running:

```bash
npm install
# or
./tools/scripts/setup-precommit.sh
```

## Manual Installation

If you need to reinstall the hooks:

```bash
npx husky install
```

## Bypassing Hooks

In emergency situations, you can bypass hooks:

```bash
git commit --no-verify -m "emergency fix"
```

**Note**: Use `--no-verify` sparingly and only in genuine emergencies.
