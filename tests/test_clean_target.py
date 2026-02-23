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


def test_clean_keeps_venv(tmp_path: Path):
    """Clean keeps skills/.venv intact."""
    skills = tmp_path / "skills"
    skills.mkdir()
    venv = skills / ".venv"
    venv.mkdir()
    (venv / "bin").mkdir()
    (venv / "bin" / "python3").write_text("#!/usr/bin/env python3")
    skill = skills / "my-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# test")

    clean_target(tmp_path, dry_run=False)
    assert venv.exists(), ".venv should survive cleaning"
    assert not skill.exists(), "skill dirs should be removed"


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
