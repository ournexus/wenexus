# WeNexus Frontend

Frontend monorepo for WeNexus platform, built with Turborepo.

## Structure

```
frontend/
├── apps/
│   ├── web/        # Main web application (Next.js)
│   ├── admin/      # Admin dashboard (Next.js)
│   └── mobile/     # Mobile app (React Native)
├── packages/
│   ├── ui/         # Shared UI components
│   ├── shared/     # Shared utilities and hooks
│   ├── types/      # TypeScript type definitions
│   └── utils/      # Utility functions
```

## Getting Started

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build all apps
pnpm build

# Run linting
pnpm lint

# Run type checking
pnpm typecheck
```

## Pre-commit Hooks

This directory has its own `.pre-commit-config.yaml` for frontend-specific hooks:

- **ESLint** - JavaScript/TypeScript linting
- **Prettier** - Code formatting
- **TypeScript Check** - Type validation

To run pre-commit hooks manually:

```bash
pre-commit run --all-files -c .pre-commit-config.yaml
```

## Package Manager

This project uses **pnpm** for dependency management. Install it via:

```bash
npm install -g pnpm
# or
corepack enable && corepack prepare pnpm@latest --activate
```
