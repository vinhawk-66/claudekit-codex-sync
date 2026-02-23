# System Architecture

## High-Level Design

```
┌─────────────────────┐    ┌──────────────────────────┐
│ ClaudeKit Source     │    │ Codex Target              │
│ ~/.claude/ or zip    │───▶│ ./.codex or ~/.codex      │
│   skills/*           │    │   skills/*                │
│   commands/          │    │   claudekit/commands/     │
│   output-styles/     │    │   claudekit/output-styles/│
│   scripts/           │    │   claudekit/scripts/      │
└─────────────────────┘    │   prompts/* (generated)   │
                            │   config.toml             │
                            └──────────────────────────┘
```

Workspace baseline: `./AGENTS.md` is ensured in the current working directory.

## Pipeline

1. **CLI parse (`cli.py`)**
- Select scope: project (default) or global (`-g`)
- Optional fresh cleanup (`-f`)
- Select source: live (`~/.claude/`) or zip (`--zip`)

2. **Asset/skill sync**
- Copy managed assets and skills
- Apply registry-aware overwrite behavior (`--force`)

3. **Normalization**
- Rewrite `.claude` references to `.codex`
- Normalize agent TOMLs and compatibility patches

4. **Config enforcement**
- Enforce `config.toml` defaults
- Enforce `[features]` flags
- Register agents from `agents/*.toml`
- Ensure workspace-level `AGENTS.md` baseline file exists

5. **Prompt export**
- Generate prompt files for Codex runtime from `claudekit/commands/*.md`

6. **Dependency bootstrap**
- Try symlink reuse of `~/.claude/skills/.venv`
- Fallback to local venv + dependency install

7. **Runtime verification**
- Execute health checks and emit summary

## CLI Contract (v0.2)

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

## Design Notes

- Project-first scope reduces accidental global writes while developing.
- `clean_target.py` preserves `skills/.venv` to keep refresh runs fast.
- Registry writes are defensive (`mkdir` before save) to avoid missing-path failures.
- Bootstrap path prefers symlink reuse for speed; fallback path ensures portability.
