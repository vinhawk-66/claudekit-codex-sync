"""Structured CLI output for ckc-sync."""

from __future__ import annotations

import os
import sys

_IS_TTY = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
_NO_COLOR = os.environ.get("NO_COLOR") is not None


def _c(code: str, text: str) -> str:
    """Wrap text in ANSI code if TTY and not NO_COLOR."""
    if not _IS_TTY or _NO_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def bold(t: str) -> str:
    return _c("1", t)


def green(t: str) -> str:
    return _c("32", t)


def yellow(t: str) -> str:
    return _c("33", t)


def cyan(t: str) -> str:
    return _c("36", t)


def dim(t: str) -> str:
    return _c("2", t)


def red(t: str) -> str:
    return _c("31", t)


def log_header(
    source: str, target: str, scope: str, dry_run: bool, version: str = "0.2.5"
) -> None:
    """Print header with source/target info."""
    mode = " (dry-run)" if dry_run else ""
    print(bold(f"ckc-sync v{version}{mode}"))
    print(f"  source  {source}")
    print(f"  target  {target} ({scope})")


def log_section(name: str) -> None:
    """Print section header."""
    print(f"\n{bold(cyan('▸'))} {bold(name)}")


def log_summary(
    added: int = 0,
    updated: int = 0,
    skipped: int = 0,
    removed: int = 0,
    skip_reason: str = "",
) -> None:
    """Print summary counts for a section."""
    parts: list[str] = []
    if added:
        parts.append(green(f"+ {added} added"))
    if updated:
        parts.append(yellow(f"↻ {updated} updated"))
    if removed:
        parts.append(red(f"- {removed} removed"))
    if skipped:
        reason = f" ({skip_reason})" if skip_reason else ""
        parts.append(dim(f"⊘ {skipped} skipped{reason}"))
    if not parts:
        parts.append(green("✓ no changes"))
    print(f"  {'  '.join(parts)}")


def log_ok(msg: str) -> None:
    """Print success item."""
    print(f"  {green('✓')} {msg}")


def log_skip(msg: str) -> None:
    """Print skipped item."""
    print(f"  {dim('⊘')} {msg}")


def log_warn(msg: str) -> None:
    """Print warning to stderr."""
    print(f"  {yellow('⚠')} {msg}", file=sys.stderr)


def log_error(msg: str) -> None:
    """Print error to stderr."""
    print(f"  {red('✗')} {msg}", file=sys.stderr)


def log_done() -> None:
    """Print completion message."""
    print(f"\n{green('✓')} {bold('completed')}")
