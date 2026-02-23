# Eliminate `claudekit/` Subdirectory

Remove `~/.codex/claudekit/` nesting — copy assets directly to `~/.codex/`.

## Problem

Assets copy to `~/.codex/claudekit/{scripts,rules,commands,...}` then paths rewrite to reference `claudekit/`. Unnecessary since `~/.claude/` always exists and assets should live at top-level.

## Phases

| # | Phase | Status | Files |
|---|---|---|---|
| 1 | [Path rewrites](file:///home/vinhawk/claudekit-codex-sync/plans/260223-1550-eliminate-claudekit-subdir/phase-01-path-rewrites.md) | `[x]` | `constants.py` |
| 2 | [Asset copy](file:///home/vinhawk/claudekit-codex-sync/plans/260223-1550-eliminate-claudekit-subdir/phase-02-asset-copy.md) | `[x]` | `asset_sync_dir.py`, `asset_sync_zip.py` |
| 3 | [Consumers](file:///home/vinhawk/claudekit-codex-sync/plans/260223-1550-eliminate-claudekit-subdir/phase-03-consumers.md) | `[x]` | `prompt_exporter.py`, `path_normalizer.py`, `clean_target.py` |
| 4 | [Tests + docs + release](file:///home/vinhawk/claudekit-codex-sync/plans/260223-1550-eliminate-claudekit-subdir/phase-04-tests-docs-release.md) | `[x]` | tests, docs, README, npm |

## Before → After

```
~/.codex/                    ~/.codex/
  claudekit/                   commands/*.md      ← direct
    commands/*.md              output-styles/*.md  ← direct
    output-styles/*.md         rules/*.md          ← direct
    rules/*.md                 scripts/*.cjs       ← direct
    scripts/*.cjs              .ck.json            ← direct
    .ck.json                   .env.example        ← direct
    .env.example
```

## Dependencies

Phase 1 → Phase 2 → Phase 3 → Phase 4 (strict sequential)

## Risk

Low — localized string replacements + path changes. No logic change.
