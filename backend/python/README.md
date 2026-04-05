# WeNexus Python Backend

Python services for WeNexus platform - AI/ML and data processing.

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)

## Setup

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies (core + dev)
uv sync --dev

# Install with ML dependencies (optional, requires compatible platform)
uv sync --dev --extra ml
```

## Development

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

## Project Structure

```
backend/python/
├── src/                    # Source code
│   ├── main.py            # FastAPI application entry
│   ├── api/               # API routes
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   └── utils/             # Utilities
├── tests/                  # Test files
├── alembic/               # Database migrations
└── pyproject.toml         # Project configuration
```

## Optional Dependencies

- **ml**: AI/ML packages (torch, transformers, langchain, etc.)
  - Note: Some ML packages may not be available on all platforms

```bash
# Install with ML dependencies
uv sync --dev --extra ml
```
