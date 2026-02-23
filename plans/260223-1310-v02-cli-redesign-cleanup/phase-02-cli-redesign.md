# Phase 2 — CLI Redesign: `ckc-sync`

## Overview
- Priority: P0
- Status: [x] Implemented (code complete, local install step pending)
- Estimated: 45 min

## Key Insights
- `ck migrate -g -f` pattern from ClaudeKit sets UX precedent
- Default scope project (`./.codex/`) is more useful than always global
- 14 flags → 8 flags: remove redundant, merge overlapping, rename verbose

## Code Changes

### [MODIFY] `src/claudekit_codex_sync/cli.py`

**Replace entire `parse_args()` function (lines 29-47) with:**

```python
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="ckc-sync",
        description="Sync ClaudeKit skills, agents, and config to Codex CLI.",
    )
    # Scope
    p.add_argument(
        "-g", "--global", dest="global_scope", action="store_true",
        help="Sync to ~/.codex/ (default: ./.codex/)",
    )
    # Sync mode
    p.add_argument(
        "-f", "--fresh", action="store_true",
        help="Clean target dirs before sync",
    )
    p.add_argument(
        "--force", action="store_true",
        help="Overwrite user-edited files without backup",
    )
    p.add_argument(
        "--zip", dest="zip_path", type=Path,
        help="Sync from zip instead of live ~/.claude/",
    )
    p.add_argument(
        "--source", type=Path, default=None,
        help="Custom source dir (default: ~/.claude/)",
    )
    # Content
    p.add_argument(
        "--mcp", action="store_true",
        help="Include MCP skills",
    )
    p.add_argument(
        "--no-deps", action="store_true",
        help="Skip dependency bootstrap (venv)",
    )
    # Output
    p.add_argument(
        "-n", "--dry-run", action="store_true",
        help="Preview only",
    )
    return p.parse_args()
```

**Replace `main()` function (lines 50-191) with:**

```python
def main() -> int:
    args = parse_args()

    # Scope: -g → global (~/.codex/), default → project (./.codex/)
    if args.global_scope:
        codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser().resolve()
    else:
        codex_home = (Path.cwd() / ".codex").resolve()

    workspace = Path.cwd().resolve()
    codex_home.mkdir(parents=True, exist_ok=True)

    # Fresh: clean target before sync
    if args.fresh:
        from .clean_target import clean_target
        removed = clean_target(codex_home, dry_run=args.dry_run)
        print(f"fresh: removed {removed} files")

    # Load registry
    registry = load_registry(codex_home)

    # Source resolution
    use_live = args.zip_path is None
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

    # Sync assets
    if use_live:
        assets_stats = sync_assets_from_dir(
            source, codex_home=codex_home, include_hooks=True, dry_run=args.dry_run
        )
        skills_stats = sync_skills_from_dir(
            source,
            codex_home=codex_home,
            include_mcp=args.mcp,
            include_conflicts=args.force,
            dry_run=args.dry_run,
        )
    else:
        with zipfile.ZipFile(zip_path) as zf:
            assets_stats = sync_assets(
                zf, codex_home=codex_home, include_hooks=True, dry_run=args.dry_run
            )
            skills_stats = sync_skills(
                zf,
                codex_home=codex_home,
                include_mcp=args.mcp,
                include_conflicts=args.force,
                dry_run=args.dry_run,
            )

    print(f"assets: added={assets_stats['added']} updated={assets_stats['updated']}")
    print(f"skills: added={skills_stats['added']} updated={skills_stats['updated']}")

    # Normalize
    changed = normalize_files(codex_home=codex_home, include_mcp=args.mcp, dry_run=args.dry_run)
    print(f"normalize_changed={changed}")

    agent_toml_changed = normalize_agent_tomls(codex_home=codex_home, dry_run=args.dry_run)
    print(f"agent_toml_changed={agent_toml_changed}")

    # Register agents in config.toml
    from .config_enforcer import register_agents
    agents_registered = register_agents(codex_home=codex_home, dry_run=args.dry_run)
    print(f"agents_registered={agents_registered}")

    # Baseline config
    baseline_changed = 0
    if ensure_agents(workspace=workspace, dry_run=args.dry_run):
        baseline_changed += 1
    if enforce_config(codex_home=codex_home, include_mcp=args.mcp, dry_run=args.dry_run):
        baseline_changed += 1
    if ensure_bridge_skill(codex_home=codex_home, dry_run=args.dry_run):
        baseline_changed += 1

    config_path = codex_home / "config.toml"
    enforce_multi_agent_flag(config_path, dry_run=args.dry_run)
    print(f"baseline_changed={baseline_changed}")

    # Prompts
    prompt_stats = export_prompts(codex_home=codex_home, include_mcp=args.mcp, dry_run=args.dry_run)
    print(f"prompts: added={prompt_stats['added']} total={prompt_stats['total_generated']}")

    # Dependencies
    bootstrap_stats = None
    if not args.no_deps:
        bootstrap_stats = bootstrap_deps(
            codex_home=codex_home,
            include_mcp=args.mcp,
            dry_run=args.dry_run,
        )
        print(f"bootstrap: py_ok={bootstrap_stats['python_ok']} py_fail={bootstrap_stats['python_fail']}")
        if bootstrap_stats["python_fail"] and not args.dry_run:
            raise SyncError("Dependency bootstrap reported failures")

    # Verify
    verify_stats = verify_runtime(codex_home=codex_home, dry_run=args.dry_run)
    print(f"verify: {verify_stats}")

    # Save registry
    if not args.dry_run:
        save_registry(codex_home, registry)

    # Summary
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
```

