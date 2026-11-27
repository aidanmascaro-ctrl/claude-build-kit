#!/usr/bin/env python3
"""Self-check for install.py. Run: python3 tests/test_install.py

Installs into a throwaway CLAUDE_CONFIG_DIR that already has someone's own hooks and a skill of
their own, then checks: their things survive, running it twice adds nothing twice, an installed
guard runs the way Claude Code starts it, and uninstall puts settings.json back exactly as it was.
The folder name has a space in it, to catch quoting mistakes (Windows user names often have one).
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

KIT = pathlib.Path(__file__).resolve().parent.parent
T = pathlib.Path(tempfile.mkdtemp(prefix="build kit "))
ENV = dict(os.environ, CLAUDE_CONFIG_DIR=str(T))

THEIRS = {
    "model": "sonnet",
    "hooks": {
        "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "my-own-check.sh"}]}],
        "Stop": [{"hooks": [{"type": "command", "command": "say done"}]}],
    },
}
(T / "settings.json").write_text(json.dumps(THEIRS))
(T / "skills" / "hub-workflow").mkdir(parents=True)
(T / "skills" / "hub-workflow" / "SKILL.md").write_text("my own hub skill")


def run(*args):
    r = subprocess.run([sys.executable, str(KIT / "install.py"), *args], env=ENV, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def settings():
    return json.loads((T / "settings.json").read_text())


def commands(s):
    """Each hook as one line. On Windows the script and its options are in "args" (no shell)."""
    return [" ".join([h["command"], *h.get("args", [])])
            for groups in s.get("hooks", {}).values() for g in groups for h in g["hooks"]]


def run_hook(h, payload):
    """Start a hook the way Claude Code does: with no shell when it has "args", else with sh -c."""
    argv = [h["command"], *h["args"]] if "args" in h else ["sh", "-c", h["command"]]
    r = subprocess.run(argv, input=json.dumps(payload).encode(), capture_output=True)
    assert r.returncode == 0, (argv, r.stderr)
    return json.loads(r.stdout or b"{}")


code, out = run()
assert code == 0, out
s = settings()
assert s["model"] == "sonnet", "unrelated settings are kept"
assert "my-own-check.sh" in commands(s) and "say done" in commands(s), "their own hooks are kept"
kit_cmds = [c for c in commands(s) if "build-kit" in c]
assert len(kit_cmds) == 6, kit_cmds
assert any("--handoff-at 120000" in c for c in kit_cmds)
assert (T / "skills" / "hub-workflow" / "SKILL.md").read_text() == "my own hub skill", "their skill untouched"
assert "skipped skill hub-workflow" in out
assert (T / "skills" / "new-project" / ".build-kit").exists()
assert all((T / "hooks" / "build-kit" / n).exists() for n in
           ["block-destructive.py", "block-secret-dumps.py", "block-secret-writes.py", "context-guard.py"])
assert list(T.glob("settings.json.bak-build-kit-*")), "a backup was made"

# The installed delete guard, started from settings.json, stops a home wipe from both shell tools.
guard = next(h for g in s["hooks"]["PreToolUse"] if g.get("matcher") == "Bash|PowerShell"
             for h in g["hooks"] if "block-destructive" in json.dumps(h))
for tool, wipe in [("Bash", "rm -rf ~"), ("PowerShell", "Remove-Item -Recurse -Force ~")]:
    out = run_hook(guard, {"tool_name": tool, "tool_input": {"command": wipe}, "cwd": str(KIT)})
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny", (tool, out)
assert run_hook(guard, {"tool_name": "Bash", "tool_input": {"command": "git status"}, "cwd": str(KIT)}) == {}

code, out = run("--handoff-at", "300000")
assert code == 0, out
kit_cmds = [c for c in commands(settings()) if "build-kit" in c]
assert len(kit_cmds) == 6, "running again adds nothing twice"
assert any("--handoff-at 300000" in c for c in kit_cmds), "a re-run updates the handoff point"

assert run("--handoff-at", "lots")[0] != 0
assert run("--handoff-at")[0] != 0
before = (T / "settings.json").read_bytes()
code, out = run("--help")
assert code == 0 and "--uninstall" in out, "--help explains and installs nothing"
assert run("--uninstal")[0] == 2, "a typo stops instead of installing"
assert (T / "settings.json").read_bytes() == before

code, out = run("--uninstall")
assert code == 0, out
assert settings() == THEIRS, ("uninstall restores their settings exactly", settings())
assert not (T / "skills" / "new-project").exists()
assert (T / "skills" / "hub-workflow" / "SKILL.md").exists(), "uninstall never removes their skill"
assert not (T / "hooks" / "build-kit").exists()

(T / "settings.json").write_text("{ not json")
code, out = run()
assert code != 0 and "isn't valid JSON" in out, out
assert (T / "settings.json").read_text() == "{ not json", "a broken settings file is never touched"

print("PASS: install keeps their settings and skills, is safe to re-run, the installed guard runs, "
      "uninstall restores settings")
