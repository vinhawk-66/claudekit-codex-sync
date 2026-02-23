"""Runtime verification."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Any

from .utils import run_cmd


def verify_runtime(*, codex_home: Path, dry_run: bool) -> Dict[str, Any]:
    """Verify runtime health after sync."""
    if dry_run:
        return {"skipped": True}

    run_cmd(["codex", "--help"], dry_run=False)

    copy_script = codex_home / "skills" / "copywriting" / "scripts" / "extract-writing-styles.py"
    py_bin = codex_home / "skills" / ".venv" / "bin" / "python3"
    copywriting_ok = False
    if copy_script.exists() and py_bin.exists():
        run_cmd([str(py_bin), str(copy_script), "--list"], dry_run=False)
        copywriting_ok = True

    prompts_count = len(list((codex_home / "prompts").glob("*.md")))
    skills_count = len(list((codex_home / "skills").rglob("SKILL.md")))
    return {
        "codex_help": "ok",
        "copywriting": "ok" if copywriting_ok else "skipped",
        "prompts": prompts_count,
        "skills": skills_count,
    }
