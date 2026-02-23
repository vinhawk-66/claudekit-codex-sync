"""Bridge skill generation."""

from __future__ import annotations

from pathlib import Path

from .utils import load_template, write_text_if_changed


def ensure_bridge_skill(*, codex_home: Path, dry_run: bool) -> bool:
    """Ensure claudekit-command-bridge skill exists."""
    bridge_dir = codex_home / "skills" / "claudekit-command-bridge"
    scripts_dir = bridge_dir / "scripts"
    if not dry_run:
        scripts_dir.mkdir(parents=True, exist_ok=True)
    changed = False

    skill_md = load_template("bridge-skill.md")
    resolve_script = load_template("bridge-resolve-command.py")
    docs_init = load_template("bridge-docs-init.sh")
    project_status = load_template("bridge-project-status.sh")

    changed |= write_text_if_changed(bridge_dir / "SKILL.md", skill_md, dry_run=dry_run)
    changed |= write_text_if_changed(
        scripts_dir / "resolve-command.py", resolve_script, executable=True, dry_run=dry_run
    )
    changed |= write_text_if_changed(
        scripts_dir / "docs-init.sh", docs_init, executable=True, dry_run=dry_run
    )
    changed |= write_text_if_changed(
        scripts_dir / "project-status.sh", project_status, executable=True, dry_run=dry_run
    )
    return changed
