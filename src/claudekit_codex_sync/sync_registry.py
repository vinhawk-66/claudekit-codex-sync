"""Sync registry with SHA-256 checksums and backup support."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .utils import compute_hash, create_backup

REGISTRY_FILE = ".claudekit-sync-registry.json"


def load_registry(codex_home: Path) -> Dict[str, Any]:
    """Load sync registry from disk."""
    registry_path = codex_home / REGISTRY_FILE
    if not registry_path.exists():
        return {
            "version": 1,
            "lastSync": None,
            "sourceDir": None,
            "entries": {},
        }
    return json.loads(registry_path.read_text(encoding="utf-8"))


def save_registry(codex_home: Path, registry: Dict[str, Any]) -> None:
    """Save sync registry to disk."""
    registry_path = codex_home / REGISTRY_FILE
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry["lastSync"] = datetime.now(timezone.utc).isoformat()
    registry_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")


def check_user_edit(entry: Dict[str, str], target: Path) -> bool:
    """Check if user has modified the file since last sync."""
    if not target.exists():
        return False
    current_hash = compute_hash(target)
    return current_hash != entry.get("targetHash", "")


def update_entry(
    registry: Dict[str, Any],
    rel_path: str,
    source: Path,
    target: Path,
) -> None:
    """Update registry entry after sync."""
    source_hash = compute_hash(source) if source.exists() else ""
    target_hash = compute_hash(target) if target.exists() else ""
    registry["entries"][rel_path] = {
        "sourceHash": source_hash,
        "targetHash": target_hash,
        "syncedAt": datetime.now(timezone.utc).isoformat(),
    }


def maybe_backup(
    registry: Dict[str, Any],
    rel_path: str,
    target: Path,
    respect_edits: bool,
) -> Optional[Path]:
    """Backup file if user has edited it and respect_edits is enabled."""
    if not target.exists():
        return None
    entry = registry.get("entries", {}).get(rel_path)
    if not entry:
        return None
    if not respect_edits:
        return None
    if check_user_edit(entry, target):
        backup = create_backup(target)
        return backup
    return None
