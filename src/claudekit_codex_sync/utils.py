"""Utility functions for ClaudeKit Codex Sync."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


class SyncError(RuntimeError):
    """Custom error for sync operations."""
    pass


def eprint(msg: str) -> None:
    """Print to stderr."""
    print(msg, file=sys.stderr)


def run_cmd(
    cmd: Sequence[str],
    *,
    cwd: Optional[Path] = None,
    dry_run: bool = False,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess:
    """Run a shell command with optional dry-run mode."""
    pretty = " ".join(cmd)
    if dry_run:
        return subprocess.CompletedProcess(cmd, 0, "", "")
    return subprocess.run(
        list(cmd),
        cwd=str(cwd) if cwd else None,
        check=check,
        text=True,
        capture_output=capture,
    )


def ensure_parent(path: Path, dry_run: bool) -> None:
    """Ensure parent directory exists."""
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)


def write_bytes_if_changed(
    path: Path, data: bytes, *, mode: Optional[int], dry_run: bool
) -> Tuple[bool, bool]:
    """Write bytes to file if content changed. Returns (changed, is_new)."""
    exists = path.exists()
    if exists and path.read_bytes() == data:
        if mode is not None and not dry_run:
            os.chmod(path, mode)
        return False, False
    if dry_run:
        return True, not exists
    ensure_parent(path, dry_run=False)
    path.write_bytes(data)
    if mode is not None:
        os.chmod(path, mode)
    return True, not exists


def write_text_if_changed(
    path: Path, text: str, *, executable: bool = False, dry_run: bool = False
) -> bool:
    """Write text to file if content changed."""
    mode = None
    if executable:
        mode = 0o755
    data = text.encode("utf-8")
    changed, _ = write_bytes_if_changed(path, data, mode=mode, dry_run=dry_run)
    return changed


def load_manifest(path: Path) -> Set[str]:
    """Load manifest file as set of paths."""
    if not path.exists():
        return set()
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def save_manifest(path: Path, values: Iterable[str], dry_run: bool) -> None:
    """Save manifest file from set of paths."""
    data = "\n".join(sorted(set(values)))
    if data:
        data += "\n"
    write_text_if_changed(path, data, dry_run=dry_run)


def apply_replacements(text: str, rules: Sequence[Tuple[str, str]]) -> str:
    """Apply string replacements in sequence."""
    out = text
    for old, new in rules:
        out = out.replace(old, new)
    return out


def is_excluded_path(parts: Sequence[str]) -> bool:
    """Check if path contains excluded directories."""
    blocked = {".system", "node_modules", ".venv", "dist", "build", "__pycache__", ".pytest_cache"}
    return any(p in blocked for p in parts)


def compute_hash(path: Path) -> str:
    """Compute SHA-256 hash of file contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_backup(path: Path) -> Path:
    """Create a timestamped backup of a file."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_suffix(f".ck-backup-{ts}{path.suffix}")
    shutil.copy2(path, backup)
    return backup


def load_template(name: str) -> str:
    """Load a template file from the templates directory."""
    templates_dir = Path(__file__).parent.parent.parent / "templates"
    return (templates_dir / name).read_text(encoding="utf-8")
