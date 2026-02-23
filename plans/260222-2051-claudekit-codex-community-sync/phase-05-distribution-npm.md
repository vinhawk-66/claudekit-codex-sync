# Phase 05: NPM Distribution

## Goal
Ship a clean npm user experience without rewriting core logic.

## Tasks
1. Create Node CLI wrapper package:
   - preflight checks (`python3`, `codex` availability)
   - argument passthrough
   - error mapping with actionable remediation
2. Commands:
   - `sync`
   - `transpile-agents`
   - `benchmark`
   - `verify`
3. Add npm metadata:
   - bin entry
   - semver strategy
   - changelog generation
4. Add smoke tests for `npx` path on Linux/macOS/WSL.

## Deliverables
- Installable npm package runnable via `npx`.
- CLI docs with examples.

## Acceptance Criteria
- `npx <package> sync --help` works on supported environments.
- Wrapper cleanly forwards exit codes from core engine.
- Common failure modes have clear remediation text.

## Risks
- Python missing in user environment.

## Mitigation
- Preflight + auto-detected install hints per OS.
