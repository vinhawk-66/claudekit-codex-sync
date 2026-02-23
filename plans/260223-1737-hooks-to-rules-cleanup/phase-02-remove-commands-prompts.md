# Phase 2: Remove Commands & Prompts Sync

Status: pending
Priority: high
Effort: 0.5d

## Goal

Eliminate commands/prompts duplication from pipeline. Commands already removed from `ASSET_DIRS` in Phase 1, now remove prompt generation.

## Context

- Codex [deprecated custom prompts](https://developers.openai.com/codex/custom-prompts) in favor of skills
- `prompt_exporter.py` generates duplicates of every command → wasteful
- Bridge skill already maps legacy `/commands` → Codex skills
- Both `commands/` and `prompts/` produce identical content

## Steps

### 2.1 Remove prompt export from CLI

**File:** [cli.py](file:///home/vinhawk/claudekit-codex-sync/src/claudekit_codex_sync/cli.py)

Remove import and call:

```diff
-from .prompt_exporter import export_prompts
+from .rules_generator import generate_hook_rules
```

Remove prompt export call (~line 188):

```diff
-    prompt_stats = export_prompts(codex_home=codex_home, include_mcp=args.mcp, dry_run=args.dry_run)
-    print(f"prompts: added={prompt_stats['added']} total={prompt_stats['total_generated']}")
```

Add rules generation call after normalize step (~line 163):

```diff
+    rules_generated = generate_hook_rules(codex_home=codex_home, dry_run=args.dry_run)
+    print(f"hook_rules_generated={rules_generated}")
```

Update summary dict:

```diff
-        "prompts": prompt_stats,
+        "rules_generated": rules_generated,
```

### 2.2 Remove prompts manifest from clean_target

**File:** [clean_target.py](file:///home/vinhawk/claudekit-codex-sync/src/claudekit_codex_sync/clean_target.py)

`".claudekit-generated-prompts.txt"` stays in cleanup list (for cleaning old installs) but `"prompts"` is already in the subdir cleanup loop — no change needed.

### 2.3 Remove PROMPT_MANIFEST/PROMPT_REPLACEMENTS usage

**File:** [constants.py](file:///home/vinhawk/claudekit-codex-sync/src/claudekit_codex_sync/constants.py)

Keep `PROMPT_REPLACEMENTS` and `PROMPT_MANIFEST` constants (no harm, `prompt_exporter.py` still importable). But mark as deprecated with comment:

```python
# DEPRECATED: prompt_exporter.py no longer called from CLI pipeline (v0.2.5)
PROMPT_MANIFEST = ".claudekit-generated-prompts.txt"
```

## Todo

- [ ] Remove `export_prompts` import from `cli.py`
- [ ] Remove prompt export call from `cli.py`
- [ ] Add `generate_hook_rules` import and call to `cli.py`
- [ ] Update summary dict in `cli.py`
- [ ] Mark `PROMPT_MANIFEST` as deprecated in `constants.py`

## Verification

```bash
python3 -m py_compile src/claudekit_codex_sync/cli.py
PYTHONPATH=src python3 -m claudekit_codex_sync.cli -g -n  # dry-run should not error
```
