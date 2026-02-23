# Phase 5 — Safety Fixes + Tests + Docs

## Overview
- Priority: P1
- Status: [x] Implemented (release ops pending)
- Estimated: 30 min

## Code Changes

### [MODIFY] `src/claudekit_codex_sync/path_normalizer.py`

**Add defensive mkdir in `convert_agents_md_to_toml()` (after line ~113):**

```python
def convert_agents_md_to_toml(*, codex_home: Path, dry_run: bool) -> int:
    """Convert ClaudeKit agent .md files to Codex .toml format."""
    from .constants import (
        CLAUDE_MODEL_REASONING_EFFORT,
        CLAUDE_TO_CODEX_MODELS,
        READ_ONLY_AGENT_ROLES,
    )

    agents_dir = codex_home / "agents"
    if not agents_dir.exists():
        return 0

    # Defensive: ensure target dir exists for writing .toml
    if not dry_run:
        agents_dir.mkdir(parents=True, exist_ok=True)

    # ... rest unchanged
```

### [NEW] `tests/test_clean_target.py`

```python
"""Tests for clean_target module."""

import json
from pathlib import Path

from claudekit_codex_sync.clean_target import clean_target


def test_clean_removes_agents(tmp_path: Path):
    """Clean removes agents dir."""
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "planner.toml").write_text("model = 'test'")
    (agents / "researcher.toml").write_text("model = 'test'")

    removed = clean_target(tmp_path, dry_run=False)
    assert not agents.exists()
    assert removed >= 2


def test_clean_keeps_venv(tmp_path: Path):
    """Clean keeps skills/.venv intact."""
    skills = tmp_path / "skills"
    skills.mkdir()
    venv = skills / ".venv"
    venv.mkdir()
    (venv / "bin").mkdir()
    (venv / "bin" / "python3").write_text("#!/usr/bin/env python3")
    skill = skills / "my-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# test")

    clean_target(tmp_path, dry_run=False)
    assert venv.exists(), ".venv should survive cleaning"
    assert not skill.exists(), "skill dirs should be removed"


def test_clean_dry_run(tmp_path: Path):
    """Dry run counts but doesn't delete."""
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "test.toml").write_text("x = 1")

    removed = clean_target(tmp_path, dry_run=True)
    assert removed >= 1
    assert agents.exists(), "dry-run should not delete"


def test_clean_removes_registry(tmp_path: Path):
    """Clean clears sync registry."""
    registry = tmp_path / ".claudekit-sync-registry.json"
    registry.write_text(json.dumps({"version": 1}))

    clean_target(tmp_path, dry_run=False)
    assert not registry.exists()
```

### [NEW] `tests/test_cli_args.py`

```python
"""Tests for CLI argument parsing."""

import sys
from unittest.mock import patch

from claudekit_codex_sync.cli import parse_args


def test_default_args():
    """Default: project scope, no flags."""
    with patch.object(sys, "argv", ["ckc-sync"]):
        args = parse_args()
    assert not args.global_scope
    assert not args.fresh
    assert not args.force
    assert not args.mcp
    assert not args.no_deps
    assert not args.dry_run
    assert args.zip_path is None
    assert args.source is None


def test_global_flag():
    """'-g' enables global scope."""
    with patch.object(sys, "argv", ["ckc-sync", "-g"]):
        args = parse_args()
    assert args.global_scope


def test_fresh_flag():
    """'-f' enables fresh clean."""
    with patch.object(sys, "argv", ["ckc-sync", "-f"]):
        args = parse_args()
    assert args.fresh


def test_combined_short_flags():
    """'-g -f -n' all work together."""
    with patch.object(sys, "argv", ["ckc-sync", "-g", "-f", "-n"]):
        args = parse_args()
    assert args.global_scope
    assert args.fresh
    assert args.dry_run


def test_zip_flag():
    """'--zip' sets zip path and implies zip mode."""
    with patch.object(sys, "argv", ["ckc-sync", "--zip", "test.zip"]):
        args = parse_args()
    assert str(args.zip_path) == "test.zip"


def test_mcp_flag():
    """'--mcp' includes MCP skills."""
    with patch.object(sys, "argv", ["ckc-sync", "--mcp"]):
        args = parse_args()
    assert args.mcp
```

### [MODIFY] Docs

Update these files to reflect new CLI:
- `README.md` — new command name, flags, examples
- `docs/installation-guide.md` — new command, npm install
- `docs/codebase-summary.md` — new modules (clean_target.py), removed scripts/

**README.md Quick Start update:**
```markdown
## Quick Start

```bash
npm install -g claudekit-codex-sync

# Project sync (to ./.codex/)
ckc-sync

# Global sync (to ~/.codex/)
ckc-sync -g

# Fresh re-sync
ckc-sync -g -f

# Preview
ckc-sync -g -n
```
```

## Verification

```bash
# Run all tests
PYTHONPATH=src python3 -m pytest tests/ -v

# Expected: 11 existing + 10 new = 21 tests passing

# Lint
python3 -m py_compile src/claudekit_codex_sync/*.py

# Full sync test
ckc-sync -g -f    # fresh global sync
ckc-sync -n       # project dry-run
```

## Todo
- [x] Add defensive mkdir in `path_normalizer.py`
- [x] Create `tests/test_clean_target.py` (4 tests)
- [x] Create `tests/test_cli_args.py` (6 tests)
- [x] Update `README.md`, `docs/installation-guide.md`, `docs/codebase-summary.md`
- [x] Run all tests
- [ ] `git commit && git push && npm publish`
