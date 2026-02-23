"""Clean target directories for --fresh sync."""

from __future__ import annotations

import shutil
from pathlib import Path


def clean_target(codex_home: Path, *, dry_run: bool) -> int:
    """Remove agents, skills (keep .venv), prompts, asset dirs before fresh sync."""
    removed = 0

    # Clean top-level asset dirs + legacy claudekit/ from pre-v0.2.3
    for subdir in ("agents", "prompts", "commands", "output-styles", "rules", "scripts", "hooks", "claudekit"):
        target = codex_home / subdir
        if target.exists():
            count = sum(1 for item in target.rglob("*") if item.is_file())
            removed += count
            print(f"fresh: rm {subdir}/ ({count} files)")
            if not dry_run:
                shutil.rmtree(target)

    skills = codex_home / "skills"
    if skills.exists():
        for item in skills.iterdir():
            if item.name == ".venv":
                # Keep symlinks (pointing to ~/.claude/skills/.venv)
                # Delete real venv dirs so symlink can be created on next bootstrap
                if item.is_symlink():
                    continue
                # Real venv dir → delete so symlink-first strategy works
                count = sum(1 for p in item.rglob("*") if p.is_file())
                removed += count
                if not dry_run:
                    shutil.rmtree(item)
                print("fresh: rm skills/.venv (real dir, will be re-symlinked)")
                continue
            if item.is_dir():
                count = sum(1 for path in item.rglob("*") if path.is_file())
                removed += count
                if not dry_run:
                    shutil.rmtree(item)
            else:
                removed += 1
                if not dry_run:
                    item.unlink()
        print("fresh: rm skills/* (kept .venv)")

    # Clean top-level files (add .ck.json, .env.example)
    for name in (
        ".claudekit-sync-registry.json",
        ".sync-manifest-assets.txt",
        ".claudekit-generated-prompts.txt",
        ".ck.json",
        ".env.example",
    ):
        target = codex_home / name
        if target.exists():
            removed += 1
            if not dry_run:
                target.unlink()

    return removed
