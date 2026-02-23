# Phase 07: QA, CI, and Release

## Goal
Ship safely with repeatable quality gates and predictable releases.

## Tasks
1. CI matrix:
   - Ubuntu
   - macOS
   - WSL smoke runner (if available)
2. Test pipeline:
   - unit
   - integration
   - parity benchmark threshold gate
3. Release pipeline:
   - semantic versioning
   - changelog generation
   - npm publish
   - git tag/release notes
4. Add compatibility matrix and deprecation policy.

## Deliverables
- Automated CI + release workflow.
- Stable release quality bars documented and enforced.

## Acceptance Criteria
- Release candidate fails if parity below threshold.
- Tagged release publishes npm package and changelog.
- Rollback procedure validated once.

## Risks
- Flaky parity tests block releases.

## Mitigation
- Separate flaky detector and quarantine process; keep stable core gate strict.
