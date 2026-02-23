"""Tests for path_normalizer module."""

import pytest
from claudekit_codex_sync.constants import SKILL_MD_REPLACEMENTS
from claudekit_codex_sync.path_normalizer import apply_replacements


def test_claude_to_codex_path():
    """Test that .claude paths are normalized to .codex paths."""
    text = "$HOME/.claude/skills/brainstorm/SKILL.md"
    result = apply_replacements(text, SKILL_MD_REPLACEMENTS)
    assert ".claude" not in result
    assert ".codex" in result or "CODEX_HOME" in result


def test_home_claude_replacement():
    """Test $HOME/.claude/skills/ replacement."""
    text = "$HOME/.claude/skills/test/skill.py"
    result = apply_replacements(text, SKILL_MD_REPLACEMENTS)
    assert result == "${CODEX_HOME:-$HOME/.codex}/skills/test/skill.py"


def test_dot_slash_claude_replacement():
    """Test ./.claude/skills/ replacement."""
    text = "./.claude/skills/test/skill.py"
    result = apply_replacements(text, SKILL_MD_REPLACEMENTS)
    assert result == "${CODEX_HOME:-$HOME/.codex}/skills/test/skill.py"


def test_tilde_claude_replacement():
    """Test ~/.claude/ replacement."""
    text = "~/.claude/config.json"
    result = apply_replacements(text, SKILL_MD_REPLACEMENTS)
    assert result == "~/.codex/config.json"


def test_ck_json_replacement():
    """Test .ck.json path replacement."""
    text = "~/.claude/.ck.json"
    result = apply_replacements(text, SKILL_MD_REPLACEMENTS)
    assert result == "~/.codex/claudekit/.ck.json"


def test_no_change_for_non_claude():
    """Test that non-claude paths are not changed."""
    text = "/some/other/path/file.txt"
    result = apply_replacements(text, SKILL_MD_REPLACEMENTS)
    assert result == text


def test_multiple_replacements():
    """Test multiple paths in same text."""
    text = """
    Use skills from $HOME/.claude/skills/
    And scripts from ./.claude/scripts/
    Config at ~/.claude/.ck.json
    """
    result = apply_replacements(text, SKILL_MD_REPLACEMENTS)
    assert "$HOME/.claude/skills/" not in result
    assert "./.claude/scripts/" not in result
    assert "~/.claude/.ck.json" not in result
