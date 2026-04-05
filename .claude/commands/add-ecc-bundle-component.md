---
name: add-ecc-bundle-component
description: Workflow command scaffold for add-ecc-bundle-component in wenexus.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-ecc-bundle-component

Use this workflow when working on **add-ecc-bundle-component** in `wenexus`.

## Goal

Adds a new component or configuration file as part of an ECC bundle for wenexus, typically for skills, agents, commands, or configuration.

## Common Files

- `.claude/skills/wenexus/SKILL.md`
- `.agents/skills/wenexus/SKILL.md`
- `.agents/skills/wenexus/agents/openai.yaml`
- `.claude/commands/feature-development.md`
- `.claude/commands/refactoring.md`
- `.claude/commands/feature-development-python-backend-agent.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create or copy a new ECC-related file in the appropriate directory (e.g., .claude/skills/wenexus/, .agents/skills/wenexus/, .claude/commands/, .codex/agents/).
- Commit the file with a message indicating addition to the ECC bundle.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.