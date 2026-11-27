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

failures = []
for cmd, cwd in MUST_DENY:
    v = guard.assess(cmd, cwd)
    if not v or v[0] != "deny":
        failures.append(f"  NOT BLOCKED ({v}): {cmd!r}")
for cmd, cwd in MUST_ASK:
    v = guard.assess(cmd, cwd)
    if not v or v[0] != "ask":
        failures.append(f"  NOT ASKED ({v}): {cmd!r}")
for cmd, cwd in MUST_ALLOW:
    if (v := guard.assess(cmd, cwd)) is not None:
        failures.append(f"  FALSE ALARM ({v[0]}: {v[1][:80]}): {cmd!r}")

total = len(MUST_DENY) + len(MUST_ASK) + len(MUST_ALLOW)
if failures:
    print(f"FAIL — {len(failures)}/{total} wrong:")
    print("\n".join(failures))
    sys.exit(1)
print(f"PASS — {len(MUST_DENY)} blocked, {len(MUST_ASK)} asked, {len(MUST_ALLOW)} allowed, {total}/{total} correct")
