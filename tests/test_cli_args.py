"""Tests for CLI argument parsing."""

import sys
from unittest.mock import patch

from claudekit_codex_sync.cli import parse_args


def test_default_args():
    """Default: project scope, no flags."""
    with patch.object(sys, "argv", ["ckc-sync"]):
        args = parse_args()
    assert not args.global_scope
    assert not args.fresh
    assert not args.force
    assert not args.mcp
    assert not args.no_deps
    assert not args.dry_run
    assert args.zip_path is None
    assert args.source is None


def test_global_flag():
    """'-g' enables global scope."""
    with patch.object(sys, "argv", ["ckc-sync", "-g"]):
        args = parse_args()
    assert args.global_scope


def test_fresh_flag():
    """'-f' enables fresh clean."""
    with patch.object(sys, "argv", ["ckc-sync", "-f"]):
        args = parse_args()
    assert args.fresh


def test_combined_short_flags():
    """'-g -f -n' all work together."""
    with patch.object(sys, "argv", ["ckc-sync", "-g", "-f", "-n"]):
        args = parse_args()
    assert args.global_scope
    assert args.fresh
    assert args.dry_run


def test_zip_flag():
    """'--zip' sets zip path and implies zip mode."""
    with patch.object(sys, "argv", ["ckc-sync", "--zip", "test.zip"]):
        args = parse_args()
    assert str(args.zip_path) == "test.zip"


def test_mcp_flag():
    """'--mcp' includes MCP skills."""
    with patch.object(sys, "argv", ["ckc-sync", "--mcp"]):
        args = parse_args()
    assert args.mcp
