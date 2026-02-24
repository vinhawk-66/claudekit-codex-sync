"""Tests for runtime_verifier module."""
from pathlib import Path

from claudekit_codex_sync.runtime_verifier import verify_runtime


def test_dry_run_returns_skipped(tmp_path: Path):
    """Dry run returns skipped flag."""
    result = verify_runtime(codex_home=tmp_path, dry_run=True)
    assert result["skipped"] is True


def test_empty_codex_home(tmp_path: Path):
    """Empty codex_home reports not-found/0 counts."""
    (tmp_path / "skills").mkdir()
    result = verify_runtime(codex_home=tmp_path, dry_run=False)
    assert result["copywriting"] in ("not-found", "no-venv")
    assert result["skills"] == 0
