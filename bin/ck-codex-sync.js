#!/usr/bin/env node
const { execSync } = require('child_process');
const path = require('path');
const script = path.join(__dirname, 'ck-codex-sync');
try {
  execSync(`python3 "${script}" ${process.argv.slice(2).join(' ')}`, { stdio: 'inherit' });
} catch (e) {
  process.exit(e.status || 1);
}
