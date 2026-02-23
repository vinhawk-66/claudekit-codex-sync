#!/usr/bin/env python3
"""All-in-one ClaudeKit -> Codex sync CLI."""

from __future__ import annotations

import argparse
import json
import os
import zipfile
from pathlib import Path
from typing import Any, Dict

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
from .path_normalizer import normalize_agent_tomls, normalize_files
from .prompt_exporter import export_prompts
from .runtime_verifier import verify_runtime
from .source_resolver import detect_claude_source, find_latest_zip, validate_source
from .sync_registry import load_registry, save_registry
from .utils import SyncError, eprint


def print_summary(summary: Dict[str, Any]) -> None:
    print(json.dumps(summary, indent=2, ensure_ascii=False))


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

    workspace = Path.cwd().resolve()
    if not args.dry_run:
        codex_home.mkdir(parents=True, exist_ok=True)

    if args.fresh:
        removed = clean_target(codex_home, dry_run=args.dry_run)
        print(f"fresh: removed {removed} files")

    registry = load_registry(codex_home)

    use_live = args.zip_path is None
    if not use_live and not args.force and not args.dry_run:
        raise SyncError("zip sync requires --force for write mode")

    if use_live:
        source = args.source or detect_claude_source()
        validation = validate_source(source)
        print(f"source: {source} (live)")
        print(f"validation: {validation}")
        registry["sourceDir"] = str(source)
    else:
        zip_path = find_latest_zip(args.zip_path)
        print(f"zip: {zip_path}")
        registry["sourceDir"] = None

    print(f"codex_home: {codex_home}")
    print(f"scope: {'global' if args.global_scope else 'project'}")
    print(f"fresh={args.fresh} force={args.force} mcp={args.mcp} dry_run={args.dry_run}")

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

    print(f"assets: added={assets_stats['added']} updated={assets_stats['updated']}")
    print(f"skills: added={skills_stats['added']} updated={skills_stats['updated']}")

    changed = normalize_files(codex_home=codex_home, include_mcp=args.mcp, dry_run=args.dry_run)
    print(f"normalize_changed={changed}")

    # enforce_config BEFORE register_agents — enforce_config rewrites config.toml
    baseline_changed = 0
    if ensure_agents(workspace=workspace, dry_run=args.dry_run):
        baseline_changed += 1
    if enforce_config(codex_home=codex_home, include_mcp=args.mcp, dry_run=args.dry_run):
        baseline_changed += 1
    if ensure_bridge_skill(codex_home=codex_home, dry_run=args.dry_run):
        baseline_changed += 1

    config_path = codex_home / "config.toml"
    if enforce_multi_agent_flag(config_path, dry_run=args.dry_run):
        print(f"upsert: multi_agent = true in {config_path}")

    print(f"baseline_changed={baseline_changed}")

    # Convert .md → .toml and normalize BEFORE registering
    agent_toml_changed = normalize_agent_tomls(codex_home=codex_home, dry_run=args.dry_run)
    print(f"agent_toml_changed={agent_toml_changed}")

    # register_agents AFTER .toml files exist and config is stable
    agents_registered = register_agents(codex_home=codex_home, dry_run=args.dry_run)
    print(f"agents_registered={agents_registered}")

    prompt_stats = export_prompts(codex_home=codex_home, include_mcp=args.mcp, dry_run=args.dry_run)
    print(f"prompts: added={prompt_stats['added']} total={prompt_stats['total_generated']}")

    bootstrap_stats = None
    if not args.no_deps:
        bootstrap_stats = bootstrap_deps(
            codex_home=codex_home,
            include_mcp=args.mcp,
            dry_run=args.dry_run,
        )
        print(
            f"bootstrap: py_ok={bootstrap_stats['python_ok']} "
            f"py_fail={bootstrap_stats['python_fail']}"
        )
        if (bootstrap_stats["python_fail"] or bootstrap_stats["node_fail"]) and not args.dry_run:
            raise SyncError("Dependency bootstrap reported failures")

    verify_stats = verify_runtime(codex_home=codex_home, dry_run=args.dry_run)
    print(f"verify: {verify_stats}")

    if not args.dry_run:
        save_registry(codex_home, registry)

    summary = {
        "source": str(source) if use_live else str(zip_path),
        "source_mode": "live" if use_live else "zip",
        "codex_home": str(codex_home),
        "scope": "global" if args.global_scope else "project",
        "fresh": args.fresh,
        "assets": assets_stats,
        "skills": skills_stats,
        "normalize_changed": changed,
        "agent_toml_changed": agent_toml_changed,
        "agents_registered": agents_registered,
        "prompts": prompt_stats,
        "bootstrap": bootstrap_stats,
        "verify": verify_stats,
    }
    print_summary(summary)
    print("done: ckc-sync completed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SyncError as exc:
        eprint(f"error: {exc}")
        raise SystemExit(2)
