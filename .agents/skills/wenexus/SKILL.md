```markdown
# wenexus Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill teaches you how to contribute to the `wenexus` codebase, a Python backend (with some frontend) project following Domain-Driven Design (DDD) principles. You'll learn the project's coding conventions, commit patterns, and the main workflows for adding features, endpoints, refactoring, and maintaining code quality. The guide also covers how to extend the frontend agent UI and how to write and organize tests.

---

## Coding Conventions

### File Naming

- **Python files:** Use `snake_case.py` (e.g., `fact_checker.py`, `main.py`)
- **Frontend files:** Use standard React/TypeScript conventions

### Import Style

- **Alias imports** are preferred:
  ```python
  import wenexus.service.agent.graph as agent_graph
  from wenexus.model.user import UserModel as User
  ```

### Export Style

- **Named exports**:
  ```python
  # In src/wenexus/service/agent/agent.py
  class FactCheckerAgent:
      ...
  ```

### Commit Messages

- **Conventional commits** with these prefixes:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `refactor:` for code restructuring
  - `chore:` for maintenance
  - `docs:` for documentation
  - `ci:` for continuous integration
- **Example:**  
  ```
  feat(agent): add fact checker agent with async support
  ```

---

## Workflows

### Feature Development: Python Backend Agent

**Trigger:** When adding a new agent, agent capability, or major agent refactor to the backend  
**Command:** `/new-agent-feature`

1. Add or modify files under `src/wenexus/service/agent/[agent_name]` (e.g., `agent.py`, `graph.py`, `state.py`, `providers/`)
2. Update or create corresponding model files under `src/wenexus/model/` and/or `src/wenexus/repository/model/`
3. Update or create facade entrypoints under `src/wenexus/facade/` (e.g., `facade/fact_checker.py`)
4. Update `main.py` to wire up the new agent or capability
5. Add or update tests under `tests/unit/service/agent/[agent_name]/` or `tests/agent/[agent_name]/`

**Example:**
```python
# src/wenexus/service/agent/fact_checker/agent.py
class FactCheckerAgent:
    def check(self, statement: str) -> bool:
        ...
```

---

### API Endpoint Addition or Major Extension

**Trigger:** When exposing a new API endpoint (especially for agents or LangGraph compatibility)  
**Command:** `/new-api-endpoint`

1. Create or update router files under `src/wenexus/facade/[api_name]/routers/`
2. Add or update API models under `src/wenexus/model/` or `src/wenexus/facade/model/`
3. Implement or update service logic under `src/wenexus/service/[api_name]/`
4. Wire up the new endpoint in `main.py` or the facade main router
5. Add or update tests for the new endpoint

**Example:**
```python
# src/wenexus/facade/fact_checker/routers/fact_checker_router.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/fact-check")
def fact_check(request: FactCheckRequest):
    ...
```

---

### Python Backend Refactor: DDD or Async

**Trigger:** When restructuring backend code for DDD or converting sync code to async  
**Command:** `/refactor-ddd-async`

1. Move or rename files to the new DDD structure under `service/`, `model/`, `facade/`
2. Update imports and wiring in `main.py`
3. Refactor function signatures and logic for `async/await` if needed
4. Update or migrate corresponding tests
5. Update documentation if architecture changes

**Example:**
```python
# Before
def get_agent(...):
    ...

# After (async)
async def get_agent(...):
    ...
```

---

### Python Type Checking and Linting Fix

**Trigger:** When resolving type/lint errors after a feature, refactor, or dependency upgrade  
**Command:** `/fix-type-lint`

1. Update type annotations in affected Python files (`service`, `model`, `facade`, `repository`)
2. Update `pyproject.toml` config for `mypy` or `ruff`
3. Fix or suppress linter warnings (e.g., `UP042`, `UP043`)
4. Commit with `fix:` or `chore:` message referencing the type/lint issue

**Example:**
```python
def process_agent(agent: "Agent") -> None:
    ...
```

---

### Frontend Agent UI Feature

**Trigger:** When adding or improving agent chat features in the frontend  
**Command:** `/new-agent-ui-feature`

1. Add or update a page under `src/app/[locale]/(landing)/agent/`
2. Implement or modify React components under `components/agent/components/`
3. Add or update hooks and providers under `components/agent/hooks/` and `components/agent/providers/`
4. Update types in `components/agent/types/`
5. Update `package.json` and `pnpm-lock.yaml` for new dependencies
6. Update auth config if needed

**Example:**
```tsx
// src/components/agent/components/AgentChat.tsx
export function AgentChat() {
  // React component logic
}
```

---

## Testing Patterns

- **Test files:** Follow the pattern `*.test.ts` (mainly for frontend/TypeScript)
- **Backend tests:** Located under `tests/unit/service/agent/[agent_name]/` and `tests/agent/[agent_name]/`
- **Framework:** Not explicitly detected; follow Python or JS/TS conventions as appropriate
- **Example:**  
  ```
  backend/python/tests/unit/service/agent/fact_checker/test_agent.py
  ```

---

## Commands

| Command               | Purpose                                                      |
|-----------------------|--------------------------------------------------------------|
| /new-agent-feature    | Start a new backend agent or major agent feature             |
| /new-api-endpoint     | Add a new API endpoint or major API extension                |
| /refactor-ddd-async   | Refactor backend code for DDD or async/await                 |
| /fix-type-lint        | Fix type errors or linter warnings in backend Python files   |
| /new-agent-ui-feature | Implement or extend the frontend agent chat UI               |
```
