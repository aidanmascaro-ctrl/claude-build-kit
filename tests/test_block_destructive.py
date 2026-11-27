#!/usr/bin/env python3
"""Self-check for block-destructive.py. Run: python3 tests/test_block_destructive.py

Cases live in this file rather than on a command line because the guard would
(correctly) stop a shell command containing these strings as literal text.
Several MUST_ALLOW cases are real commands from past sessions that a first
draft of the guard got wrong.
"""
import importlib.util
import os
import pathlib
import sys

spec = importlib.util.spec_from_file_location(
    "guard", pathlib.Path(__file__).parent.parent / "hooks" / "block-destructive.py"
)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

HOME = os.path.expanduser("~")
PROJECT = HOME + "/Documents/my-app"
SCRATCH = "/private/tmp/x/scratchpad"

# (command, cwd)
MUST_DENY = [
    ("rm -rf /", PROJECT),
    ("rm -rf /*", PROJECT),
    ("rm -rf ~", PROJECT),
    ("rm -rf ~/", PROJECT),
    ('rm -rf "$HOME"', PROJECT),
    ("sudo rm -rf /Users", PROJECT),
    ("rm -rf /home/sam", PROJECT),                   # someone's Linux home
    ("rm -rf ~/Documents", PROJECT),
    ("rm -rf ~/.claude", PROJECT),
    ("rm -rf Documents", HOME),                      # relative, resolved against cwd
    ("cd ~ && rm -rf Movies", PROJECT),              # cd is tracked
    ("rm -rf ..", HOME + "/Documents"),
    ('bash -c "rm -rf ~"', PROJECT),                 # shell -c is looked inside
    ("rm -rf /Applications", PROJECT),
    ("diskutil eraseDisk APFS Blank disk4", PROJECT),
    ("dd if=/dev/zero of=/dev/disk4 bs=1m", PROJECT),
    ("mkfs.ext4 /dev/sdb1", PROJECT),
]

MUST_ASK = [
    ("rm -rf src", PROJECT),
    ("rm -rf .", PROJECT),
    ("rm -rf *", PROJECT),
    ('rm -rf "$UNKNOWN"', PROJECT),
    ("rm -rf ~/Library/Application\\ Support/My\\ App", PROJECT),
    ('rm "/Volumes/External/footage/A001.mov"', PROJECT),   # non-recursive, external drive
    ("git reset --hard HEAD~3", PROJECT),
    ("git push --force origin main", PROJECT),
    ("git push -f", PROJECT),
    ("git push origin +main", PROJECT),
    ("git clean -fdx", PROJECT),
    ("git checkout .", PROJECT),
    ("git checkout -- src", PROJECT),
    ("git restore .", PROJECT),
    ("git branch -D feature/x", PROJECT),
    ("git stash clear", PROJECT),
    ("git stash drop", PROJECT),
    ("git -C /Users/a/repo worktree remove --force .claude/worktrees/x", PROJECT),
    ('psql "$DATABASE_URL" -c "DROP TABLE users;"', PROJECT),
    ('sqlite3 ~/.myapp/storage.sqlite "DELETE FROM usage_log;"', PROJECT),
    ("supabase db reset --linked", PROJECT),
    ("gh repo delete someone/old-site --yes", PROJECT),
    ("vercel rm my-app --yes", PROJECT),
    ("find . -name x | xargs rm -rf", PROJECT),
    # Quoting the parser can't follow: a hard block is downgraded to a question.
    ("echo \"a ; rm -rf ~ ; echo 'b", PROJECT),
]

