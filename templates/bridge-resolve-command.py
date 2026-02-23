#!/usr/bin/env python3
import sys

MAP = {
    "/preview": "markdown-novel-viewer",
    "/kanban": "plans-kanban",
    "/review/codebase": "code-review",
    "/test": "web-testing",
    "/test/ui": "web-testing",
    "/worktree": "git",
    "/plan": "plan",
    "/plan/validate": "plan",
    "/plan/archive": "project-management",
    "/plan/red-team": "plan",
    "/docs/init": "claudekit-command-bridge (docs-init.sh)",
    "/docs/update": "claudekit-command-bridge",
    "/docs/summarize": "claudekit-command-bridge",
    "/journal": "claudekit-command-bridge",
    "/watzup": "claudekit-command-bridge",
    "/ask": "claudekit-command-bridge (architecture mode)",
    "/coding-level": "claudekit-command-bridge (explanation depth)",
    "/ck-help": "claudekit-command-bridge (this resolver)",
}


def main() -> int:
    raw = " ".join(sys.argv[1:]).strip()
    if not raw:
        print('Usage: resolve-command.py "<legacy-command-or-intent>"')
        return 1

    cmd = raw.split()[0]
    if cmd in MAP:
        print(f"{cmd} -> {MAP[cmd]}")
        return 0

    for prefix, target in [
        ("/docs/", "claudekit-command-bridge"),
        ("/plan/", "plan"),
        ("/review/", "code-review"),
        ("/test", "web-testing"),
    ]:
        if cmd.startswith(prefix):
            print(f"{cmd} -> {target}")
            return 0

    print(f"{cmd} -> no direct map; use find-skills + claudekit-command-bridge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
