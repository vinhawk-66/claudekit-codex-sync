# Phase 4 — Wire Unused Functions + Backup

## Overview
- Priority: P1
- Status: [x] Complete
- Estimated: 20 min

## Problem

3 functions exist but are never called:
- `register_agents()` → needed to register `[agents.*]` sections in config.toml
- `update_entry()` → needed to track synced files in registry
- `maybe_backup()` → needed for `--respect-edits`/`--force` logic

## Code Changes

### [MODIFY] `src/claudekit_codex_sync/cli.py` (already done in Phase 2)

`register_agents()` is wired in Phase 2's `main()`:
```python
from .config_enforcer import register_agents
agents_registered = register_agents(codex_home=codex_home, dry_run=args.dry_run)
```

### [MODIFY] `src/claudekit_codex_sync/asset_sync_dir.py`

**Add registry tracking to `sync_assets_from_dir()`. Change line 13 signature to accept `registry` and `force`:**

```python
from .sync_registry import maybe_backup, update_entry


def sync_assets_from_dir(
    source: Path,
    *,
    codex_home: Path,
    include_hooks: bool,
    dry_run: bool,
    registry: dict | None = None,
    force: bool = True,
) -> Dict[str, int]:
    """Sync non-skill assets from live directory."""
    claudekit_dir = codex_home / "claudekit"
    claudekit_dir.mkdir(parents=True, exist_ok=True)
    added = updated = skipped = 0

    for dirname in ASSET_DIRS:
        src_dir = source / dirname
        if not src_dir.exists():
            continue
        dst_dir = claudekit_dir / dirname
        if not dry_run:
            dst_dir.mkdir(parents=True, exist_ok=True)

        for src_file in sorted(src_dir.rglob("*")):
            if not src_file.is_file() or is_excluded_path(src_file.parts):
                continue
            rel = src_file.relative_to(src_dir)
            rel_path = f"claudekit/{dirname}/{rel}"
            dst = dst_dir / rel

            # Skip user-edited files unless --force
            if not force and registry and dst.exists():
                backup = maybe_backup(registry, rel_path, dst, respect_edits=True)
                if backup:
                    skipped += 1
                    continue

            data = src_file.read_bytes()
            mode = src_file.stat().st_mode & 0o777 if src_file.stat().st_mode & 0o111 else None
            changed, is_added = write_bytes_if_changed(dst, data, mode=mode, dry_run=dry_run)
            if changed:
                if is_added:
                    added += 1
                    print(f"add: {rel_path}")
                else:
                    updated += 1
                    print(f"update: {rel_path}")
                # Track in registry
                if registry and not dry_run:
                    update_entry(registry, rel_path, src_file, dst)

    for filename in ASSET_FILES:
        src = source / filename
        if not src.exists():
            continue
        rel_path = f"claudekit/{filename}"
        dst = claudekit_dir / filename

        if not force and registry and dst.exists():
            backup = maybe_backup(registry, rel_path, dst, respect_edits=True)
            if backup:
                skipped += 1
                continue

        data = src.read_bytes()
        mode = src.stat().st_mode & 0o777 if src.stat().st_mode & 0o111 else None
        changed, is_added = write_bytes_if_changed(dst, data, mode=mode, dry_run=dry_run)
        if changed:
            if is_added:
                added += 1
                print(f"add: {rel_path}")
            else:
                updated += 1
                print(f"update: {rel_path}")
            if registry and not dry_run:
                update_entry(registry, rel_path, src, dst)

    return {"added": added, "updated": updated, "removed": 0, "skipped": skipped}
```

### [MODIFY] `src/claudekit_codex_sync/sync_registry.py`

**Add defensive mkdir to `save_registry()` (line 28-32):**

```python
def save_registry(codex_home: Path, registry: Dict[str, Any]) -> None:
    """Save sync registry to disk."""
    registry_path = codex_home / REGISTRY_FILE
    registry_path.parent.mkdir(parents=True, exist_ok=True)  # defensive
    registry["lastSync"] = datetime.now(timezone.utc).isoformat()
    registry_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
```

## Verification

```bash
# Test backup behavior
# 1. Sync normally
ckc-sync -g

# 2. Edit a file manually
echo "# user edit" >> ~/.codex/claudekit/commands/some-file.md

# 3. Re-sync without --force → should skip edited file
ckc-sync -g
# Expected: "skip(user-edit): claudekit/commands/some-file.md"

# 4. Re-sync with --force → should overwrite
ckc-sync -g --force
# Expected: "update: claudekit/commands/some-file.md"

# Test registry saved
cat ~/.codex/.claudekit-sync-registry.json | python3 -m json.tool | head -5
```

## Todo
- [x] Wire `register_agents()` in cli.py (done in Phase 2)
- [x] Add `registry`/`force` params to `sync_assets_from_dir()`
- [x] Call `maybe_backup()` + `update_entry()` in sync loop
- [x] Add defensive mkdir in `save_registry()`
