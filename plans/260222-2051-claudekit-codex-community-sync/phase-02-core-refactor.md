# Phase 02: Core Refactor

## Goal
Refactor existing `claudekit-sync-all.py` into maintainable modules while preserving behavior.

## Tasks
1. Split monolithic script into modules:
   - zip/source discovery
   - asset sync
   - skill sync
   - normalization/patches
   - prompt export
   - verification
2. Introduce typed config object and explicit defaults.
3. Add stable machine-readable output mode (`--json`).
4. Preserve existing flags and backward compatibility behavior.
5. Add regression tests against current fixture zip.

## Deliverables
- Modular core package with testable units.
- No functional regressions versus current script baseline.

## Acceptance Criteria
- Existing command scenarios produce equivalent outputs (except intentional formatting changes).
- Unit tests cover critical branches (zip selection, exclusion rules, manifests, idempotency).
- Re-run idempotency verified on fixture workspace.

## Risks
- Refactor introduces hidden behavior drift.

## Mitigation
- Snapshot-based regression assertions before/after refactor.
