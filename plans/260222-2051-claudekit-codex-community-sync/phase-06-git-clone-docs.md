# Phase 06: Git-Clone Workflow and Docs

## Goal
Ensure users who prefer direct clone can run the toolkit with zero ambiguity.

## Tasks
1. Add `scripts/install.sh` and `scripts/install.ps1` for bootstrap.
2. Add one-command usage examples for:
   - latest zip auto-sync
   - explicit zip path
   - global vs workspace scope
   - dry-run and rollback flow
3. Add migration guide from private script path to community repo CLI.
4. Add troubleshooting section for common environment issues.

## Deliverables
- Git-clone installation path fully documented.
- Copy/paste-ready command docs for common workflows.

## Acceptance Criteria
- Fresh machine can clone and run sync in <=10 minutes using docs only.
- Troubleshooting covers top 10 expected errors.

## Risks
- Docs drift from implementation.

## Mitigation
- Add docs validation checklist in release process.
