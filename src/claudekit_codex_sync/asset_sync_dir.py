"""Asset and skill synchronization from live directory."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict

from .constants import ASSET_DIRS, ASSET_FILES, CONFLICT_SKILLS, EXCLUDED_SKILLS_ALWAYS, MCP_SKILLS
from .sync_registry import check_user_edit, maybe_backup, update_entry
from .utils import compute_hash, create_backup, is_excluded_path, write_bytes_if_changed


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
    if not dry_run:
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

            if not force and registry and dst.exists():
                entry = registry.get("entries", {}).get(rel_path)
                if entry:
                    if dry_run and check_user_edit(entry, dst):
                        skipped += 1
                        print(f"skip(user-edit): {rel_path}")
                        continue
                    backup = maybe_backup(registry, rel_path, dst, respect_edits=True)
                    if backup:
                        skipped += 1
                        print(f"skip(user-edit): {rel_path}")
                        continue
                elif compute_hash(src_file) != compute_hash(dst):
                    if dry_run:
                        print(f"[dry-run] backup(untracked): {rel_path}")
                    else:
                        backup = create_backup(dst)
                        print(f"backup(untracked): {rel_path} -> {backup.name}")

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
            if registry and not dry_run and dst.exists():
                update_entry(registry, rel_path, src_file, dst)

    for filename in ASSET_FILES:
        src = source / filename
        if not src.exists():
            continue
        rel_path = f"claudekit/{filename}"
        dst = claudekit_dir / filename

        if not force and registry and dst.exists():
            entry = registry.get("entries", {}).get(rel_path)
            if entry:
                if dry_run and check_user_edit(entry, dst):
                    skipped += 1
                    print(f"skip(user-edit): {rel_path}")
                    continue
                backup = maybe_backup(registry, rel_path, dst, respect_edits=True)
                if backup:
                    skipped += 1
                    print(f"skip(user-edit): {rel_path}")
                    continue
            elif compute_hash(src) != compute_hash(dst):
                if dry_run:
                    print(f"[dry-run] backup(untracked): {rel_path}")
                else:
                    backup = create_backup(dst)
                    print(f"backup(untracked): {rel_path} -> {backup.name}")

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
        if registry and not dry_run and dst.exists():
            update_entry(registry, rel_path, src, dst)

    return {"added": added, "updated": updated, "removed": 0, "skipped": skipped}


def sync_skills_from_dir(
    source: Path,
    *,
    codex_home: Path,
    include_mcp: bool,
    include_conflicts: bool,
    dry_run: bool,
) -> Dict[str, int]:
    """Sync skills from live directory."""
    skills_src = source / "skills"
    skills_dst = codex_home / "skills"
    added = updated = skipped = 0

    if not skills_src.exists():
        return {"added": 0, "updated": 0, "skipped": 0, "total_skills": 0}

    for skill_dir in sorted(skills_src.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue
        skill = skill_dir.name

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
        if not include_conflicts and (skills_dst / ".system" / skill).exists():
            skipped += 1
            print(f"skip: {skill}")
            continue

        dst = skills_dst / skill
        exists = dst.exists()
        if exists:
            updated += 1
            print(f"update: {skill}")
        else:
            added += 1
            print(f"add: {skill}")

        if dry_run:
            continue

        if exists:
            shutil.rmtree(dst)
        ignore = shutil.ignore_patterns("*.pyc", "__pycache__", ".venv", "node_modules", "dist", "build")
        shutil.copytree(skill_dir, dst, ignore=ignore)

    if not dry_run:
        skills_dst.mkdir(parents=True, exist_ok=True)
    total_skills = len(list(skills_dst.rglob("SKILL.md")))
    return {"added": added, "updated": updated, "skipped": skipped, "total_skills": total_skills}
