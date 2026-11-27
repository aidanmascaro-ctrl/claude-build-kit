#!/usr/bin/env python3
"""PreToolUse guard: refuse to WRITE secret-shaped values into durable files.

Companion to block-secret-dumps.py, which guards Bash output. This one guards
file content — handoffs, memory, docs, code, commit messages. Those outlive the
session and often reach git, so a credential written there is worse than one in
a transcript.

Writing a secret into a file whose JOB is holding secrets (.env, ~/.secrets.env)
is correct and allowed. Everywhere else is refused.

Exit 0 always; a block is the permissionDecision JSON on stdout.
"""
from __future__ import annotations

import json
import re
import sys

# Files that legitimately store credentials — a secret belongs in these.
# Windows paths arrive with backslashes, so either separator counts.
SECRET_STORE = re.compile(
    r"(?:^|[/\\])(?:\.env(?:\.[\w.-]+)?|[\w.-]+\.env|\.secrets\.env|\.npmrc|\.pgpass|\.netrc"
    r"|id_rsa|id_ed25519|credentials(?:\.json)?)$"
)

PATTERNS = [
    ("Anthropic API key",        re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}")),
    ("OpenAI-style key",         re.compile(r"sk-[A-Za-z0-9]{32,}")),
    ("GitHub token",             re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("GitHub fine-grained PAT",  re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("Stripe secret key",        re.compile(r"\b[rs]k_(?:live|test)_[A-Za-z0-9]{20,}")),
    ("Google OAuth token",       re.compile(r"ya29\.[A-Za-z0-9_-]{20,}")),
    ("Slack token",              re.compile(r"xox[abprs]-[A-Za-z0-9-]{10,}")),
    ("AWS access key id",        re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private key block",        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("JWT",                      re.compile(r"\bey[A-Za-z0-9_-]{10,}\.ey[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+")),
    ("long hex secret",          re.compile(r"(?<![A-Za-z0-9])[0-9a-f]{48,}(?![A-Za-z0-9])")),
    ("credential in a URL",      re.compile(r"://[^/\s:@]+:[^/\s@]{6,}@")),
    ("assigned secret",          re.compile(
        r"(?i)\b\w*(?:APIKEY|API_KEY|ACCESS_TOKEN|AUTH_TOKEN|SECRET|PASSWORD|CREDENTIAL)\w*"
        r"\s*[=:]\s*['\"]?([A-Za-z0-9_./+-]{16,})")),
]

# Placeholders that only look like secrets, plus env-var READS — `const pw =
# process.env.APP_PASSWORD` is the pattern we want people using, not a leak.
BENIGN = re.compile(
    r"(?i)REDACTED|<[a-z_ .-]+>|\bxxx+|your[-_]|example|placeholder|CHANGEME|\bfake\b|\bdummy\b|\.\.\."
    r"|\$\{?\w+\}?"
    r"|process\.env|import\.meta\.env|os\.environ|os\.getenv|ENV\[|getenv\(|Deno\.env"
)


def find(content: str) -> tuple[str, int] | None:
    for lineno, line in enumerate(content.splitlines(), 1):
        for kind, pat in PATTERNS:
            m = pat.search(line)
            # Judge only the matched fragment. Checking the whole line let a real
            # secret pass whenever the line happened to contain "example" etc.
            if m and not BENIGN.search(m.group(0)):
                return kind, lineno
    return None


def main() -> None:
    try:
        payload = json.load(sys.stdin.buffer)  # bytes, so Windows' default text encoding can't garble it
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    ti = payload.get("tool_input") or {}
    path = ti.get("file_path") or ""
    if SECRET_STORE.search(path):
        sys.exit(0)  # A credentials file is the right home for a credential.

    content = ti.get("content") or ti.get("new_string") or ""
    hit = find(content)
    if not hit:
        sys.exit(0)

    kind, lineno = hit
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"Secret-leak guard: this write puts what looks like a {kind} into "
                    f"{path or 'a file'} at line {lineno}. Durable files reach git and future "
                    "sessions. Reference the secret by name and location instead "
                    "(\"STRIPE_SECRET_KEY in .env\"), use $VAR in any command, or "
                    "write <redacted>. If this is a placeholder the guard misread, make it "
                    "obviously fake (example/dummy/<your-key-here>) and it will pass."
                ),
            }
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
