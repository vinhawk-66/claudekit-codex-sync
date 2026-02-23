# Phase 1: Path Rewrites

**Priority:** Critical (all other phases depend on this)
**Status:** `[ ]` Not started
**File:** `src/claudekit_codex_sync/constants.py`

## Overview

Remove `claudekit/` from all replacement target paths in 3 replacement lists + 1 adaptation list.

## Key Insight

Every `claudekit/` in the target side of replacements becomes unnecessary when assets live at `codex_home/` directly.

## Changes

### SKILL_MD_REPLACEMENTS (L15-35)

```python
SKILL_MD_REPLACEMENTS: List[Tuple[str, str]] = [
    ("$HOME/.claude/skills/", "${CODEX_HOME:-$HOME/.codex}/skills/"),
    ("$HOME/.claude/scripts/", "${CODEX_HOME:-$HOME/.codex}/scripts/"),
    ("$HOME/.claude/rules/", "${CODEX_HOME:-$HOME/.codex}/rules/"),
    ("$HOME/.claude/", "${CODEX_HOME:-$HOME/.codex}/"),
    ("./.claude/skills/", "${CODEX_HOME:-$HOME/.codex}/skills/"),
    (".claude/skills/", "${CODEX_HOME:-$HOME/.codex}/skills/"),
    ("./.claude/scripts/", "${CODEX_HOME:-$HOME/.codex}/scripts/"),
    (".claude/scripts/", "${CODEX_HOME:-$HOME/.codex}/scripts/"),
    ("./.claude/rules/", "${CODEX_HOME:-$HOME/.codex}/rules/"),
    (".claude/rules/", "${CODEX_HOME:-$HOME/.codex}/rules/"),
    ("~/.claude/.ck.json", "~/.codex/.ck.json"),
    ("./.claude/.ck.json", "~/.codex/.ck.json"),
    (".claude/.ck.json", "~/.codex/.ck.json"),
    ("~/.claude/", "~/.codex/"),
    ("./.claude/", "./.codex/"),
    ("<project>/.claude/", "<project>/.codex/"),
    (".claude/", ".codex/"),
    ("`.claude`", "`.codex`"),
    ("$HOME/${CODEX_HOME:-$HOME/.codex}/", "${CODEX_HOME:-$HOME/.codex}/"),
]
```

### PROMPT_REPLACEMENTS (L37-52)

```python
PROMPT_REPLACEMENTS: List[Tuple[str, str]] = [
    ("$HOME/.claude/skills/", "${CODEX_HOME:-$HOME/.codex}/skills/"),
    ("$HOME/.claude/scripts/", "${CODEX_HOME:-$HOME/.codex}/scripts/"),
    ("$HOME/.claude/rules/", "${CODEX_HOME:-$HOME/.codex}/rules/"),
    ("$HOME/.claude/", "${CODEX_HOME:-$HOME/.codex}/"),
    ("./.claude/skills/", "~/.codex/skills/"),
    (".claude/skills/", "~/.codex/skills/"),
    ("./.claude/scripts/", "~/.codex/scripts/"),
    (".claude/scripts/", "~/.codex/scripts/"),
    ("./.claude/rules/", "~/.codex/rules/"),
    (".claude/rules/", "~/.codex/rules/"),
    ("~/.claude/.ck.json", "~/.codex/.ck.json"),
    ("./.claude/.ck.json", "~/.codex/.ck.json"),
    (".claude/.ck.json", "~/.codex/.ck.json"),
    ("$HOME/${CODEX_HOME:-$HOME/.codex}/", "${CODEX_HOME:-$HOME/.codex}/"),
]
```

### AGENT_TOML_REPLACEMENTS (L54-62)

```python
AGENT_TOML_REPLACEMENTS: List[Tuple[str, str]] = [
    ("$HOME/.claude/skills/", "${CODEX_HOME:-$HOME/.codex}/skills/"),
    ("$HOME/.claude/scripts/", "${CODEX_HOME:-$HOME/.codex}/scripts/"),
    ("$HOME/.claude/rules/", "${CODEX_HOME:-$HOME/.codex}/rules/"),
    ("$HOME/.claude/.ck.json", "${CODEX_HOME:-$HOME/.codex}/.ck.json"),
    ("$HOME/.claude/.mcp.json", "${CODEX_HOME:-$HOME/.codex}/.mcp.json"),
    ("$HOME/.claude/", "${CODEX_HOME:-$HOME/.codex}/"),
    ("~/.claude/", "~/.codex/"),
]
```

## Todo

- [ ] Replace all 3 lists + remove double-expansion fix
- [ ] Compile check

## Success Criteria

`grep -c "claudekit" constants.py` returns 0 (except REGISTRY_FILE and PROMPT_MANIFEST names)
