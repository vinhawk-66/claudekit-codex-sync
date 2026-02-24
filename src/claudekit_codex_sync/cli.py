#!/usr/bin/env python3
"""All-in-one ClaudeKit -> Codex sync CLI."""

from __future__ import annotations

import argparse
import os
import zipfile
from pathlib import Path

from .asset_sync_dir import sync_assets_from_dir, sync_skills_from_dir
from .asset_sync_zip import sync_assets, sync_skills
from .bridge_generator import ensure_bridge_skill
from .clean_target import clean_target
from .config_enforcer import (
    enforce_config,
    enforce_multi_agent_flag,
    ensure_agents,
    register_agents,
)
from .dep_bootstrapper import bootstrap_deps
from .log_formatter import log_done, log_error, log_ok, log_section, log_skip
from .log_formatter import log_header, log_summary
from .path_normalizer import normalize_agent_tomls, normalize_files
from .rules_generator import generate_hook_rules
from .runtime_verifier import verify_runtime
from .source_resolver import detect_claude_source, find_latest_zip, validate_source
from .sync_registry import load_registry, save_registry
from .utils import SyncError, eprint


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="ckc-sync",
        description="Sync ClaudeKit skills, agents, and config to Codex CLI.",
    )
    p.add_argument(
        "-g",
        "--global",
        dest="global_scope",
        action="store_true",
        help="Sync to ~/.codex/ (default: ./.codex/)",
    )
    p.add_argument(
        "-f",
        "--fresh",
        action="store_true",
        help="Clean target dirs before sync",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Overwrite user-edited files without backup (required for zip write mode)",
    )
    p.add_argument(
        "--zip",
        dest="zip_path",
        type=Path,
        help="Sync from zip instead of live ~/.claude/",
    )
    p.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Custom source dir (default: ~/.claude/)",
    )
    p.add_argument(
        "--mcp",
        action="store_true",
        help="Include MCP skills",
    )
    p.add_argument(
        "--no-deps",
        action="store_true",
        help="Skip dependency bootstrap (venv)",
    )
    p.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Preview only",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.global_scope:
        codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser().resolve()
    else:
        codex_home = (Path.cwd() / ".codex").resolve()

    scope = "global" if args.global_scope else "project"
    workspace = Path.cwd().resolve()
    if not args.dry_run:
        codex_home.mkdir(parents=True, exist_ok=True)

    # --- Fresh cleanup ---
    if args.fresh:
        removed = clean_target(codex_home, dry_run=args.dry_run)
        log_section("Fresh")
        log_summary(removed=removed)

    registry = load_registry(codex_home)

    use_live = args.zip_path is None
    if not use_live and not args.force and not args.dry_run:
        raise SyncError("zip sync requires --force for write mode")

    if use_live:
        source = args.source or detect_claude_source()
        validation = validate_source(source)
        if not validation["skills"] and not args.dry_run:
            raise SyncError(
                f"Source {source} missing skills/ directory. "
                "Cannot sync without skills. Use --source to specify correct path."
            )
        registry["sourceDir"] = str(source)
    else:
        zip_path = find_latest_zip(args.zip_path)
        registry["sourceDir"] = None

    # --- Header ---
    src_display = str(source) if use_live else str(zip_path)
    log_header(src_display, str(codex_home), scope, args.dry_run)

    # --- Sync assets & skills ---
    if use_live:
        assets_stats = sync_assets_from_dir(
            source,
            codex_home=codex_home,
            include_hooks=True,
            dry_run=args.dry_run,
            registry=registry,
            force=args.force,
        )
        skills_stats = sync_skills_from_dir(
            source,
            codex_home=codex_home,
            include_mcp=args.mcp,
            include_conflicts=False,
            dry_run=args.dry_run,
        )
    else:
        with zipfile.ZipFile(zip_path) as zf:
            assets_stats = sync_assets(
                zf,
                codex_home=codex_home,
                include_hooks=True,
                dry_run=args.dry_run,
            )
            skills_stats = sync_skills(
                zf,
                codex_home=codex_home,
                include_mcp=args.mcp,
                include_conflicts=False,
                dry_run=args.dry_run,
            )

    log_section("Assets")
    log_summary(
        added=assets_stats["added"],
        updated=assets_stats.get("updated", 0),
        skipped=assets_stats.get("skipped", 0),
        skip_reason="user-edit",
    )

    log_section("Skills")
    log_summary(
        added=skills_stats["added"],
        updated=skills_stats.get("updated", 0),
        skipped=skills_stats.get("skipped", 0),
    )

    # --- Normalize paths ---
    changed = normalize_files(codex_home=codex_home, include_mcp=args.mcp, dry_run=args.dry_run)
    log_section("Normalize")
    log_summary(updated=changed)

    # --- Hook rules ---
    rules_generated = generate_hook_rules(codex_home=codex_home, dry_run=args.dry_run)

    # --- Config enforcement ---
    baseline_changed = 0
    if ensure_agents(workspace=workspace, dry_run=args.dry_run):
        baseline_changed += 1
    if enforce_config(codex_home=codex_home, include_mcp=args.mcp, dry_run=args.dry_run):
        baseline_changed += 1
    if ensure_bridge_skill(codex_home=codex_home, dry_run=args.dry_run):
        baseline_changed += 1

    config_path = codex_home / "config.toml"
    multi_agent_changed = enforce_multi_agent_flag(config_path, dry_run=args.dry_run)

    log_section("Config")
    parts = []
    if baseline_changed:
        parts.append("config.toml")
    if multi_agent_changed:
        parts.append("multi_agent=true")
    if rules_generated:
        parts.append(f"{rules_generated} rules")
    if parts:
        log_ok("  ".join(parts))
    else:
        log_ok("no changes")

    # --- Agent conversion ---
    agent_toml_changed = normalize_agent_tomls(codex_home=codex_home, dry_run=args.dry_run)
    agents_registered = register_agents(codex_home=codex_home, dry_run=args.dry_run)

    if agent_toml_changed or agents_registered:
        log_section("Agents")
        log_summary(updated=agent_toml_changed + agents_registered)

    # --- Bootstrap deps ---
    bootstrap_stats = None
    if not args.no_deps:
        bootstrap_stats = bootstrap_deps(
            codex_home=codex_home,
            include_mcp=args.mcp,
            dry_run=args.dry_run,
        )
        log_section("Bootstrap")
        py_ok = bootstrap_stats["python_ok"]
        py_fail = bootstrap_stats["python_fail"]
        node_ok = bootstrap_stats["node_ok"]
        node_fail = bootstrap_stats["node_fail"]
        if py_fail or node_fail:
            log_error(f"py:{py_ok}ok/{py_fail}fail  node:{node_ok}ok/{node_fail}fail")
            if not args.dry_run:
                raise SyncError("Dependency bootstrap reported failures")
        else:
            venv_path = codex_home / "skills" / ".venv"
            venv_status = "symlinked" if venv_path.is_symlink() else "created"
            log_ok(f"venv {venv_status}")
            if py_ok or node_ok:
                log_ok(f"deps installed (py:{py_ok} node:{node_ok})")
            else:
                log_skip("deps shared")

    # --- Verify ---
    verify_stats = verify_runtime(codex_home=codex_home, dry_run=args.dry_run)
    log_section("Verify")
    if verify_stats.get("skipped"):
        log_skip("dry-run")
    else:
        codex_st = verify_stats.get("codex", "unknown")
        copy_st = verify_stats.get("copywriting", "unknown")
        skills_n = verify_stats.get("skills", 0)
        status_parts = []
        if codex_st == "ok":
            status_parts.append("codex")
        if copy_st == "ok":
            status_parts.append("copywriting")
        if skills_n:
            status_parts.append(f"{skills_n} skills")
        if status_parts:
            log_ok("  ".join(status_parts))
        if codex_st not in ("ok", "not-found"):
            log_error(f"codex: {codex_st}")
        if copy_st not in ("ok", "not-found"):
            log_error(f"copywriting: {copy_st}")

    if not args.dry_run:
        save_registry(codex_home, registry)

    log_done()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SyncError as exc:
        eprint(f"error: {exc}")
        raise SystemExit(2)

