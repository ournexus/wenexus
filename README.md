<div align="center">
  <img src="docs/design/logos/wenexus-logo-complete.svg" alt="WeNexus Logo" width="120" height="120">

# WeNexus: The Consensus Amplifier

_Connecting minds, building consensus, amplifying understanding_

</div>

WeNexus is a platform designed to bridge information gaps and create meaningful connections in an
age of information overload and polarizing echo chambers. We don't just need another network; we
need a Nexus - a central point where We, as a society, can finally connect, understand, and agree.

## Project Structure

This is a monorepo containing all WeNexus applications and services:

```
wenexus/
├── frontend/               # Frontend monorepo (npm workspaces + Turborepo)
│   ├── apps/
│   │   ├── web/           # Main web application (Next.js)
│   │   ├── admin/         # Admin dashboard (Next.js)
│   │   └── mobile/        # Mobile application (React Native)
│   ├── packages/
│   │   ├── ui/            # Shared UI components
│   │   ├── shared/        # Common utilities and hooks
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   └── .pre-commit-config.yaml  # Frontend-specific hooks
│
├── backend/                # Backend services
│   ├── java/              # Java microservices (Spring Boot + Maven)
│   │   ├── core-service/
│   │   ├── user-service/
│   │   ├── content-service/
│   │   ├── consensus-service/
│   │   └── .pre-commit-config.yaml  # Java-specific hooks
│   └── python/            # Python services (FastAPI + AI/ML)
│       ├── src/
│       ├── tests/
│       └── .pre-commit-config.yaml  # Python-specific hooks
│
├── docs/                   # Documentation
│   ├── design/            # Design specifications and assets
│   ├── prd/               # Product requirements documents
│   ├── technical/         # Technical specifications
│   └── changelog/         # Release notes and change logs
├── tools/                  # Development tools and scripts
└── .github/                # GitHub workflows and templates
```

## Getting Started

### Prerequisites

- Node.js 18+
- pnpm 9+ (`npm install -g pnpm`)
- Java 17+
- Maven 3.8+
- Python 3.11+
- uv (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Quick Start

```bash
# Install root dependencies and setup pre-commit
pnpm install
pnpm run setup:precommit

# Frontend development
cd frontend && pnpm install && pnpm dev

# Java backend
cd backend/java && mvn clean package

# Python backend
cd backend/python && uv sync --dev && uv run uvicorn src.main:app --reload
```

### Available Scripts (from root)

| Command | Description |
|---------|-------------|
| `pnpm frontend:dev` | Start frontend dev server |
| `pnpm frontend:build` | Build all frontend apps |
| `pnpm backend:java:build` | Build Java services |
| `pnpm backend:python:dev` | Start Python dev server |
| `pnpm precommit` | Run all pre-commit hooks |

## Architecture Overview

WeNexus follows a microservices architecture with:

- **Frontend**: Next.js applications with TypeScript, managed by Turborepo
- **Backend**: Java services (Spring Boot) for core business logic, Python services (FastAPI) for AI/ML
- **Shared Packages**: Common UI components and utilities across frontend apps

## Pre-commit Hooks

Each technology stack has its own pre-commit configuration:

| Stack | Config Location | Hooks |
|-------|-----------------|-------|
| **Global** | `.pre-commit-config.yaml` | YAML/JSON validation, secrets detection, conventional commits |
| **Frontend** | `frontend/.pre-commit-config.yaml` | ESLint, Prettier, TypeScript |
| **Java** | `backend/java/.pre-commit-config.yaml` | Google Java Format, Checkstyle, SpotBugs |
| **Python** | `backend/python/.pre-commit-config.yaml` | Black, isort, flake8, mypy, Ruff |

## Contributing

[Contributing guidelines will be added]

## License

[License information will be added based on project requirements]
