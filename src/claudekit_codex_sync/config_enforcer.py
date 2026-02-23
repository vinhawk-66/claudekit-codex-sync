"""Config enforcement for Codex."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List


def ensure_agents(*, workspace: Path, dry_run: bool) -> bool:
    """Ensure AGENTS.md exists in workspace."""
    from .utils import load_template, write_text_if_changed
    target = workspace / "AGENTS.md"
    template = load_template("agents-md.md")
    return write_text_if_changed(target, template, dry_run=dry_run)


def enforce_config(*, codex_home: Path, include_mcp: bool, dry_run: bool) -> bool:
    """Enforce Codex config defaults."""
    config = codex_home / "config.toml"
    if config.exists():
        text = config.read_text(encoding="utf-8")
    else:
        text = ""
    orig = text

    if re.search(r"^project_doc_max_bytes\s*=", text, flags=re.M):
        text = re.sub(r"^project_doc_max_bytes\s*=.*$", "project_doc_max_bytes = 65536", text, flags=re.M)
    else:
        text = (text.rstrip("\n") + "\nproject_doc_max_bytes = 65536\n").lstrip("\n")

    fallback_line = 'project_doc_fallback_filenames = ["AGENTS.md", "CLAUDE.md", "AGENTS.override.md"]'
    if re.search(r"^project_doc_fallback_filenames\s*=", text, flags=re.M):
        text = re.sub(r"^project_doc_fallback_filenames\s*=.*$", fallback_line, text, flags=re.M)
    else:
        text = text.rstrip("\n") + "\n" + fallback_line + "\n"

    mcp_management_path = str((codex_home / "skills" / "mcp-management").resolve())
    mcp_builder_path = str((codex_home / "skills" / "mcp-builder").resolve())
    mcp_enabled = "true" if include_mcp else "false"

    pattern = re.compile(r"\n\[\[skills\.config\]\]\n(?:[^\n]*\n)*?(?=\n\[\[skills\.config\]\]|\Z)", re.M)
    blocks = pattern.findall("\n" + text)
    kept: List[str] = []
    for block in blocks:
        if f'path = "{mcp_management_path}"' in block:
            continue
        if f'path = "{mcp_builder_path}"' in block:
            continue
        kept.append(block.rstrip("\n"))

    base = pattern.sub("", "\n" + text).lstrip("\n").rstrip("\n")
    for block in kept:
        if block:
            base += "\n\n" + block

    base += f'\n\n[[skills.config]]\npath = "{mcp_management_path}"\nenabled = {mcp_enabled}\n'
    base += f'\n[[skills.config]]\npath = "{mcp_builder_path}"\nenabled = {mcp_enabled}\n'

    if base == orig:
        return False
    if not dry_run:
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(base, encoding="utf-8")
    return True


def enforce_multi_agent_flag(config_path: Path, dry_run: bool) -> bool:
    """Ensure multi_agent and child_agents_md flags are set in config."""
    text = config_path.read_text() if config_path.exists() else ""
    orig = text

    if "[features]" in text:
        if "multi_agent" not in text:
            text = text.replace("[features]", "[features]\nmulti_agent = true")
        if "child_agents_md" not in text:
            text = text.replace("[features]", "[features]\nchild_agents_md = true")
    else:
        text += "\n[features]\nmulti_agent = true\nchild_agents_md = true\n"

    if text != orig and not dry_run:
        config_path.write_text(text)
    return text != orig


def _extract_description(toml_text: str) -> str:
    """Extract first meaningful sentence from developer_instructions."""
    match = re.search(
        r'developer_instructions\s*=\s*"""(.*?)"""',
        toml_text,
        re.DOTALL,
    )
    if not match:
        return ""
    body = match.group(1).strip()
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        # Strip markdown bold
        line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
        # Take first sentence
        dot = line.find(". ")
        if dot > 0:
            return line[: dot + 1]
        return line[:120]
    return ""


def register_agents(*, codex_home: Path, dry_run: bool) -> int:
    """Register agent TOMLs as [agents.*] roles in config.toml."""
    agents_dir = codex_home / "agents"
    config_path = codex_home / "config.toml"
    if not agents_dir.exists():
        return 0

    text = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    added = 0

    for toml_file in sorted(agents_dir.glob("*.toml")):
        slug = toml_file.stem
        section_header = f"[agents.{slug}]"
        if section_header in text:
            continue

        content = toml_file.read_text(encoding="utf-8")
        desc = _extract_description(content) or f"{slug.replace('_', ' ').title()} agent"
        # Escape quotes in description
        desc = desc.replace('"', '\\"')

        text += (
            f"\n{section_header}\n"
            f'description = "{desc}"\n'
            f'config_file = "agents/{toml_file.name}"\n'
        )
        added += 1

    if added > 0 and not dry_run:
        config_path.write_text(text, encoding="utf-8")
    return added