MUST_ALLOW = [
    ("rm -rf node_modules dist .next", PROJECT),
    ("rm -rf build 2>/dev/null", PROJECT),                     # redirect is not a target
    ("rm -rf target/debug", PROJECT + "/core"),            # inside Rust build output
    ("rm -rf .build/release", PROJECT),
    ("rm -rf /tmp/foo", PROJECT),
    (f"rm -rf {SCRATCH}/shots", PROJECT),
    ('rm -rf "$TMPDIR/my-wt"', PROJECT),
    ('S=/private/tmp/a/scratchpad/deploy; rm -rf "$S" && mkdir -p "$S"', PROJECT),
    ('S=/private/tmp/a/scratchpad; T=$S/render-probe; rm -rf $T; mkdir -p $T/a', PROJECT),
    ("X=$(mktemp -d); rm -rf $X", PROJECT),
    (f"cd {SCRATCH} && rm -rf shots2", PROJECT),               # relative after cd into temp
    ("rm -rf shots", SCRATCH),                                 # relative, cwd is temp
    ('rm -rf "$CLAUDE_JOB_DIR/tmp/preview"', PROJECT),
    # Heredoc body is file content, not a command.
    ("cat > clean.sh <<'EOF'\nrm -rf ~/Documents\nEOF\nchmod +x clean.sh", PROJECT),
    # Newlines separate commands: the rm is judged with the assignment above it.
    (f"S={SCRATCH} && cat > \"$S/a.py\" <<'EOF'\nprint(1)\nEOF\nD=\"$S/rerun_tmp\"; rm -rf \"$D\"", PROJECT),
    ("rm notes.txt", PROJECT),
    ("rm -f ~/.zcompdump", PROJECT),                           # non-recursive file in home
    ("git push --force-with-lease origin claude/x", PROJECT),
    ("git push -u origin feature", PROJECT),
    ("git reset --soft HEAD~1", PROJECT),
    ("git checkout -b new-branch", PROJECT),
    ("git checkout HEAD -- src/lib.rs", PROJECT),  # undo own edit
    ("git restore --staged src/app.ts", PROJECT),
    ("git branch -d task/website", PROJECT),          # hub-workflow cleanup
    ("git worktree remove .claude/worktrees/x", PROJECT),
    (f"git worktree remove --force {SCRATCH}/my-wt", PROJECT),
    ('git stash drop "$N"', PROJECT),                          # named drop after apply
    ("git clean -n", PROJECT),
    ('grep -rn "DROP TABLE" migrations/', PROJECT),            # text search, no DB client
    ("docker exec -i supabase_db_x psql -U postgres -c 'drop table t;'", PROJECT),  # local dev DB
    ('sqlite3 db.sqlite "DELETE FROM jobs WHERE id = 3;"', PROJECT),
    ("echo 'rm -rf /' > notes.txt", PROJECT),                  # quoted text only
    ("trash ~/Documents/old-folder", PROJECT),
    ("npm run build", PROJECT),
    ("git status", PROJECT),
]

# ---------- Windows, with a fake Windows home, so these run on any computer ----------
# (command, cwd, shell). "bash" is Git Bash, which Claude Code's Bash tool uses on Windows;
# "powershell" is its PowerShell tool. cwd arrives as C:\\... or /c/..., so both are used.
WIN_HOME = "C:\\Users\\sam"
WIN_PROJECT = WIN_HOME + "\\Documents\\my-app"
GIT_BASH_PROJECT = "/c/Users/sam/Documents/my-app"

WIN_MUST_DENY = [
    ("rm -rf /c/Users/sam", GIT_BASH_PROJECT, "bash"),
    ('rm -rf "C:\\Users\\sam"', WIN_PROJECT, "bash"),
    ("rm -rf C:/Users/sam/Documents", WIN_PROJECT, "bash"),
    ("rm -rf ~", WIN_PROJECT, "bash"),
    ("rm -rf ~/AppData", GIT_BASH_PROJECT, "bash"),
    ('rm -rf "$USERPROFILE"', WIN_PROJECT, "bash"),
    ("rm -rf /c/Users/alex", WIN_PROJECT, "bash"),                 # someone else's home
    ("rm -rf 'C:\\'", WIN_PROJECT, "bash"),                         # a whole drive
    ("rm -rf /c/*", WIN_PROJECT, "bash"),
    ('rm -rf "C:\\Windows"', WIN_PROJECT, "bash"),
    ('rm -rf "/c/Program Files"', WIN_PROJECT, "bash"),
    ('rm -rf "C:\\Program Files (x86)"', WIN_PROJECT, "bash"),
    ("rm -rf /c/Users", WIN_PROJECT, "bash"),
    ("rm -rf Documents", WIN_HOME, "bash"),                          # relative to a C:\\ cwd
    ("rm -rf ..", WIN_HOME + "\\Documents", "bash"),
    ('cmd //c "rd /s /q C:\\Users\\sam"', WIN_PROJECT, "bash"),
    ('powershell -Command "Remove-Item -Recurse -Force C:\\Users\\sam\\Documents"', WIN_PROJECT, "bash"),
    ("Remove-Item -Recurse -Force C:\\Users\\sam", WIN_PROJECT, "powershell"),
    ("Remove-Item -Recurse -Force $env:USERPROFILE\\Documents", WIN_PROJECT, "powershell"),
    ("Remove-Item -Path ~\\Desktop -Recurse", WIN_PROJECT, "powershell"),
    ("rm -r ~\\Documents", WIN_PROJECT, "powershell"),           # rm is Remove-Item there
    ('Remove-Item -Recurse -Force "C:\\Program Files"', WIN_PROJECT, "powershell"),
    ("Set-Location C:\\Users\\sam; Remove-Item -Recurse Music", WIN_PROJECT, "powershell"),
    ("cmd /c rd /s /q C:\\Users\\sam", WIN_PROJECT, "powershell"),
    ('cmd /c rd /s /q "C:\\Program Files"', WIN_PROJECT, "powershell"),
    ("del /s /q C:\\Users\\sam", WIN_PROJECT, "powershell"),
    ("Format-Volume -DriveLetter D", WIN_PROJECT, "powershell"),
    ("Clear-Disk -Number 1 -RemoveData", WIN_PROJECT, "powershell"),
    ("format D: /q", WIN_PROJECT, "powershell"),
]

