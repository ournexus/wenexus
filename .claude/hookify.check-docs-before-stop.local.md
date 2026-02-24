---
name: check-docs-before-stop
enabled: true
event: stop
pattern: .*
action: block
---

**Stop! Documentation check required before finishing.**

Before completing this task, you MUST verify the following:

### 1. Documentation that may need updating

Check if any of these were affected by your changes:

- [ ] `docs/technical/` - Does this commit need a corresponding technical doc (`YYMMDD-description.md`)?
- [ ] Module `__init__.py` or `index.ts` - Did you update module docstrings/JSDoc for changed modules?
- [ ] `package.json` - Did you update the `description` field if functionality changed?
- [ ] Directory `README.md` - Did you update README for directories where files changed?

### 2. Unnecessary documentation that should be deleted

Check if you accidentally created any of these:

- [ ] Summary/overview/guide documents (e.g., `xxx-summary.md`, `xxx-overview.md`, `xxx-guide.md`)
- [ ] Duplicate documentation files that overlap with existing docs
- [ ] Documentation in `docs/theory/`, `docs/prd/`, or `docs/design/` (these are read-only for AI)
- [ ] Any `.md` files not explicitly requested by the user

### Action required

Review your changes with `git diff` and `git status`, then confirm:

1. All necessary documentation has been updated
2. No unnecessary documentation was created
3. If issues found, fix them before stopping
