"""Dependency bootstrap for skills."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Dict

from .utils import eprint, is_excluded_path, run_cmd


def _try_symlink_venv(codex_home: Path, *, dry_run: bool) -> bool:
    """Try to symlink from existing ClaudeKit venv. Returns True if successful."""
    source_venv = Path.home() / ".claude" / "skills" / ".venv"
    target_venv = codex_home / "skills" / ".venv"

    if target_venv.is_symlink() and not target_venv.resolve().exists():
        if not dry_run:
            target_venv.unlink()

    if target_venv.is_symlink() and target_venv.resolve().exists():
        print("skip: skills/.venv (symlink intact)")
        return True
    if target_venv.exists() and not target_venv.is_symlink():
        print("skip: skills/.venv (exists)")
        return True

    if source_venv.exists():
        if not dry_run:
            target_venv.parent.mkdir(parents=True, exist_ok=True)
            if target_venv.is_symlink():
                target_venv.unlink()
            target_venv.symlink_to(source_venv)
        print(f"symlink: skills/.venv -> {source_venv}")
        return True

    return False


def _install_node_deps(*, skills_dir: Path, include_mcp: bool, dry_run: bool) -> tuple[int, int]:
    """Install Node dependencies for skills."""
    node_ok = node_fail = 0
    npm = shutil.which("npm")
    if not npm:
        eprint("npm not found; skipping Node dependency bootstrap")
        return node_ok, node_fail

    pkg_files = sorted(skills_dir.rglob("package.json"))
    for pkg in pkg_files:
        if is_excluded_path(pkg.parts):
            continue
        if not include_mcp and ("mcp-builder" in pkg.parts or "mcp-management" in pkg.parts):
            continue
        try:
            run_cmd([npm, "install", "--prefix", str(pkg.parent)], dry_run=dry_run)
            node_ok += 1
        except subprocess.CalledProcessError:
            node_fail += 1
            eprint(f"node deps failed: {pkg.parent}")
    return node_ok, node_fail


def bootstrap_deps(
    *,
    codex_home: Path,
    include_mcp: bool,
    dry_run: bool,
) -> Dict[str, int]:
    """Bootstrap Python and Node dependencies for skills."""
    skills_dir = codex_home / "skills"
    py_ok = py_fail = node_ok = node_fail = 0

    symlinked = _try_symlink_venv(codex_home, dry_run=dry_run)
    venv_dir = skills_dir / ".venv"
    py_bin = venv_dir / "bin" / "python3"
    if symlinked and not dry_run and not py_bin.exists():
        eprint("warn: skills/.venv missing bin/python3, recreating local venv")
        if venv_dir.is_symlink():
            venv_dir.unlink()
        symlinked = False

    if not symlinked:
        if not shutil.which("python3"):
            from .utils import SyncError

            raise SyncError("python3 not found")
        run_cmd(["python3", "-m", "venv", str(venv_dir)], dry_run=dry_run)
        run_cmd([str(py_bin), "-m", "pip", "install", "--upgrade", "pip"], dry_run=dry_run)

    # Skip dependency install when venv is symlinked — packages already in source
    if not symlinked:
        req_files = sorted(skills_dir.rglob("requirements*.txt"))
        for req in req_files:
            if is_excluded_path(req.parts):
                continue
            if not include_mcp and ("mcp-builder" in req.parts or "mcp-management" in req.parts):
                continue
            try:
                run_cmd([str(py_bin), "-m", "pip", "install", "-r", str(req)], dry_run=dry_run)
                py_ok += 1
            except subprocess.CalledProcessError:
                py_fail += 1
                eprint(f"python deps failed: {req}")

        node_ok, node_fail = _install_node_deps(
            skills_dir=skills_dir,
            include_mcp=include_mcp,
            dry_run=dry_run,
        )
    else:
        print("skip: deps install (venv symlinked, packages shared)")

    return {
        "python_ok": py_ok,
        "python_fail": py_fail,
        "node_ok": node_ok,
        "node_fail": node_fail,
    }
