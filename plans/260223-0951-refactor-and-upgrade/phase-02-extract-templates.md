# Phase 2: Extract Templates

Status: pending
Priority: high
Effort: 0.25d

## Goal
Move 295 lines of inline template strings from `claudekit-sync-all.py` to separate files in `templates/`.

## Mapping

| Constant (in Python) | Target File | Lines |
|---|---|---|
| `AGENTS_TEMPLATE` (L57-102) | `templates/agents-md.md` | 45 |
| `COMMAND_MAP_TEMPLATE` (L105-149) | `templates/command-map.md` | 44 |
| `BRIDGE_SKILL_TEMPLATE` (L152-215) | `templates/bridge-skill.md` | 63 |
| `BRIDGE_RESOLVE_SCRIPT` (L218-270) | `templates/bridge-resolve-command.py` | 52 |
| `BRIDGE_DOCS_INIT_SCRIPT` (L273-298) | `templates/bridge-docs-init.sh` | 25 |
| `BRIDGE_STATUS_SCRIPT` (L301-350) | `templates/bridge-project-status.sh` | 49 |

## Loading Pattern

In Python modules, use:
```python
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"

def load_template(name: str) -> str:
    return (TEMPLATES_DIR / name).read_text(encoding="utf-8")
```

## Todo
- [ ] Create 6 template files from inline strings
- [ ] Remove inline strings from Python
- [ ] Add `load_template()` utility
