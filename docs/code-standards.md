# Code Standards

## Language & Runtime

- **Python 3.12+** — Core sync logic
- **Node.js** — CLI wrapper only (`bin/ck-codex-sync.js`)
- No external Python dependencies in core (stdlib only: `pathlib`, `re`, `shutil`, `json`, `zipfile`, `argparse`, `hashlib`)

## File Organization

- **Kebab-case** for filenames: `asset-sync-dir.py` (Python uses snake_case for modules, so `asset_sync_dir.py`)
- **Max 200 LOC** per module — enforced; largest is `path_normalizer.py` at 248 (due to agent conversion addition, refactor candidate)
- **One concern per module** — each `.py` file handles exactly one phase of the sync pipeline
- Constants separated into `constants.py`; utilities into `utils.py`

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Modules | `snake_case` | `config_enforcer.py` |
| Functions | `snake_case` | `enforce_multi_agent_flag()` |
| Constants | `UPPER_SNAKE_CASE` | `CLAUDE_TO_CODEX_MODELS` |
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

## Error Handling

- Custom `SyncError` exception for user-facing errors
- `eprint()` for stderr output
- CLI catches `SyncError` → exits with code 2
- No silent failures — all operations log what they change

## Testing

- Framework: **pytest**
- Location: `tests/`
- Naming: `test_<module>.py`
- Run: `PYTHONPATH=src python3 -m pytest tests/ -v`
- Current coverage: `config_enforcer` (4 tests), `path_normalizer` (7 tests)

## Path Conventions

All paths use `Path` objects (not strings). Environment-based paths use `${CODEX_HOME:-$HOME/.codex}` pattern.

## Git Conventions

- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- No AI references in commit messages
- `.gitignore`: `__pycache__/`, `*.pyc`, `node_modules/`, `.pytest_cache/`
