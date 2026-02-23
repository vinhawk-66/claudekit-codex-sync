# Phase 6: Backup + Registry

Status: pending
Priority: high
Effort: 0.5d

## Goal
Track synced files with SHA-256 checksums. Backup before overwrite.

## Registry Format (`~/.codex/.claudekit-sync-registry.json`)
```json
{
  "version": 1,
  "lastSync": "2026-02-23T02:26:00Z",
  "sourceDir": "~/.claude",
  "entries": {
    "skills/brainstorm/SKILL.md": {
      "sourceHash": "abc...",
      "targetHash": "def...",
      "syncedAt": "2026-02-23T02:26:00Z"
    }
  }
}
```

## Add to utils.py
```python
import hashlib, json, datetime

def compute_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def create_backup(path: Path) -> Path:
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_suffix(f".ck-backup-{ts}{path.suffix}")
    shutil.copy2(path, backup)
    return backup
```

## New `sync_registry.py` (~120 lines)
```python
def load_registry(codex_home: Path) -> dict: ...
def save_registry(codex_home: Path, registry: dict): ...
def check_user_edit(entry: dict, target: Path) -> bool:
    return compute_hash(target) != entry["targetHash"]
def update_entry(registry, rel_path, source, target): ...
```

## Integration
Before overwriting:
1. Check registry → if user edited, backup + warn
2. After writing → update registry with new hashes

## Todo
- [ ] Add compute_hash, create_backup to utils
- [ ] Create sync_registry.py
- [ ] Integrate into asset_sync and path_normalizer
- [ ] Add --respect-edits flag
