"""Tests for rules_generator module."""

from pathlib import Path

from claudekit_codex_sync.rules_generator import generate_hook_rules


def test_generates_all_rule_files(tmp_path: Path):
    """Generates 3 rule files."""
    count = generate_hook_rules(codex_home=tmp_path, dry_run=False)
    assert count == 3
    assert (tmp_path / "rules" / "security-privacy.md").exists()
    assert (tmp_path / "rules" / "file-naming.md").exists()
    assert (tmp_path / "rules" / "code-quality-reminders.md").exists()


def test_idempotent(tmp_path: Path):
    """Second run returns 0 (no changes)."""
    generate_hook_rules(codex_home=tmp_path, dry_run=False)
    count = generate_hook_rules(codex_home=tmp_path, dry_run=False)
    assert count == 0


def test_dry_run(tmp_path: Path):
    """Dry run counts but doesn't create."""
    count = generate_hook_rules(codex_home=tmp_path, dry_run=True)
    assert count == 3
    assert not (tmp_path / "rules").exists()
