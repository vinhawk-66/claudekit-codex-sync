#!/usr/bin/env bash
set -euo pipefail

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SRC_DIR="${CODEX_HOME}/claudekit/commands"
DEST_DIR="${CODEX_HOME}/prompts"
MANIFEST_NAME=".claudekit-generated-prompts.txt"
PREFIX=""
FORCE="false"
DRY_RUN="false"
INCLUDE_MCP="false"

usage() {
  cat <<'EOF'
Export ClaudeKit commands into Codex custom prompts.

Usage:
  export-claudekit-prompts.sh [options]

Options:
  --source <dir>        Source commands directory (default: ~/.codex/claudekit/commands).
  --dest <dir>          Prompt output directory (default: ~/.codex/prompts).
  --prefix <value>      Prefix for generated prompt names (default: empty).
  --force               Overwrite existing unmanaged prompt files on name collision.
  --include-mcp         Include use-mcp.md (disabled by default).
  --dry-run             Show planned changes without writing files.
  -h, --help            Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      shift
      SRC_DIR="${1:-}"
      ;;
    --dest)
      shift
      DEST_DIR="${1:-}"
      ;;
    --prefix)
      shift
      PREFIX="${1:-}"
      ;;
    --force)
      FORCE="true"
      ;;
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

if [[ ! -d "$SRC_DIR" ]]; then
  echo "Source directory not found: $SRC_DIR" >&2
  exit 1
fi

MANIFEST="${DEST_DIR}/${MANIFEST_NAME}"
declare -A previous_generated=()
if [[ -f "$MANIFEST" ]]; then
  while IFS= read -r line; do
    [[ -n "$line" ]] && previous_generated["$line"]=1
  done < "$MANIFEST"
fi

should_skip() {
  local rel="$1"
  local base
  base="$(basename "$rel")"
  if [[ "$base" == "codex-command-map.md" ]]; then
    return 0
  fi
  if [[ "$base" == "use-mcp.md" && "$INCLUDE_MCP" != "true" ]]; then
    return 0
  fi
  return 1
}

transform_content() {
  sed \
    -e 's#\$HOME/\.claude/skills/#${CODEX_HOME:-$HOME/.codex}/skills/#g' \
    -e 's#\$HOME/\.claude/scripts/#${CODEX_HOME:-$HOME/.codex}/claudekit/scripts/#g' \
    -e 's#\$HOME/\.claude/rules/#${CODEX_HOME:-$HOME/.codex}/claudekit/rules/#g' \
    -e 's#\$HOME/\.claude/#${CODEX_HOME:-$HOME/.codex}/#g' \
    -e 's#\./\.claude/skills/#~/.codex/skills/#g' \
    -e 's#\.claude/skills/#~/.codex/skills/#g' \
    -e 's#\./\.claude/scripts/#~/.codex/claudekit/scripts/#g' \
    -e 's#\.claude/scripts/#~/.codex/claudekit/scripts/#g' \
    -e 's#\./\.claude/rules/#~/.codex/claudekit/rules/#g' \
    -e 's#\.claude/rules/#~/.codex/claudekit/rules/#g' \
    -e 's#~/.claude/.ck.json#~/.codex/claudekit/.ck.json#g' \
    -e 's#\./\.claude/.ck.json#~/.codex/claudekit/.ck.json#g' \
    -e 's#\.claude/.ck.json#~/.codex/claudekit/.ck.json#g' \
    -e 's#\$HOME/\${CODEX_HOME:-\$HOME/\.codex}/#${CODEX_HOME:-$HOME/.codex}/#g'
}

build_prompt_file() {
  local src="$1"
  local rel="$2"
  local out="$3"
  local cmd_path
  cmd_path="/${rel%.md}"
  local transformed
  transformed="$(mktemp /tmp/ck-prompt-content.XXXXXX)"
  transform_content < "$src" > "$transformed"

  if [[ "$(head -n 1 "$transformed")" == "---" ]]; then
    cat "$transformed" > "$out"
  else
    {
      echo "---"
      echo "description: ClaudeKit compatibility prompt for ${cmd_path}"
      echo "---"
      echo
      cat "$transformed"
    } > "$out"
  fi

  rm -f "$transformed"
}

mapfile -t source_files < <(find "$SRC_DIR" -type f -name '*.md' | sort)
if [[ ${#source_files[@]} -eq 0 ]]; then
  echo "No markdown command files found in: $SRC_DIR" >&2
  exit 1
fi

tmp_dir="$(mktemp -d /tmp/ck-prompts.XXXXXX)"
cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

if [[ "$DRY_RUN" != "true" ]]; then
  mkdir -p "$DEST_DIR"
fi

declare -A generated=()
added=0
updated=0
skipped=0
collisions=0
removed=0

for src in "${source_files[@]}"; do
  rel="${src#$SRC_DIR/}"
  if should_skip "$rel"; then
    skipped=$((skipped + 1))
    echo "skip: $rel"
    continue
  fi

  prompt_name="${rel%.md}"
  prompt_name="${prompt_name//\//-}"
  prompt_file="${PREFIX}${prompt_name}.md"
  prompt_dest="${DEST_DIR}/${prompt_file}"
  prompt_temp="${tmp_dir}/${prompt_file}"

  build_prompt_file "$src" "$rel" "$prompt_temp"

  if [[ -f "$prompt_dest" && -z "${previous_generated[$prompt_file]:-}" && "$FORCE" != "true" ]]; then
    collisions=$((collisions + 1))
    echo "skip(collision): $prompt_file"
    continue
  fi

  if [[ -f "$prompt_dest" ]]; then
    updated=$((updated + 1))
    echo "update: $prompt_file <= $rel"
  else
    added=$((added + 1))
    echo "add: $prompt_file <= $rel"
  fi

  generated["$prompt_file"]=1
  if [[ "$DRY_RUN" != "true" ]]; then
    install -m 0644 "$prompt_temp" "$prompt_dest"
  fi
done

if [[ "$DRY_RUN" != "true" ]]; then
  for old in "${!previous_generated[@]}"; do
    if [[ -z "${generated[$old]:-}" ]]; then
      stale_path="${DEST_DIR}/${old}"
      if [[ -f "$stale_path" ]]; then
        rm -f "$stale_path"
        removed=$((removed + 1))
        echo "remove(stale): $old"
      fi
    fi
  done

  {
    for f in "${!generated[@]}"; do
      echo "$f"
    done
  } | sort > "$MANIFEST"
fi

total_generated="${#generated[@]}"
echo "source: $SRC_DIR"
echo "dest: $DEST_DIR"
echo "added=$added updated=$updated skipped=$skipped collisions=$collisions removed=$removed total_generated=$total_generated"

if [[ "$DRY_RUN" == "true" ]]; then
  echo "DRY_RUN=true (no files changed)"
fi
