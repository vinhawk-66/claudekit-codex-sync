# Plan: Refactor & Upgrade ClaudeKit-Codex-Sync

Status: ready
Priority: high

## Overview

Refactor monolithic codebase (1151-line Python + 635-line bash) into modular npm-based project, then upgrade with new capabilities for near-100% Codex effectiveness.

## Phases

- [Phase 1: Project Structure](./phase-01-project-structure.md) — npm init, .gitignore, module dirs | **0.5d**
- [Phase 2: Extract Templates](./phase-02-extract-templates.md) — Move 295 lines of inline strings to files | **0.25d**
- [Phase 3: Modularize Python](./phase-03-modularize-python.md) — Split into 11 modules <200 lines each | **1d**
- [Phase 4: Live Source + Detection](./phase-04-live-source-detection.md) — Add ~/.claude/ direct read + auto-detection | **0.5d**
- [Phase 5: Agent TOML + Config](./phase-05-agent-toml-config.md) — Normalize paths + multi_agent flag | **0.5d**
- [Phase 6: Backup + Registry](./phase-06-backup-registry.md) — SHA-256 checksum tracking + rollback | **0.5d**
- [Phase 7: Tests + Docs + Push](./phase-07-tests-docs-push.md) — Tests, docs, git push | **0.5d**

**Total: ~3.75 days**

## Key Decisions

- **npm + git push** (not pip/PyPI)
- **Python scripts** remain Python, npm wraps them as CLI
- **Bash scripts** deleted (duplicate Python logic)
- **Plans/reports** kept as reference
- **`~/.claude/` live read** as default source (zip fallback)
- **Sub-agent instructions adapted** for Codex model (strip Claude-specific syntax)

## Architecture

```
claudekit-codex-sync/
├── package.json              # npm package
├── bin/
│   └── ck-codex-sync.js      # npm CLI entry → calls Python
├── src/
│   └── claudekit_codex_sync/
│       ├── __init__.py
│       ├── cli.py             # (~100 lines)
│       ├── source_resolver.py # (~80 lines)
│       ├── asset_sync.py      # (~160 lines)
│       ├── path_normalizer.py # (~120 lines)
│       ├── config_enforcer.py # (~80 lines)
│       ├── prompt_exporter.py # (~100 lines)
│       ├── dep_bootstrapper.py# (~60 lines)
│       ├── runtime_verifier.py# (~30 lines)
│       ├── bridge_generator.py# (~30 lines)
│       └── utils.py           # (~90 lines)
├── templates/
│   ├── agents-md.md
│   ├── command-map.md
│   ├── bridge-skill.md
│   ├── bridge-resolve-command.py
│   ├── bridge-docs-init.sh
│   └── bridge-project-status.sh
├── tests/
├── docs/
├── plans/
└── reports/
```

## Success Criteria

- [ ] All Python modules < 200 lines
- [ ] `npm install -g .` works
- [ ] `ck-codex-sync --source-mode live` syncs from ~/.claude/
- [ ] Agent TOMLs: 0 `.claude` references after sync
- [ ] `codex features list | grep multi_agent` → true after sync
- [ ] Tests pass
- [ ] Git clean, ready to push
