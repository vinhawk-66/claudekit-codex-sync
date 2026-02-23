# Codex vs Claude Agents

This document outlines the differences between Claude Code agents and Codex agents, and what is lost or preserved during sync.

## Key Differences

| Feature | Claude Code | Codex CLI |
|---------|-------------|-----------|
| **Agent Definition** | TOML files with `[[agents]]` sections | TOML files with `[[agents]]` sections |
| **Model Selection** | `model` frontmatter field | No per-agent model selection |
| **Tool Restrictions** | `tools` frontmatter field | No tool restrictions (all tools available) |
| **Memory** | `memory` frontmatter field | `developer_instructions` text only |
| **Delegation** | `Task()` tool for explicit delegation | Auto-spawn via `multi_agent = true` |

## What Transfers

The following are preserved during ClaudeKit -> Codex sync:

- **Agent name and description** - Basic identity
- **Developer instructions** - Core behavior guidance
- **Sandbox mode settings** - Security constraints
- **Agent file structure** - Organized in `~/.codex/agents/`

## What's Lost

The following Claude-specific features are stripped or adapted:

1. **Explicit Task() delegation syntax**
   - Claude: `Task(subagent_type="researcher", ...)`
   - Codex: Auto-spawn based on context

2. **Tool restrictions**
   - Claude: `tools = ["Read", "Grep", "Edit"]` limits available tools
   - Codex: All tools available to all agents

3. **Model selection**
   - Claude: `model = "haiku"` for cost/performance tuning
   - Codex: Single model for all operations

4. **Memory configuration**
   - Claude: `memory` section with context management
   - Codex: Instructions embedded in developer text

## Path Normalization

Agent TOMLs are automatically normalized during sync:

```diff
- $HOME/.claude/skills/
+ ${CODEX_HOME:-$HOME/.codex}/skills/

- ~/.claude/
+ ~/.codex/
```

## Multi-Agent Configuration

After sync, enable multi-agent mode:

```toml
[features]
multi_agent = true
```

This allows Codex to auto-spawn sub-agents based on task context, similar to Claude's `Task()` delegation but without explicit syntax.

## Recommendation

For maximum compatibility:

1. Write agent instructions assuming all tools are available
2. Use natural language for delegation intent (e.g., "use the researcher agent")
3. Keep agent instructions under 2000 tokens
4. Test agents after sync to verify behavior
