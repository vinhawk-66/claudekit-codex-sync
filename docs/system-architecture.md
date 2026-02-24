# System Architecture

## High-Level Design

```
┌─────────────────────┐    ┌──────────────────────────┐
│ ClaudeKit Source     │    │ Codex Target              │
│ ~/.claude/ or zip    │───▶│ ./.codex or ~/.codex      │
│   agents/*.md        │    │   agents/*.toml (convert) │
│   skills/*           │    │   skills/*                │
│   output-styles/     │    │   output-styles/          │
│   rules/             │    │   rules/ (+ generated)    │
│   scripts/           │    │   scripts/                │
└─────────────────────┘    │   config.toml             │
                            └──────────────────────────┘
```

Workspace baseline: `./AGENTS.md` is ensured in the current working directory.

## Pipeline (7 Steps)

1. **CLI parse (`cli.py`)**
   - Select scope: project (default) or global (`-g`)
   - Optional fresh cleanup (`-f`) with safety guard (rejects `/` and `$HOME`)
   - Select source: live (`~/.claude/`) or zip (`--zip`)
   - Fatal error if source missing `skills/` directory

2. **Asset/skill sync**
   - Copy agents `.md` directly to `codex_home/agents/` (for TOML conversion)
   - Copy managed assets (output-styles, rules, scripts) to `codex_home/`
   - Copy skills to `codex_home/skills/`
   - Apply registry-aware overwrite behavior (`--force`)
   - Silent operation — returns counts, no per-item logging

3. **Normalization**
   - Rewrite `.claude` references to `.codex` using `_BASE_PATH_REPLACEMENTS` + context-specific extensions
   - Convert agent `.md` (YAML frontmatter) → `.toml` with model mapping
   - Normalize existing agent TOMLs and compatibility patches

4. **Hook rules generation**
   - Generate `rules/` from hook behavior templates (security-privacy, file-naming, code-quality)

5. **Config enforcement**
   - Enforce `config.toml` defaults and `[features]` flags
   - Register agents from `agents/*.toml`
   - Ensure workspace-level `AGENTS.md` baseline
   - Ensure bridge skill for Codex-native routing

6. **Dependency bootstrap**
   - Try symlink reuse of `~/.claude/skills/.venv`
   - Fallback to local venv + pip install
   - Node deps always run independently (not gated by Python symlink state)

7. **Runtime verification**
   - Health checks with distinct status: `ok` / `failed` / `not-found` / `no-venv`
   - Structured output via `log_formatter.py` (~18 lines compact)

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

- Project-first scope reduces accidental global writes during development.
- Agents copied to top-level `agents/` to match conversion function expectations.
- `clean_target.py` has safety guard — rejects destructive paths (`/`, `$HOME`).
- Bootstrap: Python pip skipped when venv symlinked; Node deps always run.
- Registry writes are defensive (`mkdir` before save).
- Replacement tables use `_BASE_PATH_REPLACEMENTS` + compose pattern (DRY).
- Modules are silent — return data only. `cli.py` handles all terminal output via `log_formatter.py`.
