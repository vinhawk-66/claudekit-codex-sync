# Phase 3: Modularize Python

Status: pending
Priority: critical
Effort: 1d

## Goal
Split 1151-line `claudekit-sync-all.py` into 11 modules, each <200 lines.

## Module Split

### `src/claudekit_codex_sync/utils.py` (~90 lines)
From lines: 394-502
```python
# Functions: SyncError, eprint, run_cmd, ensure_parent,
# write_bytes_if_changed, write_text_if_changed, zip_mode,
# find_latest_zip (→ moved to source_resolver), load_manifest,
# save_manifest, apply_replacements, is_excluded_path
```

### `src/claudekit_codex_sync/source_resolver.py` (~80 lines)
From lines: 453-591
```python
# Functions: find_latest_zip, collect_skill_entries
# NEW: detect_claude_source, validate_claude_source
```

### `src/claudekit_codex_sync/asset_sync.py` (~160 lines)
From lines: 505-656
```python
# Functions: sync_assets, sync_skills
# NEW: sync_assets_from_dir, sync_skills_from_dir
```

### `src/claudekit_codex_sync/path_normalizer.py` (~120 lines)
From lines: 353-391, 493-497, 659-772
```python
# Constants: SKILL_MD_REPLACEMENTS, PROMPT_REPLACEMENTS
# NEW: AGENT_TOML_REPLACEMENTS
# Functions: apply_replacements, normalize_files, patch_copywriting_script
# NEW: normalize_agent_tomls
```

### `src/claudekit_codex_sync/config_enforcer.py` (~80 lines)
From lines: 795-846
```python
# Functions: ensure_agents, enforce_config
# NEW: enforce_multi_agent_flag
```

### `src/claudekit_codex_sync/prompt_exporter.py` (~100 lines)
From lines: 849-937
```python
# Functions: ensure_frontmatter, export_prompts
```

### `src/claudekit_codex_sync/dep_bootstrapper.py` (~60 lines)
From lines: 940-998
```python
# Functions: bootstrap_deps
```

### `src/claudekit_codex_sync/runtime_verifier.py` (~30 lines)
From lines: 1001-1021
```python
# Functions: verify_runtime
```

### `src/claudekit_codex_sync/bridge_generator.py` (~30 lines)
From lines: 775-792
```python
# Functions: ensure_bridge_skill (reads templates from files)
```

### `src/claudekit_codex_sync/cli.py` (~100 lines)
From lines: 1028-1151
```python
# Functions: parse_args, main, print_summary
# Imports all modules, orchestrates the sync
```

## Import Structure
```
cli.py
├── source_resolver.py
├── asset_sync.py ── utils.py
├── path_normalizer.py ── utils.py
├── config_enforcer.py ── utils.py
├── prompt_exporter.py ── utils.py, path_normalizer.py
├── dep_bootstrapper.py ── utils.py
├── runtime_verifier.py ── utils.py
└── bridge_generator.py ── utils.py
```

## Todo
- [ ] Create utils.py
- [ ] Create source_resolver.py
- [ ] Create asset_sync.py
- [ ] Create path_normalizer.py
- [ ] Create config_enforcer.py
- [ ] Create prompt_exporter.py
- [ ] Create dep_bootstrapper.py
- [ ] Create runtime_verifier.py
- [ ] Create bridge_generator.py
- [ ] Create cli.py (orchestrator)
- [ ] Delete old scripts/claudekit-sync-all.py
- [ ] Verify: each module <200 lines
