# Phase 4: Version Bump, Docs, Tests

Status: pending
Priority: medium
Effort: 0.5d

## Goal

Bump to v0.2.5. Update docs. Add tests for `rules_generator`. Run full verification.

## Steps

### 4.1 Version bump

**File:** [package.json](file:///home/vinhawk/claudekit-codex-sync/package.json)

```diff
-  "version": "0.2.4",
+  "version": "0.2.5",
```

### 4.2 Add test for rules_generator

**File:** `tests/test_rules_generator.py` [NEW]

```python
"""Tests for rules_generator module."""

from pathlib import Path

from claudekit_codex_sync.rules_generator import generate_hook_rules


def test_generates_all_rule_files(tmp_path: Path):
    """Generates 3 rule files."""
    count = generate_hook_rules(codex_home=tmp_path, dry_run=False)
    assert count == 3
    assert (tmp_path / "rules" / "security-privacy.md").exists()
    assert (tmp_path / "rules" / "file-naming.md").exists()
    assert (tmp_path / "rules" / "code-quality-reminders.md").exists()


def test_idempotent(tmp_path: Path):
    """Second run returns 0 (no changes)."""
    generate_hook_rules(codex_home=tmp_path, dry_run=False)
    count = generate_hook_rules(codex_home=tmp_path, dry_run=False)
    assert count == 0


def test_dry_run(tmp_path: Path):
    """Dry run counts but doesn't create."""
    count = generate_hook_rules(codex_home=tmp_path, dry_run=True)
    assert count == 3
    assert not (tmp_path / "rules").exists()
```

### 4.3 Update README

**File:** [README.md](file:///home/vinhawk/claudekit-codex-sync/README.md)

Update "What It Does" table:
- Remove `Prompt export` row
- Remove hooks from `Asset sync` description
- Add `Hook rules` row: "Generates rules/ from hook behavior (security-privacy, file-naming, code-quality)"

### 4.4 Update system-architecture

**File:** [docs/system-architecture.md](file:///home/vinhawk/claudekit-codex-sync/docs/system-architecture.md)

- Remove Step 5 (Prompt export) from pipeline
- Add step: "Hook rules generation"
- Remove `hooks/` from architecture diagram
- Remove `prompts/* (generated)` from diagram

### 4.5 Update project roadmap

**File:** [docs/project-roadmap.md](file:///home/vinhawk/claudekit-codex-sync/docs/project-roadmap.md)

Add v0.2.5 section:

```markdown
## v0.2.5 - Hooks→Rules + Remove Prompts

**Status:** Complete

- [x] Remove hooks sync (Codex has no hooks API)
- [x] Generate hook-equivalent rules (security-privacy, file-naming, code-quality)
- [x] Remove commands sync (deprecated concept)
- [x] Remove prompt export step (deprecated by OpenAI)
- [x] Update bridge skill for Codex-native routing
- [x] Add syntax adaptations for Claude→Codex patterns
- [x] Add test coverage for rules_generator
```

## Todo

- [ ] Bump version in `package.json`
- [ ] Create `tests/test_rules_generator.py`
- [ ] Update `README.md`
- [ ] Update `docs/system-architecture.md`
- [ ] Update `docs/project-roadmap.md`

## Final Verification (all 10 steps)

```bash
# 1. Compile check
python3 -m py_compile src/claudekit_codex_sync/*.py

# 2. Run all tests
PYTHONPATH=src python3 -m pytest tests/ -v

# 3. Dry-run sync
PYTHONPATH=src python3 -m claudekit_codex_sync.cli -g -n

# 4. Actual sync (fresh)
PYTHONPATH=src python3 -m claudekit_codex_sync.cli -g -f --force

# 5. Verify hooks NOT synced
ls ~/.codex/hooks/ 2>/dev/null && echo "FAIL" || echo "OK: no hooks"

# 6. Verify rules generated
ls ~/.codex/rules/security-privacy.md ~/.codex/rules/file-naming.md ~/.codex/rules/code-quality-reminders.md

# 7. Verify no prompts generated
[ ! -f ~/.codex/prompts/.claudekit-generated-prompts.txt ] && echo "OK" || echo "FAIL"

# 8. Verify no commands dir
ls ~/.codex/commands/ 2>/dev/null && echo "WARN: commands exist" || echo "OK"

# 9. Verify existing rules intact
ls ~/.codex/rules/development-rules.md ~/.codex/rules/primary-workflow.md

# 10. Token budget check
du -b ~/.codex/rules/*.md | awk '{sum+=$1} END {print "Rules: " sum " bytes / 32768 limit"}'
```
