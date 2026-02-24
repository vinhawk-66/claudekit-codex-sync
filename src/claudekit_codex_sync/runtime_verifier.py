"""Runtime verification."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict


def verify_runtime(*, codex_home: Path, dry_run: bool) -> Dict[str, Any]:
    """Verify runtime health after sync."""
    if dry_run:
        return {"skipped": True}

    # Codex binary check
    codex_bin = shutil.which("codex")
    if not codex_bin:
        codex_status = "not-found"
    else:
        result = subprocess.run(
            [codex_bin, "--version"], capture_output=True, timeout=10
        )
        codex_status = "ok" if result.returncode == 0 else "failed"

    # Copywriting script check
    copy_script = codex_home / "skills" / "copywriting" / "scripts" / "extract-writing-styles.py"
    py_bin = codex_home / "skills" / ".venv" / "bin" / "python3"
    if not copy_script.exists():
        copy_status = "not-found"
    elif not py_bin.exists():
        copy_status = "no-venv"
    else:
        result = subprocess.run(
            [str(py_bin), str(copy_script), "--list"], capture_output=True, timeout=30
        )
        copy_status = "ok" if result.returncode == 0 else "failed"

    prompts_dir = codex_home / "prompts"
    prompts_count = len(list(prompts_dir.glob("*.md"))) if prompts_dir.exists() else 0
    skills_count = len(list((codex_home / "skills").rglob("SKILL.md")))
    return {
        "codex": codex_status,
        "copywriting": copy_status,
        "prompts": prompts_count,
        "skills": skills_count,
    }
