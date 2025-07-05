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
├── apps/                    # Frontend applications
│   ├── web/                # Main web application (React + TypeScript)
│   ├── mobile/             # Mobile application (React Native)
│   └── admin/              # Admin dashboard
├── services/               # Backend services
│   ├── java-backend/       # Java microservices (Spring Boot)
│   └── python-backend/     # Python services (FastAPI, AI/ML)
├── packages/               # Shared libraries
├── docs/                   # Documentation
└── tools/                  # Development tools and scripts
```

### Technology Stack

#### Frontend

- **Web App**: React with TypeScript, Next.js
- **Mobile App**: React Native
- **Admin Dashboard**: React with TypeScript
- **Build Tool**: Turbo (monorepo management)
- **Package Manager**: npm (v9.8.1+)
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
git clone [repository-url]
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

# Set up Java backend
cd services/java-backend
mvn clean install -DskipTests
cd ../..

# Set up Python backend
cd services/python-backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
cd ../..

# Install pre-commit hooks
npx husky install
pre-commit install
pre-commit install --hook-type commit-msg
```

## Development Commands

### Root Level Commands

```bash
# Development
npm run dev              # Start all development servers
npm run build            # Build all applications
npm run test             # Run all tests
npm run lint             # Lint all code
npm run typecheck        # Type check all TypeScript

# Code Quality
npm run format           # Format code with Prettier
npm run format:check     # Check code formatting
npm run precommit        # Run pre-commit hooks manually

# Setup
npm run setup            # Full development setup
npm run setup:precommit  # Setup pre-commit hooks only
```

### Service-Specific Commands

**Java Backend**

```bash
cd services/java-backend
mvn clean install       # Build all services
mvn spring-boot:run      # Run services
mvn test                # Run tests
```

**Python Backend**

```bash
cd services/python-backend
source venv/bin/activate # Activate virtual environment
uvicorn src.main:app --reload  # Start FastAPI server
pytest                  # Run tests
black .                 # Format code
isort .                 # Sort imports
flake8 .                # Lint code
mypy src/               # Type checking
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

- `apps/web/.env.local`
- `services/java-backend/.env`
- `services/python-backend/.env`

### Key Environment Variables

- Database connections (PostgreSQL)
- Redis configuration
- API keys (OpenAI, etc.)
- JWT secrets
- Service URLs

## Testing

### Frontend Testing

```bash
# Run tests for specific app
npm run test --workspace=@wenexus/web
npm run test --workspace=@wenexus/mobile
npm run test --workspace=@wenexus/admin
```

### Backend Testing

```bash
# Java tests
cd services/java-backend && mvn test

# Python tests
cd services/python-backend && pytest
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

Remember: WeNexus aims to connect minds and build consensus - every line of code should reflect this
mission of bringing people together through technology.
