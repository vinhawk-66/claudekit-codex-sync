#!/usr/bin/env python3
"""
All-in-one ClaudeKit -> Codex sync script.

Features:
- Auto-detect newest ClaudeKit zip from temp directories
- Sync non-skill assets into ~/.codex/claudekit
- Sync skills into ~/.codex/skills
- Re-apply Codex compatibility customizations (paths, bridge skill, copywriting patch)
- Synthesize AGENTS.md
- Enforce Codex config defaults
- Export prompts to ~/.codex/prompts
- Bootstrap Python/Node dependencies
- Verify runtime health

Designed to run on Linux/macOS/WSL with Python 3.9+.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


ASSET_DIRS = {"agents", "commands", "output-styles", "rules", "scripts"}
ASSET_FILES = {
    "CLAUDE.md",
    ".ck.json",
    ".ckignore",
    ".env.example",
    ".mcp.json.example",
    "settings.json",
    "metadata.json",
    "statusline.cjs",
    "statusline.sh",
    "statusline.ps1",
}

EXCLUDED_SKILLS_ALWAYS = {"template-skill"}
MCP_SKILLS = {"mcp-builder", "mcp-management"}
CONFLICT_SKILLS = {"skill-creator"}

PROMPT_MANIFEST = ".claudekit-generated-prompts.txt"
ASSET_MANIFEST = ".sync-manifest-assets.txt"


AGENTS_TEMPLATE = """# AGENTS.md

Codex working profile for this workspace, adapted from ClaudeKit rules and workflows.

## Operating Principles

- Follow `YAGNI`, `KISS`, `DRY`.
- Prefer direct, maintainable solutions over speculative abstraction.
- Do not claim completion without evidence (tests, checks, or concrete validation).
- Never use fake implementations just to make tests/build pass.

## Default Workflow

1. Read context first: `README.md` and relevant docs under `./docs/`.
2. For non-trivial work, create/update a plan in `./plans/` before coding.
3. Implement in existing files unless new files are clearly needed.
4. Validate with project compile/lint/test commands.
5. Run code-review mindset before finalizing (bugs, regressions, missing tests first).
6. Update docs when behavior, architecture, contracts, or operations change.

## Quality Gates

- Handle edge cases and error paths explicitly.
- Keep security and performance implications visible in design decisions.
- Keep code readable and intention-revealing; add comments only when needed for non-obvious logic.

## Documentation Rules

- `./docs` is the source of truth for project docs.
- Keep docs synchronized with code and implementation decisions.
- When summarizing/reporting, be concise and list unresolved questions at the end.

## Skill Usage

- Activate relevant skills intentionally per task.
- For legacy ClaudeKit command intents (`/ck-help`, `/coding-level`, `/ask`, `/docs/*`, `/journal`, `/watzup`), use `$claudekit-command-bridge`.

## Reference Material (Imported from ClaudeKit)

- `~/.codex/claudekit/CLAUDE.md`
- `~/.codex/claudekit/rules/development-rules.md`
- `~/.codex/claudekit/rules/primary-workflow.md`
- `~/.codex/claudekit/rules/orchestration-protocol.md`
- `~/.codex/claudekit/rules/documentation-management.md`
- `~/.codex/claudekit/rules/team-coordination-rules.md`
"""


COMMAND_MAP_TEMPLATE = """# ClaudeKit -> Codex Command Map

## Covered by existing skills

- `/preview` -> `markdown-novel-viewer`
- `/kanban` -> `plans-kanban`
- `/review/codebase` -> `code-review`
- `/test`, `/test/ui` -> `web-testing`
- `/worktree` -> `git`
- `/plan/*` -> `plan`

## Converted into bridge workflows

- `/ck-help` -> `claudekit-command-bridge` (`resolve-command.py`)
- `/coding-level` -> `claudekit-command-bridge` (depth rubric + output styles)
- `/ask` -> `claudekit-command-bridge` (architecture mode)
- `/docs/init`, `/docs/update`, `/docs/summarize` -> `claudekit-command-bridge`
- `/journal`, `/watzup` -> `claudekit-command-bridge`

