#!/usr/bin/env bash
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
