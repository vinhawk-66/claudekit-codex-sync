"""Generate hook-equivalent rules from templates."""

from __future__ import annotations

from pathlib import Path

from .utils import load_template, write_text_if_changed


RULE_TEMPLATES = {
    "security-privacy.md": "rule-security-privacy.md",
    "file-naming.md": "rule-file-naming.md",
    "code-quality-reminders.md": "rule-code-quality.md",
}


def generate_hook_rules(*, codex_home: Path, dry_run: bool) -> int:
    """Generate rules that replace ClaudeKit hook behavior."""
    rules_dir = codex_home / "rules"
    if not dry_run:
        rules_dir.mkdir(parents=True, exist_ok=True)

    generated = 0
    for rule_name, template_name in RULE_TEMPLATES.items():
        content = load_template(template_name)
        target = rules_dir / rule_name
        if write_text_if_changed(target, content, dry_run=dry_run):
            generated += 1

    return generated
