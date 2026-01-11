# WeNexus Backend

Backend services for WeNexus platform.

## Structure

```
backend/
├── java/           # Java microservices (Spring Boot)
│   ├── core-service/
│   ├── user-service/
│   ├── content-service/
│   └── consensus-service/
└── python/         # Python services (FastAPI)
    ├── src/        # AI/ML and data processing
    └── tests/
```

## Java Backend

### Prerequisites

- Java 17+
- Maven 3.8+

### Commands

```bash
# Build all services
mvn clean package

# Run tests
mvn test

# Start a specific service
mvn spring-boot:run -pl core-service
```

### Pre-commit Hooks

Java-specific hooks in `java/.pre-commit-config.yaml`:

- **Google Java Format** - Code formatting
- **Checkstyle** - Code style validation
- **SpotBugs** - Bug detection (on push)

## Python Backend

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)

### Setup

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --dev
```

### Commands

```bash
# Start development server
uv run uvicorn src.main:app --reload

# Run tests
uv run pytest

# Format and lint code
uv run ruff format .
uv run ruff check --fix .

# Type checking
uv run mypy src/
```

### Pre-commit Hooks

Python-specific hooks in `python/.pre-commit-config.yaml`:

- **Ruff** - Fast linting and formatting (replaces Black, isort, flake8)
- **mypy** - Type checking
