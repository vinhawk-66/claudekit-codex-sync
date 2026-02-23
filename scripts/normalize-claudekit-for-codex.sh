#!/usr/bin/env bash
set -euo pipefail

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILLS_DIR="${CODEX_HOME}/skills"
CLAUDEKIT_DIR="${CODEX_HOME}/claudekit"
DRY_RUN="false"
INCLUDE_MCP="false"

usage() {
  cat <<'EOF'
Re-apply Codex compatibility transforms after ClaudeKit sync.

Usage:
  normalize-claudekit-for-codex.sh [options]

Options:
  --include-mcp     Also normalize MCP skills/docs (disabled by default).
  --dry-run         Show planned changes without writing files.
  -h, --help        Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --include-mcp)
      INCLUDE_MCP="true"
      ;;
    --dry-run)
      DRY_RUN="true"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "Skills directory not found: $SKILLS_DIR" >&2
  exit 1
fi

if [[ ! -d "$CLAUDEKIT_DIR" ]]; then
  echo "ClaudeKit directory not found: $CLAUDEKIT_DIR" >&2
  exit 1
fi

transform_file() {
  local file="$1"
  local tmp
  tmp="$(mktemp /tmp/ck-normalize.XXXXXX)"

  sed \
    -e 's#\$HOME/\.claude/skills/#${CODEX_HOME:-$HOME/.codex}/skills/#g' \
    -e 's#\$HOME/\.claude/scripts/#${CODEX_HOME:-$HOME/.codex}/claudekit/scripts/#g' \
    -e 's#\$HOME/\.claude/rules/#${CODEX_HOME:-$HOME/.codex}/claudekit/rules/#g' \
    -e 's#\$HOME/\.claude/#${CODEX_HOME:-$HOME/.codex}/#g' \
    -e 's#\./\.claude/skills/#${CODEX_HOME:-$HOME/.codex}/skills/#g' \
    -e 's#\.claude/skills/#${CODEX_HOME:-$HOME/.codex}/skills/#g' \
    -e 's#\./\.claude/scripts/#${CODEX_HOME:-$HOME/.codex}/claudekit/scripts/#g' \
    -e 's#\.claude/scripts/#${CODEX_HOME:-$HOME/.codex}/claudekit/scripts/#g' \
    -e 's#\./\.claude/rules/#${CODEX_HOME:-$HOME/.codex}/claudekit/rules/#g' \
    -e 's#\.claude/rules/#${CODEX_HOME:-$HOME/.codex}/claudekit/rules/#g' \
    -e 's#~/.claude/.ck.json#~/.codex/claudekit/.ck.json#g' \
    -e 's#\./\.claude/.ck.json#~/.codex/claudekit/.ck.json#g' \
    -e 's#\.claude/.ck.json#~/.codex/claudekit/.ck.json#g' \
    -e 's#~/.claude/#~/.codex/#g' \
    -e 's#\./\.claude/#./.codex/#g' \
    -e 's#<project>/.claude/#<project>/.codex/#g' \
    -e 's#\.claude/#.codex/#g' \
    -e 's#`\.claude`#`.codex`#g' \
    -e 's#\$HOME/\${CODEX_HOME:-\$HOME/\.codex}/#${CODEX_HOME:-$HOME/.codex}/#g' \
    "$file" > "$tmp"

  if cmp -s "$file" "$tmp"; then
    rm -f "$tmp"
    return 1
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    rm -f "$tmp"
    return 0
  fi

  cp "$tmp" "$file"
  rm -f "$tmp"
  return 0
}

changed=0

while IFS= read -r -d '' file; do
  if [[ "$INCLUDE_MCP" != "true" && ( "$file" == *"/mcp-builder/"* || "$file" == *"/mcp-management/"* ) ]]; then
    continue
  fi
  if transform_file "$file"; then
    changed=$((changed + 1))
    echo "normalize: ${file#$CODEX_HOME/}"
  fi
done < <(find "$SKILLS_DIR" -type f -name 'SKILL.md' -not -path '*/.system/*' -print0)

while IFS= read -r -d '' file; do
  if transform_file "$file"; then
    changed=$((changed + 1))
    echo "normalize: ${file#$CODEX_HOME/}"
  fi
done < <(find "$CLAUDEKIT_DIR" -type f -name '*.md' -print0)

copywriting_script="${SKILLS_DIR}/copywriting/scripts/extract-writing-styles.py"
if [[ -f "$copywriting_script" ]]; then
  if [[ "$DRY_RUN" == "true" ]]; then
    if ! grep -q "CODEX_HOME = Path(os.environ.get('CODEX_HOME'" "$copywriting_script"; then
      echo "normalize: skills/copywriting/scripts/extract-writing-styles.py (patch pending)"
      changed=$((changed + 1))
    fi
  else
    patch_result="$(python3 - "$copywriting_script" <<'PY'
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
original = text
needs_patch = "CODEX_HOME = Path(os.environ.get('CODEX_HOME'" not in text

if needs_patch:
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
    text, func_count = re.subn(
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
    text, block_count = re.subn(
        r"PROJECT_ROOT = find_project_root\(Path\(__file__\)\.parent\)\nSTYLES_DIR = PROJECT_ROOT / 'assets' / 'writing-styles'\nAI_MULTIMODAL_SCRIPTS = PROJECT_ROOT / '.claude' / 'skills' / 'ai-multimodal' / 'scripts'\n",
        new_block,
        text,
        count=1,
    )
    if func_count == 0 or block_count == 0:
        print("error:copywriting_patch_pattern_miss")
        sys.exit(2)

if text != original:
    path.write_text(text, encoding="utf-8")
    print("patched")
else:
    print("unchanged")
PY
)"
    if [[ "$patch_result" == "patched" ]]; then
      echo "normalize: skills/copywriting/scripts/extract-writing-styles.py"
      changed=$((changed + 1))
    fi
  fi
fi

default_style="${SKILLS_DIR}/copywriting/assets/writing-styles/default.md"
fallback_style="${SKILLS_DIR}/copywriting/references/writing-styles.md"
if [[ ! -f "$default_style" && -f "$fallback_style" ]]; then
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "add: skills/copywriting/assets/writing-styles/default.md"
  else
    mkdir -p "$(dirname "$default_style")"
    cp "$fallback_style" "$default_style"
    echo "add: skills/copywriting/assets/writing-styles/default.md"
  fi
  changed=$((changed + 1))
fi

map_file="${CLAUDEKIT_DIR}/commands/codex-command-map.md"
if [[ ! -f "$map_file" ]]; then
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "add: claudekit/commands/codex-command-map.md"
  else
    cat > "$map_file" <<'EOF'
# ClaudeKit -> Codex Command Map

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

- `/use-mcp` (excluded per user request: no MCP sync)
- Hooks (excluded per user request)

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
EOF
  fi
  changed=$((changed + 1))
fi

echo "changed=$changed"
if [[ "$DRY_RUN" == "true" ]]; then
  echo "DRY_RUN=true (no files changed)"
fi
