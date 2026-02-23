---
title: "ClaudeKit Codex Community Toolkit"
description: "Productize sync scripts for npm + git clone and add parity proof between Claude and Codex workflows"
status: pending
priority: P1
effort: 5d
branch: local/home-vinhawk
tags: [feature, tooling, codex, claudekit, community]
created: 2026-02-22
---

# ClaudeKit Codex Community Toolkit

## Summary
Build a community-ready toolkit that syncs ClaudeKit -> Codex with full automation, supports npm and git-clone distribution, and includes measurable parity testing to support "near-similar behavior" claims.

## Scope
### In scope
- Productize current sync engine into reusable CLI package.
- Add Claude-agent -> Codex-agent role transpiler.
- Add parity benchmark harness with reproducible scoring.
- Publish via npm (`npx`) and git clone workflow.
- Add docs, CI, release process, compatibility matrix.

### Out of scope (v1)
- Full TypeScript rewrite of existing Python core.
- MCP/hooks parity as default behavior.
- Proprietary cloud telemetry or hosted backend.

## Key Decisions
1. Keep Python core for v1 to reduce regression risk.
2. Add Node wrapper for npm UX (`npx`).
3. Use prefixed roles (`ck-*`) by default to avoid accidental built-in override.
4. Prove parity with benchmark metrics, not subjective statements.
5. Ship staged releases (`v1` -> `v1.1`) instead of big-bang rewrite.

## Phases
| Phase | File | Goal | Effort |
|---|---|---|---|
| Phase 1 | [phase-01-productization.md](./phase-01-productization.md) | Repo/product baseline and public packaging structure | 0.5d |
| Phase 2 | [phase-02-core-refactor.md](./phase-02-core-refactor.md) | Refactor current script into maintainable core modules | 1d |
| Phase 3 | [phase-03-agent-transpiler.md](./phase-03-agent-transpiler.md) | Claude agent definitions -> Codex roles transpilation | 1d |
| Phase 4 | [phase-04-parity-harness.md](./phase-04-parity-harness.md) | Deterministic benchmark + scoring and reports | 1d |
| Phase 5 | [phase-05-distribution-npm.md](./phase-05-distribution-npm.md) | npm wrapper, npx flow, preflight checks | 0.75d |
| Phase 6 | [phase-06-git-clone-docs.md](./phase-06-git-clone-docs.md) | Git-clone install flow, docs, examples | 0.5d |
| Phase 7 | [phase-07-qa-release.md](./phase-07-qa-release.md) | CI matrix, release automation, quality gates | 0.25d |

## Architecture Overview
```
┌───────────────────────────────────────────────────────────────────┐
│ community repo (public)                                           │
│  ├─ packages/cli-node (npm wrapper, preflight, UX)               │
│  ├─ packages/core-python (sync engine + transpiler + benchmark)  │
│  ├─ fixtures/ (zip + ~/.claude snapshots for tests)              │
│  ├─ docs/ (install, config, parity methodology)                  │
│  └─ .github/workflows/ (CI matrix + release)                     │
└───────────────────────────────────────────────────────────────────┘
                       │
                       ▼
             user machine (Ubuntu/macOS/WSL)
                       │
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
   npx claudekit-codex-sync      git clone + ./scripts/install.sh
```

## Success Criteria
1. Install and run success >=95% on Ubuntu/macOS/WSL.
2. Sync + verify pass >=98% on supported fixtures.
3. Parity benchmark >=85% before public parity claim.
4. Re-run idempotency: second run produces no destructive drift.
5. Clear rollback path documented and tested.

## Risks & Mitigations
| Risk | Impact | Mitigation |
|---|---|---|
| Runtime semantics differ Claude vs Codex | False parity claims | Use outcome-based scoring + publish raw reports |
| npm wrapper fails due missing Python | Install friction | Preflight checks + one-line remediation |
| Agent transpiler overfits one kit version | Fragile updates | Schema validation + fixture regression tests |
| Codex feature drift (`multi_agent`) | Break role flows | Version matrix + compatibility checks |

## Deliverables
- Public-ready repository structure.
- CLI commands for sync, transpile, benchmark, verify.
- Published npm package + tagged git release.
- Benchmark report template and reproducible results.
- Operational docs for users and contributors.

## Implementation Notes
- Keep MCP/hooks opt-in flags intact.
- Preserve latest-zip selection behavior as default.
- Ensure `--dry-run` and `--json` output for automation consumers.
- Add "strict mode" for CI (non-zero exit on parity threshold miss).

## Open Questions
1. Final npm package name preference (`claudekit-codex-sync` vs alternatives)?
2. License choice for community repo (MIT/Apache-2.0)?
3. Initial support policy: LTS + latest Codex only, or broad version range?
