"""Tests for clean_target module."""

import json
from pathlib import Path

from claudekit_codex_sync.clean_target import clean_target


def test_clean_removes_agents(tmp_path: Path):
    """Clean removes agents dir."""
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "planner.toml").write_text("model = 'test'")
    (agents / "researcher.toml").write_text("model = 'test'")

    removed = clean_target(tmp_path, dry_run=False)
    assert not agents.exists()
    assert removed >= 2


def test_clean_keeps_venv_symlink(tmp_path: Path):
    """Clean keeps symlinked .venv but deletes real .venv dirs."""
    skills = tmp_path / "skills"
    skills.mkdir()

    # Create a real source venv to symlink to
    source_venv = tmp_path / "source_venv"
    source_venv.mkdir()
    (source_venv / "bin").mkdir()
    (source_venv / "bin" / "python3").write_text("#!/usr/bin/env python3")

    # Symlink .venv → source_venv (simulates symlink to ~/.claude/skills/.venv)
    venv = skills / ".venv"
    venv.symlink_to(source_venv)

    skill = skills / "my-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# test")

    clean_target(tmp_path, dry_run=False)
    assert venv.is_symlink(), "symlinked .venv should survive cleaning"
    assert not skill.exists(), "skill dirs should be removed"


def test_clean_deletes_real_venv(tmp_path: Path):
    """Clean deletes real (non-symlink) .venv for re-symlinking."""
    skills = tmp_path / "skills"
    skills.mkdir()
    venv = skills / ".venv"
    venv.mkdir()
    (venv / "bin").mkdir()
    (venv / "bin" / "python3").write_text("#!/usr/bin/env python3")

    clean_target(tmp_path, dry_run=False)
    assert not venv.exists(), "real .venv should be deleted for re-symlinking"


def test_clean_dry_run(tmp_path: Path):
    """Dry run counts but doesn't delete."""
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "test.toml").write_text("x = 1")

    removed = clean_target(tmp_path, dry_run=True)
    assert removed >= 1
    assert agents.exists(), "dry-run should not delete"


def test_clean_removes_registry(tmp_path: Path):
    """Clean clears sync registry."""
    registry = tmp_path / ".claudekit-sync-registry.json"
    registry.write_text(json.dumps({"version": 1}))

    clean_target(tmp_path, dry_run=False)
    assert not registry.exists()
