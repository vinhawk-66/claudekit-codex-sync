# Phase 04: Parity Benchmark Harness

## Goal
Provide objective evidence for "near-similar behavior" between Claude flow and Codex transpiled flow.

## Tasks
1. Define benchmark suite (20-30 scenarios):
   - planning
   - code review
   - bug debug
   - docs update
   - research orchestration
2. Define scoring rubric:
   - task success
   - artifact completeness
   - policy compliance
   - orchestration quality
   - severity-weighted output quality
3. Implement benchmark runner:
   - fixture setup
   - command execution
   - result collection
   - score aggregation
4. Add report outputs:
   - JSON raw results
   - Markdown summary
   - trend comparison across versions
5. Add fail threshold gates for CI (`--min-parity`).

## Deliverables
- Reproducible parity suite and scorer.
- Public benchmark report format.

## Acceptance Criteria
- Single command runs full suite and outputs machine-readable report.
- Score reproducibility within acceptable variance window.
- Threshold gate blocks release when parity score is below target.

## Risks
- Benchmark bias or non-determinism.

## Mitigation
- Freeze fixtures, pin prompts, repeat-run averaging, and publish methodology.
