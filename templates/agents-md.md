# AGENTS.md

Codex working profile for this workspace, adapted from ClaudeKit rules and workflows.

## Operating Principles

- Follow `YAGNI`, `KISS`, `DRY`.
- Prefer direct, maintainable solutions over speculative abstraction.
- Do not claim completion without evidence (tests, checks, or concrete validation).
- Never use fake implementations just to make tests/build pass.

## Default Workflow

1. Read context first: `README.md` and relevant docs under `./docs/`.
2. For non-trivial work, create/update a plan in `./plans/` before coding.
3. Implement in existing files unless new files are clearly needed.
4. Validate with project compile/lint/test commands.
5. Run code-review mindset before finalizing (bugs, regressions, missing tests first).
6. Update docs when behavior, architecture, contracts, or operations change.

## Quality Gates

- Handle edge cases and error paths explicitly.
- Keep security and performance implications visible in design decisions.
- Keep code readable and intention-revealing; add comments only when needed for non-obvious logic.

## Documentation Rules

- `./docs` is the source of truth for project docs.
- Keep docs synchronized with code and implementation decisions.
- When summarizing/reporting, be concise and list unresolved questions at the end.

## Skill Usage

- Activate relevant skills intentionally per task.
- For legacy ClaudeKit command intents (`/ck-help`, `/coding-level`, `/ask`, `/docs/*`, `/journal`, `/watzup`), use `$claudekit-command-bridge`.

## Reference Material (Imported from ClaudeKit)

- `~/.codex/claudekit/CLAUDE.md`
- `~/.codex/claudekit/rules/development-rules.md`
- `~/.codex/claudekit/rules/primary-workflow.md`
- `~/.codex/claudekit/rules/orchestration-protocol.md`
- `~/.codex/claudekit/rules/documentation-management.md`
- `~/.codex/claudekit/rules/team-coordination-rules.md`
