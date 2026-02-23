#!/usr/bin/env python3
"""All-in-one ClaudeKit -> Codex sync CLI."""

from __future__ import annotations

import argparse
import json
import os
import zipfile
from pathlib import Path
from typing import Any, Dict, Optional

from .asset_sync_dir import sync_assets_from_dir, sync_skills_from_dir
from .asset_sync_zip import sync_assets, sync_skills
from .bridge_generator import ensure_bridge_skill
from .config_enforcer import ensure_agents, enforce_config, enforce_multi_agent_flag
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
        description="All-in-one ClaudeKit -> Codex sync script."
    )
    p.add_argument("--zip", dest="zip_path", type=Path, help="Specific ClaudeKit zip path")
    p.add_argument("--codex-home", type=Path, default=None, help="Codex home (default: $CODEX_HOME or ~/.codex)")
    p.add_argument("--workspace", type=Path, default=Path.cwd(), help="Workspace root for AGENTS.md")
    p.add_argument("--source-mode", choices=["auto", "live", "zip"], default="auto", help="Source mode")
    p.add_argument("--source-dir", type=Path, default=None, help="Source directory for live mode")
    p.add_argument("--include-mcp", action="store_true", help="Include MCP skills/prompts")
    p.add_argument("--include-hooks", action="store_true", help="Include hooks")
    p.add_argument("--include-conflicts", action="store_true", help="Include conflicting skills")
    p.add_argument("--include-test-deps", action="store_true", help="Install test requirements")
    p.add_argument("--skip-bootstrap", action="store_true", help="Skip dependency bootstrap")
    p.add_argument("--skip-verify", action="store_true", help="Skip verification")
    p.add_argument("--skip-agent-toml", action="store_true", help="Skip agent TOML normalization")
    p.add_argument("--respect-edits", action="store_true", help="Backup user-edited files")
    p.add_argument("--dry-run", action="store_true", help="Preview changes only")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    codex_home = (args.codex_home or Path(os.environ.get("CODEX_HOME", "~/.codex"))).expanduser().resolve()
    workspace = args.workspace.expanduser().resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    # Load registry for backup/respect-edits
    registry = load_registry(codex_home)

    source_mode = args.source_mode
    use_live = source_mode == "live" or (source_mode == "auto" and args.source_dir)

    if use_live:
        source = args.source_dir or detect_claude_source()
        validation = validate_source(source)
        print(f"source: {source} (live)")
        print(f"validation: {validation}")
        registry["sourceDir"] = str(source)
    else:
        zip_path = find_latest_zip(args.zip_path)
        print(f"zip: {zip_path}")
        registry["sourceDir"] = None

    print(f"codex_home: {codex_home}")
    print(f"workspace: {workspace}")
    print(
        f"include_mcp={args.include_mcp} include_hooks={args.include_hooks} "
        f"dry_run={args.dry_run} respect_edits={args.respect_edits}"
    )

    codex_home.mkdir(parents=True, exist_ok=True)

    if use_live:
        assets_stats = sync_assets_from_dir(
            source, codex_home=codex_home, include_hooks=args.include_hooks, dry_run=args.dry_run
        )
        skills_stats = sync_skills_from_dir(
            source,
            codex_home=codex_home,
            include_mcp=args.include_mcp,
            include_conflicts=args.include_conflicts,
            dry_run=args.dry_run,
        )
    else:
        with zipfile.ZipFile(zip_path) as zf:  # type: ignore
            assets_stats = sync_assets(
                zf, codex_home=codex_home, include_hooks=args.include_hooks, dry_run=args.dry_run
            )
            skills_stats = sync_skills(
                zf,
                codex_home=codex_home,
                include_mcp=args.include_mcp,
                include_conflicts=args.include_conflicts,
                dry_run=args.dry_run,
            )

    print(
        f"assets: added={assets_stats['added']} updated={assets_stats['updated']} "
        f"removed={assets_stats['removed']}"
    )
    print(
        f"skills: added={skills_stats['added']} updated={skills_stats['updated']} "
        f"skipped={skills_stats['skipped']}"
    )

    changed = normalize_files(codex_home=codex_home, include_mcp=args.include_mcp, dry_run=args.dry_run)
    print(f"normalize_changed={changed}")

    # Agent TOML normalization
    agent_toml_changed = 0
    if not args.skip_agent_toml:
        agent_toml_changed = normalize_agent_tomls(codex_home=codex_home, dry_run=args.dry_run)
        print(f"agent_toml_changed={agent_toml_changed}")

    baseline_changed = 0
    if ensure_agents(workspace=workspace, dry_run=args.dry_run):
        baseline_changed += 1
        print(f"upsert: {workspace / 'AGENTS.md'}")
    if enforce_config(codex_home=codex_home, include_mcp=args.include_mcp, dry_run=args.dry_run):
        baseline_changed += 1
        print(f"upsert: {codex_home / 'config.toml'}")
    if ensure_bridge_skill(codex_home=codex_home, dry_run=args.dry_run):
        baseline_changed += 1
        print(f"upsert: {codex_home / 'skills' / 'claudekit-command-bridge'}")

    # Enable multi_agent flag
    config_path = codex_home / "config.toml"
    if enforce_multi_agent_flag(config_path, dry_run=args.dry_run):
        print(f"upsert: multi_agent = true in {config_path}")

    print(f"baseline_changed={baseline_changed}")

    prompt_stats = export_prompts(codex_home=codex_home, include_mcp=args.include_mcp, dry_run=args.dry_run)
    print(
        f"prompts: added={prompt_stats['added']} updated={prompt_stats['updated']} "
        f"total_generated={prompt_stats['total_generated']}"
    )

    bootstrap_stats = None
    if not args.skip_bootstrap:
        bootstrap_stats = bootstrap_deps(
            codex_home=codex_home,
            include_mcp=args.include_mcp,
            include_test_deps=args.include_test_deps,
            dry_run=args.dry_run,
        )
        print(
            f"bootstrap: python_ok={bootstrap_stats['python_ok']} "
            f"python_fail={bootstrap_stats['python_fail']}"
        )
        if (bootstrap_stats["python_fail"] or bootstrap_stats["node_fail"]) and not args.dry_run:
            raise SyncError("Dependency bootstrap reported failures")

    verify_stats = None
    if not args.skip_verify:
        verify_stats = verify_runtime(codex_home=codex_home, dry_run=args.dry_run)
        print(f"verify: {verify_stats}")

    # Save registry
    if not args.dry_run:
        save_registry(codex_home, registry)

    summary = {
        "source": str(source) if use_live else str(zip_path),
        "source_mode": "live" if use_live else "zip",
        "codex_home": str(codex_home),
        "workspace": str(workspace),
        "dry_run": args.dry_run,
        "include_mcp": args.include_mcp,
        "include_hooks": args.include_hooks,
        "assets": assets_stats,
        "skills": skills_stats,
        "normalize_changed": changed,
        "agent_toml_changed": agent_toml_changed,
        "baseline_changed": baseline_changed,
        "prompts": prompt_stats,
        "bootstrap": bootstrap_stats,
        "verify": verify_stats,
    }
    print_summary(summary)
    print("done: claudekit all-in-one sync completed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SyncError as exc:
        eprint(f"error: {exc}")
        raise SystemExit(2)
