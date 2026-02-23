# Test Report: claudekit-codex-sync v0.2.3+fix

**Date:** 2026-02-23 16:25  
**Scope:** Pre-push deep verification after eliminating `claudekit/` subdirectory  
**Changes tested:** `constants.py`, `clean_target.py`, `asset_sync_dir.py`, `asset_sync_zip.py`, `path_normalizer.py`, `prompt_exporter.py`

---

## 1. Unit Tests — 22/22 ✅

| Module | Tests | Status |
|---|---|---|
| `test_clean_target.py` | 5 | ✅ |
| `test_cli_args.py` | 6 | ✅ |
| `test_config_enforcer.py` | 4 | ✅ |
| `test_path_normalizer.py` | 7 | ✅ |

## 2. Compile Check — 8/8 ✅

All 8 modified Python modules compile without errors.

## 3. E2E Sync (local source, `--fresh`) — ✅

| Metric | Value |
|---|---|
| Assets added | 146 |
| Skills added | 54 (4 skipped) |
| Normalize changed | 28 |
| Agents converted & registered | 14 |
| Prompts generated | 20 |
| Verify | codex=ok, copywriting=ok |

## 4. Filesystem Validation — 7/7 ✅

| Check | Result |
|---|---|
| `~/.codex/claudekit/` does NOT exist | ✅ |
| `~/.codex/scripts/` (17 files) | ✅ |
| `~/.codex/rules/` (5 files) | ✅ |
| `~/.codex/commands/` (22 files) | ✅ |
| `~/.codex/hooks/` (81 files) | ✅ |
| `~/.codex/output-styles/` (6 files) | ✅ |
| `~/.codex/.ck.json` + `.env.example` | ✅ |

## 5. Reference Integrity — 5/5 ✅

Zero stale `claudekit/` filesystem paths found in:

| Location | Stale refs |
|---|---|
| Skills | 0 |
| Agent TOMLs | 0 |
| Prompts | 0 (1 GitHub URL, correctly excluded) |
| Rules | 0 |
| Commands | 0 |

## 6. Runtime Script Execution — 5/5 ✅

| Script | Language | Exit | Notes |
|---|---|---|---|
| `set-active-plan.cjs` | Node.js | 0 | Requires `../hooks/lib/` — now synced |
| `validate-docs.cjs` | Node.js | 0 | Generated validation report |
| `worktree.cjs list` | Node.js | 0 | Listed 1 worktree |
| `ck-help.py` | Python | 0 | CK help search works |
| `fix-shebang-permissions.sh` | Bash | 0 | Expected "Error: .claude not found" (runs from codex context) |

---

## Bugs Found & Fixed

| Bug | Severity | Fix |
|---|---|---|
| Scripts crash with `MODULE_NOT_FOUND` for `../hooks/lib/` | **High** | Added `hooks` to `ASSET_DIRS` in `constants.py` |
| Stale `claudekit/` dir not cleaned on fresh sync | **Medium** | Added `"claudekit"` to clean list in `clean_target.py` |

## Verdict

**✅ ALL 6 TEST CATEGORIES PASS — READY TO PUSH**
