# Codebase Summary

## Overview

**claudekit-codex-sync** bridges ClaudeKit (`~/.claude/`) to Codex CLI (`.codex/` project scope by default, optional global `~/.codex/`) by syncing skills, assets, prompts, and runtime defaults.

## Stats

| Component | Files | Purpose |
|---|---|---|
| `src/claudekit_codex_sync/` | 14 | Core Python sync modules |
| `templates/` | 6 | Generated content templates |
| `tests/` | 4 | pytest suite |
| `bin/` | 2 | npm CLI entry points |

## Module Map

### Core Orchestration

- **`cli.py`** — Main entry point with 8-flag interface (`-g`, `-f`, `--force`, `--zip`, `--source`, `--mcp`, `--no-deps`, `-n`).
- **`clean_target.py`** — Fresh-sync cleaner for `--fresh` (preserves `skills/.venv`).

### Source Resolution

- **`source_resolver.py`** — Live source discovery and zip source lookup.

### Asset & Skill Sync

- **`asset_sync_dir.py`** — Live sync for assets and skills with registry-aware overwrite/backup behavior for managed assets.
- **`asset_sync_zip.py`** — Zip-based sync path.

### Normalization & Conversion

- **`path_normalizer.py`** — `.claude` path rewrites, copywriting script patch, agent markdown-to-TOML conversion.
- **`constants.py`** — Replacement patterns, model mapping, asset allowlists.

### Config & Prompting

- **`config_enforcer.py`** — `config.toml` enforcement + agent registration.
- **`prompt_exporter.py`** — Prompt generation.
- **`bridge_generator.py`** — Bridge skill generation.

### Runtime Support

- **`dep_bootstrapper.py`** — Symlink-first dependency bootstrap (`~/.claude/skills/.venv` -> `codex_home/skills/.venv` fallback to create/install).
- **`runtime_verifier.py`** — Runtime health checks.
- **`sync_registry.py`** — Sync registry and user-edit detection helpers.
- **`utils.py`** — Shared helpers and `SyncError`.

## Data Flow

```
Source (~/.claude/ or zip)
    ↓
source_resolver.py
    ↓
asset_sync_dir.py / asset_sync_zip.py
    ↓
path_normalizer.py
    ↓
config_enforcer.py
    ↓
prompt_exporter.py
    ↓
dep_bootstrapper.py
    ↓
runtime_verifier.py
    ↓
Configured Codex home (.codex project scope or ~/.codex global)
```

## Test Coverage

| File | Tests |
|---|---|
| `tests/test_config_enforcer.py` | 4 |
| `tests/test_path_normalizer.py` | 7 |
| `tests/test_clean_target.py` | 4 |
| `tests/test_cli_args.py` | 6 |
| **Total** | **21** |
