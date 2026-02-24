# Codebase Summary

## Overview

**claudekit-codex-sync** bridges ClaudeKit (`~/.claude/`) to Codex CLI (`.codex/` project scope by default, optional global `~/.codex/`) by syncing skills, assets, and runtime defaults.

## Stats

| Component | Files | Purpose |
|---|---|---|
| `src/claudekit_codex_sync/` | 16 | Core Python sync modules |
| `templates/` | 9 | Generated content templates |
| `tests/` | 10 | pytest suite (39 tests) |
| `bin/` | 2 | npm CLI entry points |

## Module Map

### Core Orchestration

- **`cli.py`** (279 LOC) — Main entry point, 8-flag interface, orchestrates 7-step pipeline, uses `log_formatter` for structured output.
- **`clean_target.py`** (69 LOC) — Fresh-sync cleaner (`--fresh`). Safety guard rejects `/` and `$HOME` as codex_home.
- **`log_formatter.py`** (103 LOC) — Structured CLI output with ANSI color, TTY detection, `NO_COLOR` support.

### Source Resolution

- **`source_resolver.py`** (86 LOC) — Live source discovery and zip source lookup. Fatal when `skills/` missing.

### Asset & Skill Sync

- **`asset_sync_dir.py`** (172 LOC) — Live sync for assets, agents, skills. Registry-aware overwrite/backup. Silent operation (returns counts only).
- **`asset_sync_zip.py`** (150 LOC) — Zip-based sync path.

### Normalization & Conversion

- **`path_normalizer.py`** (255 LOC) — `.claude` path rewrites, copywriting script patch, agent `.md`→`.toml` conversion.
- **`constants.py`** (78 LOC) — `_BASE_PATH_REPLACEMENTS` (shared base), model mapping, asset allowlists. DRY composition pattern.

### Config & Rules

- **`config_enforcer.py`** (140 LOC) — `config.toml` enforcement + agent registration.
- **`rules_generator.py`** (32 LOC) — Hook-equivalent rules from templates (security-privacy, file-naming, code-quality).
- **`bridge_generator.py`** (34 LOC) — Bridge skill generation for Codex-native routing.

### Runtime Support

- **`dep_bootstrapper.py`** (113 LOC) — Symlink-first venv bootstrap. Node deps run independently of Python venv state.
- **`runtime_verifier.py`** (47 LOC) — Runtime health checks with distinct status: `ok`/`failed`/`not-found`/`no-venv`.
- **`sync_registry.py`** (77 LOC) — Sync registry and user-edit detection via SHA-256 checksums.
- **`utils.py`** (129 LOC) — Shared helpers and `SyncError`.

## Data Flow

```
Source (~/.claude/ or zip)
    ↓
source_resolver.py (validate: skills/ must exist)
    ↓
asset_sync_dir.py / asset_sync_zip.py
    ↓
path_normalizer.py (rewrite + .md→.toml convert)
    ↓
rules_generator.py (hook→rules)
    ↓
config_enforcer.py + bridge_generator.py
    ↓
dep_bootstrapper.py (Python symlink + Node deps)
    ↓
runtime_verifier.py
    ↓
log_formatter.py → structured terminal output
    ↓
Configured Codex home (.codex/ or ~/.codex/)
```

## Test Coverage

| File | Tests | Coverage |
|---|---|---|
| `test_asset_sync_dir.py` | 6 | copy, idempotent, agents, dry-run, skills, exclusion |
| `test_agent_converter.py` | 3 | md→toml, sandbox, no-frontmatter |
| `test_safety_guards.py` | 3 | reject root, reject home, accept normal |
| `test_runtime_verifier.py` | 2 | dry-run, empty codex_home |
| `test_path_normalizer.py` | 7 | path replacement patterns |
| `test_config_enforcer.py` | 4 | multi_agent flag enforcement |
| `test_clean_target.py` | 5 | cleanup + venv retention |
| `test_cli_args.py` | 6 | argument parsing |
| `test_rules_generator.py` | 3 | rule generation + idempotency |
| **Total** | **39** | |
