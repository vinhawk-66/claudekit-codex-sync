# Phase 1 — Delete Dead Code + Trim Constants

## Overview
- Priority: P0
- Status: [x] Complete
- Estimated: 10 min

## What to Delete

### `scripts/` directory (1782 LOC — ENTIRE DIR)

```bash
rm -rf scripts/
```

All 4 files are superseded by `src/claudekit_codex_sync/`:
- `claudekit-sync-all.py` (1150 LOC) → `cli.py` + all modules
- `normalize-claudekit-for-codex.sh` (261) → `path_normalizer.py`
- `export-claudekit-prompts.sh` (221) → `prompt_exporter.py`
- `bootstrap-claudekit-skill-scripts.sh` (150) → `dep_bootstrapper.py`

### `reports/` directory

```bash
rm -rf reports/
```

Contains only `brainstorm-260222-2051-claudekit-codex-community-sync.md` — old brainstorm, no longer relevant.

## Code Changes

### [MODIFY] `src/claudekit_codex_sync/constants.py`

**Current (lines 5-17):**
```python
ASSET_DIRS = {"agents", "commands", "output-styles", "rules", "scripts"}
ASSET_FILES = {
    "CLAUDE.md",
    ".ck.json",
    ".ckignore",
    ".env.example",
    ".mcp.json.example",
    "settings.json",
    "metadata.json",
    "statusline.cjs",
    "statusline.sh",
    "statusline.ps1",
}
```

**Replace with:**
```python
ASSET_DIRS = {"commands", "output-styles", "scripts"}
ASSET_FILES = {".env.example"}
```

**Rationale:**
- `agents` → already handled by `convert_agents_md_to_toml()` in `path_normalizer.py`
- `rules` → Codex uses `config.toml` + `AGENTS.md`, not rules dir
- `CLAUDE.md` → replaced by `AGENTS.md`
- `.ck.json`, `.ckignore`, `.mcp.json.example` → ClaudeKit internal metadata
- `settings.json`, `metadata.json` → ClaudeKit UI config
- `statusline.cjs/sh/ps1` → Claude CLI statusbar, not applicable to Codex

## Verification

```bash
# After deletion
ls scripts/ 2>/dev/null && echo "FAIL: scripts/ still exists" || echo "PASS"
ls reports/ 2>/dev/null && echo "FAIL: reports/ still exists" || echo "PASS"

# Verify constants
python3 -c "
from src.claudekit_codex_sync.constants import ASSET_DIRS, ASSET_FILES
assert 'agents' not in ASSET_DIRS, 'agents should be removed'
assert 'rules' not in ASSET_DIRS, 'rules should be removed'
assert len(ASSET_FILES) == 1, f'Expected 1 file, got {len(ASSET_FILES)}'
print('PASS: constants trimmed')
"

# Run tests
PYTHONPATH=src python3 -m pytest tests/ -v
```

## Todo
- [x] `rm -rf scripts/ reports/`
- [x] Edit `constants.py`: trim `ASSET_DIRS` + `ASSET_FILES`
- [x] Run tests
