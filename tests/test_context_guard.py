#!/usr/bin/env python3
"""Self-check for context-guard.py. Run: python3 tests/test_context_guard.py

Builds small fake transcripts in a temp folder and feeds the hook the same JSON Claude Code does,
both through its functions and as a real subprocess (stdin in, stdout out, exit code 0).
"""
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile

HOOK = pathlib.Path(__file__).parent.parent / "hooks" / "context-guard.py"
spec = importlib.util.spec_from_file_location("guard", HOOK)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

T = tempfile.mkdtemp()
guard.STATE = os.path.join(T, "state")
PROJECT = os.path.expanduser("~/Documents/my-app")
POINT = guard.DEFAULT_POINT


def assistant(tokens, sidechain=False, model="claude-sonnet"):
    return {"type": "assistant", "isSidechain": sidechain, "message": {"model": model, "usage": {
        "input_tokens": 2, "cache_read_input_tokens": tokens - 1002, "cache_creation_input_tokens": 1000,
        "output_tokens": 50}}}


def transcript(name, records, pad=0):
    path = os.path.join(T, name + ".jsonl")
    with open(path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
            if pad:  # big tool results between messages, so the backwards reader crosses chunks
                f.write(json.dumps({"type": "user", "message": {"content": "x" * pad}}) + "\n")
    return path


def stop(path, sid="s1", active=False, point=POINT):
    return guard.on_stop({"hook_event_name": "Stop", "session_id": sid, "transcript_path": path,
                          "cwd": PROJECT, "stop_hook_active": active}, point)


# --- reading the context size ---
p = transcript("plain", [assistant(90_000), {"type": "user"}, assistant(114_000)])
assert guard.context_tokens(p) == 114_000, guard.context_tokens(p)
p = transcript("side", [assistant(114_000), assistant(900_000, sidechain=True),
                        assistant(0, model="<synthetic>")])
assert guard.context_tokens(p) == 114_000, "subagent and synthetic messages must be skipped"
p = transcript("compacted", [assistant(190_000), {"type": "system", "subtype": "compact_boundary",
                                                   "compactMetadata": {"postTokens": 31_000}}])
assert guard.context_tokens(p) == 31_000, "after a compaction the context is the post-compact size"
p = transcript("big", [assistant(150_000), assistant(160_000)], pad=700_000)
assert guard.context_tokens(p) == 160_000, "must read across 1 MB chunks"
p = transcript("first-line-only", [assistant(130_000)], pad=3_000_000)
assert guard.context_tokens(p) == 130_000, "the very first line must be read too"
assert guard.context_tokens(os.path.join(T, "missing.jsonl")) == 0

# --- the handoff point comes from the command line ---
assert guard.handoff_point([]) == POINT
assert guard.handoff_point(["--handoff-at", "300000"]) == 300_000
assert guard.handoff_point(["--handoff-at", "lots"]) == POINT
assert guard.handoff_point(["--handoff-at", "0"]) == POINT
assert guard.handoff_point(["--handoff-at"]) == POINT

# --- Stop: once per point, again 50k later, reset after dropping below ---
assert stop(transcript("a", [assistant(POINT - 1)])) is None
out = stop(transcript("b", [assistant(124_000)]))
assert out and out["decision"] == "block" and "124k" in out["reason"] and "120k" in out["reason"], out
assert "handoff file" in out["reason"] and "/clear" in out["reason"] and "start_session" in out["reason"]
assert stop(transcript("c", [assistant(150_000)])) is None, "fires once per point"
assert stop(transcript("d", [assistant(124_000)]), active=True) is None, "stop_hook_active: never loop"
assert stop(transcript("e", [assistant(174_000)])), "again 50k after the first nudge"
assert stop(transcript("f", [assistant(190_000)])) is None
assert stop(transcript("g", [assistant(40_000)])) is None  # compacted or fresh: state forgotten
assert not os.path.exists(os.path.join(guard.STATE, "s1.json"))
assert stop(transcript("h", [assistant(125_000)])), "fires again after the state was reset"
assert stop(transcript("i", [assistant(250_000)]), sid="big", point=300_000) is None, "custom point"
assert stop(transcript("j", [assistant(301_000)]), sid="big", point=300_000)
assert stop(transcript("k", [assistant(400_000)]), sid="../../evil") is not None  # bad id: no state file
assert not any("evil" in n for n in os.listdir(T))

# --- PreCompact never blocks ---
for trigger in ("auto", "manual"):
    out = guard.on_precompact({"trigger": trigger, "transcript_path": p})
    assert isinstance(out, str) and "exact words" in out, out

# --- SessionStart ---
assert guard.on_session_start({"source": "startup"}) is None
assert guard.on_session_start({"source": "resume"}) is None
ctx = guard.on_session_start({"source": "compact"})["hookSpecificOutput"]
assert ctx["hookEventName"] == "SessionStart" and "board" in ctx["additionalContext"]


# --- as a real subprocess, the way Claude Code runs it ---
def run(payload, *args):
    env = dict(os.environ, HOME=T)  # state goes to the temp folder, not the real ~/.claude
    r = subprocess.run([sys.executable, str(HOOK), *args], input=payload, capture_output=True,
                       text=True, env=env)
    assert r.returncode == 0, (r.returncode, r.stderr)
    return r.stdout


big = transcript("sub", [assistant(222_000)])
out = json.loads(run(json.dumps({"hook_event_name": "Stop", "session_id": "sub", "cwd": PROJECT,
                                 "transcript_path": big})))
assert out["decision"] == "block"
assert os.path.exists(os.path.join(T, ".claude/state/context-guard/sub.json"))
assert run(json.dumps({"hook_event_name": "Stop", "session_id": "sub2", "cwd": PROJECT,
                       "transcript_path": big}), "--handoff-at", "300000") == "", "custom point via argv"
assert "exact words" in run(json.dumps({"hook_event_name": "PreCompact", "trigger": "auto",
                                         "transcript_path": big}))
assert run("not json") == "" and run("{}") == "" and run('{"hook_event_name": "Stop"}') == ""

print("PASS: context guard: size reading, handoff point, Stop nudges, PreCompact, SessionStart, subprocess")
