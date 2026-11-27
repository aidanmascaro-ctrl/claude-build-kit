#!/usr/bin/env python3
"""Self-check for block-secret-dumps.py. Run: python3 tests/test_block_secret_dumps.py

Cases live in this file rather than on a command line because the guard would
(correctly) block a shell command containing these strings as literal text.
"""
import importlib.util
import pathlib
import sys

spec = importlib.util.spec_from_file_location(
    "guard", pathlib.Path(__file__).parent.parent / "hooks" / "block-secret-dumps.py"
)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

MUST_BLOCK = [
    "env | grep -i stripe",                                   # the classic leak
    'grep -n "^[A-Z_]*KEY" /opt/homebrew/lib/node_modules/some-tool/.env',
    "cat ~/.secrets.env",
    "head -20 .env.local",
    "echo $GITHUB_PERSONAL_ACCESS_TOKEN",
    'echo "${ANTHROPIC_API_KEY}"',
    "printenv STRIPE_SECRET_KEY",
    "printenv",
    'sqlite3 ~/.myapp/storage.sqlite "select access_token from accounts;"',
    "cat ~/.ssh/id_rsa",
    "cat ~/.aws/credentials",
    # Windows: PowerShell, cmd and backslash paths
    "type .env",
    r"type C:\Users\sam\my-app\.env.local",
    "Get-Content .env",
    r"gc ~\.aws\credentials",
    "more .env.production",
    r"Select-String KEY C:\Users\sam\my-app\.env",
    "findstr KEY .env",
    "Get-ChildItem env:",
    "gci env:",
    "gci Env:*KEY*",
    "dir env:",
    "ls Env:",
    "Get-ChildItem -Path Env:",
    "Get-Item env:STRIPE_SECRET_KEY",
    "[Environment]::GetEnvironmentVariables()",
    "set",
    "set | more",
    "cmd /c set",
    "echo $env:STRIPE_SECRET_KEY",
    "Write-Output $env:ANTHROPIC_API_KEY",
    "Write-Host \"key: $env:GITHUB_TOKEN\"",
    "echo %STRIPE_SECRET_KEY%",
    "$env:GITHUB_PERSONAL_ACCESS_TOKEN",
]

MUST_ALLOW = [
    'source ~/.secrets.env && echo "len=${#GITHUB_PERSONAL_ACCESS_TOKEN}"',
    'curl -s -H "Authorization: Bearer $STRIPE_SECRET_KEY" https://api.stripe.com/v1/charges',
    "cut -d= -f1 /Users/a/my-app/.env.local",
    "env NODE_ENV=production npm run build",
    "/usr/bin/env python3 script.py",
    "printenv PATH",
    "git status",
    "grep -l STRIPE ~/.zshrc",
    "npm run build",
    'sqlite3 ~/.myapp/storage.sqlite "select count(*) from accounts;"',
    'sqlite3 -header ~/.myapp/storage.sqlite "select name, plan from accounts;"',
    'sqlite3 ~/.myapp/storage.sqlite ".tables" | grep -iE "user|plan"',
    # Names a secret file in one segment, prints unrelated output in another.
    'source ~/.secrets.env && curl -s http://127.0.0.1:8080/v1/models | head -40',
    "source ~/.secrets.env; git log --oneline | head -5",
    # printf on one line, a token used in a curl on another — unrelated.
    'printf "checking: "\ncurl -s -H "Authorization: Bearer $STRIPE_SECRET_KEY" http://x/api',
    # tokens_in / tokens_cache_read are usage counts, not credentials.
    'sqlite3 ~/.myapp/storage.sqlite "select name, tokens_in from usage_log limit 3;"',
    'sqlite3 ~/.myapp/storage.sqlite "select sum(tokens_cache_read) from usage_log;"',
    # Windows: everyday commands that look close but print nothing secret
    "set -euo pipefail",
    "set -e; npm test",
    "dir $env:TEMP",
    r"Get-ChildItem C:\Users\sam\my-app",
    "type python",
    "git gc",
    "Get-Content README.md",
    "gc package.json | Select-String version",
    'Write-Output "done"',
    '$env:NODE_ENV = "production"; npm run build',
    r"cut -d= -f1 C:\Users\sam\my-app\.env",
    'Invoke-RestMethod -Headers @{Authorization="Bearer $env:STRIPE_SECRET_KEY"} https://api.stripe.com/v1/charges',
    "file --mime-type .env",
]

failures = []
for cmd in MUST_BLOCK:
    if guard.reason(cmd) is None:
        failures.append(f"  LEAKED THROUGH: {cmd}")
for cmd in MUST_ALLOW:
    if (why := guard.reason(cmd)) is not None:
        failures.append(f"  FALSE POSITIVE ({why}): {cmd}")

total = len(MUST_BLOCK) + len(MUST_ALLOW)
if failures:
    print(f"FAIL: {len(failures)}/{total} wrong:")
    print("\n".join(failures))
    sys.exit(1)
print(f"PASS: {len(MUST_BLOCK)} blocked, {len(MUST_ALLOW)} allowed, {total}/{total} correct")
