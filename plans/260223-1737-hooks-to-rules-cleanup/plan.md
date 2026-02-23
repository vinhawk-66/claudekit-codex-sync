# v0.2.5 — Hooks→Rules, Remove Commands/Prompts, Harden Pipeline

Remove non-functional hooks, eliminate commands/prompts bloat, generate hook-equivalent rules.

## Problem

- 15+ hooks copied to `~/.codex/hooks/` but Codex CLI has no hooks API → dead code
- Commands duplicated as both `commands/` and `prompts/` → bloat
- Custom prompts [deprecated by OpenAI](https://developers.openai.com/codex/custom-prompts)
- Bridge skill already maps legacy commands → Codex skills

## Phases

| # | Phase | Status | Key Changes |
|---|---|---|---|
| 1 | [Remove hooks, generate rules](phase-01-hooks-to-rules.md) | `[x]` | `constants.py`, 3 templates, `rules_generator.py` |
| 2 | [Remove commands/prompts](phase-02-remove-commands-prompts.md) | `[x]` | `cli.py`, `clean_target.py` |
| 3 | [Update bridge skill + syntax](phase-03-bridge-and-syntax.md) | `[x]` | `templates/bridge-skill.md`, `constants.py` |
| 4 | [Version bump, docs, tests](phase-04-version-docs-tests.md) | `[x]` | `package.json`, `README.md`, docs, tests |

## Before → After

```
~/.codex/                     ~/.codex/
  hooks/  ❌ NOT WORKING        rules/
    15+ .cjs files               development-rules.md    ← existing
  commands/  ⚠️ deprecated       primary-workflow.md     ← existing
    18+ .md files                 security-privacy.md     ← NEW from hooks
  prompts/   ⚠️ duplicate        file-naming.md          ← NEW from hooks
    18+ .md files                 code-quality-reminders.md ← NEW from hooks
  rules/   ✅                   skills/  ✅ unchanged
  skills/  ✅                   agents/  ✅ unchanged
  agents/  ✅                   scripts/ ✅ unchanged
```

## Dependencies

Phase 1 → Phase 2 → Phase 3 → Phase 4 (strict sequential)

## Research Sources

- [Codex Skills docs](https://developers.openai.com/codex/skills): Skills at `$HOME/.agents/skills/`
- [Custom Prompts docs](https://developers.openai.com/codex/custom-prompts): **Deprecated**, use skills
- Codex rules: `~/.codex/rules/*.md` loaded at startup, always in context
- Token budget: 37 KiB used / 65 KiB limit → ~28 KiB remaining

## Risk

Low — removes dead code, generates static rules from templates. No logic change to working features.
