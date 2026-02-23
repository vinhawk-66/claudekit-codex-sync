# Phase 1: Project Structure

Status: pending
Priority: critical
Effort: 0.5d

## Goal
Initialize npm project structure, .gitignore, and module directories.

## Steps

### 1.1 Initialize npm
```bash
cd /home/vinhawk/claudekit-codex-sync
npm init -y
```

Edit `package.json`:
```json
{
  "name": "claudekit-codex-sync",
  "version": "0.1.0",
  "description": "Sync ClaudeKit skills, agents, and config to Codex CLI",
  "main": "bin/ck-codex-sync.js",
  "bin": { "ck-codex-sync": "bin/ck-codex-sync.js" },
  "scripts": {
    "sync": "python3 src/claudekit_codex_sync/cli.py",
    "test": "python3 -m pytest tests/",
    "lint": "python3 -m py_compile src/claudekit_codex_sync/*.py"
  },
  "keywords": ["claudekit", "codex", "sync", "skills"],
  "license": "MIT"
}
```

### 1.2 Create bin/ck-codex-sync.js
```javascript
#!/usr/bin/env node
const { execSync } = require('child_process');
const path = require('path');
const script = path.join(__dirname, '..', 'src', 'claudekit_codex_sync', 'cli.py');
try {
  execSync(`python3 "${script}" ${process.argv.slice(2).join(' ')}`, { stdio: 'inherit' });
} catch (e) {
  process.exit(e.status || 1);
}
```

### 1.3 Create .gitignore
```
node_modules/
__pycache__/
*.pyc
.venv/
dist/
build/
*.egg-info/
.pytest_cache/
```

### 1.4 Create directories
```bash
mkdir -p src/claudekit_codex_sync templates tests docs
touch src/claudekit_codex_sync/__init__.py
```

### 1.5 Delete redundant bash scripts
```bash
git rm scripts/normalize-claudekit-for-codex.sh
git rm scripts/export-claudekit-prompts.sh
git rm scripts/bootstrap-claudekit-skill-scripts.sh
```

## Todo
- [ ] npm init + package.json
- [ ] bin/ck-codex-sync.js
- [ ] .gitignore
- [ ] Create src/ templates/ tests/ docs/ dirs
- [ ] Delete redundant bash scripts
