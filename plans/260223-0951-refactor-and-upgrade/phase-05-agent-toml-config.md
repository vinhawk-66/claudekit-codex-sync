# Phase 5: Agent TOML Normalization + Multi-Agent Config

Status: pending
Priority: critical
Effort: 0.5d

## Goal
Fix 16 `.claude` references in agent TOMLs. Enable `multi_agent = true`.

## Agent TOML Normalization

Add to `path_normalizer.py`:
```python
AGENT_TOML_REPLACEMENTS: List[Tuple[str, str]] = [
    ("$HOME/.claude/skills/", "${CODEX_HOME:-$HOME/.codex}/skills/"),
    ("$HOME/.claude/scripts/", "${CODEX_HOME:-$HOME/.codex}/claudekit/scripts/"),
    ("$HOME/.claude/rules/", "${CODEX_HOME:-$HOME/.codex}/claudekit/rules/"),
    ("$HOME/.claude/.ck.json", "${CODEX_HOME:-$HOME/.codex}/claudekit/.ck.json"),
    ("$HOME/.claude/.mcp.json", "${CODEX_HOME:-$HOME/.codex}/claudekit/.mcp.json"),
    ("$HOME/.claude/", "${CODEX_HOME:-$HOME/.codex}/"),
    ("~/.claude/", "~/.codex/"),
]

def normalize_agent_tomls(*, codex_home: Path, dry_run: bool) -> int:
    agents_dir = codex_home / "agents"
    if not agents_dir.exists():
        return 0
    changed = 0
    for toml_file in sorted(agents_dir.glob("*.toml")):
        text = toml_file.read_text(encoding="utf-8")
        new_text = apply_replacements(text, AGENT_TOML_REPLACEMENTS)
        if new_text != text:
            changed += 1
            if not dry_run:
                toml_file.write_text(new_text, encoding="utf-8")
    return changed
```

## Adapt Claude-Specific Syntax

Strip from developer_instructions:
```python
CLAUDE_SYNTAX_ADAPTATIONS = [
    # Task() tool references → natural language
    ("Task(Explore)", "the explore agent"),
    ("Task(researcher)", "the researcher agent"),
    ("Task(", "delegate to "),
    # Claude-specific paths
    ("$HOME/.claude/skills/*", "${CODEX_HOME:-$HOME/.codex}/skills/*"),
]
```

## Multi-Agent Config

Add to `config_enforcer.py`:
```python
def enforce_multi_agent_flag(config_path: Path, dry_run: bool) -> bool:
    text = config_path.read_text() if config_path.exists() else ""
    if "[features]" in text:
        if "multi_agent" not in text:
            text = text.replace("[features]", "[features]\nmulti_agent = true")
    else:
        text += "\n[features]\nmulti_agent = true\n"
    if not dry_run:
        config_path.write_text(text)
    return True
```

## Verification
```bash
# Before: expect 16 hits
grep -c '\.claude' ~/.codex/agents/*.toml

# After: expect 0
grep -c '\.claude' ~/.codex/agents/*.toml

# Multi-agent:
codex features list | grep multi_agent
# Expected: multi_agent    experimental    true
```

## Todo
- [ ] Add AGENT_TOML_REPLACEMENTS
- [ ] Add normalize_agent_tomls()
- [ ] Add Claude syntax adaptations
- [ ] Add enforce_multi_agent_flag()
- [ ] Test: 0 .claude refs in TOMLs
- [ ] Test: multi_agent = true
