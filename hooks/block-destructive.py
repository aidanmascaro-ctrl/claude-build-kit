#!/usr/bin/env python3
"""PreToolUse guard: stop Bash commands that destroy work or data.

Why: agent sessions often run with permission prompts skipped, and then nothing
stands between an agent and `rm -rf ~`, `git reset --hard` or `DROP TABLE`.
The idea comes from gstack's /careful (MIT); this is a fresh, smaller version.

Two tiers:
  deny  no task needs it: wiping /, the home folder, a top-level home or
        system folder, or a disk.
  ask   sometimes legitimate: the user confirms in the permission prompt.

Commands are read in order, like the shell: `cd` and `X=...` are tracked, so
`S=/private/tmp/x; rm -rf "$S"` and `cd "$S" && rm -rf shots` are judged on
the real path. Temp folders and build output are always fine to delete.

Tuned on thousands of real agent commands, so everyday work doesn't trip it.
Exit 0 always. The decision goes out as permissionDecision JSON on stdout.
Malformed input is let through: not this hook's call to make.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys

SEPARATORS = {";", "&&", "||", "|", "&", ";;", "|&"}
WRAPPERS = {"sudo", "command", "nohup", "time", "xargs", "exec", "nice", "caffeinate",
            "then", "do", "else", "!", "env"}
SHELLS = {"bash", "sh", "zsh", "eval"}

HOME = os.path.expanduser("~")
SYSTEM = {"/", "/Users", "/System", "/Library", "/Applications", "/usr", "/bin", "/sbin",
          "/etc", "/var", "/private", "/opt", "/Volumes", "/cores"}
# Machine-made folders: anything inside them is regenerable.
REBUILDABLE_TREES = {"node_modules", "build", ".build", ".next", ".nuxt", ".svelte-kit", ".turbo",
                     ".cache", ".parcel-cache", "__pycache__", ".pytest_cache", "DerivedData",
                     "target", ".venv", "venv", ".playwright-mcp"}
# Common names that can also hold real work (renders in `out/`), so only the folder itself.
REBUILDABLE_NAMES = {"dist", "out", "coverage"}
TEMP_ROOTS = ("/tmp/", "/private/tmp/", "/var/folders/", "/private/var/folders/", "$TMPDIR", "${TMPDIR}",
              "$CLAUDE_JOB_DIR", "${CLAUDE_JOB_DIR}", HOME + "/.claude/jobs/", "$(mktemp",
              "$(getconf DARWIN_USER_TEMP_DIR")
ASSIGN = re.compile(r"[A-Za-z_]\w*=")
VAR = re.compile(r"\$\{?([A-Za-z_]\w*)\}?")

DB_CLIENT = re.compile(r"\b(?:psql|sqlite3?|mysql|mariadb|duckdb|supabase|pg_\w+)\b")
SQL_DESTROY = re.compile(
    r"\b(?:drop\s+(?:table|database|schema)|truncate\s+(?:table\s+)?[\w.\"]+"
    r"|delete\s+from\s+[\w.\"]+\s*(?:;|$|[\"']))",
    re.IGNORECASE | re.MULTILINE,
)
# A dev database in a local container or on this machine: dropping tables there is routine.
LOCAL_DB = re.compile(r"docker\s+exec|localhost|127\.0\.0\.1|supabase_db_")
# Heredoc bodies are file contents, not commands: `cat > clean.sh <<EOF ... rm -rf build ...`.
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?^\s*\2\s*$", re.DOTALL | re.MULTILINE)
# Redirections are not arguments: `rm -rf build 2>/dev/null` deletes build, not /dev/null.
REDIRECT = re.compile(r"(?<=\s)\d*(?:&>>?|>>?|<)\s*(?:&\d+|[^\s;&|]+)")

# (argv prefix, reason). Matched on the words before any flag.
ASK_PREFIXES = [
    (("gh", "repo", "delete"), "deletes a GitHub repository"),
    (("vercel", "rm"), "deletes Vercel deployments or projects"),
    (("vercel", "remove"), "deletes Vercel deployments or projects"),
    (("terraform", "destroy"), "destroys infrastructure"),
    (("kubectl", "delete"), "deletes Kubernetes resources"),
    (("docker", "system", "prune"), "deletes Docker data"),
    (("docker", "volume", "prune"), "deletes Docker volumes"),
]
DISK_ERASE = {"erasedisk", "erasevolume", "zerodisk", "secureerase", "partitiondisk", "reformat",
              "deletecontainer", "deletevolume"}

TRASH_TIP = " `trash <path>` moves it to the Bin instead, which can be undone."


# ---------- parsing ----------

def commands(cmd: str) -> tuple[list[list[str]], bool]:
    """Split a shell command line into argv lists, one per simple command.
    The flag is False when quoting defeated the parser and a rough split was used."""
    text = REDIRECT.sub("", HEREDOC.sub("", cmd)).replace("\\\n", " ").replace("\n", " ; ")
    lex = shlex.shlex(text, posix=True, punctuation_chars=";&|")
    lex.whitespace_split = True
    reliable = True
    try:
        toks = list(lex)
    except ValueError:  # quotes nested inside $(...) and the like: fall back to a rough split
        toks, reliable = re.split(r"\s+|(?=[;&|])|(?<=[;&|])", text), False
    out, cur = [], []
    for t in toks:
        if not t:
            continue
        if t in SEPARATORS or set(t) <= set(";&|"):
            if cur:
                out.append(cur)
            cur = []
            continue
        if not cur:
            t = t.lstrip("({")  # `(cd x && rm -rf y)`, `{ rm -rf y; }`
            if not t:
                continue
        cur.append(t)
    if cur:
        out.append(cur)
    return out, reliable


def expand(text: str, env: dict[str, str]) -> str:
    for _ in range(5):  # nested: D=$S/fake, S=/tmp/x
        new = VAR.sub(lambda m: env.get(m.group(1), m.group(0)), text)
        if new == text:
            break
        text = new
    return text


def resolve(path: str, env: dict[str, str]) -> str:
    """Best guess at the absolute path a target means. Unknown variables stay as `$NAME`."""
    p = expand(path, env)
    if p == "~" or p.startswith("~/"):
        p = env["HOME"] + p[1:]
    if not p.startswith(("/", "$")) and "PWD" in env:
        p = os.path.join(env["PWD"], p)
    if p.endswith("/*"):
        p = p[:-2] or "/"
    return os.path.normpath(p) if p.startswith("/") else p.rstrip("/")


def track(argv: list[str], env: dict[str, str]) -> None:
    """Update env for standalone `X=y`, `export X=y` and `cd dir`, as the shell would."""
    while argv and argv[0] in ("then", "do", "else"):
        argv = argv[1:]
    if not argv:
        return
    if ASSIGN.match(argv[0]) and argv[0].split("=", 1)[1].startswith(("$(", "`")):
        name, value = argv[0].split("=", 1)  # X=$(mktemp -d): the parser split it; the head is enough
        env[name] = value
        return
    if argv[0] in ("export", "readonly", "declare", "local"):
        argv = argv[1:]
    elif not all(ASSIGN.match(t) for t in argv):
        argv = argv if argv[0] == "cd" else []  # `HOME=x cmd` only lasts for that one command
    if argv and argv[0] == "cd":
        target = next((a for a in argv[1:] if not a.startswith("-")), "~")
        new = resolve(target, env)
        if new.startswith("/"):
            env["PWD"] = new
        else:
            env.pop("PWD", None)
        return
    for t in argv:
        if ASSIGN.match(t):
            name, value = t.split("=", 1)
            env[name] = expand(value, env)


def strip_wrappers(argv: list[str]) -> list[str]:
    # shortcut: `find -delete`, `find -exec rm`, `$(...)` and Python's shutil.rmtree are not
    # inspected; add them if an agent ever reaches for them.
    while argv and (argv[0] in WRAPPERS or ASSIGN.match(argv[0])):
        argv = argv[1:]
        while argv and argv[0].startswith("-") and argv[0] != "--":  # sudo -E, xargs -0
            argv = argv[1:]
    return argv


# ---------- rules ----------

def disposable(path: str) -> bool:
    parts = path.split("/")
    return (path.startswith(TEMP_ROOTS) or any(p in REBUILDABLE_TREES for p in parts)
            or parts[-1] in REBUILDABLE_NAMES)


def check_rm(args: list[str], env: dict[str, str]) -> tuple[str, str] | None:
    flags, targets, end = [], [], False
    for a in args:
        if not end and a == "--":
            end = True
        elif not end and a.startswith("-"):
            flags.append(a)
        else:
            targets.append(a)
    recursive = any(f == "--recursive" or (not f.startswith("--") and re.search("[rR]", f)) for f in flags)
    verdict = None
    for t in targets:
        p = resolve(t, env)
        if disposable(p):
            continue
        if p in SYSTEM or p == env["HOME"] or p == HOME or re.fullmatch(r"/(?:Users|home)/[^/]+", p):
            return "deny", f"deletes {t}, a home or system folder.{TRASH_TIP}"
        if recursive and os.path.dirname(p) in (HOME, env["HOME"]):
            return "deny", f"deletes {t}, a whole top-level folder in your home.{TRASH_TIP}"
        if p.startswith("/Volumes/"):
            verdict = ("ask", f"deletes {t} on an external drive.{TRASH_TIP}")
        elif recursive and not verdict:
            verdict = ("ask", f"recursively deletes {t}.{TRASH_TIP}")
    return verdict


def broad(paths: list[str]) -> bool:
    """A whole tree or folder, not one named file. shortcut: guesses "folder" from a missing
    file extension, so `Makefile` asks too; check the real path if that gets noisy."""
    return any(p in (".", ":/", "*") or p.endswith("/") or "." not in os.path.basename(p) for p in paths)


def check_git(args: list[str], env: dict[str, str]) -> str | None:
    while args and args[0].startswith("-"):  # global options: -C dir, -c k=v, --no-pager
        args = args[2:] if args[0] in ("-C", "-c") else args[1:]
    if not args:
        return None
    sub, rest = args[0], args[1:]
    paths = rest[rest.index("--") + 1:] if "--" in rest else [a for a in rest if not a.startswith("-")]
    if sub == "push" and ("--force" in rest or "-f" in rest or any(a.startswith("+") for a in rest)):
        return "force-pushes, which can overwrite commits on the remote (--force-with-lease is allowed)"
    if sub == "reset" and "--hard" in rest:
        return "discards uncommitted changes (git reset --hard)"
    if sub == "clean" and any(a == "--force" or re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", a) for a in rest):
        return "deletes untracked files (git clean -f)"
    # One named file is an agent undoing its own edit; a folder or `.` can wipe real work.
    if sub == "checkout" and ("." in rest or ("--" in rest and broad(paths))):
        return "discards uncommitted changes across a folder (git checkout --)"
    if sub == "restore" and not ("--staged" in rest and "--worktree" not in rest and "-W" not in rest):
        if paths and broad(paths):
            return "discards uncommitted changes across a folder (git restore)"
    if sub == "branch" and ("-D" in rest or ("--delete" in rest and "--force" in rest)):
        return "force-deletes a branch that may not be merged (git branch -D)"
    if sub == "stash" and (rest == ["drop"] or rest[:1] == ["clear"]):  # a named drop is fine
        return "throws away stashed changes"
    if sub == "worktree" and rest[:1] == ["remove"] and ("--force" in rest or "-f" in rest):
        if not all(disposable(resolve(p, env)) for p in paths[1:]):
            return "removes a worktree even though it has uncommitted changes"
    return None


def judge(argv: list[str], env: dict[str, str], depth: int) -> tuple[str, str] | None:
    piped = argv[0] == "xargs"
    argv = strip_wrappers(argv)
    if not argv:
        return None
    name, args = os.path.basename(argv[0]), argv[1:]
    if piped and name == "rm" and not any(not a.startswith("-") for a in args):
        args = args + ["files piped in by xargs"]  # targets come from stdin: judge them as unknown
    if name in SHELLS and depth < 3:  # bash -c "...", eval "..."
        script = " ".join(args) if name == "eval" else (args[args.index("-c") + 1] if "-c" in args[:-1] else "")
        return assess(script, env.get("PWD"), depth + 1) if script else None
    if name == "rm":
        return check_rm(args, env)
    if name == "git":
        why = check_git(args, env)
        return ("ask", why) if why else None
    if name == "mkfs" or name.startswith("mkfs."):
        return "deny", "formats a disk"
    if name == "dd" and any(a.startswith("of=/dev/") for a in args):
        return "deny", "writes straight onto a disk device"
    if name == "diskutil" and any(a.lower() in DISK_ERASE for a in args):
        return "deny", "erases or repartitions a disk"
    if name == "supabase" and args[:2] == ["db", "reset"] and any(a.startswith(("--linked", "--db-url")) for a in args):
        return "ask", "resets a remote Supabase database"
    words = tuple([name] + [a for a in args if not a.startswith("-")])
    for prefix, why in ASK_PREFIXES:
        if words[: len(prefix)] == prefix:
            return "ask", why
    return None


def assess(cmd: str, cwd: str | None = None, depth: int = 0) -> tuple[str, str] | None:
    """Return ("deny"|"ask", reason) for the worst part of a command, or None."""
    found = []
    if DB_CLIENT.search(cmd) and SQL_DESTROY.search(cmd) and not LOCAL_DB.search(cmd):
        found.append(("ask", "runs SQL that drops, truncates or empties a table"))
    env = {"HOME": HOME, **({"PWD": cwd} if cwd else {})}
    cmds, reliable = commands(cmd)
    for argv in cmds:
        track(argv, env)
        if verdict := judge(argv, env, depth):
            found.append(verdict)
    found.sort(key=lambda v: v[0] != "deny")
    if found and not reliable and found[0][0] == "deny":
        # A rough split can mistake quoted text (`grep 'rm -rf ~'`) for a command: ask, don't block.
        return "ask", found[0][1] + " (The guard could not fully parse this command, so it is asking.)"
    return found[0] if found else None


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    cmd = (payload.get("tool_input") or {}).get("command") or ""
    verdict = assess(cmd, payload.get("cwd"))
    if not verdict:
        sys.exit(0)

    decision, why = verdict[0], verdict[1].rstrip(".")
    if decision == "deny":
        text = (f"Destructive-command guard blocked this: the command {why}. "
                "If it is really wanted, the user can run it themselves with `! <command>`.")
    else:
        text = f"Destructive-command guard: this command {why}. Approve only if that's intended."
    json.dump({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                      "permissionDecision": decision,
                                      "permissionDecisionReason": text}}, sys.stdout)


if __name__ == "__main__":
    main()
