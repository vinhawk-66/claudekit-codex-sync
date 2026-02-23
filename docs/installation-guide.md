# Installation Guide

## Prerequisites

- Python 3.12+
- Node.js 18+ (for npm)
- [Codex CLI](https://developers.openai.com/codex/cli) installed (`npm install -g @openai/codex`)
- ClaudeKit installed (`~/.claude/` directory exists with agents and skills)

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
ck-codex-sync --help
```

## Usage

### Sync from live `~/.claude/` directory (recommended)

```bash
ck-codex-sync --source-mode live
```

### Sync from ClaudeKit export zip

```bash
ck-codex-sync --zip path/to/claudekit-export.zip
```

### Preview without making changes

```bash
ck-codex-sync --source-mode live --dry-run
```

### Include MCP skills

```bash
ck-codex-sync --source-mode live --include-mcp
```

### Full options

```
--source-mode {auto,live,zip}   Source selection (default: auto)
--source-dir PATH               Custom source directory for live mode
--zip PATH                      Specific ClaudeKit zip path
--codex-home PATH               Codex home (default: $CODEX_HOME or ~/.codex)
--workspace PATH                Workspace root for AGENTS.md
--include-mcp                   Include MCP skills/prompts
--include-hooks                 Include hooks
--include-conflicts             Include conflicting skills
--include-test-deps             Install test requirements
--skip-bootstrap                Skip dependency bootstrap
--skip-verify                   Skip runtime verification
--skip-agent-toml               Skip agent TOML normalization
--respect-edits                 Backup user-edited files
--dry-run                       Preview changes only
```

## What Gets Synced

| Source (`~/.claude/`) | Destination (`~/.codex/`) |
|---|---|
| `agents/*.md` | `agents/*.toml` (converted + model mapped) |
| `skills/*/` | `skills/*/` (paths normalized) |
| `commands/` | `claudekit/commands/` |
| `rules/` | `claudekit/rules/` |
| `scripts/` | `claudekit/scripts/` |
| prompt files | `prompts/` (exported) |

## Post-Install

After sync, launch Codex CLI to verify:

```bash
cxp --full-auto   # or however you launch Codex
```

The sync automatically:
- Enables `multi_agent = true` and `child_agents_md = true`
- Registers all agent roles in `config.toml`
- Sets correct model per agent (see [model mapping](../README.md#agent-model-mapping))
