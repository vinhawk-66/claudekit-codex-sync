# Phase 4: Tests, Docs, Release

**Priority:** Medium
**Status:** `[ ]` Not started
**Files:** Tests, `README.md`, `docs/system-architecture.md`, `docs/codebase-summary.md`

## Overview

Verify changes, update docs, bump version, push git + npm publish.

## Changes

### Tests

Update `test_clean_target.py` — test now cleans individual dirs not `claudekit/`.

### Docs

#### system-architecture.md — Update diagram

```diff
 │   agents/*.toml (convert) │
 │   skills/*                │
-│   claudekit/commands/     │
-│   claudekit/output-styles/│
-│   claudekit/rules/        │
-│   claudekit/scripts/      │
+│   commands/               │
+│   output-styles/          │
+│   rules/                  │
+│   scripts/                │
```

#### README.md — Update sync table

```diff
-| **Asset sync** | Copies agents → `agents/`, commands/output-styles/rules/scripts → `codex_home/claudekit/` |
+| **Asset sync** | Copies agents → `agents/`, commands/output-styles/rules/scripts → `codex_home/` directly |
```

### Release

1. `npm version patch` → v0.2.3
2. `git add -A && git commit`
3. `git push origin master`
4. `npm publish --access public`

## Verification Plan

```bash
# Compile
python3 -m py_compile src/claudekit_codex_sync/*.py

# Tests
PYTHONPATH=src python3 -m pytest tests/ -v

# E2E
ckc-sync -g -f

# Filesystem
ls ~/.codex/scripts/      # exists with ClaudeKit scripts
ls ~/.codex/rules/        # exists  
ls ~/.codex/commands/     # exists
ls ~/.codex/claudekit/    # SHOULD NOT EXIST
grep -r "claudekit/" ~/.codex/skills/ | wc -l  # should be 0
```

## Todo

- [ ] Update tests
- [ ] Update `system-architecture.md`
- [ ] Update `codebase-summary.md`
- [ ] Update `README.md`
- [ ] Run full test suite
- [ ] E2E verify on real filesystem
- [ ] Bump version, commit, push, npm publish

## Success Criteria

- 22+ tests pass
- `~/.codex/claudekit/` does NOT exist after sync
- All assets at top-level `~/.codex/` dirs
- Skills reference `~/.codex/scripts/` (no `claudekit/`)
- v0.2.3 published to npm
