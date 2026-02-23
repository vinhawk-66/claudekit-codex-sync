# Project Overview — PDR

## Product

**claudekit-codex-sync** — CLI tool that syncs ClaudeKit configuration to OpenAI Codex CLI.

## Problem Statement

ClaudeKit users who also use Codex CLI face duplicate setup: re-configuring agents, skills, prompts, and paths. The two platforms use incompatible formats (ClaudeKit: Markdown agents with YAML frontmatter, Claude model names; Codex: TOML agents, GPT model names).

## Solution

A single-command sync tool that:
1. Copies all assets from `~/.claude/` → `~/.codex/`
2. Rewrites paths (`.claude` → `.codex`)
3. Converts agent definitions (`.md` → `.toml`)
4. Maps model names (`opus` → `gpt-5.3-codex`, `haiku` → `gpt-5.3-codex-spark`)
5. Configures multi-agent features and registers agent roles

## Target Users

ClaudeKit power-users who also use or are migrating to Codex CLI.

## Key Metrics

- Zero manual configuration needed after sync
- All synced agents load correctly in Codex
- No `.claude` path references remain in synced files
- 14+ agent roles with correct model assignments

## Status

**v0.1.0** — Functional. All core features implemented:
- [x] Live directory sync
- [x] Zip archive sync
- [x] Path normalization (37+ files per sync)
- [x] Agent .md → .toml conversion with model mapping
- [x] Multi-agent config (multi_agent + child_agents_md)
- [x] Agent registration (14 roles)
- [x] Prompt export (20+ prompts)
- [x] Dependency bootstrap
- [x] Runtime verification
- [ ] Full test coverage (11/~40 target tests)
- [ ] Idempotent re-sync (partial — registry exists but not fully wired)
