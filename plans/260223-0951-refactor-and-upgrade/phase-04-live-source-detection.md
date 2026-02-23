# Phase 4: Live Source + Claude Dir Detection

Status: pending
Priority: critical
Effort: 0.5d

## Goal
Add `--source-mode live` to read directly from `~/.claude/` instead of zip. Auto-detect Claude installation.

## Changes to `source_resolver.py`

```python
def detect_claude_source() -> Path:
    """Auto-detect Claude Code installation."""
    candidates = [
        Path.home() / ".claude",
        Path(os.environ.get("USERPROFILE", "")) / ".claude",
    ]
    for p in candidates:
        if p.exists() and (p / "skills").is_dir():
            return p
    raise SyncError("Claude Code not found. Use --source-dir to specify.")

def validate_source(source: Path) -> dict:
    return {
        "skills": (source / "skills").is_dir(),
        "agents": (source / "agents").is_dir(),
        "commands": (source / "commands").is_dir(),
        "rules": (source / "rules").is_dir(),
        "claude_md": (source / "CLAUDE.md").is_file(),
    }
```

## Changes to `cli.py`

Add args:
```python
p.add_argument("--source-mode", choices=["auto", "live", "zip"], default="auto")
p.add_argument("--source-dir", type=Path, default=None)
```

Route in main:
```python
if source_mode == "live" or (source_mode == "auto" and source_dir):
    source = source_dir or detect_claude_source()
    sync_assets_from_dir(source, ...)
    sync_skills_from_dir(source, ...)
else:
    zip_path = find_latest_zip(args.zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        sync_assets(zf, ...)
        sync_skills(zf, ...)
```

## Changes to `asset_sync.py`

```python
def sync_skills_from_dir(source: Path, *, codex_home: Path, ...) -> Dict[str, int]:
    skills_src = source / "skills"
    skills_dst = codex_home / "skills"
    for skill_dir in sorted(skills_src.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue
        # apply same exclusion logic as sync_skills
        dst = skills_dst / skill_dir.name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(skill_dir, dst)
```

## Todo
- [ ] Add detect_claude_source() + validate
- [ ] Add --source-mode, --source-dir args
- [ ] Add sync_assets_from_dir()
- [ ] Add sync_skills_from_dir()
- [ ] Route in main()
