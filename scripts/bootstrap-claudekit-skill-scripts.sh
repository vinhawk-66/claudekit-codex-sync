#!/usr/bin/env bash
set -euo pipefail

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILLS_DIR="${CODEX_HOME}/skills"
VENV_DIR="${SKILLS_DIR}/.venv"
RUN_PYTHON=true
RUN_NODE=true
DRY_RUN=false
INCLUDE_TEST_DEPS=false
INCLUDE_MCP=false

usage() {
  cat <<'EOF'
Install runtime dependencies for ClaudeKit skills synced into Codex.

Usage:
  bootstrap-claudekit-skill-scripts.sh [options]

Options:
  --python-only        Install Python dependencies only
  --node-only          Install Node.js dependencies only
  --include-test-deps  Also install requirements from test folders
  --include-mcp        Also include mcp-builder and mcp-management skills
  --dry-run            Print actions only
  -h, --help           Show help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --python-only)
      RUN_PYTHON=true
      RUN_NODE=false
      ;;
    --node-only)
      RUN_PYTHON=false
      RUN_NODE=true
      ;;
    --include-test-deps)
      INCLUDE_TEST_DEPS=true
      ;;
    --include-mcp)
      INCLUDE_MCP=true
      ;;
    --dry-run)
      DRY_RUN=true
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

py_ok=0
py_fail=0
node_ok=0
node_fail=0

skip_mcp_path() {
  local p="$1"
  if [[ "$INCLUDE_MCP" == true ]]; then
    return 1
  fi
  [[ "$p" == *"/mcp-builder/"* || "$p" == *"/mcp-management/"* ]]
}

if [[ "$RUN_PYTHON" == true ]]; then
  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 not found" >&2
    exit 1
  fi

  if [[ "$DRY_RUN" == true ]]; then
    echo "[dry-run] python3 -m venv \"$VENV_DIR\""
  else
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/python3" -m pip install --upgrade pip >/dev/null
  fi

  while IFS= read -r req; do
    if skip_mcp_path "$req"; then
      continue
    fi
    if [[ "$DRY_RUN" == true ]]; then
      echo "[dry-run] $VENV_DIR/bin/python3 -m pip install -r \"$req\""
      py_ok=$((py_ok + 1))
      continue
    fi
    if "$VENV_DIR/bin/python3" -m pip install -r "$req" >/dev/null; then
      py_ok=$((py_ok + 1))
    else
      echo "python deps failed: $req" >&2
      py_fail=$((py_fail + 1))
    fi
  done < <(
    find "$SKILLS_DIR" \
      \( -path '*/.system/*' -o -path '*/node_modules/*' -o -path '*/.venv/*' -o -path '*/dist/*' -o -path '*/build/*' \) -prune -o \
      -type f -name 'requirements*.txt' -print \
      | if [[ "$INCLUDE_TEST_DEPS" == true ]]; then cat; else grep -Ev '/tests?/'; fi \
      | sort -u
  )
fi

if [[ "$RUN_NODE" == true ]]; then
  if ! command -v npm >/dev/null 2>&1; then
    echo "npm not found" >&2
    exit 1
  fi

  while IFS= read -r pkg; do
    if skip_mcp_path "$pkg"; then
      continue
    fi
    dir="$(dirname "$pkg")"
    if [[ "$DRY_RUN" == true ]]; then
      echo "[dry-run] npm install --prefix \"$dir\""
      node_ok=$((node_ok + 1))
      continue
    fi
    if npm install --prefix "$dir" >/dev/null; then
      node_ok=$((node_ok + 1))
    else
      echo "node deps failed: $dir" >&2
      node_fail=$((node_fail + 1))
    fi
  done < <(
    find "$SKILLS_DIR" \
      \( -path '*/.system/*' -o -path '*/node_modules/*' -o -path '*/.venv/*' -o -path '*/dist/*' -o -path '*/build/*' \) -prune -o \
      -type f -name package.json -print \
      | sort -u
  )
fi

echo "python_ok=$py_ok python_fail=$py_fail node_ok=$node_ok node_fail=$node_fail"
if [[ $py_fail -gt 0 || $node_fail -gt 0 ]]; then
  exit 2
fi
