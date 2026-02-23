"""Tests for config_enforcer module."""

import pytest
from claudekit_codex_sync.config_enforcer import enforce_multi_agent_flag


def test_adds_multi_agent_to_existing_features(tmp_path):
    """Test adding multi_agent to existing [features] section."""
    config = tmp_path / "config.toml"
    config.write_text("[features]\n")
    enforce_multi_agent_flag(config, dry_run=False)
    content = config.read_text()
    assert "multi_agent = true" in content


def test_creates_features_section_if_missing(tmp_path):
    """Test creating [features] section if it doesn't exist."""
    config = tmp_path / "config.toml"
    config.write_text("some_other_setting = 1\n")
    enforce_multi_agent_flag(config, dry_run=False)
    content = config.read_text()
    assert "[features]" in content
    assert "multi_agent = true" in content


def test_preserves_existing_config(tmp_path):
    """Test that existing config is preserved when adding multi_agent."""
    config = tmp_path / "config.toml"
    original = 'project_doc_max_bytes = 65536\n'
    config.write_text(original)
    enforce_multi_agent_flag(config, dry_run=False)
    content = config.read_text()
    assert "project_doc_max_bytes = 65536" in content
    assert "multi_agent = true" in content


def test_creates_file_if_not_exists(tmp_path):
    """Test creating config file if it doesn't exist."""
    config = tmp_path / "config.toml"
    enforce_multi_agent_flag(config, dry_run=False)
    assert config.exists()
    content = config.read_text()
    assert "[features]" in content
    assert "multi_agent = true" in content