**Note:** `include_test_deps` removed from `bootstrap_deps()` call — see Phase 3.

### [NEW] `src/claudekit_codex_sync/clean_target.py`

Complete new file:

```python
"""Clean target directories for --fresh sync."""

from __future__ import annotations

import shutil
from pathlib import Path


def clean_target(codex_home: Path, *, dry_run: bool) -> int:
    """Remove agents, skills (keep .venv), prompts, claudekit before fresh sync."""
    removed = 0

    # Remove entire dirs
    for subdir in ("agents", "prompts", "claudekit"):
        target = codex_home / subdir
        if target.exists():
            count = sum(1 for _ in target.rglob("*") if _.is_file())
            removed += count
            print(f"fresh: rm {subdir}/ ({count} files)")
            if not dry_run:
                shutil.rmtree(target)

    # Skills: remove skill dirs but keep .venv
    skills = codex_home / "skills"
    if skills.exists():
        for item in skills.iterdir():
            if item.name == ".venv":
                continue
            if item.is_dir():
                count = sum(1 for _ in item.rglob("*") if _.is_file())
                removed += count
                if not dry_run:
                    shutil.rmtree(item)
            else:
                removed += 1
                if not dry_run:
                    item.unlink()
        print(f"fresh: rm skills/* (kept .venv)")

    # Clear registry + manifests
    for name in (
        ".claudekit-sync-registry.json",
        ".sync-manifest-assets.txt",
        ".claudekit-generated-prompts.txt",
    ):
        f = codex_home / name
        if f.exists():
            removed += 1
            if not dry_run:
                f.unlink()

    return removed
```

### [MODIFY] `package.json`

**Current:**
```json
{
  "name": "claudekit-codex-sync",
  "version": "0.1.0",
  "bin": {
    "ck-codex-sync": "bin/ck-codex-sync.js"
  }
}
```

**Replace with:**
```json
{
  "name": "claudekit-codex-sync",
  "version": "0.2.0",
  "description": "Sync ClaudeKit skills, agents, and config to Codex CLI",
  "main": "bin/ck-codex-sync.js",
  "bin": {
    "ckc-sync": "bin/ck-codex-sync.js",
    "ck-codex-sync": "bin/ck-codex-sync.js"
  },
  "scripts": {
    "sync": "python3 src/claudekit_codex_sync/cli.py",
    "test": "python3 -m pytest tests/",
    "lint": "python3 -m py_compile src/claudekit_codex_sync/*.py"
  },
  "keywords": ["claudekit", "codex", "sync", "skills"],
  "license": "MIT"
}
```

## Verification

```bash
# Verify new flags
ckc-sync --help
ckc-sync -g -n            # dry-run global
ckc-sync -n               # dry-run project
ckc-sync -g -f -n         # dry-run fresh global

# Backward compat
ck-codex-sync --help      # old name still works
```

## Todo
- [x] Rewrite `parse_args()` with 8 flags
- [x] Rewrite `main()` with scope logic + fresh + force + register_agents
- [x] Create `clean_target.py`
- [x] Update `package.json` (add `ckc-sync` bin, bump version)
- [ ] Run `npm install -g .` to register new command