WIN_MUST_ASK = [
    ('rm -rf "C:\\Users\\sam\\Documents\\my-app\\src"', WIN_PROJECT, "bash"),
    ('rm -rf "$TEMPLATES"', WIN_PROJECT, "bash"),                  # not $TEMP
    ("Remove-Item -Recurse src", WIN_PROJECT, "powershell"),
    ("Remove-Item -rec -Force .", WIN_PROJECT, "powershell"),
    ("rd /s /q src", WIN_PROJECT, "powershell"),
    ("del /s *.log", WIN_PROJECT, "powershell"),
    ("Get-ChildItem C:\\Users\\sam | Remove-Item -Recurse -Force", WIN_PROJECT, "powershell"),
    ("git reset --hard", WIN_PROJECT, "powershell"),
    ("git push --force", WIN_PROJECT, "powershell"),
]

WIN_MUST_ALLOW = [
    ("rm -rf node_modules dist", WIN_PROJECT, "bash"),
    ('rm -rf "$TEMP/x"', WIN_PROJECT, "bash"),
    ("rm -rf /tmp/x", WIN_PROJECT, "bash"),                         # Git Bash's /tmp is the temp folder
    ('rm -rf "C:\\Users\\sam\\AppData\\Local\\Temp\\shots"', WIN_PROJECT, "bash"),
    ('rm -rf "C:\\Users\\sam\\Documents\\my-app\\dist"', WIN_PROJECT, "bash"),
    ("cd /c/Users/sam/Documents/my-app && rm -rf build", WIN_HOME, "bash"),
    ("rm -rf .next", GIT_BASH_PROJECT, "bash"),
    ("rm notes.txt", WIN_PROJECT, "bash"),
    ("Remove-Item -Recurse -Force node_modules", WIN_PROJECT, "powershell"),
    ("Remove-Item -Recurse -Force $env:TEMP\\my-test", WIN_PROJECT, "powershell"),
    ("Remove-Item -Recurse -Force %TEMP%\\my-test", WIN_PROJECT, "powershell"),
    ('Remove-Item -Recurse "C:\\Users\\sam\\AppData\\Local\\Temp\\x"', WIN_PROJECT, "powershell"),
    ("Set-Location C:\\Users\\sam\\Documents\\my-app; Remove-Item -Recurse .next", WIN_HOME, "powershell"),
    ("Remove-Item notes.txt", WIN_PROJECT, "powershell"),
    ("rm -Force notes.txt", WIN_PROJECT, "powershell"),            # -Force isn't -r
    ("rmdir empty-folder", WIN_PROJECT, "powershell"),             # no /s: empty folders only
    ('cmd /c "del /q notes.txt"', WIN_PROJECT, "powershell"),
    ("Get-ChildItem -Recurse src | Select-String TODO", WIN_PROJECT, "powershell"),
    ("npm run build", WIN_PROJECT, "powershell"),
    ("git status", WIN_PROJECT, "powershell"),
]

failures = []


def run(cases, want):
    for cmd, cwd, *shell in cases:
        v = guard.assess(cmd, cwd, shell=shell[0] if shell else "bash")
        got = v[0] if v else "allow"
        if got != want:
            failures.append(f"  {want.upper()} EXPECTED, GOT {got} ({v[1][:70] if v else ''}): {cmd!r}")


run(MUST_DENY, "deny")
run(MUST_ASK, "ask")
run(MUST_ALLOW, "allow")
real_home, guard.HOME = guard.HOME, WIN_HOME
run(WIN_MUST_DENY, "deny")
run(WIN_MUST_ASK, "ask")
run(WIN_MUST_ALLOW, "allow")
guard.HOME = real_home

deny, ask, allow = (len(MUST_DENY) + len(WIN_MUST_DENY), len(MUST_ASK) + len(WIN_MUST_ASK),
                    len(MUST_ALLOW) + len(WIN_MUST_ALLOW))
total = deny + ask + allow
if failures:
    print(f"FAIL: {len(failures)}/{total} wrong:")
    print("\n".join(failures))
    sys.exit(1)
print(f"PASS: {deny} blocked, {ask} asked, {allow} allowed, {total}/{total} correct (Mac, Linux and Windows)")
