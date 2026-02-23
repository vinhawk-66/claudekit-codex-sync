# Project Roadmap

## v0.1.0 — Initial Release ✅

**Status:** Complete

- [x] Project structure (modular Python, npm wrapper)
- [x] Dual source support (live directory + zip archive)
- [x] Path normalization (`.claude` → `.codex`)
- [x] Asset sync (agents, commands, rules, scripts)
- [x] Skill sync (54+ skills)
- [x] Agent .md → .toml conversion
- [x] Claude → Codex model mapping
- [x] Multi-agent config enforcement
- [x] Agent registration in config.toml
- [x] Prompt export
- [x] Dependency bootstrap
- [x] Runtime verification
- [x] Basic test suite (11 tests)
- [x] Documentation (README, architecture, code standards)

## v0.2.0 — Quality & Coverage

**Status:** Planned

- [ ] Full test coverage for all 13 modules
- [ ] Integration tests (end-to-end sync flow)
- [ ] Idempotent re-sync (skip unchanged files)
- [ ] `--respect-edits` fully wired (detect user modifications via SHA-256)
- [ ] Proper error messages for common failures
- [ ] `path_normalizer.py` refactor (currently 248 LOC, split conversion out)

## v0.3.0 — Distribution

**Status:** Planned

- [ ] PyPI package (alongside npm)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Versioned releases with changelog
- [ ] Community contribution guide
- [ ] Cross-platform testing (Linux, macOS, WSL)

## v0.4.0 — Advanced Features

**Status:** Future

- [ ] Incremental sync (only changed files)
- [ ] Watch mode (auto-sync on file changes)
- [ ] Custom model mapping config (user-defined model overrides)
- [ ] MCP server migration support
- [ ] Bi-directional sync (Codex → ClaudeKit)
