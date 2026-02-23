"""Dependency bootstrap for skills."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Dict

from .utils import eprint, is_excluded_path, run_cmd


def bootstrap_deps(
    *,
    codex_home: Path,
    include_mcp: bool,
    include_test_deps: bool,
    dry_run: bool,
) -> Dict[str, int]:
    """Bootstrap Python and Node dependencies for skills."""
    skills_dir = codex_home / "skills"
    venv_dir = skills_dir / ".venv"

    if not shutil.which("python3"):
        from .utils import SyncError
        raise SyncError("python3 not found")

    py_ok = py_fail = node_ok = node_fail = 0

    run_cmd(["python3", "-m", "venv", str(venv_dir)], dry_run=dry_run)
    py_bin = venv_dir / "bin" / "python3"
    run_cmd([str(py_bin), "-m", "pip", "install", "--upgrade", "pip"], dry_run=dry_run)

    req_files = sorted(skills_dir.rglob("requirements*.txt"))
    for req in req_files:
        rel = req.relative_to(skills_dir).as_posix()
        if is_excluded_path(req.parts):
            continue
        if not include_test_deps and "/test" in rel:
            continue
        if not include_mcp and ("mcp-builder" in req.parts or "mcp-management" in req.parts):
            continue
        try:
            run_cmd([str(py_bin), "-m", "pip", "install", "-r", str(req)], dry_run=dry_run)
            py_ok += 1
        except subprocess.CalledProcessError:
            py_fail += 1
            eprint(f"python deps failed: {req}")

    npm = shutil.which("npm")
    if npm:
        pkg_files = sorted(skills_dir.rglob("package.json"))
        for pkg in pkg_files:
            rel = pkg.relative_to(skills_dir).as_posix()
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
    else:
        eprint("npm not found; skipping Node dependency bootstrap")

    return {
        "python_ok": py_ok,
        "python_fail": py_fail,
        "node_ok": node_ok,
        "node_fail": node_fail,
    }
