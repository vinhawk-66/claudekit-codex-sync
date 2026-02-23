## Code Review Summary

### Scope
- **Files Modified**: 9 files
  - src/claudekit_codex_sync/constants.py
  - src/claudekit_codex_sync/asset_sync_dir.py
  - src/claudekit_codex_sync/asset_sync_zip.py
  - src/claudekit_codex_sync/prompt_exporter.py
  - src/claudekit_codex_sync/path_normalizer.py
  - src/claudekit_codex_sync/clean_target.py
  - src/claudekit_codex_sync/cli.py
  - docs/codebase-summary.md
  - docs/system-architecture.md
- **LOC Changed**: ~200 lines
- **Focus**: Eliminate claudekit/ subdirectory, copy assets directly to codex_home/
- **Tests**: 22 tests pass

### Overall Assessment
Good structural change that flattens the directory hierarchy. Assets now copy directly to codex_home/ instead of codex_home/claudekit/. All path constants updated consistently. CLI execution order corrected to handle agent conversion before registration.

**Score: 8/10**

---

### Critical Issues
None found.

---

### High Priority Issues

#### 1. Missing Agent Sync in Zip Path (asset_sync_zip.py)
**Issue**: asset_sync_dir.py syncs agents from source/agents/ to codex_home/agents/, but asset_sync_zip.py has no equivalent logic.

**Impact**: Zip-based sync will not copy agents, breaking agent conversion/registration.

**Location**: src/claudekit_codex_sync/asset_sync_zip.py

**Fix**: Add agent sync logic to sync_assets() or create separate sync_agents() function for zip path:
```python
# After processing ASSET_DIRS/ASSET_FILES, add:
for name in zf.namelist():
    if name.startswith(".claude/agents/") and name.endswith(".md"):
        rel = name[len(".claude/"):]
        # sync to codex_home/agents/
```

---

### Medium Priority Issues

#### 2. Inconsistent Empty Directory Cleanup (asset_sync_zip.py:83-89)
**Issue**: The cleanup loop iterates over ALL directories in codex_home, not just asset directories. This could remove empty directories created by other tools.

**Location**: src/claudekit_codex_sync/asset_sync_zip.py lines 83-89

**Current**:
```python
for d in sorted(codex_home.rglob("*"), reverse=True):
    if d.is_dir():
        try:
            d.rmdir()
        except OSError:
            pass
```

**Recommendation**: Limit cleanup to asset directories only, or remove this entirely if not needed.

---

#### 3. Registry Path Tracking Inconsistency
**Issue**: In asset_sync_dir.py, rel_path changed from "claudekit/{dirname}/{rel}" to "{dirname}/{rel}". Existing registries will have stale entries with "claudekit/" prefix.

**Impact**: After upgrade, registry lookups for user-edit detection may fail for existing files.

**Location**: src/claudekit_codex_sync/asset_sync_dir.py line 38

**Mitigation**: Consider registry version bump or migration logic.

---

#### 4. Missing "hooks" Directory in Clean Target
**Issue**: clean_target.py lists asset dirs to clean but "hooks" is missing, though asset_sync_zip.py handles hooks.

**Location**: src/claudekit_codex_sync/clean_target.py line 14

**Current**:
```python
for subdir in ("agents", "prompts", "commands", "output-styles", "rules", "scripts"):
```

**Fix**: Add "hooks" if it should be cleaned during --fresh.

---

### Low Priority Issues

#### 5. Test Coverage Gap for New Agent Sync
**Issue**: No tests verify the new agent sync logic in asset_sync_dir.py (lines 112-132).

**Recommendation**: Add test to verify:
- Agents copied from source/agents/ to codex_home/agents/
- Only .md files copied
- Proper handling of nested agent files

---

#### 6. Documentation Inconsistency (README.md)
**Issue**: README.md line 16 still says assets go to "codex_home/claudekit/" but should say "codex_home/" directly.

**Location**: README.md line 16

**Current**:
```
| **Asset sync** | Copies agents .md → `agents/` (for TOML conversion), commands/output-styles/rules/scripts → `codex_home/claudekit/` |
```

**Fix**: Change "codex_home/claudekit/" to "codex_home/"

---

### Positive Observations

1. **Good**: Path replacements in constants.py are consistent across all three replacement lists (SKILL_MD_REPLACEMENTS, PROMPT_REPLACEMENTS, AGENT_TOML_REPLACEMENTS).

2. **Good**: CLI execution order fix (lines 165-186) correctly places normalize_agent_tomls() before register_agents(), ensuring .toml files exist before registration.

3. **Good**: clean_target.py now properly handles .venv symlinks vs real directories.

4. **Good**: Added .ck.json and .env.example to ASSET_FILES and cleanup list.

5. **Good**: Added "rules" to ASSET_DIRS set.

---

### Recommended Actions (Priority Order)

1. **Fix zip agent sync** - Add agent handling to asset_sync_zip.py
2. **Fix README** - Update asset sync path documentation
3. **Consider registry migration** - Handle old "claudekit/" prefixed entries
4. **Add hooks to clean_target** - If hooks should be cleaned on --fresh
5. **Add tests for agent sync** - Cover new agent copy logic

---

### Edge Cases Verified

| Case | Status |
|------|--------|
| Missing source directories | OK - checked with .exists() |
| Dry run mode | OK - respected throughout |
| Nested agent files | OK - uses rglob("*.md") |
| Empty directories after sync | OK - cleanup in zip sync |
| Symlinked .venv | OK - preserved in clean_target |
| Real .venv directory | OK - deleted for re-symlink |

---

### Unresolved Questions

1. Should "hooks" directory be added to clean_target.py cleanup list?
2. Is there a migration strategy for existing registry entries with "claudekit/" prefix?
3. Should asset_sync_zip.py also sync agents like asset_sync_dir.py does?
