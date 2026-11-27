#!/usr/bin/env python3
"""Context guard: long chats hand off to a fresh session before they get compacted.

Why: when a chat gets long, Claude Code compacts it, swapping the history for a summary. Detail
goes missing and the session starts to drift. Handing off to a fresh session that reads a written
handoff file keeps the exact decisions and open items.

One script, three events (install.py registers it in ~/.claude/settings.json):
  Stop          past the handoff point, tell the session to hand off now. Once per point, then
                again every 50k tokens if ignored. Only between turns, never mid-task.
  PreCompact    never blocks. Tells the summary what to keep, in case a compaction happens anyway.
  SessionStart  after a compaction: the summary may be wrong, so re-read the files first.

The handoff point is the first argument: `context-guard.py --handoff-at 120000`. The default suits
a 200k-token window; with a 1M window, 300000 or more is comfortable.

Context size = the last main-chain assistant message's input + cache-read + cache-creation tokens.
Exit 0 always; malformed input is let through. Run tests/test_context_guard.py after any change.
"""
from __future__ import annotations

import json
import os
import re
import sys

DEFAULT_POINT = 120_000
REPEAT = 50_000
STATE = os.path.expanduser("~/.claude/state/context-guard")

HANDOFF_STEPS = (
    "1. Write a handoff file: in the project's .claude/hub/handoffs/<date-time>.md (a task session "
    "in a worktree writes .claude/hub/handoff-<n>.md in its worktree). Start it with one line saying "
    "who should read it. Put in: what's done, what's in progress (files, branch, last commit, "
    "uncommitted work), decisions with the user's exact words, open questions, and what's next. "
    "2. If you're a hub, update .claude/hub/board.md; if you're a task session, tell your hub. "
    "3. Start the fresh session, told to read that file: in the Claude desktop app use start_session "
    "(same title, folder and role); in a terminal, tell the user to type /clear and then paste "
    "\"Continue from <the handoff file's path>\". "
    "If this session's job is already done, say so in one line and stop instead.")


def handoff_point(argv: list[str]) -> int:
    """The --handoff-at value, or the default if it's missing or not a positive number."""
    if "--handoff-at" in argv[:-1]:
        value = argv[argv.index("--handoff-at") + 1]
        if value.isdigit() and int(value) > 0:
            return int(value)
    return DEFAULT_POINT


def tokens_in(line: bytes):
    """Context size recorded on one transcript line, or None if the line doesn't say."""
    if b'"compact_boundary"' in line:
        try:
            d = json.loads(line)
        except ValueError:
            return None
        if d.get("subtype") == "compact_boundary":
            return (d.get("compactMetadata") or {}).get("postTokens") or 0
        return None
    if b'"assistant"' not in line or b'"usage"' not in line:
        return None
    try:
        d = json.loads(line)
    except ValueError:
        return None
    m = d.get("message") or {}
    if d.get("type") != "assistant" or d.get("isSidechain") or m.get("model") == "<synthetic>":
        return None
    u = m.get("usage") or {}
    total = sum(u.get(k) or 0 for k in
                ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
    return total or None


def context_tokens(path: str) -> int:
    """Read the transcript backwards until a line gives the current context size."""
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            pos = f.tell()
            rest = b""
            while pos > 0:
                step = min(1 << 20, pos)
                pos -= step
                f.seek(pos)
                lines = (f.read(step) + rest).split(b"\n")
                rest = lines.pop(0) if pos > 0 else b""  # may be a partial line
                for line in reversed(lines):
                    t = tokens_in(line)
                    if t is not None:
                        return t
    except OSError:
        pass
    return 0


def should_nudge(tokens: int, point: int, last):
    """New value for the 'last nudged at' state, and whether to nudge now."""
    if tokens < point:
        return None, False           # below the point (or compacted): forget earlier nudges
    if last is None or tokens >= last + REPEAT:
        return tokens, True
    return last, False


def state_file(session_id: str):
    return os.path.join(STATE, session_id + ".json") if re.fullmatch(r"[\w-]{1,80}", session_id or "") else None


def on_stop(p: dict, point: int = DEFAULT_POINT):
    if p.get("stop_hook_active"):
        return None                  # already continuing because of a Stop hook: never loop
    tokens = context_tokens(p.get("transcript_path") or "")
    sf = state_file(p.get("session_id") or "")
    last = None
    if sf:
        try:
            with open(sf) as f:
                last = json.load(f).get("nudged_at")
        except (OSError, ValueError):
            pass
    new, nudge = should_nudge(tokens, point, last)
    if sf and new != last:
        try:
            if new is None:
                os.remove(sf)
            else:
                os.makedirs(STATE, exist_ok=True)
                with open(sf, "w") as f:
                    json.dump({"nudged_at": new}, f)
        except OSError:
            pass
    if not nudge:
        return None
    return {"decision": "block", "reason": (
        f"Context guard: this chat is at {tokens // 1000}k tokens, past its {point // 1000}k "
        "handoff point. Don't start anything new. Hand off now, so it never gets compacted. "
        + HANDOFF_STEPS)}


def on_precompact(p: dict):
    return ("Context guard: keep the user's exact words (quoted, with dates), every decision and "
            "why, and every open item: questions waiting, running tasks by name, the branch, "
            "worktree, last commit and uncommitted files.")


def on_session_start(p: dict):
    if p.get("source") != "compact":
        return None
    return {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": (
        "Context guard: this session was just compacted, so the summary above may be wrong or "
        "missing detail. Before doing anything else, re-read CLAUDE.md, your brief if you have one, "
        ".claude/hub/board.md and the newest handoff if they exist, and check the real state with "
        "git (status, log, worktree list). Trust those files over the summary.")}}


def main() -> None:
    try:
        p = json.load(sys.stdin)
    except ValueError:
        sys.exit(0)
    event = p.get("hook_event_name")
    if event == "Stop":
        out = on_stop(p, handoff_point(sys.argv[1:]))
    elif event == "PreCompact":
        out = on_precompact(p)
    elif event == "SessionStart":
        out = on_session_start(p)
    else:
        out = None
    if isinstance(out, str):
        print(out)
    elif out:
        json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
