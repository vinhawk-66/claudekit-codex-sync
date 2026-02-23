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

## v0.3.0 - Coverage + Reliability

**Status:** Planned

- [ ] Increase unit coverage for sync modules not yet directly tested
- [ ] Add integration tests for live/zip sync end-to-end paths
- [ ] Add CI matrix for Linux/macOS/WSL behavior
- [ ] Improve validation and user-facing error messages

## v0.4.0 - Distribution + Advanced Features

**Status:** Future

- [ ] PyPI distribution (alongside npm)
- [ ] Release automation and changelog workflow
- [ ] Incremental sync / watch mode
- [ ] Customizable model mapping policy
