"""Tests for safety guards."""
import pytest
from pathlib import Path

from claudekit_codex_sync.clean_target import clean_target
from claudekit_codex_sync.utils import SyncError


def test_rejects_root_as_codex_home():
    """Refuses to clean / as codex_home."""
    with pytest.raises(SyncError, match="Unsafe codex_home"):
        clean_target(Path("/"), dry_run=False)


def test_rejects_home_as_codex_home():
    """Refuses to clean $HOME as codex_home."""
    with pytest.raises(SyncError, match="Unsafe codex_home"):
        clean_target(Path.home(), dry_run=False)


def test_accepts_normal_codex_path(tmp_path: Path):
    """Normal .codex path works fine."""
    codex = tmp_path / ".codex"
    codex.mkdir()
    (codex / "agents").mkdir()
    (codex / "agents" / "test.toml").write_text("x = 1")
    removed = clean_target(codex, dry_run=False)
    assert removed >= 1
