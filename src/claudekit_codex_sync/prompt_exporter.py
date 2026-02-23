"""Prompt export functionality."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Set

from .constants import PROMPT_MANIFEST, PROMPT_REPLACEMENTS
from .utils import apply_replacements, load_manifest, save_manifest, write_bytes_if_changed


def ensure_frontmatter(content: str, command_path: str) -> str:
    """Ensure content has YAML frontmatter."""
    if content.lstrip().startswith("---"):
        return content
    return f"---\ndescription: ClaudeKit compatibility prompt for /{command_path}\n---\n\n{content}"


def export_prompts(
    *,
    codex_home: Path,
    include_mcp: bool,
    dry_run: bool,
) -> Dict[str, int]:
    """Export prompts from claudekit/commands to prompts directory."""
    from .utils import SyncError

    source = codex_home / "claudekit" / "commands"
    prompts_dir = codex_home / "prompts"
    manifest_path = prompts_dir / PROMPT_MANIFEST

    if not source.exists():
        if dry_run:
            print(f"skip: prompt export dry-run requires existing {source}")
            return {"added": 0, "updated": 0, "skipped": 0, "removed": 0, "collisions": 0, "total_generated": 0}
        raise SyncError(f"Prompt source directory not found: {source}")

    old_manifest = load_manifest(manifest_path)
    files = sorted(source.rglob("*.md"))
    generated: Set[str] = set()
    added = updated = skipped = removed = collisions = 0

    if not dry_run:
        prompts_dir.mkdir(parents=True, exist_ok=True)

    for src in files:
        rel = src.relative_to(source).as_posix()
        base = src.name
        if base == "codex-command-map.md":
            skipped += 1
            print(f"skip: {rel}")
            continue
        if base == "use-mcp.md" and not include_mcp:
            skipped += 1
            print(f"skip: {rel}")
            continue

        prompt_name = rel[:-3].replace("/", "-") + ".md"
        dst = prompts_dir / prompt_name
        text = src.read_text(encoding="utf-8", errors="ignore")
        text = apply_replacements(text, PROMPT_REPLACEMENTS)
        text = ensure_frontmatter(text, rel[:-3])
        data = text.encode("utf-8")

        if dst.exists() and prompt_name not in old_manifest:
            collisions += 1
            print(f"skip(collision): {prompt_name}")
            continue

        generated.add(prompt_name)
        changed, is_added = write_bytes_if_changed(dst, data, mode=0o644, dry_run=dry_run)
        if changed:
            if is_added:
                added += 1
                print(f"add: {prompt_name} <= {rel}")
            else:
                updated += 1
                print(f"update: {prompt_name} <= {rel}")

    for name in sorted(old_manifest - generated):
        target = prompts_dir / name
        if target.exists():
            removed += 1
            print(f"remove(stale): {name}")
            if not dry_run:
                target.unlink()

    save_manifest(manifest_path, generated, dry_run=dry_run)
    return {"added": added, "updated": updated, "skipped": skipped, "removed": removed, "collisions": collisions, "total_generated": len(generated)}
