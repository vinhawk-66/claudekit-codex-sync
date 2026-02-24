"""Tests for asset_sync_dir module."""
from pathlib import Path

from claudekit_codex_sync.asset_sync_dir import sync_assets_from_dir, sync_skills_from_dir


def test_copies_asset_dirs(tmp_path: Path):
    """Copies files from rules/, scripts/, output-styles/ to codex_home."""
    source = tmp_path / "source"
    codex = tmp_path / "codex"
    (source / "rules").mkdir(parents=True)
    (source / "rules" / "test.md").write_text("# rule")
    (source / "scripts").mkdir()
    (source / "scripts" / "test.py").write_text("print('hi')")

    stats = sync_assets_from_dir(
        source, codex_home=codex, include_hooks=False,
        dry_run=False, registry=None, force=True,
    )
    assert stats["added"] == 2
    assert (codex / "rules" / "test.md").exists()
    assert (codex / "scripts" / "test.py").exists()


def test_idempotent_sync(tmp_path: Path):
    """Second sync reports 0 added, 0 updated."""
    source = tmp_path / "source"
    codex = tmp_path / "codex"
    (source / "rules").mkdir(parents=True)
    (source / "rules" / "test.md").write_text("# rule")

    sync_assets_from_dir(
        source, codex_home=codex, include_hooks=False,
        dry_run=False, registry=None, force=True,
    )
    stats = sync_assets_from_dir(
        source, codex_home=codex, include_hooks=False,
        dry_run=False, registry=None, force=True,
    )
    assert stats["added"] == 0
    assert stats["updated"] == 0


def test_copies_agents_md(tmp_path: Path):
    """Copies agents/*.md to codex_home/agents/."""
    source = tmp_path / "source"
    codex = tmp_path / "codex"
    (source / "agents").mkdir(parents=True)
    (source / "agents" / "planner.md").write_text("---\nmodel: opus\n---\nTest agent")

    stats = sync_assets_from_dir(
        source, codex_home=codex, include_hooks=False,
        dry_run=False, registry=None, force=True,
    )
    assert stats["added"] >= 1
    assert (codex / "agents" / "planner.md").exists()


def test_dry_run_no_write(tmp_path: Path):
    """Dry run reports counts but creates no files."""
    source = tmp_path / "source"
    codex = tmp_path / "codex"
    (source / "rules").mkdir(parents=True)
    (source / "rules" / "test.md").write_text("# rule")

    stats = sync_assets_from_dir(
        source, codex_home=codex, include_hooks=False,
        dry_run=True, registry=None, force=True,
    )
    assert stats["added"] >= 1
    assert not (codex / "rules").exists()


def test_sync_skills_basic(tmp_path: Path):
    """Copies skill directories."""
    source = tmp_path / "source"
    codex = tmp_path / "codex"
    skill = source / "skills" / "test-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# Test Skill")
    (skill / "script.py").write_text("print('test')")

    stats = sync_skills_from_dir(
        source, codex_home=codex, include_mcp=False,
        include_conflicts=False, dry_run=False,
    )
    assert stats["added"] == 1
    assert (codex / "skills" / "test-skill" / "SKILL.md").exists()


def test_excludes_template_skill(tmp_path: Path):
    """Skips template-skill."""
    source = tmp_path / "source"
    codex = tmp_path / "codex"
    (source / "skills" / "template-skill").mkdir(parents=True)
    (source / "skills" / "template-skill" / "SKILL.md").write_text("# Template")

    stats = sync_skills_from_dir(
        source, codex_home=codex, include_mcp=False,
        include_conflicts=False, dry_run=False,
    )
    assert stats["skipped"] == 1
    assert not (codex / "skills" / "template-skill").exists()
