# Project Overview - PDR

## Product

**claudekit-codex-sync** — CLI tool that syncs ClaudeKit configuration into Codex CLI-compatible layout.

## Problem Statement

ClaudeKit and Codex CLI use different file layouts, model naming, and config conventions. Users migrating between tools spend time on repetitive manual setup.

## Solution

Single-command sync that:
1. Copies skills and managed assets from ClaudeKit source
2. Normalizes path references (`.claude` -> `.codex`)
3. Enforces Codex config defaults and feature flags
4. Registers available agents
5. Exports prompts and verifies runtime readiness

## Target Users

ClaudeKit users moving to or co-using Codex CLI.

## Key Metrics

- Project-scope default sync (`./.codex`) with optional global scope (`-g`)
- 21 automated tests covering core path normalization/config plus CLI parsing and fresh-clean behavior
- Backward-compatible command alias (`ck-codex-sync`) retained during v0.2
- Faster bootstrap for existing ClaudeKit users via symlink-first venv reuse

## Status

**v0.2.0** — CLI redesign and cleanup complete:
- [x] New `ckc-sync` command surface
- [x] `--fresh` clean target workflow
- [x] `--force` overwrite handling for managed assets
- [x] Symlink-first dependency bootstrap
- [x] Expanded tests and docs refresh
