# WeNexus - The Consensus Amplifier

## Project Overview

WeNexus is a comprehensive platform designed to bridge information gaps and create meaningful
connections in an age of information overload and polarizing echo chambers. This is a monorepo
containing all WeNexus applications and services.

**Key Concept**: WeNexus is not just another network; it's a Nexus - a central point where We, as a
society, can finally connect, understand, and agree.

## Architecture

### Monorepo Structure

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
├── tools/                  # Development tools and scripts
└── .pre-commit-config.yaml # Global hooks (YAML, secrets, commits)
```

### Technology Stack

#### Frontend

- **Web App**: React with TypeScript, Next.js
- **Mobile App**: React Native
- **Admin Dashboard**: React with TypeScript
- **Build Tool**: Turbo (monorepo management)
- **Package Manager**: pnpm (v9.0.0+)
- **Node.js**: >=18.0.0

#### Backend Services

**Java Backend (Spring Boot Microservices)**

- **Framework**: Spring Boot 3.1.5, Spring Cloud 2022.0.4
- **Java Version**: 17+
- **Build Tool**: Maven
- **Services**:
  - `core-service`: Core business logic
  - `user-service`: User management
  - `content-service`: Content management
  - `consensus-service`: Consensus building algorithms

**Python Backend (AI/ML Services)**

- **Framework**: FastAPI
- **Python Version**: 3.11+
- **Key Dependencies**:
  - AI/ML: transformers, torch, sentence-transformers, langchain, openai
  - Data: numpy, pandas, scikit-learn
  - Database: SQLAlchemy, asyncpg, alembic
  - Async: uvicorn, celery, redis
  - Auth: python-jose, passlib
  - Monitoring: structlog, prometheus-client

## Development Environment

### Prerequisites

- Node.js 18+
- Java 17+
- Python 3.11+
- Maven (for Java services)
- npm 8.0.0+

### Quick Setup

```bash
# Clone the repository
git clone git@github.com:your-org/wenexus.git
cd wenexus

# Run the setup script
./tools/scripts/setup-dev.sh

# This script will:
# 1. Install Node.js dependencies
# 2. Set up Java backend (mvn clean install)
# 3. Set up Python backend (virtual environment + dependencies)
# 4. Install pre-commit hooks
# 5. Create environment files
# 6. Build shared packages
```

### Manual Setup

```bash
# Install root dependencies
npm install

# Set up frontend
cd frontend
pnpm install
cd ..

# Set up Java backend
cd backend/java
mvn clean install -DskipTests
cd ../..

# Set up Python backend (using uv)
cd backend/python
uv sync --dev
cd ../..

# Install pre-commit hooks
npx husky install
pre-commit install
pre-commit install --hook-type commit-msg
```

## Development Commands

### Root Level Commands

```bash
# Frontend
npm run frontend:dev     # Start frontend dev server
npm run frontend:build   # Build all frontend apps
npm run frontend:lint    # Lint frontend code
npm run frontend:test    # Run frontend tests

# Backend
npm run backend:java:build   # Build Java services
npm run backend:java:test    # Run Java tests
npm run backend:python:dev   # Start Python dev server
npm run backend:python:test  # Run Python tests

# Code Quality
npm run precommit        # Run pre-commit hooks manually

# Setup
npm run setup            # Full development setup
npm run setup:precommit  # Setup pre-commit hooks only
```

### Service-Specific Commands

**Frontend**

```bash
cd frontend
pnpm dev                # Start all apps in dev mode
pnpm build              # Build all apps
pnpm lint               # Lint all code
pnpm typecheck          # Type check TypeScript
```

**Java Backend**

```bash
cd backend/java
mvn clean install       # Build all services
mvn spring-boot:run -pl core-service  # Run specific service
mvn test                # Run tests
```

**Python Backend**

```bash
cd backend/python
uv run uvicorn src.main:app --reload  # Start FastAPI server
uv run pytest                         # Run tests
uv run ruff format .                  # Format code
uv run ruff check --fix .             # Lint code
uv run mypy src/                      # Type checking
```

## Code Quality & Standards

### Pre-commit Hooks

The project uses comprehensive pre-commit hooks for code quality:

- **Code Formatting**: Prettier (JS/TS), Black (Python)
- **Linting**: ESLint (JS/TS), Flake8 (Python)
- **Type Checking**: TypeScript, MyPy
- **Security**: Secret detection, dependency scanning
- **Brand Consistency**: WeNexus naming conventions
- **Custom Checks**: No console.log in production, TypeScript exports

### Code Style

**TypeScript/JavaScript**

- Prettier formatting (2 spaces, 80 chars, single quotes)
- ESLint with Next.js and TypeScript rules
- No `console.log` in production code
- Explicit return types for exported functions

**Python**

- Black formatting (88 characters)
- isort for import sorting
- flake8 for linting
- mypy for type checking
- All public functions must have type annotations

**Java**

- Google Java Format
- Google Java Style Guide
- Javadoc for all public methods
- Optional for nullable values

### Commit Convention

Uses Conventional Commits:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types**: feat, fix, docs, style, refactor, perf, test, ci, chore **Scopes**: web, mobile, admin,
api, ai, auth, ui, docs

## Environment Configuration

### Environment Files

Create these files from examples (done automatically by setup script):

- `frontend/apps/web/.env.local`
- `backend/java/.env`
- `backend/python/.env`

### Key Environment Variables

- Database connections (PostgreSQL)
- Redis configuration
- API keys (OpenAI, etc.)
- JWT secrets
- Service URLs

## Testing

### Frontend Testing

```bash
cd frontend

