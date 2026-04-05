---
name: add-ecc-bundle-component
description: Workflow command scaffold for add-ecc-bundle-component in wenexus.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-ecc-bundle-component

Use this workflow when working on **add-ecc-bundle-component** in `wenexus`.

## Goal

Adds a new component as part of the wenexus-conventions ECC bundle, typically by creating a new configuration, skill, agent, or command file in a structured directory.

## Common Files

- `.claude/skills/wenexus/SKILL.md`
- `.agents/skills/wenexus/SKILL.md`
- `.agents/skills/wenexus/agents/openai.yaml`
- `.claude/ecc-tools.json`
- `.claude/identity.json`
- `.codex/config.toml`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create a new file in a relevant subdirectory (e.g., .claude/skills/wenexus/, .agents/skills/wenexus/, .codex/agents/)
- Name the file according to the component type (e.g., SKILL.md, .toml, .yaml, .json, .md)
- Commit the new file with a standardized commit message referencing the ECC bundle

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.