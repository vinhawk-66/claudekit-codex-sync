# Project Roadmap

## v0.1.0 - Initial Release

**Status:** Complete

- [x] Core sync pipeline
- [x] Live + zip source support
- [x] Path normalization
- [x] Config enforcement
- [x] Prompt export
- [x] Dependency bootstrap
- [x] Runtime verification

## v0.2.0 - CLI Redesign + Cleanup

**Status:** Complete

- [x] New CLI surface: `ckc-sync` + backward-compatible `ck-codex-sync`
- [x] 8-flag interface and project-scope default
- [x] Fresh clean flow (`-f`) with safe `.venv` retention
- [x] Symlink-first venv bootstrap optimization
- [x] Registry/backup wiring for managed asset overwrite policy
- [x] Safety hardening (`save_registry` and agent conversion defensive mkdir)
- [x] Expanded test suite to 21 tests (clean target + CLI args)
- [x] Documentation refresh for new CLI contract
- [x] Removed legacy standalone `scripts/` and stale `reports/`

## v0.2.5 - Hooks→Rules + Remove Prompts

**Status:** Complete

- [x] Remove hooks sync (Codex has no hooks API)
- [x] Generate hook-equivalent rules (security-privacy, file-naming, code-quality)
- [x] Remove commands sync (deprecated concept)
- [x] Remove prompt export step (deprecated by OpenAI)
- [x] Update bridge skill for Codex-native routing
- [x] Add syntax adaptations for Claude→Codex patterns
- [x] Add test coverage for rules_generator

## v0.2.6 - Optimization + Safety + Logging

**Status:** Complete

- [x] Remove dead code (`prompt_exporter.py`, `PROMPT_MANIFEST`, `PROMPT_REPLACEMENTS`)
- [x] DRY replacement tables (`_BASE_PATH_REPLACEMENTS` + compose pattern)
- [x] Safety boundary for `--fresh` (reject `/` and `$HOME`)
- [x] Fatal source validation (require `skills/` directory)
- [x] Runtime verifier status differentiation (`ok`/`failed`/`not-found`/`no-venv`)
- [x] Decouple Node deps from Python venv symlink state
- [x] Structured logging (`log_formatter.py`) — 100→18 lines output
- [x] Test coverage expansion (25 → 39 tests: asset sync, safety, verifier, agent converter)

## v0.3.0 - Coverage + Reliability

**Status:** Planned

- [ ] Integration tests for live/zip sync end-to-end paths
- [ ] Add CI matrix for Linux/macOS/WSL behavior
- [ ] Split `path_normalizer.py` into focused modules (<200 LOC)
- [ ] Proper TOML parser for config updates (replace substring checks)
- [ ] Per-file skill sync via checksum (avoid full directory re-copy)

## v0.4.0 - Distribution + Advanced Features

**Status:** Future

- [ ] PyPI distribution (alongside npm)
- [ ] Release automation and changelog workflow
- [ ] Incremental sync / watch mode
- [ ] Customizable model mapping policy
