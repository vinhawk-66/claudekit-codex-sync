#!/usr/bin/env bash
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
