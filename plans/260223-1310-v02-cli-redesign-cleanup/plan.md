# v0.2 Plan — CLI Redesign + Cleanup

## Overview

| Phase | What | Files | Status |
|---|---|---|---|
| 1 | Delete dead code + trim constants | `scripts/`, `constants.py` | [x] Complete |
| 2 | CLI redesign (ckc-sync, 8 flags) | `cli.py`, `clean_target.py`, `package.json`, `bin/` | [x] Implemented (local install step pending) |
| 3 | Symlink venv | `dep_bootstrapper.py` | [x] Complete |
| 4 | Wire unused functions + backup | `cli.py`, `asset_sync_dir.py`, `sync_registry.py` | [x] Complete |
| 5 | Safety fixes + tests + docs | `path_normalizer.py`, tests, docs | [x] Implemented (release ops pending) |

Details: see phase files.

## Tracking Notes
- Validation run on 2026-02-23: `python3 -m py_compile src/claudekit_codex_sync/*.py` passed.
- Validation run on 2026-02-23: `PYTHONPATH=src python3 -m pytest tests/ -q` passed (`21 passed`).
- Pending non-implementation ops: `npm install -g .`, `git commit && git push && npm publish`.
