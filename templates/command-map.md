# ClaudeKit -> Codex Command Map

## Covered by existing skills

- `/preview` -> `markdown-novel-viewer`
- `/kanban` -> `plans-kanban`
- `/review/codebase` -> `code-review`
- `/test`, `/test/ui` -> `web-testing`
- `/worktree` -> `git`
- `/plan/*` -> `plan`

## Converted into bridge workflows

- `/ck-help` -> `claudekit-command-bridge` (`resolve-command.py`)
- `/coding-level` -> `claudekit-command-bridge` (depth rubric + output styles)
- `/ask` -> `claudekit-command-bridge` (architecture mode)
- `/docs/init`, `/docs/update`, `/docs/summarize` -> `claudekit-command-bridge`
- `/journal`, `/watzup` -> `claudekit-command-bridge`

## Explicitly excluded in this sync

- `/use-mcp` (excluded when `--include-mcp` is not set)
- Hooks (excluded when `--include-hooks` is not set)

## Custom Prompt Aliases (`/prompts:<name>`)

- `/ask` -> `/prompts:ask`
- `/ck-help` -> `/prompts:ck-help`
- `/coding-level` -> `/prompts:coding-level`
- `/docs/init` -> `/prompts:docs-init`
- `/docs/summarize` -> `/prompts:docs-summarize`
- `/docs/update` -> `/prompts:docs-update`
- `/journal` -> `/prompts:journal`
- `/kanban` -> `/prompts:kanban`
- `/plan/archive` -> `/prompts:plan-archive`
- `/plan/red-team` -> `/prompts:plan-red-team`
- `/plan/validate` -> `/prompts:plan-validate`
- `/preview` -> `/prompts:preview`
- `/review/codebase` -> `/prompts:review-codebase`
- `/review/codebase/parallel` -> `/prompts:review-codebase-parallel`
- `/test` -> `/prompts:test`
- `/test/ui` -> `/prompts:test-ui`
- `/watzup` -> `/prompts:watzup`
- `/worktree` -> `/prompts:worktree`
