# claudekit-codex-sync

Sync [ClaudeKit](https://github.com/anthropics/claudekit) skills, config assets, prompts, and runtime setup to [Codex CLI](https://developers.openai.com/codex).

## Problem

ClaudeKit uses `~/.claude/` conventions and agent markdown frontmatter. Codex uses `~/.codex/`, TOML config, and different runtime defaults. Manual migration is slow and error-prone.

## What It Does

| Step | Action |
|---|---|
| **Scope select** | Sync to project `./.codex/` (default) or global `~/.codex/` (`-g`) |
| **Fresh clean** | Optional `-f` cleanup of target dirs before sync |
| **Source resolve** | Uses live `~/.claude/` or `--zip` export |
| **Asset sync** | Copies commands/output-styles/scripts and `.env.example` to `codex_home/claudekit/` |
| **Skill sync** | Copies skills into `codex_home/skills/` |
| **Path normalize** | Rewrites `.claude` references to `.codex` |
| **Config enforce** | Ensures `config.toml`, feature flags, and agent registration |
| **Prompt export** | Generates Codex-compatible prompt files |
| **Dep bootstrap** | Symlink-first venv strategy, fallback install |
| **Runtime verify** | Health-checks synced environment |

## Installation

```bash
# Install from npm registry
npm install -g claudekit-codex-sync

# Or install from source
git clone https://github.com/vinhawk-66/claudekit-codex-sync.git
cd claudekit-codex-sync
npm install -g .
```

## Quick Start

```bash
# Project sync (to ./.codex/)
ckc-sync

# Global sync (to ~/.codex/)
ckc-sync -g

# Fresh global re-sync
ckc-sync -g -f

# Preview only
ckc-sync -g -n
```

## Usage

```bash
# Custom live source (instead of ~/.claude)
ckc-sync --source /path/to/.claude

# Sync from exported zip
ckc-sync --zip claudekit-export.zip --force

# Include MCP skills
ckc-sync --mcp

# Skip dependency bootstrap
ckc-sync --no-deps

# Overwrite user-edited managed assets
ckc-sync --force

# Backward-compatible command name
ck-codex-sync -g -n
```

## CLI Options

```
-g, --global      Sync to ~/.codex/ (default: ./.codex/)
-f, --fresh       Clean target dirs before sync
--force           Overwrite user-edited files without backup (required for zip write mode)
--zip PATH        Sync from zip instead of live ~/.claude/
--source PATH     Custom source dir (default: ~/.claude/)
--mcp             Include MCP skills
--no-deps         Skip dependency bootstrap (venv)
-n, --dry-run     Preview only
```

## Agent Model Mapping

Per [official Codex docs](https://developers.openai.com/codex/multi-agent):

| Claude Model | Codex Model | Reasoning | Used By |
|---|---|---|---|
| `opus` | `gpt-5.3-codex` | xhigh | planner, code_simplifier |
| `sonnet` | `gpt-5.3-codex` | high | debugger, fullstack_developer |
| `haiku` | `gpt-5.3-codex-spark` | medium | researcher, tester, docs_manager |

Read-only roles remain: brainstormer, code_reviewer, researcher, project_manager, journal_writer.

## Project Structure

```
├── bin/ck-codex-sync.js
├── src/claudekit_codex_sync/
│   ├── cli.py
│   ├── clean_target.py
│   ├── source_resolver.py
│   ├── asset_sync_dir.py
│   ├── asset_sync_zip.py
│   ├── path_normalizer.py
│   ├── config_enforcer.py
│   ├── prompt_exporter.py
│   ├── bridge_generator.py
│   ├── dep_bootstrapper.py
│   ├── runtime_verifier.py
│   ├── sync_registry.py
│   ├── constants.py
│   └── utils.py
├── templates/
├── tests/
└── docs/
```

## Development

```bash
# Run tests
PYTHONPATH=src python3 -m pytest tests/ -v

# Compile check
python3 -m py_compile src/claudekit_codex_sync/*.py

# Local dry-run sync
PYTHONPATH=src python3 -m claudekit_codex_sync.cli -n
```

## Documentation

- [System Architecture](./docs/system-architecture.md)
- [Code Standards](./docs/code-standards.md)
- [Codebase Summary](./docs/codebase-summary.md)
- [Project Roadmap](./docs/project-roadmap.md)
- [Installation Guide](./docs/installation-guide.md)
- [Codex vs Claude Agents](./docs/codex-vs-claude-agents.md)
- [Project Overview (PDR)](./docs/project-overview-pdr.md)

## License

MIT
