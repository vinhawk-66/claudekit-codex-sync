# Phase 01: Productization Baseline

## Goal
Turn current private script set into a repository-grade project layout ready for public collaboration.

## Tasks
1. Define repository structure (`packages`, `scripts`, `docs`, `fixtures`, `tests`).
2. Add base metadata:
   - `README.md`
   - `LICENSE`
   - `CONTRIBUTING.md`
   - `SECURITY.md`
   - `CODE_OF_CONDUCT.md`
3. Add configuration conventions:
   - `.editorconfig`
   - `.gitignore`
   - formatting/lint standards
4. Define support matrix doc:
   - OS support
   - Codex version compatibility
   - Python/Node requirements

## Deliverables
- Public repo skeleton with contribution standards.
- Clear scope and support boundaries.

## Acceptance Criteria
- New contributor can clone repo and understand project purpose in <5 minutes.
- Required project policy files exist and are coherent.
- Basic local setup instructions are complete and tested once.

## Risks
- Over-documentation before stable CLI behavior.

## Mitigation
- Keep docs minimal for v1 and expand only after phase 5.