## Explicitly excluded in this sync

- `/use-mcp` (excluded when `--include-mcp` is not set)
- Hooks (excluded when `--include-hooks` is not set)

## Custom Prompt Aliases (`/prompts:<name>`)

- `/ask` -> `/prompts:ask`
- `/ck-help` -> `/prompts:ck-help`
- `/coding-level` -> `/prompts:coding-level`
- `/docs/init` -> `/prompts:docs-init`
- `/docs/summarize` -> `/prompts:docs-summarize`
- `/docs/update` -> `/prompts:docs-update`
- `/journal` -> `/prompts:journal`
- `/kanban` -> `/prompts:kanban`
- `/plan/archive` -> `/prompts:plan-archive`
- `/plan/red-team` -> `/prompts:plan-red-team`
- `/plan/validate` -> `/prompts:plan-validate`
- `/preview` -> `/prompts:preview`
- `/review/codebase` -> `/prompts:review-codebase`
- `/review/codebase/parallel` -> `/prompts:review-codebase-parallel`
- `/test` -> `/prompts:test`
- `/test/ui` -> `/prompts:test-ui`
- `/watzup` -> `/prompts:watzup`
- `/worktree` -> `/prompts:worktree`
"""


BRIDGE_SKILL_TEMPLATE = """---
name: claudekit-command-bridge
description: Bridge legacy ClaudeKit commands to Codex-native workflows. Use when users mention /ck-help, /coding-level, /ask, /docs/*, /journal, /watzup, or ask for Claude command equivalents.
---

# ClaudeKit Command Bridge

Translate ClaudeKit command intent into Codex skills/workflows.

## Quick Mapping

| Legacy command | Codex target |
|---|---|
| `/preview` | `markdown-novel-viewer` skill |
| `/kanban` | `plans-kanban` skill |
| `/review/codebase` | `code-review` skill |
| `/test` or `/test/ui` | `web-testing` skill |
| `/worktree` | `git` skill + git worktree commands |
| `/plan/*` | `plan` skill |
| `/docs/init` | Run `scripts/docs-init.sh` then review docs |
| `/docs/update` | Update docs from latest code changes |
| `/docs/summarize` | Summarize codebase into `docs/codebase-summary.md` |
| `/journal` | Write concise entry under `docs/journals/` |
| `/watzup` | Produce status report from plans + git state |
| `/ask` | Architecture consultation mode (no implementation) |
| `/coding-level` | Adjust explanation depth (levels 0-5 rubric below) |
| `/ck-help` | Run `scripts/resolve-command.py "<request>"` |

## Commands Converted Here

### `/ask` -> Architecture mode

- Provide architecture analysis, tradeoffs, risks, and phased strategy.
- Do not start implementation unless user explicitly asks.

### `/coding-level` -> Explanation depth policy

Use requested level when explaining:

- `0`: ELI5, minimal jargon, analogies.
- `1`: Junior, explain why and common mistakes.
- `2`: Mid, include patterns and tradeoffs.
- `3`: Senior, architecture and constraints focus.
- `4`: Lead, risk/business impact and strategy.
- `5`: Expert, concise implementation-first.

### `/docs/init`, `/docs/update`, `/docs/summarize`

- Initialize docs structure with `scripts/docs-init.sh`.
- Keep docs source of truth under `./docs`.

### `/journal`, `/watzup`

- Write concise journal entries in `docs/journals/`.
- For status, summarize plans and git state.

## Helper Scripts

```bash
python3 ${CODEX_HOME:-$HOME/.codex}/skills/claudekit-command-bridge/scripts/resolve-command.py "/docs/update"
${CODEX_HOME:-$HOME/.codex}/skills/claudekit-command-bridge/scripts/docs-init.sh
${CODEX_HOME:-$HOME/.codex}/skills/claudekit-command-bridge/scripts/project-status.sh
```
"""


BRIDGE_RESOLVE_SCRIPT = """#!/usr/bin/env python3
import sys

MAP = {
    "/preview": "markdown-novel-viewer",
    "/kanban": "plans-kanban",
    "/review/codebase": "code-review",
    "/test": "web-testing",
    "/test/ui": "web-testing",
    "/worktree": "git",
    "/plan": "plan",
    "/plan/validate": "plan",
    "/plan/archive": "project-management",
    "/plan/red-team": "plan",
    "/docs/init": "claudekit-command-bridge (docs-init.sh)",
    "/docs/update": "claudekit-command-bridge",
    "/docs/summarize": "claudekit-command-bridge",
    "/journal": "claudekit-command-bridge",
    "/watzup": "claudekit-command-bridge",
    "/ask": "claudekit-command-bridge (architecture mode)",
    "/coding-level": "claudekit-command-bridge (explanation depth)",
    "/ck-help": "claudekit-command-bridge (this resolver)",
}


def main() -> int:
    raw = " ".join(sys.argv[1:]).strip()
    if not raw:
        print('Usage: resolve-command.py "<legacy-command-or-intent>"')
        return 1

    cmd = raw.split()[0]
    if cmd in MAP:
        print(f"{cmd} -> {MAP[cmd]}")
        return 0

    for prefix, target in [
        ("/docs/", "claudekit-command-bridge"),
        ("/plan/", "plan"),
        ("/review/", "code-review"),
        ("/test", "web-testing"),
    ]:
        if cmd.startswith(prefix):
            print(f"{cmd} -> {target}")
            return 0

    print(f"{cmd} -> no direct map; use find-skills + claudekit-command-bridge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


BRIDGE_DOCS_INIT_SCRIPT = """#!/usr/bin/env bash
set -euo pipefail

DOCS_DIR="${1:-docs}"
mkdir -p "$DOCS_DIR"
mkdir -p "$DOCS_DIR/journals"

create_if_missing() {
  local file="$1"
  local content="$2"
  if [[ ! -f "$file" ]]; then
    printf "%s\\n" "$content" > "$file"
    echo "created: $file"
  else
    echo "exists: $file"
  fi
}

create_if_missing "$DOCS_DIR/project-overview-pdr.md" "# Project Overview / PDR"
create_if_missing "$DOCS_DIR/code-standards.md" "# Code Standards"
create_if_missing "$DOCS_DIR/codebase-summary.md" "# Codebase Summary"
create_if_missing "$DOCS_DIR/design-guidelines.md" "# Design Guidelines"
create_if_missing "$DOCS_DIR/deployment-guide.md" "# Deployment Guide"
create_if_missing "$DOCS_DIR/system-architecture.md" "# System Architecture"
create_if_missing "$DOCS_DIR/project-roadmap.md" "# Project Roadmap"
"""


BRIDGE_STATUS_SCRIPT = """#!/usr/bin/env bash
set -euo pipefail

PLANS_DIR="${1:-plans}"

echo "## Project Status"
echo

if [[ -d "$PLANS_DIR" ]]; then
  total_plans=0
  completed=0
  in_progress=0
  pending=0

  while IFS= read -r plan; do
    total_plans=$((total_plans + 1))
    status="$(grep -E '^status:' "$plan" | head -n1 | awk '{print $2}')"
    case "$status" in
      completed) completed=$((completed + 1)) ;;
      in-progress|in_progress) in_progress=$((in_progress + 1)) ;;
      pending|"") pending=$((pending + 1)) ;;
      *) ;;
    esac
  done < <(find "$PLANS_DIR" -type f -name plan.md | sort)

  echo "- Plans: $total_plans"
  echo "- Completed: $completed"
  echo "- In progress: $in_progress"
  echo "- Pending/unknown: $pending"
  echo
else
  echo "- Plans directory not found: $PLANS_DIR"
  echo
fi

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "## Git"
  echo
  echo "- Branch: $(git rev-parse --abbrev-ref HEAD)"
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "- Working tree: dirty"
  else
    echo "- Working tree: clean"
  fi
else
  echo "## Git"
  echo
  echo "- Not in a git repository"
fi
"""


SKILL_MD_REPLACEMENTS: List[Tuple[str, str]] = [
    ("$HOME/.claude/skills/", "${CODEX_HOME:-$HOME/.codex}/skills/"),
    ("$HOME/.claude/scripts/", "${CODEX_HOME:-$HOME/.codex}/claudekit/scripts/"),
    ("$HOME/.claude/rules/", "${CODEX_HOME:-$HOME/.codex}/claudekit/rules/"),
    ("$HOME/.claude/", "${CODEX_HOME:-$HOME/.codex}/"),
    ("./.claude/skills/", "${CODEX_HOME:-$HOME/.codex}/skills/"),
    (".claude/skills/", "${CODEX_HOME:-$HOME/.codex}/skills/"),
    ("./.claude/scripts/", "${CODEX_HOME:-$HOME/.codex}/claudekit/scripts/"),
    (".claude/scripts/", "${CODEX_HOME:-$HOME/.codex}/claudekit/scripts/"),
    ("./.claude/rules/", "${CODEX_HOME:-$HOME/.codex}/claudekit/rules/"),
    (".claude/rules/", "${CODEX_HOME:-$HOME/.codex}/claudekit/rules/"),
    ("~/.claude/.ck.json", "~/.codex/claudekit/.ck.json"),
    ("./.claude/.ck.json", "~/.codex/claudekit/.ck.json"),
    (".claude/.ck.json", "~/.codex/claudekit/.ck.json"),
    ("~/.claude/", "~/.codex/"),
    ("./.claude/", "./.codex/"),
    ("<project>/.claude/", "<project>/.codex/"),
    (".claude/", ".codex/"),
    ("`.claude`", "`.codex`"),
    ("$HOME/${CODEX_HOME:-$HOME/.codex}/", "${CODEX_HOME:-$HOME/.codex}/"),
]


PROMPT_REPLACEMENTS: List[Tuple[str, str]] = [
    ("$HOME/.claude/skills/", "${CODEX_HOME:-$HOME/.codex}/skills/"),
    ("$HOME/.claude/scripts/", "${CODEX_HOME:-$HOME/.codex}/claudekit/scripts/"),
    ("$HOME/.claude/rules/", "${CODEX_HOME:-$HOME/.codex}/claudekit/rules/"),
    ("$HOME/.claude/", "${CODEX_HOME:-$HOME/.codex}/"),
    ("./.claude/skills/", "~/.codex/skills/"),
    (".claude/skills/", "~/.codex/skills/"),
    ("./.claude/scripts/", "~/.codex/claudekit/scripts/"),
    (".claude/scripts/", "~/.codex/claudekit/scripts/"),
    ("./.claude/rules/", "~/.codex/claudekit/rules/"),
    (".claude/rules/", "~/.codex/claudekit/rules/"),
    ("~/.claude/.ck.json", "~/.codex/claudekit/.ck.json"),
    ("./.claude/.ck.json", "~/.codex/claudekit/.ck.json"),
    (".claude/.ck.json", "~/.codex/claudekit/.ck.json"),
    ("$HOME/${CODEX_HOME:-$HOME/.codex}/", "${CODEX_HOME:-$HOME/.codex}/"),
]


class SyncError(RuntimeError):
    pass


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def run_cmd(
    cmd: Sequence[str],
    *,
    cwd: Optional[Path] = None,
    dry_run: bool = False,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess:
    pretty = " ".join(cmd)
    if dry_run:
        print(f"[dry-run] {pretty}")
        return subprocess.CompletedProcess(cmd, 0, "", "")
    return subprocess.run(
        list(cmd),
        cwd=str(cwd) if cwd else None,
        check=check,
        text=True,
        capture_output=capture,
    )


def ensure_parent(path: Path, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)


def write_bytes_if_changed(path: Path, data: bytes, *, mode: Optional[int], dry_run: bool) -> Tuple[bool, bool]:
    exists = path.exists()
    if exists and path.read_bytes() == data:
        if mode is not None and not dry_run:
            os.chmod(path, mode)
        return False, False
    if dry_run:
        return True, not exists
    ensure_parent(path, dry_run=False)
    path.write_bytes(data)
    if mode is not None:
        os.chmod(path, mode)
    return True, not exists


def write_text_if_changed(path: Path, text: str, *, executable: bool = False, dry_run: bool = False) -> bool:
    mode = None
    if executable:
        mode = 0o755
    data = text.encode("utf-8")
    changed, _ = write_bytes_if_changed(path, data, mode=mode, dry_run=dry_run)
    return changed


def zip_mode(info: zipfile.ZipInfo) -> Optional[int]:
    unix_mode = (info.external_attr >> 16) & 0o777
    if unix_mode:
        return unix_mode
    return None


def find_latest_zip(explicit_zip: Optional[Path]) -> Path:
    if explicit_zip:
        p = explicit_zip.expanduser().resolve()
        if not p.exists():
            raise SyncError(f"Zip not found: {p}")
        return p

    candidates: List[Path] = []
    roots = {Path("/tmp"), Path(tempfile.gettempdir())}
    for root in roots:
        if root.exists():
            candidates.extend(root.glob("claudekit-*/*.zip"))

    if not candidates:
        raise SyncError("No ClaudeKit zip found. Expected /tmp/claudekit-*/*.zip")

    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    return latest.resolve()