# Run all tests
pnpm test

# Run tests for specific app
pnpm --filter @wenexus/web test
pnpm --filter @wenexus/mobile test
pnpm --filter @wenexus/admin test
```

### Backend Testing

```bash
# Java tests
cd backend/java && mvn test

# Python tests
cd backend/python && uv run pytest
```

### Test Coverage Requirements

- Minimum 80% code coverage
- Integration tests for core user flows
- Unit tests for all new features

## Deployment

### Build Process

```bash
npm run build           # Build all applications
```

### CI/CD Pipeline

- **GitHub Actions**: `.github/workflows/ci-cd.yml`
- **Stages**: lint → typecheck → test → build → security scan → deploy
- **Environments**: staging → production
- **Security**: Trivy vulnerability scanning

## Documentation

### Key Documentation Locations

- `docs/prd/`: Product requirements
- `docs/technical/`: Technical specifications
- `docs/design/`: Design assets and guidelines
- `docs/changelog/`: Release notes

### API Documentation

- Java services: Spring Boot Actuator + Swagger
- Python services: FastAPI automatic documentation

## Troubleshooting

### Common Issues

1. **Pre-commit failures**: Run `pre-commit clean && pre-commit install`
2. **Node.js dependencies**: Delete `node_modules` and run `npm install`
3. **Java build issues**: Ensure Java 17+ is installed and JAVA_HOME is set
4. **Python virtual environment**: Recreate with `python3 -m venv venv`

### Getting Help

- Check documentation in `docs/` directory
- Review existing code patterns
- Consult team coding standards in `docs/technical/coding-standards/`

## Project Philosophy

WeNexus is built on the principle of consensus amplification - helping people find common ground in
an increasingly polarized world. The codebase reflects this through:

- **Collaborative Architecture**: Microservices that work together
- **Inclusive Design**: Accessible and user-friendly interfaces
- **Transparent Process**: Open development practices and documentation
- **Quality Focus**: Comprehensive testing and code review

## Security Considerations

- **Secret Management**: Never commit secrets; use environment variables
- **Input Validation**: Validate all user inputs
- **Authentication**: JWT-based auth with proper expiration
- **Dependencies**: Regular security audits and updates
- **Privacy**: GDPR/privacy-compliant data handling

## Review & Commit Standards

### Development Workflow with Smart Fix

WeNexus uses an intelligent code quality system that automatically fixes issues and guides the
commit process:

#### 1. Code Development

- Write code following project conventions
- Use meaningful variable names and clear logic
- Add appropriate comments for complex business logic
- Ensure proper error handling and edge cases

#### 2. Pre-Commit Quality Checks

The project uses **layered pre-commit hooks**:

| Layer | Config Location | Hooks |
|-------|-----------------|-------|
| **Global** | `.pre-commit-config.yaml` | YAML/JSON validation, secrets detection, conventional commits |
| **Frontend** | `frontend/.pre-commit-config.yaml` | ESLint, Prettier, TypeScript |
| **Java** | `backend/java/.pre-commit-config.yaml` | Google Java Format, Checkstyle |
| **Python** | `backend/python/.pre-commit-config.yaml` | Black, isort, flake8, mypy |

```bash
# Automatic workflow when committing:
git add .
git commit -m "feat(web): add user authentication"

# Smart Fix automatically:
# 1. Formats staged files (Prettier/Black/isort)
# 2. Re-stages fixed files
# 3. Runs pre-commit hooks
```

#### 3. Review Standards

Before committing, ensure:

- [ ] **Functionality**: Code works as intended
- [ ] **Tests**: Adequate test coverage (minimum 80%)
- [ ] **Documentation**: Updated relevant docs
- [ ] **Performance**: No obvious performance regressions
- [ ] **Security**: No sensitive data or vulnerabilities
- [ ] **Accessibility**: UI changes meet accessibility standards

#### 4. Commit Message Standards

Follow Conventional Commits format:

```bash
# Format
<type>(<scope>): <description>

# Examples
feat(web): add user profile management
fix(api): resolve authentication token expiry
docs(readme): update setup instructions
style(ui): improve button hover states
refactor(auth): extract validation logic
test(user): add integration tests for signup
```

**Valid Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `ci`, `chore` **Valid
Scopes**: `web`, `mobile`, `admin`, `api`, `ai`, `auth`, `ui`, `docs`

#### 5. Manual Override (Emergency Only)

```bash
# Skip all hooks (use sparingly)
git commit --no-verify -m "emergency: critical hotfix"

# Run smart fix manually
./tools/scripts/smart-fix.sh
```

#### 6. Post-Commit Verification

After committing:

- [ ] Verify CI/CD pipeline passes
- [ ] Check deployment to staging environment
- [ ] Confirm no breaking changes introduced
- [ ] Update related documentation if needed

#### 7. Code Review Guidelines

When reviewing PRs:

- **Functionality**: Does it solve the intended problem?
- **Code Quality**: Is it readable and maintainable?
- **Performance**: Any performance implications?
- **Security**: Are there security considerations?
- **Testing**: Adequate test coverage?
- **Documentation**: Clear and up-to-date?

#### 8. Troubleshooting Pre-commit

```bash
# Clean and reinstall hooks
pre-commit clean && pre-commit install

# Run hooks manually on all files
pre-commit run --all-files

# Run specific hook
pre-commit run eslint --all-files
```

Remember: WeNexus aims to connect minds and build consensus - every line of code should reflect this
mission of bringing people together through technology.
