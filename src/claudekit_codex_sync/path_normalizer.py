"""Path normalization for Codex compatibility."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from .constants import (
    AGENT_TOML_REPLACEMENTS,
    CLAUDE_SYNTAX_ADAPTATIONS,
    SKILL_MD_REPLACEMENTS,
)
from .utils import apply_replacements, load_template, write_text_if_changed


def normalize_files(
    *,
    codex_home: Path,
    include_mcp: bool,
    dry_run: bool,
) -> int:
    """Normalize paths in skill files and claudekit files."""
    changed = 0
    skills_dir = codex_home / "skills"
    claudekit_dir = codex_home / "claudekit"

    for path in sorted(skills_dir.rglob("SKILL.md")):
        if ".system" in path.parts:
            continue
        rel = path.relative_to(codex_home).as_posix()
        if not include_mcp and any(m in rel for m in ("/mcp-builder/", "/mcp-management/")):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        new_text = apply_replacements(text, SKILL_MD_REPLACEMENTS)
        if new_text != text:
            changed += 1
            print(f"normalize: {rel}")
            if not dry_run:
                path.write_text(new_text, encoding="utf-8")

    for path in sorted(claudekit_dir.rglob("*.md")):
        rel = path.relative_to(codex_home).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        new_text = apply_replacements(text, SKILL_MD_REPLACEMENTS)
        if new_text != text:
            changed += 1
            print(f"normalize: {rel}")
            if not dry_run:
                path.write_text(new_text, encoding="utf-8")

    copy_script = skills_dir / "copywriting" / "scripts" / "extract-writing-styles.py"
    if patch_copywriting_script(copy_script, dry_run=dry_run):
        changed += 1
        print("normalize: skills/copywriting/scripts/extract-writing-styles.py")

    default_style = skills_dir / "copywriting" / "assets" / "writing-styles" / "default.md"
    fallback_style = skills_dir / "copywriting" / "references" / "writing-styles.md"
    if not default_style.exists() and fallback_style.exists():
        changed += 1
        print("add: skills/copywriting/assets/writing-styles/default.md")
        if not dry_run:
            default_style.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(fallback_style, default_style)

    command_map = codex_home / "claudekit" / "commands" / "codex-command-map.md"
    template = load_template("command-map.md")
    if write_text_if_changed(command_map, template, dry_run=dry_run):
        changed += 1
        print("upsert: claudekit/commands/codex-command-map.md")

    return changed


def convert_agents_md_to_toml(*, codex_home: Path, dry_run: bool) -> int:
    """Convert ClaudeKit agent .md files to Codex .toml format."""
    from .constants import (
        CLAUDE_MODEL_REASONING_EFFORT,
        CLAUDE_TO_CODEX_MODELS,
        READ_ONLY_AGENT_ROLES,
    )

    agents_dir = codex_home / "agents"
    if not agents_dir.exists():
        return 0

    converted = 0
    for md_file in sorted(agents_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        # Parse YAML frontmatter
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue

        frontmatter = parts[1].strip()
        body = parts[2].strip()

        # Extract fields from frontmatter
        claude_model = ""
        for line in frontmatter.splitlines():
            m = re.match(r"^model:\s*(.+)$", line)
            if m:
                claude_model = m.group(1).strip().strip("'\"")

        # Map model
        codex_model = CLAUDE_TO_CODEX_MODELS.get(claude_model, "gpt-5.3-codex")
        effort = CLAUDE_MODEL_REASONING_EFFORT.get(claude_model, "high")

        # Determine sandbox mode
        slug = md_file.stem.replace("-", "_")
        if slug in READ_ONLY_AGENT_ROLES:
            sandbox = "read-only"
        else:
            sandbox = "workspace-write"

        # Build TOML
        toml_lines = []
        if codex_model:
            toml_lines.append(f'model = "{codex_model}"')
            toml_lines.append(f'model_reasoning_effort = "{effort}"')
        toml_lines.append(f'sandbox_mode = "{sandbox}"')
        toml_lines.append("")
        # Escape triple quotes in body
        safe_body = body.replace('"""', '\\"\\"\\"\\"')
        toml_lines.append(f'developer_instructions = """\n{safe_body}\n"""')

        toml_content = "\n".join(toml_lines) + "\n"
        toml_file = agents_dir / f"{slug}.toml"

        if not dry_run:
            toml_file.write_text(toml_content, encoding="utf-8")
        converted += 1
        print(f"convert: agents/{md_file.name} → agents/{slug}.toml ({codex_model}, {sandbox})")

    return converted