def load_manifest(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def save_manifest(path: Path, values: Iterable[str], dry_run: bool) -> None:
    data = "\n".join(sorted(set(values)))
    if data:
        data += "\n"
    write_text_if_changed(path, data, dry_run=dry_run)


def apply_replacements(text: str, rules: Sequence[Tuple[str, str]]) -> str:
    out = text
    for old, new in rules:
        out = out.replace(old, new)
    return out


def is_excluded_path(parts: Sequence[str]) -> bool:
    blocked = {".system", "node_modules", ".venv", "dist", "build", "__pycache__", ".pytest_cache"}
    return any(p in blocked for p in parts)


def sync_assets(
    zf: zipfile.ZipFile,
    *,
    codex_home: Path,
    include_hooks: bool,
    dry_run: bool,
) -> Dict[str, int]:
    claudekit_dir = codex_home / "claudekit"
    manifest_path = claudekit_dir / ASSET_MANIFEST
    old_manifest = load_manifest(manifest_path)

    selected: List[Tuple[str, str]] = []
    for name in zf.namelist():
        if name.endswith("/") or not name.startswith(".claude/"):
            continue
        rel = name[len(".claude/") :]
        first = rel.split("/", 1)[0]
        if first == "hooks" and include_hooks:
            selected.append((name, rel))
            continue
        if first in ASSET_DIRS or rel in ASSET_FILES:
            selected.append((name, rel))

    new_manifest = {rel for _, rel in selected}

    added = 0
    updated = 0
    removed = 0

    # Remove stale managed files.
    stale = sorted(old_manifest - new_manifest)
    for rel in stale:
        target = claudekit_dir / rel
        if target.exists():
            removed += 1
            print(f"remove: {rel}")
            if not dry_run:
                target.unlink()

    # Write assets.
    for zip_name, rel in sorted(selected, key=lambda x: x[1]):
        info = zf.getinfo(zip_name)
        data = zf.read(zip_name)
        dst = claudekit_dir / rel
        changed, is_added = write_bytes_if_changed(dst, data, mode=zip_mode(info), dry_run=dry_run)
        if not changed:
            continue
        if is_added:
            added += 1
            print(f"add: {rel}")
        else:
            updated += 1
            print(f"update: {rel}")

    if not dry_run:
        claudekit_dir.mkdir(parents=True, exist_ok=True)
    save_manifest(manifest_path, new_manifest, dry_run=dry_run)

    if not dry_run:
        # Clean empty folders.
        for d in sorted(claudekit_dir.rglob("*"), reverse=True):
            if d.is_dir():
                try:
                    d.rmdir()
                except OSError:
                    pass

    return {
        "added": added,
        "updated": updated,
        "removed": removed,
        "managed_files": len(new_manifest),
    }


def collect_skill_entries(zf: zipfile.ZipFile) -> Dict[str, List[Tuple[str, str]]]:
    skill_files: Dict[str, List[Tuple[str, str]]] = {}
    for name in zf.namelist():
        if name.endswith("/") or not name.startswith(".claude/skills/"):
            continue
        rel = name[len(".claude/skills/") :]
        parts = rel.split("/", 1)
        if len(parts) != 2:
            continue
        skill, inner = parts
        skill_files.setdefault(skill, []).append((name, inner))
    return skill_files


def sync_skills(
    zf: zipfile.ZipFile,
    *,
    codex_home: Path,
    include_mcp: bool,
    include_conflicts: bool,
    dry_run: bool,
) -> Dict[str, int]:
    skills_dir = codex_home / "skills"
    skill_entries = collect_skill_entries(zf)

    added = 0
    updated = 0
    skipped = 0

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

    skills_dir.mkdir(parents=True, exist_ok=True)
    total_skills = len(list(skills_dir.rglob("SKILL.md")))
    return {
        "added": added,
        "updated": updated,
        "skipped": skipped,
        "total_skills": total_skills,
    }


def patch_copywriting_script(copy_script: Path, *, dry_run: bool) -> bool:
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


def normalize_files(
    *,
    codex_home: Path,
    include_mcp: bool,
    dry_run: bool,
) -> int:
    changed = 0
    skills_dir = codex_home / "skills"
    claudekit_dir = codex_home / "claudekit"

    skill_files = sorted(skills_dir.rglob("SKILL.md"))
    for path in skill_files:
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
    if write_text_if_changed(command_map, COMMAND_MAP_TEMPLATE, dry_run=dry_run):
        changed += 1
        print("upsert: claudekit/commands/codex-command-map.md")

    return changed


def ensure_bridge_skill(*, codex_home: Path, dry_run: bool) -> bool:
    bridge_dir = codex_home / "skills" / "claudekit-command-bridge"
    scripts_dir = bridge_dir / "scripts"
    if not dry_run:
        scripts_dir.mkdir(parents=True, exist_ok=True)
    changed = False

    changed |= write_text_if_changed(bridge_dir / "SKILL.md", BRIDGE_SKILL_TEMPLATE, dry_run=dry_run)
    changed |= write_text_if_changed(
        scripts_dir / "resolve-command.py", BRIDGE_RESOLVE_SCRIPT, executable=True, dry_run=dry_run
    )
    changed |= write_text_if_changed(
        scripts_dir / "docs-init.sh", BRIDGE_DOCS_INIT_SCRIPT, executable=True, dry_run=dry_run
    )
    changed |= write_text_if_changed(
        scripts_dir / "project-status.sh", BRIDGE_STATUS_SCRIPT, executable=True, dry_run=dry_run
    )
    return changed


def ensure_agents(*, workspace: Path, dry_run: bool) -> bool:
    target = workspace / "AGENTS.md"
    return write_text_if_changed(target, AGENTS_TEMPLATE, dry_run=dry_run)


def enforce_config(*, codex_home: Path, include_mcp: bool, dry_run: bool) -> bool:
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


def ensure_frontmatter(content: str, command_path: str) -> str:
    if content.lstrip().startswith("---"):
        return content
    return f"---\ndescription: ClaudeKit compatibility prompt for /{command_path}\n---\n\n{content}"


def export_prompts(
    *,
    codex_home: Path,
    include_mcp: bool,
    dry_run: bool,
) -> Dict[str, int]:
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
    added = 0
    updated = 0
    skipped = 0
    removed = 0
    collisions = 0

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
        if not changed:
            continue
        if is_added:
            added += 1
            print(f"add: {prompt_name} <= {rel}")
        else:
            updated += 1
            print(f"update: {prompt_name} <= {rel}")

    stale = sorted(old_manifest - generated)
    for name in stale:
        target = prompts_dir / name
        if target.exists():
            removed += 1
            print(f"remove(stale): {name}")
            if not dry_run:
                target.unlink()

    save_manifest(manifest_path, generated, dry_run=dry_run)

    return {
        "added": added,
        "updated": updated,
        "skipped": skipped,
        "removed": removed,
        "collisions": collisions,
        "total_generated": len(generated),
    }


def bootstrap_deps(
    *,
    codex_home: Path,
    include_mcp: bool,
    include_test_deps: bool,
    dry_run: bool,
) -> Dict[str, int]:
    skills_dir = codex_home / "skills"
    venv_dir = skills_dir / ".venv"

    if not shutil.which("python3"):
        raise SyncError("python3 not found")

    py_ok = py_fail = node_ok = node_fail = 0

    run_cmd(["python3", "-m", "venv", str(venv_dir)], dry_run=dry_run)
    py_bin = venv_dir / "bin" / "python3"
    run_cmd([str(py_bin), "-m", "pip", "install", "--upgrade", "pip"], dry_run=dry_run)

    req_files = sorted(skills_dir.rglob("requirements*.txt"))
    for req in req_files:
        rel = req.relative_to(skills_dir).as_posix()
        if is_excluded_path(req.parts):
            continue
        if not include_test_deps and "/test" in rel:
            continue
        if not include_mcp and ("mcp-builder" in req.parts or "mcp-management" in req.parts):
            continue
        try:
            run_cmd([str(py_bin), "-m", "pip", "install", "-r", str(req)], dry_run=dry_run)
            py_ok += 1
        except subprocess.CalledProcessError:
            py_fail += 1
            eprint(f"python deps failed: {req}")

    npm = shutil.which("npm")
    if npm:
        pkg_files = sorted(skills_dir.rglob("package.json"))
        for pkg in pkg_files:
            rel = pkg.relative_to(skills_dir).as_posix()
            if is_excluded_path(pkg.parts):
                continue
            if not include_mcp and ("mcp-builder" in pkg.parts or "mcp-management" in pkg.parts):
                continue
            try:
                run_cmd([npm, "install", "--prefix", str(pkg.parent)], dry_run=dry_run)
                node_ok += 1
            except subprocess.CalledProcessError:
                node_fail += 1
                eprint(f"node deps failed: {pkg.parent}")
    else:
        eprint("npm not found; skipping Node dependency bootstrap")

    return {
        "python_ok": py_ok,
        "python_fail": py_fail,
        "node_ok": node_ok,
        "node_fail": node_fail,
    }


def verify_runtime(*, codex_home: Path, dry_run: bool) -> Dict[str, object]:
    if dry_run:
        return {"skipped": True}

    run_cmd(["codex", "--help"], dry_run=False)

    copy_script = codex_home / "skills" / "copywriting" / "scripts" / "extract-writing-styles.py"
    py_bin = codex_home / "skills" / ".venv" / "bin" / "python3"
    copywriting_ok = False
    if copy_script.exists() and py_bin.exists():
        run_cmd([str(py_bin), str(copy_script), "--list"], dry_run=False)
        copywriting_ok = True

    prompts_count = len(list((codex_home / "prompts").glob("*.md")))
    skills_count = len(list((codex_home / "skills").rglob("SKILL.md")))
    return {
        "codex_help": "ok",
        "copywriting": "ok" if copywriting_ok else "skipped",
        "prompts": prompts_count,
        "skills": skills_count,
    }


def print_summary(summary: Dict[str, object]) -> None:
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="All-in-one ClaudeKit -> Codex sync script (portable, no manual steps required)."
    )
    p.add_argument("--zip", dest="zip_path", type=Path, help="Specific ClaudeKit zip path")
    p.add_argument("--codex-home", type=Path, default=None, help="Codex home (default: $CODEX_HOME or ~/.codex)")
    p.add_argument("--workspace", type=Path, default=Path.cwd(), help="Workspace root for AGENTS.md")
    p.add_argument("--include-mcp", action="store_true", help="Include MCP skills/prompts and enable MCP skills")
    p.add_argument("--include-hooks", action="store_true", help="Include hooks under ~/.codex/claudekit/hooks")
    p.add_argument("--include-conflicts", action="store_true", help="Include skills conflicting with system skills")
    p.add_argument("--include-test-deps", action="store_true", help="Install test requirements in bootstrap")
    p.add_argument("--skip-bootstrap", action="store_true", help="Skip dependency bootstrap")
    p.add_argument("--skip-verify", action="store_true", help="Skip post-sync verification")
    p.add_argument("--dry-run", action="store_true", help="Preview changes only")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    codex_home = (args.codex_home or Path(os.environ.get("CODEX_HOME", "~/.codex"))).expanduser().resolve()
    workspace = args.workspace.expanduser().resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    zip_path = find_latest_zip(args.zip_path)
    print(f"zip: {zip_path}")
    print(f"codex_home: {codex_home}")
    print(f"workspace: {workspace}")
    print(
        f"include_mcp={args.include_mcp} include_hooks={args.include_hooks} dry_run={args.dry_run} "
        f"skip_bootstrap={args.skip_bootstrap} skip_verify={args.skip_verify}"
    )

    codex_home.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path) as zf:
        assets_stats = sync_assets(
            zf, codex_home=codex_home, include_hooks=args.include_hooks, dry_run=args.dry_run
        )
        print(
            f"assets: added={assets_stats['added']} updated={assets_stats['updated']} "
            f"removed={assets_stats['removed']} managed_files={assets_stats['managed_files']}"
        )

        skills_stats = sync_skills(
            zf,
            codex_home=codex_home,
            include_mcp=args.include_mcp,
            include_conflicts=args.include_conflicts,
            dry_run=args.dry_run,
        )
        print(
            f"skills: added={skills_stats['added']} updated={skills_stats['updated']} "
            f"skipped={skills_stats['skipped']} total_skills={skills_stats['total_skills']}"
        )

    changed = normalize_files(codex_home=codex_home, include_mcp=args.include_mcp, dry_run=args.dry_run)
    print(f"normalize_changed={changed}")

    baseline_changed = 0
    if ensure_agents(workspace=workspace, dry_run=args.dry_run):
        baseline_changed += 1
        print(f"upsert: {workspace / 'AGENTS.md'}")
    if enforce_config(codex_home=codex_home, include_mcp=args.include_mcp, dry_run=args.dry_run):
        baseline_changed += 1
        print(f"upsert: {codex_home / 'config.toml'}")
    if ensure_bridge_skill(codex_home=codex_home, dry_run=args.dry_run):
        baseline_changed += 1
        print(f"upsert: {codex_home / 'skills' / 'claudekit-command-bridge'}")
    print(f"baseline_changed={baseline_changed}")

    prompt_stats = export_prompts(codex_home=codex_home, include_mcp=args.include_mcp, dry_run=args.dry_run)
    print(
        f"prompts: added={prompt_stats['added']} updated={prompt_stats['updated']} "
        f"skipped={prompt_stats['skipped']} removed={prompt_stats['removed']} "
        f"collisions={prompt_stats['collisions']} total_generated={prompt_stats['total_generated']}"
    )

    bootstrap_stats = None
    if not args.skip_bootstrap:
        bootstrap_stats = bootstrap_deps(
            codex_home=codex_home,
            include_mcp=args.include_mcp,
            include_test_deps=args.include_test_deps,
            dry_run=args.dry_run,
        )
        print(
            f"bootstrap: python_ok={bootstrap_stats['python_ok']} python_fail={bootstrap_stats['python_fail']} "
            f"node_ok={bootstrap_stats['node_ok']} node_fail={bootstrap_stats['node_fail']}"
        )
        if (bootstrap_stats["python_fail"] or bootstrap_stats["node_fail"]) and not args.dry_run:
            raise SyncError("Dependency bootstrap reported failures")

    verify_stats = None
    if not args.skip_verify:
        verify_stats = verify_runtime(codex_home=codex_home, dry_run=args.dry_run)
        print(f"verify: {verify_stats}")

    summary = {
        "zip": str(zip_path),
        "codex_home": str(codex_home),
        "workspace": str(workspace),
        "dry_run": args.dry_run,
        "include_mcp": args.include_mcp,
        "include_hooks": args.include_hooks,
        "assets": assets_stats,
        "skills": skills_stats,
        "normalize_changed": changed,
        "baseline_changed": baseline_changed,
        "prompts": prompt_stats,
        "bootstrap": bootstrap_stats,
        "verify": verify_stats,
    }
    print_summary(summary)
    print("done: claudekit all-in-one sync completed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SyncError as exc:
        eprint(f"error: {exc}")
        raise SystemExit(2)
