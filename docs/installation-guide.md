# Installation Guide

## Prerequisites

- Python 3.9+
- Node.js 18+ (for npm installation)
- Codex CLI installed

## Install from Source

```bash
cd /home/vinhawk/claudekit-codex-sync
npm install -g .
```

## Verify Installation

```bash
ck-codex-sync --help
```

## Usage

### Basic Sync (from zip)

```bash
ck-codex-sync
```

### Live Source Mode (from ~/.claude/)

```bash
ck-codex-sync --source-mode live
```

### Include MCP Skills

```bash
ck-codex-sync --include-mcp
```

### Dry Run

```bash
ck-codex-sync --dry-run
```

## Configuration

The tool automatically configures:

- `~/.codex/config.toml` - Codex configuration
- `~/.codex/agents/` - Agent definitions
- `~/.codex/skills/` - Skill definitions
- `~/.codex/prompts/` - Custom prompts

## Post-Install Verification

```bash
# Check multi-agent is enabled
codex features list | grep multi_agent

# Should show: multi_agent    experimental    true
```
