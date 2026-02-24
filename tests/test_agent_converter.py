"""Tests for agent .md → .toml conversion."""
from pathlib import Path

from claudekit_codex_sync.path_normalizer import convert_agents_md_to_toml


def test_converts_md_to_toml(tmp_path: Path):
    """Converts agent .md with YAML frontmatter to .toml."""
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "planner.md").write_text(
        "---\nmodel: opus\n---\nYou are a planning agent."
    )
    converted = convert_agents_md_to_toml(codex_home=tmp_path, dry_run=False)
    assert converted == 1
    assert (agents / "planner.toml").exists()
    assert not (agents / "planner.md").exists()
    content = (agents / "planner.toml").read_text()
    assert 'model = "gpt-5.3-codex"' in content
    assert 'model_reasoning_effort = "xhigh"' in content


def test_read_only_agent_gets_sandbox(tmp_path: Path):
    """Read-only agents get read-only sandbox."""
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "brainstormer.md").write_text(
        "---\nmodel: sonnet\n---\nYou brainstorm solutions."
    )
    convert_agents_md_to_toml(codex_home=tmp_path, dry_run=False)
    content = (agents / "brainstormer.toml").read_text()
    assert 'sandbox_mode = "read-only"' in content


def test_skips_md_without_frontmatter(tmp_path: Path):
    """Skips .md files without YAML frontmatter."""
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "readme.md").write_text("# Some readme without frontmatter")
    converted = convert_agents_md_to_toml(codex_home=tmp_path, dry_run=False)
    assert converted == 0
    assert (agents / "readme.md").exists()
