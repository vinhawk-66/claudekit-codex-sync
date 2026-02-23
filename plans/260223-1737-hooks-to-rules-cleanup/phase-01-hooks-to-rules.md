# Phase 1: Remove Hooks, Generate Rules

Status: pending
Priority: critical
Effort: 0.5d

## Goal

Stop syncing hooks (dead code). Create rules that replicate hook behavior at startup.

## Context

- 15 hooks use Claude Code's hook API (SessionStart, PreToolUse, etc.)
- Codex CLI has NO hooks support — hooks dir is dead code
- Rules (`~/.codex/rules/*.md`) load at startup = always in context = equivalent to hooks

## Steps

### 1.1 Remove `"hooks"` from ASSET_DIRS

**File:** [constants.py](file:///home/vinhawk/claudekit-codex-sync/src/claudekit_codex_sync/constants.py)

```diff
-ASSET_DIRS = {"commands", "output-styles", "rules", "scripts", "hooks"}
+ASSET_DIRS = {"output-styles", "rules", "scripts"}
```

> Also removes `"commands"` — Phase 2 handles this.

### 1.2 Create rule templates

**File:** `templates/rule-security-privacy.md` [NEW]

```markdown
# Security & Privacy

## Sensitive File Access
Ask user for explicit approval before reading:
- `.env`, `.env.*` (API keys, passwords, tokens)
- `*.key`, `*.pem`, `*.p12`, `credentials.*`, `secrets.*`
- Files in `~/.ssh/`, `~/.gnupg/`, `~/.aws/`

**Flow:** State which file and why → wait for "yes" → read via cat → never output full secrets.

## Directory Access Control
Respect `.ckignore` patterns if present in project root:
- Read `.ckignore` at session start
- Do NOT access matching directories
- Common: `node_modules/`, `dist/`, `build/`, `.git/objects/`
```

**File:** `templates/rule-file-naming.md` [NEW]

```markdown
# File Naming

Apply before every file creation (skip for markdown/text):
- **JS/TS/Python/shell**: kebab-case with descriptive names
- **C#/Java/Kotlin/Swift**: PascalCase
- **Go/Rust**: snake_case
- Goal: self-documenting names for LLM tools (Grep, Glob, Search)
```

**File:** `templates/rule-code-quality.md` [NEW]

```markdown
# Code Quality Reminders

## Code Simplification
After significant file edits (5+), consider running code-simplifier agent.

## Post-Planning
After creating an implementation plan, always activate the cook skill before implementation.

## Modularization
If a code file exceeds 200 lines, consider modularizing it.
```

### 1.3 Create rules_generator module

**File:** `src/claudekit_codex_sync/rules_generator.py` [NEW]

```python
"""Generate hook-equivalent rules from templates."""

from __future__ import annotations

from pathlib import Path

from .utils import load_template, write_text_if_changed


RULE_TEMPLATES = {
    "security-privacy.md": "rule-security-privacy.md",
    "file-naming.md": "rule-file-naming.md",
    "code-quality-reminders.md": "rule-code-quality.md",
}


def generate_hook_rules(*, codex_home: Path, dry_run: bool) -> int:
    """Generate rules that replace ClaudeKit hook behavior."""
    rules_dir = codex_home / "rules"
    if not dry_run:
        rules_dir.mkdir(parents=True, exist_ok=True)

    generated = 0
    for rule_name, template_name in RULE_TEMPLATES.items():
        content = load_template(template_name)
        target = rules_dir / rule_name
        if write_text_if_changed(target, content, dry_run=dry_run):
            generated += 1
            print(f"upsert: rules/{rule_name}")

    return generated
```

### 1.4 Fix `set-active-plan.cjs` hooks/lib dependency

> [!WARNING]
> **Discovered via Codex CLI live testing (`cxp --full-auto`)**:
> `set-active-plan.cjs` line 16: `require('../hooks/lib/ck-config-utils.cjs')`.
> Currently works because hooks ARE synced. **Will break after removing hooks.**
> Only uses 2 functions: `readSessionState` + `writeSessionState` (~20 lines total).

**File:** `scripts/set-active-plan.cjs` (source in `~/.claude/scripts/`)

Inline the 3 tiny functions to remove hooks/lib dependency:

```diff
-const { writeSessionState, readSessionState } = require('../hooks/lib/ck-config-utils.cjs');
+// Inlined from hooks/lib/ck-config-utils.cjs (hooks removed in v0.2.5)
+function getSessionTempPath(sessionId) {
+  return path.join(os.tmpdir(), `ck-session-${sessionId}.json`);
+}
+function readSessionState(sessionId) {
+  if (!sessionId) return null;
+  const tempPath = getSessionTempPath(sessionId);
+  try {
+    if (!fs.existsSync(tempPath)) return null;
+    return JSON.parse(fs.readFileSync(tempPath, 'utf8'));
+  } catch (e) { return null; }
+}
+function writeSessionState(sessionId, state) {
+  if (!sessionId) return false;
+  const tempPath = getSessionTempPath(sessionId);
+  const tmpFile = tempPath + '.' + Math.random().toString(36).slice(2);
+  try {
+    fs.writeFileSync(tmpFile, JSON.stringify(state, null, 2));
+    fs.renameSync(tmpFile, tempPath);
+    return true;
+  } catch (e) {
+    try { fs.unlinkSync(tmpFile); } catch (_) {}
+    return false;
+  }
+}
```

Also need to add `const os = require('os');` if not already present.

**Option**: Instead of modifying source, apply this patch during sync in `path_normalizer.py`
by replacing the `require('../hooks/lib/...')` line with inlined functions.

## Codex CLI Live Test Results (cxp --full-auto)

| Script | Status | Notes |
|---|---|---|
| `ck-help.py` | ✅ OK | |
| `resolve_env.py` | ✅ OK | |
| `scan_commands.py` | ✅ OK | |
| `scan_skills.py` | ✅ OK | |
| `set-active-plan.cjs` (no args) | ⚠️ FAIL | Expected: usage error |
| `set-active-plan.cjs` (with plan) | ✅ OK | BUT depends on `../hooks/lib/` |
| `test-ck-help.py` | ✅ OK | |
| `test_ck_help.py` | ⚠️ FAIL | Pre-existing: intent detection mismatch |
| `test_ck_help_integration.py` | ⚠️ FAIL | Pre-existing: 17 pass / 2 fail |
| `validate-docs.cjs` | ✅ OK | |
| `win_compat.py` | ✅ OK | |
| `worktree.cjs` (no args) | ⚠️ FAIL | Expected: usage error |
| `worktree.test.cjs` | ⚠️ FAIL | Pre-existing test failures |

**Summary**: 8 OK / 5 FAIL. Of 5 FAILs: 2 expected (no-args usage), 2 pre-existing test bugs, 1 dependency issue (set-active-plan → hooks/lib).

## Todo

- [ ] Remove `"hooks"` and `"commands"` from `ASSET_DIRS`
- [ ] Create `templates/rule-security-privacy.md`
- [ ] Create `templates/rule-file-naming.md`
- [ ] Create `templates/rule-code-quality.md`
- [ ] Create `src/claudekit_codex_sync/rules_generator.py`
- [ ] Fix `set-active-plan.cjs` hooks/lib dependency (inline or patch during sync)
- [ ] Compile check: `python3 -m py_compile src/claudekit_codex_sync/rules_generator.py`

## Verification

```bash
python3 -m py_compile src/claudekit_codex_sync/rules_generator.py
python3 -m py_compile src/claudekit_codex_sync/constants.py
ls templates/rule-*.md  # should show 3 files
# After sync, verify set-active-plan.cjs no longer depends on hooks:
grep -c "hooks/lib" ~/.codex/scripts/set-active-plan.cjs  # should be 0
node ~/.codex/scripts/set-active-plan.cjs plans/test 2>&1 | head -5  # should not MODULE_NOT_FOUND
```
