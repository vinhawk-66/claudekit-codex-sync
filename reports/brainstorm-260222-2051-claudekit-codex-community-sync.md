# Brainstorm Report: ClaudeKit -> Codex Community Toolkit

## Problem Statement
You want a community-shareable toolkit that syncs ClaudeKit assets into Codex with minimal manual work, supports latest zip detection, and proves behavior is close to Claude workflows.

## Requirements
- Full-auto sync entrypoint (latest zip auto-select).
- Pull from both zip and local `~/.claude` where needed.
- Keep current exclusions default (`mcp`, `hooks`) but support opt-in.
- Add agent-role sync compatible with Codex multi-agent system.
- Publish for community consumption via:
  - `npm`/`npx` install path.
  - `git clone` + local run path.
- Provide evidence that behavior is close to ClaudeKit orchestration (not only file-copy parity).

## Current Reality Check
- Current script (`~/.codex/scripts/claudekit-sync-all.py`) is strong for assets/skills/rules/prompts sync.
- It is not yet productized as a public package.
- It does not yet implement Claude-agent -> Codex-agent role transpilation + parity benchmark harness.
- Behavior parity is therefore not yet provable by metrics.

## Approaches Evaluated

### Approach A: Keep Python Core + Add NPM Wrapper (Recommended for v1)
Pros:
- Fastest to ship.
- Reuses proven sync logic now.
- Lower regression risk.
- Easy to support both `npx` and `python3` direct run.

Cons:
- Requires Python on user machine.
- Wrapper layer adds runtime dependency checks.

### Approach B: Full Rewrite to TypeScript Core
Pros:
- Native npm experience.
- Simpler JS ecosystem integration.

Cons:
- High rewrite cost.
- High regression risk in edge behavior already solved in Python.
- Slower time-to-community release.

### Approach C: Maintain Two Cores (Python + TS)
Pros:
- Maximum flexibility.

Cons:
- Highest maintenance burden.
- Divergence risk.
- Not YAGNI.

## Recommended Strategy
- **Ship staged hybrid strategy**:
1. **v1**: Python core as source of truth + npm wrapper + git-clone workflow.
2. **v1.1**: Add agent transpiler and parity benchmark harness.
3. **v2**: Consider TS native core only if adoption justifies rewrite.

This gives speed now and keeps path to long-term polish without over-engineering.

## Claude -> Codex Customization That Matters Most
- Agent transpiler that converts Claude `agents/*.md` into Codex role config:
  - `~/.codex/config.toml` `[agents.<role>]`
  - `~/.codex/agents/<role>.toml`
- Role strategy:
  - Prefix custom roles (`ck-*`) to avoid overriding built-ins accidentally.
  - Allow explicit override mode if user wants `default/worker/explorer` replacement.
- Instruction normalization:
  - rewrite Claude-specific paths/tooling references to Codex equivalents.
  - preserve intent, not literal syntax.
- Execution guardrails:
  - per-role `sandbox_mode`, `model_reasoning_effort`, `developer_instructions`.

## Proof Plan: “Near-Similar Behavior”
Define parity suite and publish numbers:
- 20-30 canonical scenarios:
  - planning, research, review, debug, docs update, testing loops.
- A/B runs:
  - A: Claude original flow.
  - B: Codex transpiled flow.
- Score dimensions:
  - task success rate.
  - required artifact completeness.
  - policy compliance (test/lint/docs gates).
  - orchestration quality (spawn/wait/close behavior).
  - defect quality (severity-weighted findings for review/debug cases).

Target thresholds:
- >=85% parity: acceptable “near-similar”.
- >=90% parity: strong community-grade claim.

## Risks and Mitigations
- Risk: Codex/Claude runtime semantics differ.
  - Mitigation: parity scoring by outcomes, not literal step parity.
- Risk: multi-agent feature drift across Codex versions.
  - Mitigation: version compatibility matrix + CI smoke tests.
- Risk: wrapper install friction.
  - Mitigation: clear preflight checks + actionable errors.

## Success Metrics
- Install success rate >=95% on Ubuntu/macOS/WSL for default path.
- End-to-end sync success rate >=98% on supported fixtures.
- Parity benchmark >=85% before public “near-similar” claim.
- Time to run full sync + verify under 3 minutes on standard machine.

## Next Steps
- Create implementation plan with phases for:
  - productization,
  - transpiler,
  - benchmark harness,
  - npm + git distribution,
  - release process.
