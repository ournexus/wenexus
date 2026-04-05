---
name: feature-development-python-backend-agent
description: Workflow command scaffold for feature-development-python-backend-agent in wenexus.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /feature-development-python-backend-agent

Use this workflow when working on **feature-development-python-backend-agent** in `wenexus`.

## Goal

Implements a new agent or major agent feature in the Python backend, including DDD layering, runtime, repository, facade, and tests.

## Common Files

- `backend/python/src/wenexus/service/agent/*`
- `backend/python/src/wenexus/model/*`
- `backend/python/src/wenexus/repository/model/*`
- `backend/python/src/wenexus/facade/*`
- `backend/python/src/wenexus/main.py`
- `backend/python/tests/unit/service/agent/*`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Add or modify files under src/wenexus/service/agent/[agent_name] (e.g., agent.py, graph.py, state.py, providers/)
- Update or create corresponding model files under src/wenexus/model/ and/or src/wenexus/repository/model/
- Update or create facade entrypoints under src/wenexus/facade/ (e.g., facade/fact_checker.py)
- Update main.py to wire up new agent or capability
- Add or update tests under tests/unit/service/agent/[agent_name]/ or tests/agent/[agent_name]/

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.