# Phase 3 — Symlink venv

## Overview
- Priority: P1
- Status: [x] Complete
- Estimated: 15 min

## Problem

`dep_bootstrapper.py` ALWAYS:
1. Creates new `.venv` (~5s)
2. Upgrades pip (~3s)
3. Installs from all `requirements*.txt` (~50s)

But `~/.claude/skills/.venv` already exists for ClaudeKit users with all packages installed.

## Code Changes

### [MODIFY] `src/claudekit_codex_sync/dep_bootstrapper.py`

**Replace entire file with:**

```python
"""Dependency bootstrap for skills."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Dict

from .utils import eprint, is_excluded_path, run_cmd


def _try_symlink_venv(codex_home: Path, *, dry_run: bool) -> bool:
    """Try to symlink from existing ClaudeKit venv. Returns True if successful."""
    source_venv = Path.home() / ".claude" / "skills" / ".venv"
    target_venv = codex_home / "skills" / ".venv"

    # Already have a working venv (symlink or real)
    if target_venv.is_symlink() and target_venv.resolve().exists():
        print("skip: skills/.venv (symlink intact)")
        return True
    if target_venv.exists() and not target_venv.is_symlink():
        print("skip: skills/.venv (exists)")
        return True

    # Source exists → symlink
    if source_venv.exists():
        if not dry_run:
            target_venv.parent.mkdir(parents=True, exist_ok=True)
            # Remove broken symlink if exists
            if target_venv.is_symlink():
                target_venv.unlink()
            target_venv.symlink_to(source_venv)
        print(f"symlink: skills/.venv → {source_venv}")
        return True

    return False


def bootstrap_deps(
    *,
    codex_home: Path,
    include_mcp: bool,
    dry_run: bool,
) -> Dict[str, int]:
    """Bootstrap Python and Node dependencies for skills."""
    skills_dir = codex_home / "skills"

    # Try symlink first — zero-cost if ClaudeKit venv exists
    if _try_symlink_venv(codex_home, dry_run=dry_run):
        return {"python_ok": 0, "python_fail": 0, "node_ok": 0, "node_fail": 0}

    # Fallback: create fresh venv
    if not shutil.which("python3"):
        from .utils import SyncError
        raise SyncError("python3 not found")

    venv_dir = skills_dir / ".venv"
    py_ok = py_fail = node_ok = node_fail = 0

    run_cmd(["python3", "-m", "venv", str(venv_dir)], dry_run=dry_run)
    py_bin = venv_dir / "bin" / "python3"
    run_cmd([str(py_bin), "-m", "pip", "install", "--upgrade", "pip"], dry_run=dry_run)

    req_files = sorted(skills_dir.rglob("requirements*.txt"))
    for req in req_files:
        if is_excluded_path(req.parts):
            continue
        if not include_mcp and ("mcp-builder" in req.parts or "mcp-management" in req.parts):
            continue
        try:
            run_cmd([str(py_bin), "-m", "pip", "install", "-r", str(req)], dry_run=dry_run)
            py_ok += 1
        except subprocess.CalledProcessError:
            py_fail += 1
            eprint(f"python deps failed: {req}")

    npm = shutil.which("npm")
    if npm:
        pkg_files = sorted(skills_dir.rglob("package.json"))
        for pkg in pkg_files:
            if is_excluded_path(pkg.parts):
                continue
            if not include_mcp and ("mcp-builder" in pkg.parts or "mcp-management" in pkg.parts):
                continue
            try:
                run_cmd([npm, "install", "--prefix", str(pkg.parent)], dry_run=dry_run)
                node_ok += 1
            except subprocess.CalledProcessError:
                node_fail += 1
                eprint(f"node deps failed: {pkg.parent}")
    else:
        eprint("npm not found; skipping Node dependency bootstrap")

    return {
        "python_ok": py_ok,
        "python_fail": py_fail,
        "node_ok": node_ok,
        "node_fail": node_fail,
    }
```

**Changes from current:**
1. Added `_try_symlink_venv()` — if `~/.claude/skills/.venv` exists, symlink instead of rebuild
2. Removed `include_test_deps` param (edge case, removed in CLI redesign)
3. Handles broken symlink cleanup
4. Checks if venv already exists (real or symlink) before doing anything

## Verification

```bash
# Remove existing codex venv to test symlink
rm -rf ~/.codex/skills/.venv

# Run sync
ckc-sync -g -n    # should print "symlink: skills/.venv → ..."

# Verify symlink
ls -la ~/.codex/skills/.venv
# Should show: .venv -> /home/vinhawk/.claude/skills/.venv
```

## Todo
- [x] Replace `dep_bootstrapper.py` with symlink-first version
- [x] Verify symlink works on Linux/WSL
