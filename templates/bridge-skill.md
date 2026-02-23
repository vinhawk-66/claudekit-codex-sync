---
name: claudekit-command-bridge
description: Bridge legacy ClaudeKit commands to Codex-native workflows. Use when users mention /ck-help, /coding-level, /ask, /docs/*, /journal, /watzup, or ask for Claude command equivalents.
---

# ClaudeKit Command Bridge

Translate ClaudeKit command intent into Codex skills/workflows.

## Quick Mapping

| Legacy command | Codex target |
|---|---|
| `/preview` | `markdown-novel-viewer` skill |
| `/kanban` | `plans-kanban` skill |
| `/review/codebase` | `code-review` skill |
| `/test` or `/test/ui` | `web-testing` skill |
| `/worktree` | `git` skill + git worktree commands |
| `/plan/*` | `plan` skill |
| `/docs/init` | Run `scripts/docs-init.sh` then review docs |
| `/docs/update` | Update docs from latest code changes |
| `/docs/summarize` | Summarize codebase into `docs/codebase-summary.md` |
| `/journal` | Write concise entry under `docs/journals/` |
| `/watzup` | Produce status report from plans + git state |
| `/ask` | Architecture consultation mode (no implementation) |
| `/coding-level` | Adjust explanation depth (levels 0-5 rubric below) |
| `/ck-help` | Run `scripts/resolve-command.py "<request>"` |

## Commands Converted Here

### `/ask` -> Architecture mode

- Provide architecture analysis, tradeoffs, risks, and phased strategy.
- Do not start implementation unless user explicitly asks.

### `/coding-level` -> Explanation depth policy

Use requested level when explaining:

- `0`: ELI5, minimal jargon, analogies.
- `1`: Junior, explain why and common mistakes.
- `2`: Mid, include patterns and tradeoffs.
- `3`: Senior, architecture and constraints focus.
- `4`: Lead, risk/business impact and strategy.
- `5`: Expert, concise implementation-first.

### `/docs/init`, `/docs/update`, `/docs/summarize`

- Initialize docs structure with `scripts/docs-init.sh`.
- Keep docs source of truth under `./docs`.

### `/journal`, `/watzup`

- Write concise journal entries in `docs/journals/`.
- For status, summarize plans and git state.

## Helper Scripts

```bash
python3 ${CODEX_HOME:-$HOME/.codex}/skills/claudekit-command-bridge/scripts/resolve-command.py "/docs/update"
${CODEX_HOME:-$HOME/.codex}/skills/claudekit-command-bridge/scripts/docs-init.sh
${CODEX_HOME:-$HOME/.codex}/skills/claudekit-command-bridge/scripts/project-status.sh
```
