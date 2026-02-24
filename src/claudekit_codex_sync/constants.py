"""Constants for path normalization and sync operations."""

from typing import List, Set, Tuple

ASSET_DIRS = {"output-styles", "rules", "scripts"}
ASSET_FILES = {".env.example", ".ck.json"}
ASSET_MANIFEST = ".sync-manifest-assets.txt"
REGISTRY_FILE = ".claudekit-sync-registry.json"


EXCLUDED_SKILLS_ALWAYS: Set[str] = {"template-skill"}
MCP_SKILLS: Set[str] = {"mcp-builder", "mcp-management"}
CONFLICT_SKILLS: Set[str] = {"skill-creator"}

# Base path replacements shared across all contexts
_BASE_PATH_REPLACEMENTS: List[Tuple[str, str]] = [
    ("$HOME/.claude/skills/", "${CODEX_HOME:-$HOME/.codex}/skills/"),
    ("$HOME/.claude/scripts/", "${CODEX_HOME:-$HOME/.codex}/scripts/"),
    ("$HOME/.claude/rules/", "${CODEX_HOME:-$HOME/.codex}/rules/"),
    ("$HOME/.claude/", "${CODEX_HOME:-$HOME/.codex}/"),
    ("~/.claude/", "~/.codex/"),
]

SKILL_MD_REPLACEMENTS: List[Tuple[str, str]] = _BASE_PATH_REPLACEMENTS + [
    ("./.claude/skills/", "${CODEX_HOME:-$HOME/.codex}/skills/"),
    (".claude/skills/", "${CODEX_HOME:-$HOME/.codex}/skills/"),
    ("./.claude/scripts/", "${CODEX_HOME:-$HOME/.codex}/scripts/"),
    (".claude/scripts/", "${CODEX_HOME:-$HOME/.codex}/scripts/"),
    ("./.claude/rules/", "${CODEX_HOME:-$HOME/.codex}/rules/"),
    (".claude/rules/", "${CODEX_HOME:-$HOME/.codex}/rules/"),
    ("~/.claude/.ck.json", "~/.codex/.ck.json"),
    ("./.claude/.ck.json", "~/.codex/.ck.json"),
    (".claude/.ck.json", "~/.codex/.ck.json"),
    ("./.claude/", "./.codex/"),
    ("<project>/.claude/", "<project>/.codex/"),
    (".claude/", ".codex/"),
    ("`.claude`", "`.codex`"),
    ("$HOME/${CODEX_HOME:-$HOME/.codex}/", "${CODEX_HOME:-$HOME/.codex}/"),
]

AGENT_TOML_REPLACEMENTS: List[Tuple[str, str]] = _BASE_PATH_REPLACEMENTS + [
    ("$HOME/.claude/.ck.json", "${CODEX_HOME:-$HOME/.codex}/.ck.json"),
    ("$HOME/.claude/.mcp.json", "${CODEX_HOME:-$HOME/.codex}/.mcp.json"),
]

CLAUDE_SYNTAX_ADAPTATIONS: List[Tuple[str, str]] = [
    ("Task(Explore)", "the explore agent"),
    ("Task(researcher)", "the researcher agent"),
    ("Task(", "delegate to "),
    ("$HOME/.claude/skills/*", "${CODEX_HOME:-$HOME/.codex}/skills/*"),
    ("via Task tool", "via agent delegation"),
    ("Claude Code", "Codex CLI"),
    ("claude code", "Codex CLI"),
]

# Claude model → Codex model mapping (per developers.openai.com/codex/multi-agent)
CLAUDE_TO_CODEX_MODELS: dict[str, str] = {
    "opus": "gpt-5.3-codex",
    "sonnet": "gpt-5.3-codex",
    "haiku": "gpt-5.3-codex-spark",
    "inherit": "",
}

# Reasoning effort per Claude model tier
CLAUDE_MODEL_REASONING_EFFORT: dict[str, str] = {
    "opus": "xhigh",
    "sonnet": "high",
    "haiku": "medium",
}

# Agents that should be read-only (no file writes needed)
READ_ONLY_AGENT_ROLES: Set[str] = {
    "brainstormer",
    "code_reviewer",
    "researcher",
    "project_manager",
    "journal_writer",
}
