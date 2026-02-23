# Phase 3: Update Bridge Skill + Syntax Adaptations

Status: pending
Priority: medium
Effort: 0.25d

## Goal

Update bridge skill description. Add syntax adaptations for remaining Claude-specific patterns.

## Steps

### 3.1 Update bridge skill template

**File:** [templates/bridge-skill.md](file:///home/vinhawk/claudekit-codex-sync/templates/bridge-skill.md)

```diff
 ---
 name: claudekit-command-bridge
-description: Bridge legacy ClaudeKit commands to Codex-native workflows. Use when users mention /ck-help, /coding-level, /ask, /docs/*, /journal, /watzup, or ask for Claude command equivalents.
+description: Bridge legacy ClaudeKit slash commands to Codex-native skills. Activates when users mention /ck-help, /coding-level, /ask, /docs/*, /journal, /watzup, or ask for Claude command equivalents.
 ---

-# ClaudeKit Command Bridge
+# ClaudeKit → Codex Bridge

-Translate ClaudeKit command intent into Codex skills/workflows.
+Translate ClaudeKit command intent into Codex-native skills.
```

### 3.2 Add syntax adaptations

**File:** [constants.py](file:///home/vinhawk/claudekit-codex-sync/src/claudekit_codex_sync/constants.py)

Add entries to `CLAUDE_SYNTAX_ADAPTATIONS`:

```diff
 CLAUDE_SYNTAX_ADAPTATIONS: List[Tuple[str, str]] = [
     ("Task(Explore)", "the explore agent"),
     ("Task(researcher)", "the researcher agent"),
     ("Task(", "delegate to "),
     ("$HOME/.claude/skills/*", "${CODEX_HOME:-$HOME/.codex}/skills/*"),
+    ("via Task tool", "via agent delegation"),
+    ("Claude Code", "Codex CLI"),
+    ("claude code", "Codex CLI"),
 ]
```

## Todo

- [ ] Update `templates/bridge-skill.md` description
- [ ] Add syntax adaptations to `constants.py`

## Verification

```bash
python3 -m py_compile src/claudekit_codex_sync/constants.py
grep "Codex-native skills" templates/bridge-skill.md  # should match
```
