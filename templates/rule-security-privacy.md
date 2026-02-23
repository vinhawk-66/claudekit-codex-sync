# Security & Privacy

## Sensitive File Access
Ask user for explicit approval before reading:
- `.env`, `.env.*` (API keys, passwords, tokens)
- `*.key`, `*.pem`, `*.p12`, `credentials.*`, `secrets.*`
- Files in `~/.ssh/`, `~/.gnupg/`, `~/.aws/`

**Flow:** State which file and why → wait for "yes" → read via cat → never output full secrets.

## Directory Access Control
Respect `.ckignore` patterns if present in project root:
- Read `.ckignore` at session start
- Do NOT access matching directories
- Common: `node_modules/`, `dist/`, `build/`, `.git/objects/`
