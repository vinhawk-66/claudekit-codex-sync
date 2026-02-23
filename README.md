# claudekit-codex-sync

One-command bridge from [ClaudeKit](https://github.com/anthropics/claudekit) → [Codex CLI](https://developers.openai.com/codex) — syncs skills, agents, prompts, and config so ClaudeKit power-users can drop into Codex without re-doing their setup.

## Why

ClaudeKit stores agent definitions (`.md`), skills, prompts, and configuration under `~/.claude/`. Codex CLI expects its own layout under `~/.codex/` with `.toml` agent files, different path conventions, and a TOML-based config. This tool automates the translation.

## Quick Start

```bash
# Install globally
npm install -g .

# Sync from live ~/.claude/ directory
ccs codex                          # alias
ck-codex-sync --source-mode live   # full command

# Sync from exported zip
ck-codex-sync --zip claudekit-export.zip

# Preview without changes
ck-codex-sync --source-mode live --dry-run
```

## What It Does

| Step | Action |
|---|---|
| **Source resolve** | Detects `~/.claude/` (live) or latest zip export |
| **Asset sync** | Copies agents, commands, rules, scripts → `~/.codex/claudekit/` |
| **Skill sync** | Copies skills (54+) → `~/.codex/skills/` |
| **Path normalize** | Rewrites `.claude` → `.codex` in all files |
| **Agent convert** | `.md` (YAML frontmatter) → `.toml` with model mapping |
| **Model mapping** | `opus → gpt-5.3-codex`, `haiku → gpt-5.3-codex-spark` |
| **Config enforce** | Sets `multi_agent`, `child_agents_md`, registers `[agents.*]` |
| **Prompt export** | Generates Codex-compatible prompt files |
| **Dep bootstrap** | Installs Python/Node deps for skills requiring them |
| **Runtime verify** | Health-checks the synced environment |

## CLI Options

```
--source-mode live|zip|auto   Source selection (default: auto)
--source-dir PATH             Custom source directory
--zip PATH                    Specific zip file
--codex-home PATH             Codex home (default: ~/.codex)
--include-mcp                 Include MCP skills
--include-hooks               Include hooks
--skip-bootstrap              Skip dependency installation
--skip-verify                 Skip runtime verification
--skip-agent-toml             Skip agent TOML normalization
--respect-edits               Backup user-edited files
--dry-run                     Preview mode
```

## Project Structure

```
├── bin/ck-codex-sync.js           # npm CLI entry point
├── src/claudekit_codex_sync/      # Python modules (13 files, ~1500 LOC)
│   ├── cli.py                     # Main orchestrator
│   ├── source_resolver.py         # Source detection (live/zip/auto)
│   ├── asset_sync_dir.py          # Directory-based sync
│   ├── asset_sync_zip.py          # Zip-based sync
│   ├── path_normalizer.py         # Path rewriting + agent .md→.toml
│   ├── config_enforcer.py         # Config, multi-agent, agent registration
│   ├── prompt_exporter.py         # Prompt file generation
│   ├── bridge_generator.py        # Bridge skill for Codex
│   ├── dep_bootstrapper.py        # Dependency installation
│   ├── runtime_verifier.py        # Health checks
│   ├── sync_registry.py           # Backup/registry (SHA-256)
│   ├── constants.py               # Replacements, model maps
│   └── utils.py                   # Shared utilities
├── templates/                     # Template files for generated content
├── tests/                         # pytest suite
├── scripts/                       # Legacy standalone scripts
├── docs/                          # Documentation
└── plans/                         # Implementation plans
```

## Agent Model Mapping

Per [official Codex docs](https://developers.openai.com/codex/multi-agent), each agent role can override `model`, `model_reasoning_effort`, and `sandbox_mode`:

| Claude Model | Codex Model | Reasoning | Used By |
|---|---|---|---|
| `opus` | `gpt-5.3-codex` | xhigh | planner, code_simplifier |
| `sonnet` | `gpt-5.3-codex` | high | debugger, fullstack_developer |
| `haiku` | `gpt-5.3-codex-spark` | medium | researcher, tester, docs_manager |

Read-only agents (brainstormer, code_reviewer, researcher, project_manager, journal_writer) get `sandbox_mode = "read-only"`.

## Development

```bash
# Run tests
PYTHONPATH=src python3 -m pytest tests/ -v

# Lint
python3 -m py_compile src/claudekit_codex_sync/*.py

# Run sync locally 
PYTHONPATH=src python3 -m claudekit_codex_sync.cli --source-mode live --dry-run
```

## Documentation

- [System Architecture](./docs/system-architecture.md)
- [Code Standards](./docs/code-standards.md)
- [Codebase Summary](./docs/codebase-summary.md)
- [Project Roadmap](./docs/project-roadmap.md)
- [Installation Guide](./docs/installation-guide.md)
- [Codex vs Claude Agents](./docs/codex-vs-claude-agents.md)

## License

MIT
