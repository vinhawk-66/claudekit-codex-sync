# Codex vs Claude Agents

Differences between Claude Code (ClaudeKit) agents and Codex CLI agents, and how this sync tool handles the translation.

## Agent Definition Format

| Aspect | Claude Code (ClaudeKit) | Codex CLI |
|---|---|---|
| **File format** | `.md` with YAML frontmatter | `.toml` |
| **Instructions** | Markdown body below `---` | `developer_instructions = """..."""` |
| **Model** | `model: opus/sonnet/haiku` | `model = "gpt-5.3-codex"` (per-agent override) |
| **Reasoning** | Not configurable | `model_reasoning_effort = "xhigh/high/medium"` |
| **Sandbox** | Not configurable | `sandbox_mode = "read-only/workspace-write"` |
| **Tools** | `tools: [Glob, Grep, Read, ...]` | All tools available (no restriction) |
| **Delegation** | `Task(planner)` explicit call | Auto-spawn by model + `/agent` to switch threads |
| **Memory** | `memory: project` field | Instructions text + AGENTS.md |

## What the Sync Preserves

- ✅ Agent name and slug
- ✅ Developer instructions (full markdown body)
- ✅ Description (from YAML frontmatter)
- ✅ Model selection → mapped to Codex equivalents
- ✅ Sandbox mode settings
- ✅ File structure (`~/.codex/agents/`)
- ✅ Config registration (`[agents.*]` in config.toml)

## What Changes

### Model Mapping

The sync automatically maps Claude model names to Codex equivalents:

```
opus   → gpt-5.3-codex       + model_reasoning_effort = "xhigh"
sonnet → gpt-5.3-codex       + model_reasoning_effort = "high"
haiku  → gpt-5.3-codex-spark + model_reasoning_effort = "medium"
```

### Sandbox Assignment

Agents that only read/analyze get `sandbox_mode = "read-only"`:
- brainstormer, code_reviewer, researcher, project_manager, journal_writer

Agents that write code get `sandbox_mode = "workspace-write"`:
- planner, debugger, fullstack_developer, tester, code_simplifier, etc.

### Delegation Syntax

```diff
- Task(subagent_type="researcher", ...)
+ delegate to the researcher agent
```

`Task()` calls are rewritten to natural language since Codex uses model-driven auto-spawning.

### Path Normalization

```diff
- $HOME/.claude/skills/
+ ${CODEX_HOME:-$HOME/.codex}/skills/

- ~/.claude/
+ ~/.codex/
```

## What's Not Supported

- **Tool restrictions**: Claude's `tools = [...]` field is dropped — Codex gives all tools to all agents
- **Memory config**: Claude's `memory: project` is dropped — use `developer_instructions` text instead
- **Explicit model names**: Claude-specific model names are replaced, not preserved

## Multi-Agent in Codex

After sync, Codex supports multi-agent workflows via:

```toml
[features]
multi_agent = true
child_agents_md = true
```

Built-in roles: `default`, `worker`, `explorer`. Custom roles (from your synced agents) are spawned by the model based on `description` in `[agents.*]` config sections.

Use `/agent` in interactive Codex CLI to switch between active sub-agent threads.
