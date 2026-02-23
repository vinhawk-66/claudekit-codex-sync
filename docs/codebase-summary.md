# Codebase Summary

## Overview

**claudekit-codex-sync** bridges ClaudeKit (`~/.claude/`) to Codex CLI (`~/.codex/`) by syncing skills, agents, prompts, and configuration. Written primarily in Python with a Node.js CLI wrapper.

## Stats

| Component | Files | LOC | Purpose |
|---|---|---|---|
| `src/claudekit_codex_sync/` | 13 | ~1500 | Core Python modules |
| `templates/` | 5 | ~280 | Generated file templates |
| `tests/` | 2 | ~106 | pytest-based test suite |
| `scripts/` | 4 | ~1780 | Legacy standalone scripts |
| `bin/` | 2 | ~20 | npm CLI entry point |

## Module Map

### Core Orchestration

- **`cli.py`** (199 LOC) — Main entry point. Parses args, coordinates all sync phases, outputs JSON summary. Supports `live` (directory) and `zip` source modes.

### Source Resolution

- **`source_resolver.py`** (78 LOC) — Detects ClaudeKit source: `~/.claude/` for live mode, finds latest zip for zip mode. Validates source has required structure.

### Asset Sync

- **`asset_sync_dir.py`** (125 LOC) — Copies assets and skills from a live `~/.claude/` directory to `~/.codex/`. Handles `ASSET_DIRS` (agents, commands, rules, scripts) and `ASSET_FILES`.
- **`asset_sync_zip.py`** (140 LOC) — Same as above but from a ClaudeKit export zip file.

### Path Normalization

- **`path_normalizer.py`** (248 LOC) — Rewrites `.claude` → `.codex` paths in all synced files. Also converts ClaudeKit agent `.md` files (with YAML frontmatter) to Codex `.toml` format with correct model mapping.
- **`constants.py`** (104 LOC) — All replacement patterns (`SKILL_MD_REPLACEMENTS`, `AGENT_TOML_REPLACEMENTS`, `CLAUDE_SYNTAX_ADAPTATIONS`), model mapping tables, and read-only role sets.

### Configuration

- **`config_enforcer.py`** (140 LOC) — Ensures `config.toml` has correct structure, enforces `multi_agent` + `child_agents_md` feature flags, auto-registers `[agents.*]` sections from TOML files.

### Prompt & Bridge

- **`prompt_exporter.py`** (89 LOC) — Exports ClaudeKit prompts to Codex-compatible format.
- **`bridge_generator.py`** (33 LOC) — Creates a bridge skill in `~/.codex/skills/claudekit-command-bridge/`.

### Support

- **`dep_bootstrapper.py`** (73 LOC) — Installs Python/Node dependencies for skills that require them.
- **`runtime_verifier.py`** (32 LOC) — Verifies synced environment health (codex help, copywriting, prompt count, skill count).
- **`sync_registry.py`** (77 LOC) — SHA-256 checksum registry for tracking synced files and detecting user edits.
- **`utils.py`** (130 LOC) — Shared utilities: `apply_replacements()`, `load_template()`, `write_text_if_changed()`, `SyncError`.

## Data Flow

```
Source (~/.claude/ or zip)
    ↓
source_resolver.py → detect source type
    ↓
asset_sync_dir/zip.py → copy agents, skills, commands
    ↓
path_normalizer.py → rewrite paths + convert .md→.toml agents
    ↓
config_enforcer.py → update config.toml + register agents
    ↓
prompt_exporter.py → generate prompt files
    ↓
dep_bootstrapper.py → install skill dependencies
    ↓
runtime_verifier.py → health check
    ↓
Output: ~/.codex/ fully configured for Codex CLI
```

## Test Coverage

| File | Tests | Coverage |
|---|---|---|
| `config_enforcer.py` | 4 | Feature flag enforcement |
| `path_normalizer.py` | 7 | Path replacement patterns |
| **Total** | **11** | Core functionality |

Untested modules (need coverage): `cli.py`, `asset_sync_dir.py`, `asset_sync_zip.py`, `source_resolver.py`, `prompt_exporter.py`, `dep_bootstrapper.py`, `runtime_verifier.py`, `sync_registry.py`, `bridge_generator.py`, `utils.py`.