def normalize_agent_tomls(*, codex_home: Path, dry_run: bool) -> int:
    """Normalize paths and models in agent TOML files."""
    from .constants import (
        CLAUDE_MODEL_REASONING_EFFORT,
        CLAUDE_TO_CODEX_MODELS,
        READ_ONLY_AGENT_ROLES,
    )

    agents_dir = codex_home / "agents"
    if not agents_dir.exists():
        return 0

    # First convert any .md agents to .toml
    convert_agents_md_to_toml(codex_home=codex_home, dry_run=dry_run)

    changed = 0
    for toml_file in sorted(agents_dir.glob("*.toml")):
        text = toml_file.read_text(encoding="utf-8")
        new_text = apply_replacements(text, AGENT_TOML_REPLACEMENTS)
        new_text = apply_replacements(new_text, CLAUDE_SYNTAX_ADAPTATIONS)

        # Map commented Claude models to active Codex models
        for claude_name, codex_model in CLAUDE_TO_CODEX_MODELS.items():
            pattern = rf'^#\s*model\s*=\s*"{claude_name}"\s*$'
            if re.search(pattern, new_text, re.MULTILINE):
                effort = CLAUDE_MODEL_REASONING_EFFORT.get(claude_name, "high")
                if codex_model:
                    replacement = f'model = "{codex_model}"\nmodel_reasoning_effort = "{effort}"'
                else:
                    replacement = ""
                new_text = re.sub(pattern, replacement, new_text, flags=re.MULTILINE)

        # Set read-only sandbox for appropriate roles
        slug = toml_file.stem
        if slug in READ_ONLY_AGENT_ROLES:
            new_text = re.sub(
                r'^sandbox_mode\s*=\s*"workspace-write"',
                'sandbox_mode = "read-only"',
                new_text,
                flags=re.MULTILINE,
            )

        if new_text != text:
            changed += 1
            if not dry_run:
                toml_file.write_text(new_text, encoding="utf-8")
    return changed


def patch_copywriting_script(copy_script: Path, *, dry_run: bool) -> bool:
    """Patch copywriting script for Codex compatibility."""
    from .utils import SyncError

    if not copy_script.exists():
        return False

    text = copy_script.read_text(encoding="utf-8")
    original = text
    if "CODEX_HOME = Path(os.environ.get('CODEX_HOME'" in text:
        return False

    new_func = """def find_project_root(start_dir: Path) -> Path:
    \"\"\"Find project root by preferring a directory that contains assets/writing-styles.\"\"\"
    search_chain = [start_dir] + list(start_dir.parents)
    for parent in search_chain:
        if (parent / 'assets' / 'writing-styles').exists():
            return parent
    for parent in search_chain:
        if (parent / 'SKILL.md').exists():
            return parent
    for parent in search_chain:
        if (parent / '.codex').exists() or (parent / '.claude').exists():
            return parent
    return start_dir
"""

    text, count_func = re.subn(
        r"def find_project_root\(start_dir: Path\) -> Path:\n(?:    .*\n)+?    return start_dir\n",
        new_func,
        text,
        count=1,
    )

    new_block = """PROJECT_ROOT = find_project_root(Path(__file__).parent)
STYLES_DIR = PROJECT_ROOT / 'assets' / 'writing-styles'
CODEX_HOME = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))

_ai_multimodal_candidates = [
    PROJECT_ROOT / '.claude' / 'skills' / 'ai-multimodal' / 'scripts',
    CODEX_HOME / 'skills' / 'ai-multimodal' / 'scripts',
]
AI_MULTIMODAL_SCRIPTS = next((p for p in _ai_multimodal_candidates if p.exists()), _ai_multimodal_candidates[-1])
"""

    text, count_block = re.subn(
        r"PROJECT_ROOT = find_project_root\(Path\(__file__\)\.parent\)\nSTYLES_DIR = PROJECT_ROOT / 'assets' / 'writing-styles'\nAI_MULTIMODAL_SCRIPTS = PROJECT_ROOT / '.claude' / 'skills' / 'ai-multimodal' / 'scripts'\n",
        new_block,
        text,
        count=1,
    )

    if count_func == 0 or count_block == 0:
        raise SyncError("copywriting patch failed: upstream pattern changed")

    if text == original:
        return False
    if not dry_run:
        copy_script.write_text(text, encoding="utf-8")
    return True
