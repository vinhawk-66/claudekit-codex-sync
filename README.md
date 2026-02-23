# claudekit-codex-sync

Sync [ClaudeKit](https://github.com/anthropics/claudekit) skills, agents, prompts, and configuration to [Codex CLI](https://developers.openai.com/codex).

## Problem

ClaudeKit stores agent definitions (`.md` with YAML frontmatter), skills, prompts, and config under `~/.claude/`. Codex CLI uses a different layout under `~/.codex/` with `.toml` agents, GPT model names, and TOML-based config. Manually migrating is tedious and error-prone.

## What It Does

| Step | Action |
|---|---|
| **Source resolve** | Detects `~/.claude/` (live) or ClaudeKit export zip |
| **Asset sync** | Copies agents, commands, rules, scripts → `~/.codex/claudekit/` |
| **Skill sync** | Copies 54+ skills → `~/.codex/skills/` |
| **Path normalize** | Rewrites `.claude` → `.codex` in all synced files |
| **Agent convert** | `.md` (YAML frontmatter) → `.toml` with model mapping |
| **Model mapping** | `opus → gpt-5.3-codex`, `haiku → gpt-5.3-codex-spark` |
| **Config enforce** | Sets `multi_agent`, `child_agents_md`, registers `[agents.*]` |
| **Prompt export** | Generates Codex-compatible prompt files |
| **Dep bootstrap** | Installs Python/Node deps for skills requiring them |
| **Runtime verify** | Health-checks the synced environment |

## Installation

```bash
# Clone and install globally
git clone https://github.com/vinhawk-66/claudekit-codex-sync.git
cd claudekit-codex-sync
npm install -g .
```

## Usage

```bash
# Sync from live ~/.claude/ directory
ck-codex-sync --source-mode live

# Sync from exported zip
ck-codex-sync --zip claudekit-export.zip

# Preview without changes
ck-codex-sync --source-mode live --dry-run

# Include MCP skills
ck-codex-sync --source-mode live --include-mcp
```

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

## Agent Model Mapping

Per [official Codex docs](https://developers.openai.com/codex/multi-agent), each agent role can override `model`, `model_reasoning_effort`, and `sandbox_mode`:

| Claude Model | Codex Model | Reasoning | Used By |
|---|---|---|---|
| `opus` | `gpt-5.3-codex` | xhigh | planner, code_simplifier |
| `sonnet` | `gpt-5.3-codex` | high | debugger, fullstack_developer |
| `haiku` | `gpt-5.3-codex-spark` | medium | researcher, tester, docs_manager |

Read-only agents (brainstormer, code_reviewer, researcher, project_manager, journal_writer) get `sandbox_mode = "read-only"`.

## Related Tools

- **[ccs](https://www.npmjs.com/package/@kaitranntt/ccs)** (`@kaitranntt/ccs`) — Claude Code Profile & Model Switcher. Allows running Claude Code with different model backends including Codex models via CLIProxy. Example: `ccs codex` launches Claude Code using Codex as the backend model.
- **[Codex CLI](https://github.com/openai/codex)** (`@openai/codex`) — OpenAI's coding agent CLI.

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
└── docs/                          # Documentation
```

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
- [Project Overview (PDR)](./docs/project-overview-pdr.md)

## License

MIT
