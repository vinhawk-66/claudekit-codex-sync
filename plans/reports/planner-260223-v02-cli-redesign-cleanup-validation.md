# Validation + Execution Checklist

Date: 2026-02-23  
Plan: `plans/260223-1310-v02-cli-redesign-cleanup/`

## Validation Verdict
Conditionally executable. Use with preflight fixes first.

### Baseline (current repo)
- `PYTHONPATH=src python3 -m pytest tests/ -q` -> 11 passed.
- `python3 -m py_compile src/claudekit_codex_sync/*.py` -> pass.

## Blocking Conflicts (Resolve First)
1. **Agent pipeline mismatch (high)**  
Plan says remove `agents` from assets, but conversion reads only `codex_home/agents`. Current sync writes assets under `codex_home/claudekit/*`. If `agents` removed, agent conversion/registration becomes impossible.  
Refs: `plans/260223-1310-v02-cli-redesign-cleanup/phase-01-delete-dead-code.md:53`, `plans/260223-1310-v02-cli-redesign-cleanup/phase-01-delete-dead-code.md:58`, `src/claudekit_codex_sync/asset_sync_dir.py:21`, `src/claudekit_codex_sync/path_normalizer.py:83`, `src/claudekit_codex_sync/config_enforcer.py:112`.
2. **Rules/CLAUDE removal conflicts with downstream references (high)**  
Plan drops `rules` + `CLAUDE.md`, but generated `AGENTS.md` and path replacements still reference them.  
Refs: `plans/260223-1310-v02-cli-redesign-cleanup/phase-01-delete-dead-code.md:53`, `plans/260223-1310-v02-cli-redesign-cleanup/phase-01-delete-dead-code.md:60`, `templates/agents-md.md:40`, `src/claudekit_codex_sync/constants.py:29`, `src/claudekit_codex_sync/constants.py:68`.
3. **`--force` semantic collision (high)**  
Phase 2 maps `--force` to `include_conflicts`, mixing overwrite semantics with conflict-skill inclusion.  
Refs: `plans/260223-1310-v02-cli-redesign-cleanup/phase-02-cli-redesign.md:114`, `src/claudekit_codex_sync/cli.py:40`, `src/claudekit_codex_sync/asset_sync_dir.py:73`, `src/claudekit_codex_sync/asset_sync_zip.py:90`.
4. **Registry wiring incomplete in plan text (medium)**  
Phase 4 adds `registry`/`force` params to `sync_assets_from_dir`, but phase flow does not require passing these from CLI callsite; backup logic can remain inert.  
Refs: `plans/260223-1310-v02-cli-redesign-cleanup/phase-04-wire-unused-functions.md:39`, `src/claudekit_codex_sync/cli.py:83`.
5. **Phase-order runtime break risk (medium)**  
Phase 2 removes `include_test_deps` call before Phase 3 changes function signature. If implemented separately, bootstrap call breaks.  
Refs: `plans/260223-1310-v02-cli-redesign-cleanup/phase-02-cli-redesign.md:203`, `src/claudekit_codex_sync/dep_bootstrapper.py:17`.
6. **Test count in plan is wrong (low)**  
Plan expects 17 tests after adding 10; actual target should be 21 (11 existing + 10 new).  
Ref: `plans/260223-1310-v02-cli-redesign-cleanup/phase-05-safety-tests-docs.md:190`.

## Operationalized Execution Checklist

### Gate 0: Scope Lock (must pass before coding)
- [ ] Decide asset contract for `agents`, `rules`, `CLAUDE.md` (keep vs remove) and update all dependent docs/templates/replacements consistently.
- [ ] Separate flags: keep `--force` for overwrite behavior only; do not reuse for conflict-skill include.
- [ ] Decide compatibility policy for legacy flags (`--source-mode`, `--skip-verify`, `--skip-agent-toml`, `--include-hooks`, `--respect-edits`).

Dependencies: none.  
Risk: High if skipped (functional regression + broken agent/rules references).

### Phase A: CLI Redesign Skeleton (safe-first)
- [ ] Add new command surface (`ckc-sync` alias) in `package.json` while retaining `ck-codex-sync`.
- [ ] Introduce `clean_target.py` and `-f/--fresh` flow.
- [ ] Wire `register_agents()` call in CLI.
- [ ] Keep bootstrap signature compatibility until Phase B complete (or ship both changes atomically).

Dependencies: Gate 0.  
Risk: Medium (breaking CLI behavior if compatibility policy unclear).

### Phase B: Dependency Bootstrap Symlink
- [ ] Implement symlink-first venv strategy with fallback creation.
- [ ] Ensure broken symlink handling + existing real `.venv` short-circuit.
- [ ] Validate Linux/WSL behavior with dry-run and real run.

Dependencies: Phase A (if CLI flags change), or atomic with Phase A for signature safety.  
Risk: Medium (environment-specific symlink behavior).

### Phase C: Registry + Respect-Edits Wiring
- [ ] Update `sync_assets_from_dir()` to call `maybe_backup()`/`update_entry()`.
- [ ] Pass `registry` and overwrite policy from CLI callsite explicitly.
- [ ] Add defensive mkdir in `save_registry()`.
- [ ] Validate skip/backup/overwrite paths with deterministic fixtures.

Dependencies: Gate 0 flag semantics + Phase A CLI args.  
Risk: High (data-loss risk if overwrite path wrong).

### Phase D: Safety + Tests + Docs
- [ ] Add `tests/test_clean_target.py` (4 tests) and `tests/test_cli_args.py` (6 tests).
- [ ] Correct expected total test count to 21.
- [ ] Update `README.md`, `docs/installation-guide.md`, `docs/codebase-summary.md`, `docs/system-architecture.md` to exact final behavior.
- [ ] Run: `pytest`, `py_compile`, and CLI smoke matrix for both command aliases.

Dependencies: Phases A-C complete.  
Risk: Medium (doc/runtime drift if done early).

### Phase E: Release Gate
- [ ] Confirm no stale references to removed flags/assets.
- [ ] Confirm backward compatibility decision is documented.
- [ ] Package/install smoke: `npm install -g .`, `ckc-sync --help`, `ck-codex-sync --help`.

Dependencies: Phase D complete.  
Risk: Low.

## Risk Notes (Condensed)
- **Data safety:** Overwrite logic currently under-specified; treat as release blocker.
- **Architecture consistency:** Asset contract changes touch constants, templates, docs, runtime behavior; enforce single source of truth.
- **Breaking CLI UX:** Removing flags without transition policy may break existing automation.
- **Cross-platform:** Symlink behavior varies; keep fallback path mandatory.

## Unresolved Questions
1. Should `rules` and `CLAUDE.md` remain first-class synced assets in v0.2, given `templates/agents-md.md` references?
2. Should agent `.md` files be synced to `codex_home/agents` (for conversion) instead of `codex_home/claudekit/agents`, or should conversion read from `claudekit/agents`?
3. Should legacy flags remain temporarily as deprecated aliases, or be removed immediately in v0.2?
