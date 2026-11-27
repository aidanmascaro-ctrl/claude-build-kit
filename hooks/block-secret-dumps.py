#!/usr/bin/env python3
"""PreToolUse guard: refuse Bash commands that would print secrets into the transcript.

Why: one `env | grep -i stripe`, or a grep over a filled-in .env file, puts live
credentials into the session transcript, and then they have to be rotated.
Instructions alone don't prevent it; this does.

The rule is narrow on purpose — it blocks commands whose OUTPUT carries secret
material, not commands that merely use a secret. `curl -H "Authorization:
Bearer $TOKEN"` is fine; `echo $TOKEN` is not.

Covers Windows too: PowerShell and cmd ways of printing a file (type, Get-Content, gc) or the
environment (Get-ChildItem env:, set), and paths written with backslashes.

Exit 0 always. A block is signalled by the permissionDecision JSON on stdout.
"""
from __future__ import annotations

import json
import re
import sys

# Files whose contents are secret material by nature.
SECRET_PATH = re.compile(
    r"""(?:^|[\s"'=/\\])(?:
          \.env(?:\.[\w.-]+)?      # .env, .env.local, .env.production
        | [\w.-]+\.env             # secrets.env, foo.env
        | \.npmrc | \.pgpass | \.netrc
        | id_rsa | id_ed25519 | id_ecdsa
        | credentials(?:\.json)?
        # Not *.sqlite: app databases mix credentials with ordinary data, so
        # SQLITE_SECRET guards their credential columns precisely instead.
    )\b""",
    re.VERBOSE,
)

# Commands that write file contents to stdout, including Windows' (PowerShell and cmd).
PRINTER = re.compile(
    r"(?<![\w-])(?:cat|bat|less|more|head|tail|grep|egrep|fgrep|rg|ag|awk|sed|strings|xxd|od|nl|tac"
    r"|type|get-content|gc|select-string|sls|findstr|format-hex)\b",
    re.IGNORECASE,
)

# Reads that provably cannot emit a value: key names, counts, filenames, lengths.
SAFE_READ = re.compile(
    r"""(?:
          cut\s+-d\s*['\"]?=['\"]?\s+-f\s*1   # cut -d= -f1  → key names only
        | \bgrep\s+-[A-Za-z]*[lcq]\b          # grep -l/-c/-q → no matched text
        | \$\{\#                              # ${#VAR}      → length only
    )""",
    re.VERBOSE,
)

# Whole-environment dumps. `env FOO=bar cmd` is a launcher, not a dump — allowed,
# as is `printenv NAME`, which PRINTENV_NAMED judges on the name instead.
ENV_DUMP = re.compile(
    r"(?:^|[;&|]|\bthen\b|\bdo\b|\$\()\s*(?:env(?!\s+[A-Za-z_]\w*=)|printenv(?!\s+\w))\b"
)
# Windows: PowerShell's env: drive (Get-ChildItem env:, gci env:*KEY*, dir env:), .NET's list, and
# `set` alone (cmd, and bash too: both print every variable). `set -e` and `dir $env:TEMP` are fine.
WIN_ENV_DUMP = re.compile(
    r"\b(?:get-childitem|gci|dir|ls|get-item|gi)\s+(?:-(?:literal)?path\s+)?[\"']?env:"
    r"|\[(?:system\.)?environment\]::getenvironmentvariables"
    r"|(?:^|[;&|(]|\bthen\b|\bdo\b|/[ck])\s*[\"']?set\s*(?:$|[;&|)\"'])",
    re.IGNORECASE | re.MULTILINE,
)

# PAT needs the trailing guard or it swallows PATH.
SECRETY = r"(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|PRIVATE|API|PAT(?![A-Za-z]))"

# printenv NAMED_SECRET
PRINTENV_NAMED = re.compile(rf"\bprintenv\s+\w*{SECRETY}\w*", re.IGNORECASE)

# echo/printf of a secret-named variable. Stays on one line — allowing newlines let a
# printf match a $TOKEN inside an unrelated curl further down the script.
# Windows spellings too: Write-Output $env:TOKEN, echo %TOKEN%.
ECHO_SECRET = re.compile(
    rf"\b(?:echo|printf|write-output|write-host)\b[^|;&\n]*(?:\$\{{?(?:env:)?|%)\w*{SECRETY}\w*",
    re.IGNORECASE,
)
# PowerShell prints a value that stands alone as a statement: `$env:GITHUB_TOKEN`.
PS_BARE_SECRET = re.compile(rf"(?:^|[;&|(])\s*\$env:\w*{SECRETY}\w*\s*(?:$|[;&|)])",
                            re.IGNORECASE | re.MULTILINE)

# Columns that actually hold credentials. Named explicitly rather than matched on
# SECRETY, which flagged usage metrics like `tokens_in` / `tokens_cache_read`.
SQL_CRED_COL = (
    r"(?:access_token|refresh_token|id_token|token_hash|client_secret|api_key|apikey"
    r"|secret_key|password|passwd|credential|private_key)"
)

# sqlite reads of credential columns. `select *` counts; `count(*)` does not.
SQLITE_SECRET = re.compile(
    rf"\bsqlite3?\b.*\bselect\s+(?:\*|[^;]*{SQL_CRED_COL})",
    re.IGNORECASE | re.DOTALL,
)

GUIDANCE = (
    "Blocked: this command's OUTPUT would put secret material in the transcript. "
    "Get the same answer without the value: `cut -d= -f1 file` for key names, "
    "`grep -c`/`-l`/`-q` for presence, `${#VAR}` for length, "
    "or a script that reads the secret and writes it straight to its destination "
    "without printing. Using a secret (e.g. curl -H \"Authorization: Bearer $VAR\") "
    "is fine and not blocked. If you truly need the value visible, ask the user to "
    "run the command themselves with `! <command>`."
)


def reason(cmd: str) -> str | None:
    if ENV_DUMP.search(cmd) or WIN_ENV_DUMP.search(cmd):
        return "dumps the whole environment"
    if PRINTENV_NAMED.search(cmd):
        return "prints a secret-named environment variable"
    if ECHO_SECRET.search(cmd) or PS_BARE_SECRET.search(cmd):
        return "echoes a secret-named variable"
    if SQLITE_SECRET.search(cmd):
        return "selects credential columns out of a database"
    # Per SEGMENT, not per command: `source ~/.secrets.env && curl … | head` names a
    # secret file in one segment and a printer in another, and prints nothing.
    # The printer has to be reading the credentials file itself.
    for seg in re.split(r"\|\||&&|[|;\n]", cmd):
        if SECRET_PATH.search(seg) and PRINTER.search(seg) and not SAFE_READ.search(seg):
            return "prints the contents of a credentials file"
    return None


def main() -> None:
    try:
        payload = json.load(sys.stdin.buffer)  # bytes, so Windows' default text encoding can't garble it
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # Malformed input is not our call to make.

    cmd = (payload.get("tool_input") or {}).get("command") or ""
    why = reason(cmd)
    if not why:
        sys.exit(0)

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Secret-leak guard: command {why}. {GUIDANCE}",
            }
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
