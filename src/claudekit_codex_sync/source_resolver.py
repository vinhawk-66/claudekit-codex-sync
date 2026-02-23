"""Source resolution for ClaudeKit zip or live directory."""

from __future__ import annotations

import os
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .utils import SyncError


def find_latest_zip(explicit_zip: Optional[Path]) -> Path:
    """Find the latest ClaudeKit zip file."""
    if explicit_zip:
        p = explicit_zip.expanduser().resolve()
        if not p.exists():
            raise SyncError(f"Zip not found: {p}")
        return p

    candidates: List[Path] = []
    roots = {Path("/tmp"), Path(tempfile.gettempdir())}
    for root in roots:
        if root.exists():
            candidates.extend(root.glob("claudekit-*/*.zip"))

    if not candidates:
        raise SyncError("No ClaudeKit zip found. Expected /tmp/claudekit-*/*.zip")

    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    return latest.resolve()


def detect_claude_source() -> Path:
    """Auto-detect Claude Code installation directory."""
    candidates = [
        Path.home() / ".claude",
        Path(os.environ.get("USERPROFILE", "")) / ".claude",
    ]
    for p in candidates:
        if p.exists() and (p / "skills").is_dir():
            return p
    raise SyncError("Claude Code not found. Use --source to specify.")


def validate_source(source: Path) -> Dict[str, bool]:
    """Validate source directory structure."""
    return {
        "skills": (source / "skills").is_dir(),
        "agents": (source / "agents").is_dir(),
        "commands": (source / "commands").is_dir(),
        "rules": (source / "rules").is_dir(),
        "claude_md": (source / "CLAUDE.md").is_file(),
    }


def collect_skill_entries(zf: zipfile.ZipFile) -> Dict[str, List[Tuple[str, str]]]:
    """Collect skill entries from zip file."""
    skill_files: Dict[str, List[Tuple[str, str]]] = {}
    for name in zf.namelist():
        if name.endswith("/") or not name.startswith(".claude/skills/"):
            continue
        rel = name[len(".claude/skills/") :].replace("\\", "/")
        path = Path(rel)
        if path.is_absolute() or ".." in path.parts:
            raise SyncError(f"Unsafe zip entry path: {name}")
        parts = rel.split("/", 1)
        if len(parts) != 2:
            continue
        skill, inner = parts
        inner_path = Path(inner)
        if Path(skill).is_absolute() or ".." in Path(skill).parts:
            raise SyncError(f"Unsafe skill name in zip entry: {name}")
        if inner_path.is_absolute() or ".." in inner_path.parts:
            raise SyncError(f"Unsafe skill file path in zip entry: {name}")
        skill_files.setdefault(skill, []).append((name, inner))
    return skill_files


def zip_mode(info: zipfile.ZipInfo) -> Optional[int]:
    """Extract Unix mode from ZipInfo."""
    unix_mode = (info.external_attr >> 16) & 0o777
    if unix_mode:
        return unix_mode
    return None
