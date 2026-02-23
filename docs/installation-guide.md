# Installation Guide

## Prerequisites

- Python 3.12+
- Node.js 18+
- [Codex CLI](https://developers.openai.com/codex/cli) installed (`npm install -g @openai/codex`)
- ClaudeKit installed (`~/.claude/` exists) or exported ClaudeKit zip

## Install via npm

```bash
npm install -g claudekit-codex-sync
```

## Install from Source

```bash
git clone https://github.com/vinhawk-66/claudekit-codex-sync.git
cd claudekit-codex-sync
npm install -g .
```

## Verify Installation

```bash
ckc-sync --help
ck-codex-sync --help
```

## Usage

### Project sync (default target: `./.codex/`)

```bash
ckc-sync
```

### Global sync (`~/.codex/`)

```bash
ckc-sync -g
```

### Fresh re-sync

```bash
ckc-sync -g -f
```

### Preview only

```bash
ckc-sync -g -n
```

### Zip source

```bash
ckc-sync --zip path/to/claudekit-export.zip --force
```

### Custom live source

```bash
ckc-sync --source /path/to/.claude
```

## Full Options

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

## What Gets Synced

| Source/Input | Destination |
|---|---|
| `skills/*/` | `codex_home/skills/*/` |
| `commands/` | `codex_home/claudekit/commands/` |
| `output-styles/` | `codex_home/claudekit/output-styles/` |
| `scripts/` | `codex_home/claudekit/scripts/` |
| `.env.example` | `codex_home/claudekit/.env.example` |
| Generated from `codex_home/claudekit/commands/*.md` | `codex_home/prompts/*.md` |

Notes:
- In zip mode, `hooks/` entries are also synced to `codex_home/claudekit/hooks/`.

## Post-Install

After sync:

```bash
codex --help
```

The sync process enforces:
- `[features] multi_agent = true`
- `[features] child_agents_md = true`
- Bridge skill setup
- Agent registration for available `codex_home/agents/*.toml`
