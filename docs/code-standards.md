# Code Standards

## Language & Runtime

- **Python 3.12+** — Core sync logic
- **Node.js** — CLI wrapper only (`bin/ck-codex-sync.js`)
- No external Python dependencies in core (stdlib only: `pathlib`, `re`, `shutil`, `json`, `zipfile`, `argparse`, `hashlib`, `subprocess`)

## File Organization

- **Kebab-case** for filenames: `asset-sync-dir.py` (Python uses snake_case for modules, so `asset_sync_dir.py`)
- **Max 200 LOC** per module — enforced; largest is `cli.py` at 279 LOC (orchestrator exception) and `path_normalizer.py` at 255 LOC (refactor candidate)
- **One concern per module** — each `.py` file handles exactly one phase of the sync pipeline
- Constants separated into `constants.py`; utilities into `utils.py`
- Logging centralized in `log_formatter.py`; modules return data only

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Modules | `snake_case` | `config_enforcer.py` |
| Functions | `snake_case` | `enforce_multi_agent_flag()` |
| Constants | `UPPER_SNAKE_CASE` | `CLAUDE_TO_CODEX_MODELS` |
| Private constants | `_UPPER_SNAKE_CASE` | `_BASE_PATH_REPLACEMENTS` |
| Classes | `PascalCase` (none yet) | — |
| Template files | `kebab-case` | `bridge-skill.md` |

## Function Signatures

All public functions follow the pattern:
```python
def function_name(*, codex_home: Path, dry_run: bool) -> int:
    """One-line docstring."""
```

- Keyword-only args (`*` marker) for clarity
- `dry_run` flag on all write operations
- Return `int` (count of changed files) or `bool` (whether changes made)
- `Dict[str, Any]` for stats output
- **No print statements in modules** — all logging via `cli.py` + `log_formatter.py`

## Error Handling

- Custom `SyncError` exception for user-facing errors
- `eprint()` for stderr output (used only in `utils.py`)
- CLI catches `SyncError` → exits with code 2
- Safety guards: `clean_target` rejects `/` and `$HOME`; `validate_source` is fatal when `skills/` missing
- `log_error()` / `log_warn()` for structured error output to stderr

## Testing

- Framework: **pytest**
- Location: `tests/`
- Naming: `test_<module>.py`
- Run: `PYTHONPATH=src python3 -m pytest tests/ -v`
- Current count: **39 tests** across 9 test files
- Coverage: asset sync, agent converter, safety guards, runtime verifier, path normalizer, config enforcer, clean target, CLI args, rules generator

## Logging Architecture

- `log_formatter.py` — centralized output module (ANSI color, TTY detection, `NO_COLOR` support)
- Modules return data only (counts, stats dicts)
- `cli.py` calls `log_header()`, `log_section()`, `log_summary()`, `log_ok()`, `log_skip()`, `log_done()`
- Output: ~18 lines compact with Unicode symbols (`✓`, `↻`, `⊘`, `▸`)

## Path Conventions

All paths use `Path` objects (not strings). Environment-based paths use `${CODEX_HOME:-$HOME/.codex}` pattern. Replacement tables use `_BASE_PATH_REPLACEMENTS` + compose pattern for DRY.

## Git Conventions

- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- No AI references in commit messages
- `.gitignore`: `__pycache__/`, `*.pyc`, `node_modules/`, `.pytest_cache/`
