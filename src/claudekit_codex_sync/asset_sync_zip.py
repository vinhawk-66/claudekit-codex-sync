"""Asset and skill synchronization from zip files."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple

from .constants import (
    ASSET_DIRS,
    ASSET_FILES,
    ASSET_MANIFEST,
    CONFLICT_SKILLS,
    EXCLUDED_SKILLS_ALWAYS,
    MCP_SKILLS,
)
from .source_resolver import collect_skill_entries, zip_mode
from .utils import SyncError, load_manifest, save_manifest, write_bytes_if_changed


def _validate_zip_relpath(rel: str, zip_name: str) -> str:
    """Validate zip relative path and return normalized form."""
    normalized = rel.replace("\\", "/")
    path = Path(normalized)
    if path.is_absolute() or ".." in path.parts:
        raise SyncError(f"Unsafe zip entry path: {zip_name}")
    return normalized


def sync_assets(
    zf: zipfile.ZipFile,
    *,
    codex_home: Path,
    include_hooks: bool,
    dry_run: bool,
) -> Dict[str, int]:
    """Sync non-skill assets from zip to codex_home."""
    manifest_path = codex_home / ASSET_MANIFEST
    old_manifest = load_manifest(manifest_path)

    selected: List[Tuple[str, str]] = []
    for name in zf.namelist():
        if name.endswith("/") or not name.startswith(".claude/"):
            continue
        rel = _validate_zip_relpath(name[len(".claude/") :], name)
        first = rel.split("/", 1)[0]
        if first == "hooks" and include_hooks:
            selected.append((name, rel))
            continue
        if first in ASSET_DIRS or rel in ASSET_FILES:
            selected.append((name, rel))

    new_manifest = {rel for _, rel in selected}
    added = updated = removed = 0

    for rel in sorted(old_manifest - new_manifest):
        safe_rel = _validate_zip_relpath(rel, rel)
        target = codex_home / safe_rel
        if target.exists():
            removed += 1
            print(f"remove: {safe_rel}")
            if not dry_run:
                target.unlink()

    for zip_name, rel in sorted(selected, key=lambda x: x[1]):
        info = zf.getinfo(zip_name)
        data = zf.read(zip_name)
        dst = codex_home / rel
        changed, is_added = write_bytes_if_changed(dst, data, mode=zip_mode(info), dry_run=dry_run)
        if changed:
            if is_added:
                added += 1
                print(f"add: {rel}")
            else:
                updated += 1
                print(f"update: {rel}")

    if not dry_run:
        codex_home.mkdir(parents=True, exist_ok=True)
    save_manifest(manifest_path, new_manifest, dry_run=dry_run)

    if not dry_run:
        for d in sorted(codex_home.rglob("*"), reverse=True):
            if d.is_dir():
                try:
                    d.rmdir()
                except OSError:
                    pass

    return {"added": added, "updated": updated, "removed": removed, "managed_files": len(new_manifest)}


def sync_skills(
    zf: zipfile.ZipFile,
    *,
    codex_home: Path,
    include_mcp: bool,
    include_conflicts: bool,
    dry_run: bool,
) -> Dict[str, int]:
    """Sync skills from zip to codex_home/skills."""
    skills_dir = codex_home / "skills"
    skill_entries = collect_skill_entries(zf)
    added = updated = skipped = 0

    for skill in sorted(skill_entries):
        if skill in EXCLUDED_SKILLS_ALWAYS:
            skipped += 1
            print(f"skip: {skill}")
            continue
        if not include_mcp and skill in MCP_SKILLS:
            skipped += 1
            print(f"skip: {skill}")
            continue
        if skill in CONFLICT_SKILLS:
            skipped += 1
            print(f"skip: {skill}")
            continue
        if not include_conflicts and (skills_dir / ".system" / skill).exists():
            skipped += 1
            print(f"skip: {skill}")
            continue

        dst_skill_dir = skills_dir / skill
        exists = dst_skill_dir.exists()
        if exists:
            updated += 1
            print(f"update: {skill}")
        else:
            added += 1
            print(f"add: {skill}")

        if dry_run:
            continue

        if exists:
            shutil.rmtree(dst_skill_dir)
        dst_skill_dir.mkdir(parents=True, exist_ok=True)

        for zip_name, inner in sorted(skill_entries[skill], key=lambda x: x[1]):
            info = zf.getinfo(zip_name)
            data = zf.read(zip_name)
            dst = dst_skill_dir / inner
            write_bytes_if_changed(dst, data, mode=zip_mode(info), dry_run=False)

    if not dry_run:
        skills_dir.mkdir(parents=True, exist_ok=True)
    total_skills = len(list(skills_dir.rglob("SKILL.md")))
    return {"added": added, "updated": updated, "skipped": skipped, "total_skills": total_skills}
