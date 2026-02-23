# System Architecture

## High-Level Design

```
┌─────────────────────┐    ┌──────────────────────────┐
│ ClaudeKit Source     │    │ Codex CLI Target          │
│ ~/.claude/           │───▶│ ~/.codex/                 │
│   agents/*.md        │    │   agents/*.toml           │
│   skills/*/SKILL.md  │    │   skills/*/SKILL.md       │
│   commands/          │    │   claudekit/commands/     │
│   rules/             │    │   claudekit/rules/        │
│   scripts/           │    │   claudekit/scripts/      │
│   prompts/           │    │   prompts/                │
└─────────────────────┘    │   config.toml             │
                            │   AGENTS.md               │
                            └──────────────────────────┘
```

## Component Architecture

### Pipeline Pattern

The sync follows a sequential pipeline with 8 stages:

1. **Source Resolution** (`source_resolver.py`) — Determine input type (live dir or zip)
2. **Asset Sync** (`asset_sync_dir.py` / `asset_sync_zip.py`) — Copy files with dedup
3. **Path Normalization** (`path_normalizer.py`) — Text replacement across all files
4. **Agent Conversion** (`path_normalizer.py`) — `.md` → `.toml` with model mapping
5. **Config Enforcement** (`config_enforcer.py`) — TOML config + agent registration
6. **Prompt Export** (`prompt_exporter.py`) — Generate Codex prompt files
7. **Dependency Bootstrap** (`dep_bootstrapper.py`) — Install Python/Node deps
8. **Runtime Verification** (`runtime_verifier.py`) — Health check

### Source Modes

| Mode | Input | Detection |
|---|---|---|
| `live` | `~/.claude/` directory | `--source-mode live` |
| `zip` | ClaudeKit export `.zip` | Scans cwd for zips |
| `auto` | Either | Prefers live if `--source-dir` set |

### Agent Conversion Pipeline

```
ClaudeKit .md (YAML frontmatter)
  │  name: planner
  │  model: opus
  │  tools: Glob, Grep, Read, ...
  │  ---
  │  You are an expert planner...
  ▼
convert_agents_md_to_toml()
  │  Parse YAML frontmatter
  │  Map model: opus → gpt-5.3-codex
  │  Set effort: xhigh
  │  Set sandbox: workspace-write/read-only
  ▼
Codex .toml
  │  model = "gpt-5.3-codex"
  │  model_reasoning_effort = "xhigh"
  │  sandbox_mode = "workspace-write"
  │  developer_instructions = """..."""
  ▼
config.toml [agents.planner]
  │  description = "..."
  │  config_file = "agents/planner.toml"
```

### Config.toml Structure

```toml
# Global settings
model = "gpt-5.3-codex"
model_reasoning_effort = "xhigh"

[features]
multi_agent = true
child_agents_md = true

[agents.planner]
description = "Expert planner for architecture and design"
config_file = "agents/planner.toml"

[agents.researcher]
description = "Technology researcher with read-only access"
config_file = "agents/researcher.toml"
```

## Technology Stack

| Layer | Technology |
|---|---|
| CLI wrapper | Node.js (`bin/ck-codex-sync.js`) |
| Core logic | Python 3.12+ |
| Config format | TOML |
| Package manager | npm (distribution), pip (skill deps) |
| Testing | pytest |
| Target platform | OpenAI Codex CLI v0.105+ |

## Key Design Decisions

1. **Python core with Node wrapper** — Python for text processing strength; Node wrapper for `npm install -g` distribution via npm ecosystem.
2. **Text replacement strategy** — Uses ordered replacement tuples (not regex) for predictable, deterministic path rewriting. More specific patterns listed first to prevent partial matches.
3. **Model mapping at sync time** — Converts Claude model names to Codex equivalents during sync rather than at runtime, so Codex reads native model names.
4. **Dual source support** — Both live directory and zip modes allow CI/CD sync from exports and local dev sync from live Claude install.
