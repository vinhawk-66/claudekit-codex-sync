# Project Overview - PDR

## Product

**claudekit-codex-sync** — CLI tool that syncs ClaudeKit configuration into Codex CLI-compatible layout.

## Problem Statement

ClaudeKit and Codex CLI use different file layouts, model naming, and config conventions. Users migrating between tools spend time on repetitive manual setup.

## Solution

Single-command sync that:
1. Copies skills and managed assets from ClaudeKit source
2. Normalizes path references (`.claude` -> `.codex`)
3. Converts agent definitions (`.md` YAML frontmatter → `.toml`)
4. Generates hook-equivalent rules for Codex
5. Enforces Codex config defaults and feature flags
6. Registers available agents
7. Bootstraps dependencies (symlink-first strategy)
8. Verifies runtime readiness

## Target Users

ClaudeKit users moving to or co-using Codex CLI.

## Key Metrics

- Project-scope default sync (`./.codex`) with optional global scope (`-g`)
- **39 automated tests** covering sync, conversion, safety, verification, and CLI
- Backward-compatible command alias (`ck-codex-sync`) retained during v0.2
- Faster bootstrap for existing ClaudeKit users via symlink-first venv reuse
- Compact terminal output (~18 lines vs ~100 previously)

## Status

**v0.2.6** — Optimization and quality improvements:
- [x] Dead code cleanup (`prompt_exporter` removed)
- [x] DRY replacement tables (`_BASE_PATH_REPLACEMENTS`)
- [x] Safety guards (reject destructive paths)
- [x] Structured terminal logging (`log_formatter.py`)
- [x] Test coverage expansion (25 → 39 tests)
- [x] Node deps decoupled from Python symlink
- [x] Runtime verifier status differentiation
