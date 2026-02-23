# Phase 2: Asset Copy to Top-Level

**Priority:** High
**Status:** `[ ]` Not started
**Files:** `asset_sync_dir.py`, `asset_sync_zip.py`

## Overview

Change asset copy destination from `codex_home/claudekit/{dir}` to `codex_home/{dir}` directly.

## Changes

### asset_sync_dir.py

Remove `claudekit_dir` variable. Copy directly to `codex_home/`:

```python
def sync_assets_from_dir(...):
    # REMOVED: claudekit_dir = codex_home / "claudekit"
    added = updated = skipped = 0

    for dirname in ASSET_DIRS:
        src_dir = source / dirname
        if not src_dir.exists():
            continue
        dst_dir = codex_home / dirname          # ← was claudekit_dir / dirname
        if not dry_run:
            dst_dir.mkdir(parents=True, exist_ok=True)

        for src_file in sorted(src_dir.rglob("*")):
            ...
            rel_path = f"{dirname}/{rel}"        # ← was f"claudekit/{dirname}/{rel}"
            dst = dst_dir / rel
            ...

    for filename in ASSET_FILES:
        src = source / filename
        if not src.exists():
            continue
        rel_path = filename                      # ← was f"claudekit/{filename}"
        dst = codex_home / filename              # ← was claudekit_dir / filename
        ...
```

### asset_sync_zip.py

Same pattern — replace `claudekit_dir` with `codex_home` throughout.

## Todo

- [ ] Update `asset_sync_dir.py` — remove `claudekit_dir`, use `codex_home` directly
- [ ] Update `asset_sync_zip.py` — same
- [ ] Compile check

## Success Criteria

- `grep "claudekit_dir" asset_sync_dir.py` returns 0
- Assets appear at `~/.codex/scripts/` not `~/.codex/claudekit/scripts/`
