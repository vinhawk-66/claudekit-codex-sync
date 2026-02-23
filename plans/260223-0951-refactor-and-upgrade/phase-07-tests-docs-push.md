# Phase 7: Tests + Docs + Git Push

Status: pending
Priority: high
Effort: 0.5d

## Tests

### `tests/test_path_normalizer.py`
```python
from claudekit_codex_sync.path_normalizer import apply_replacements, SKILL_MD_REPLACEMENTS

def test_claude_to_codex_path():
    text = "$HOME/.claude/skills/brainstorm/SKILL.md"
    result = apply_replacements(text, SKILL_MD_REPLACEMENTS)
    assert ".claude" not in result
    assert ".codex" in result or "CODEX_HOME" in result
```

### `tests/test_config_enforcer.py`
```python
from claudekit_codex_sync.config_enforcer import enforce_multi_agent_flag

def test_adds_multi_agent(tmp_path):
    config = tmp_path / "config.toml"
    config.write_text("[features]\n")
    enforce_multi_agent_flag(config, dry_run=False)
    assert "multi_agent = true" in config.read_text()
```

## Docs

### `docs/codex-vs-claude-agents.md`
Sub-agent limitations doc:
- Claude Code: tools/model/memory frontmatter, Task() delegation
- Codex: developer_instructions text only, auto-spawn via multi_agent
- What transfers: text instructions, sandbox_mode
- What's lost: tool restriction, model selection, explicit delegation

## Git Push

```bash
cd /home/vinhawk/claudekit-codex-sync
git add -A
git commit -m "refactor: modularize codebase, npm structure, upgrade for Codex"
git push
```

## Todo
- [ ] Write test_path_normalizer.py
- [ ] Write test_config_enforcer.py
- [ ] Write codex-vs-claude-agents.md
- [ ] Run tests
- [ ] Git add, commit, push
