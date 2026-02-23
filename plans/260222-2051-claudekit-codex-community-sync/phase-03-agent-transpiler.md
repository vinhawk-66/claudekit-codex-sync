# Phase 03: Agent Transpiler

## Goal
Convert Claude agent definitions into Codex-compatible role config with predictable behavior.

## Tasks
1. Parse `~/.claude/agents/*.md` frontmatter + body.
2. Build normalization pipeline:
   - path remap (`.claude` -> `.codex` equivalents)
   - remove/translate Claude-only tool semantics
   - preserve behavioral intent in `developer_instructions`
3. Generate Codex role artifacts:
   - `[agents.<role>]` in config
   - `~/.codex/agents/<role>.toml`
4. Support modes:
   - default prefixed roles (`ck-*`)
   - optional built-in override mode
5. Add dry-run diff report for generated roles.

## Deliverables
- Deterministic agent transpilation command.
- Compatibility layer from Claude role semantics to Codex role semantics.

## Acceptance Criteria
- Generated role files pass TOML parse and Codex config validation.
- Default mode does not override `default/worker/explorer` unexpectedly.
- At least 10 common Claude agents transpiled without fatal errors.

## Risks
- Literal translation can create noisy or invalid instructions.

## Mitigation
- Rule-based sanitizer + max-size bounds + warning report for unsupported directives.
