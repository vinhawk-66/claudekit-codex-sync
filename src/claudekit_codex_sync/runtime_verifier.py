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

    # Silent codex check — just verify it exists and runs
    codex_bin = shutil.which("codex")
    codex_ok = False
    if codex_bin:
        result = subprocess.run(
            [codex_bin, "--version"], capture_output=True, timeout=10
        )
        codex_ok = result.returncode == 0

    # Silent copywriting check
    copy_script = codex_home / "skills" / "copywriting" / "scripts" / "extract-writing-styles.py"
    py_bin = codex_home / "skills" / ".venv" / "bin" / "python3"
    copywriting_ok = False
    if copy_script.exists() and py_bin.exists():
        result = subprocess.run(
            [str(py_bin), str(copy_script), "--list"], capture_output=True, timeout=30
        )
        copywriting_ok = result.returncode == 0

    prompts_count = len(list((codex_home / "prompts").glob("*.md")))
    skills_count = len(list((codex_home / "skills").rglob("SKILL.md")))
    return {
        "codex": "ok" if codex_ok else "missing",
        "copywriting": "ok" if copywriting_ok else "skipped",
        "prompts": prompts_count,
        "skills": skills_count,
    }
