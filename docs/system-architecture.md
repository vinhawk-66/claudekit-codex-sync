# System Architecture

## High-Level Design

```
┌─────────────────────┐    ┌──────────────────────────┐
│ ClaudeKit Source     │    │ Codex Target              │
│ ~/.claude/ or zip    │───▶│ ./.codex or ~/.codex      │
│   agents/*.md        │    │   agents/*.toml (convert) │
│   skills/*           │    │   skills/*                │
│   output-styles/     │    │   output-styles/          │
│   rules/             │    │   rules/                  │
│   scripts/           │    │   scripts/                │
└─────────────────────┘    │   config.toml             │
                            └──────────────────────────┘
```

Workspace baseline: `./AGENTS.md` is ensured in the current working directory.

## Pipeline

1. **CLI parse (`cli.py`)**
- Select scope: project (default) or global (`-g`)
- Optional fresh cleanup (`-f`)
- Select source: live (`~/.claude/`) or zip (`--zip`)

2. **Asset/skill sync**
- Copy agents `.md` directly to `codex_home/agents/` (for TOML conversion)
- Copy managed assets (output-styles, rules, scripts) to `codex_home/` directly
- Copy skills to `codex_home/skills/`
- Apply registry-aware overwrite behavior (`--force`)

3. **Normalization**
- Rewrite `.claude` references to `.codex`
- Convert agent `.md` (YAML frontmatter) → `.toml` with model mapping
- Normalize existing agent TOMLs and compatibility patches

4. **Config enforcement**
- Enforce `config.toml` defaults
- Enforce `[features]` flags
- Register agents from `agents/*.toml`
- Ensure workspace-level `AGENTS.md` baseline file exists

5. **Hook rules generation**
- Generate rules/ from hook behavior templates (security-privacy, file-naming, code-quality)

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
- Agents copied to top-level `agents/` (not `claudekit/agents/`) to match conversion function expectations.
- `clean_target.py` deletes real `.venv` dirs (keeps symlinks) so re-symlink works on refresh.
- Bootstrap skips pip install when venv is symlinked — packages already present.
- Registry writes are defensive (`mkdir` before save) to avoid missing-path failures.
