# Phase 3: Update Consumers

**Priority:** High
**Status:** `[ ]` Not started
**Files:** `prompt_exporter.py`, `path_normalizer.py`, `clean_target.py`

## Overview

Update all modules that read from `claudekit/` to read from top-level dirs.

## Changes

### prompt_exporter.py (L28)

```diff
-    source = codex_home / "claudekit" / "commands"
+    source = codex_home / "commands"
```

### path_normalizer.py

#### normalize_files() — L23-70

Replace single `claudekit_dir.rglob("*.md")` with iteration over individual asset dirs:

```python
def normalize_files(...):
    skills_dir = codex_home / "skills"
    changed = 0

    # Normalize skill files (unchanged)
    for path in sorted(skills_dir.rglob("*.md")):
        ...

    # Normalize asset .md files (was: claudekit_dir.rglob)
    for subdir in ("commands", "output-styles", "rules"):
        target_dir = codex_home / subdir
        if not target_dir.exists():
            continue
        for path in sorted(target_dir.rglob("*.md")):
            rel = path.relative_to(codex_home).as_posix()
            text = path.read_text(encoding="utf-8", errors="ignore")
            new_text = apply_replacements(text, SKILL_MD_REPLACEMENTS)
            if new_text != text:
                changed += 1
                print(f"normalize: {rel}")
                if not dry_run:
                    path.write_text(new_text, encoding="utf-8")

    # Copywriting script patch (unchanged)
    ...

    # Command map (updated path)
    command_map = codex_home / "commands" / "codex-command-map.md"
    ...
```

### clean_target.py

Replace `"claudekit"` in clean list with individual asset dirs:

```python
def clean_target(codex_home, *, dry_run):
    removed = 0

    # Clean top-level dirs (was: "agents", "prompts", "claudekit")
    for subdir in ("agents", "prompts", "commands", "output-styles", "rules", "scripts"):
        target = codex_home / subdir
        if target.exists():
            count = sum(1 for item in target.rglob("*") if item.is_file())
            removed += count
            print(f"fresh: rm {subdir}/ ({count} files)")
            if not dry_run:
                shutil.rmtree(target)

    # skills (keep .venv symlink, delete real .venv)
    ...

    # Clean top-level files (add .ck.json, .env.example)
    for name in (
        ".claudekit-sync-registry.json",
        ".sync-manifest-assets.txt",
        ".claudekit-generated-prompts.txt",
        ".ck.json",
        ".env.example",
    ):
        ...
```

## Todo

- [ ] Update `prompt_exporter.py` — `commands` path
- [ ] Update `path_normalizer.py` — iterate asset dirs instead of `claudekit_dir`
- [ ] Update `clean_target.py` — clean individual dirs, add `.ck.json`/`.env.example`
- [ ] Compile check
- [ ] Update tests for `clean_target.py` if needed

## Success Criteria

- `grep -r "claudekit" src/` returns only registry/manifest filenames, NOT paths
- Prompts generate correctly from `codex_home/commands/`
