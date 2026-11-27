#!/usr/bin/env python3
"""Install, update, check or remove the build kit in your Claude Code folder (~/.claude).
On Windows, type `python` where this says `python3`.

    python3 install.py                     install or update (safe to run again)
    python3 install.py --handoff-at 300000 same, with a later handoff point (for 1M-token windows)
    python3 install.py --check             run the tests and check what's installed
    python3 install.py --uninstall         remove everything this script added

What it touches:
  ~/.claude/skills/new-project, hub-workflow, unslop             (each marked with a .build-kit file)
  ~/.claude/hooks/build-kit/                                     (the four guard scripts)
  ~/.claude/settings.json                                        (hook entries; backed up first)

It never overwrites a skill you already had under the same name, and it only ever edits or removes
its own entries in settings.json. Set CLAUDE_CONFIG_DIR to install somewhere other than ~/.claude.
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

KIT = pathlib.Path(__file__).resolve().parent
SKILLS = ["new-project", "hub-workflow", "unslop"]
HOOK_FILES = ["block-destructive.py", "block-secret-dumps.py", "block-secret-writes.py", "context-guard.py"]
MARKER = ".build-kit"
DEFAULT_HANDOFF = 120_000
WINDOWS = os.name == "nt"
PY = "python" if WINDOWS else "python3"  # what to type, for messages


def claude_dir() -> pathlib.Path:
    return pathlib.Path(os.environ.get("CLAUDE_CONFIG_DIR") or "~/.claude").expanduser()


def hook_dir() -> pathlib.Path:
    return claude_dir() / "hooks" / "build-kit"


def ours(hook: dict) -> bool:
    args = hook.get("args")
    words = [str(hook.get("command", ""))] + ([str(a) for a in args] if isinstance(args, list) else [])
    return any("hooks/build-kit/" in w.replace("\\", "/") for w in words)


def registrations(handoff_at: int) -> list[tuple[str, str | None, dict]]:
    """(event, matcher, how to run it) for every hook this kit adds."""
    def cmd(name, *args):
        script = str(hook_dir() / name)
        if WINDOWS:
            # Windows often has no `python3`, and the shell that runs hooks there may be Git Bash or
            # PowerShell, which quote differently. So no shell at all: Claude Code starts this exact
            # Python with these arguments ("exec form"). Re-running the installer after a Python
            # upgrade points it at the new one.
            return {"command": sys.executable, "args": [script, *args]}
        # `python3` from PATH survives Python upgrades; a pinned path (e.g. a Homebrew keg) can vanish
        # and silently switch the guards off.
        return {"command": " ".join(["python3", f'"{script}"', *args])}
    # On Windows, Claude Code may run commands with its PowerShell tool instead of Bash.
    return [
        ("PreToolUse", "Bash|PowerShell", cmd("block-secret-dumps.py")),
        ("PreToolUse", "Bash|PowerShell", cmd("block-destructive.py")),
        ("PreToolUse", "Write|Edit", cmd("block-secret-writes.py")),
        ("Stop", None, cmd("context-guard.py", "--handoff-at", str(handoff_at))),
        ("PreCompact", None, cmd("context-guard.py")),
        ("SessionStart", "compact", cmd("context-guard.py")),
    ]


# ---------- settings.json ----------

def load_settings(path: pathlib.Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8") or "{}")  # Windows would guess another encoding
    except ValueError as e:
        sys.exit(f"Stopped: {path} isn't valid JSON ({e}). Nothing was changed. Fix it, then run again.")
    if not isinstance(data, dict):
        sys.exit(f"Stopped: {path} doesn't hold a JSON object. Nothing was changed.")
    return data


def without_ours(settings: dict) -> dict:
    """A copy of settings with every build-kit hook entry taken out, and nothing else changed."""
    hooks = settings.get("hooks")
    if not isinstance(hooks, dict):
        return dict(settings)
    kept = {}
    for event, groups in hooks.items():
        if not isinstance(groups, list):
            kept[event] = groups
            continue
        new_groups = []
        for g in groups:
            if not isinstance(g, dict) or not isinstance(g.get("hooks"), list):
                new_groups.append(g)
                continue
            inner = [h for h in g["hooks"] if not (isinstance(h, dict) and ours(h))]
            if inner:
                new_groups.append({**g, "hooks": inner})
        if new_groups:
            kept[event] = new_groups
    out = dict(settings)
    if kept:
        out["hooks"] = kept
    else:
        out.pop("hooks", None)
    return out


def with_ours(settings: dict, handoff_at: int) -> dict:
    out = without_ours(settings)
    hooks = dict(out.get("hooks") or {})
    for event, matcher, run in registrations(handoff_at):
        group = {"hooks": [{"type": "command", **run, "timeout": 10}]}
        if matcher:
            group = {"matcher": matcher, **group}
        hooks[event] = list(hooks.get(event, [])) + [group]
    out["hooks"] = hooks
    return out


def write_settings(path: pathlib.Path, new: dict) -> None:
    if path.exists():
        backup = path.with_name(f"settings.json.bak-build-kit-{time.strftime('%Y%m%d-%H%M%S')}")
        shutil.copy2(path, backup)
        print(f"  backed up settings.json to {backup.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(new, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)  # atomic, so a crash can't leave a half-written settings file


# ---------- actions ----------

def install(handoff_at: int) -> None:
    home = claude_dir()
    print(f"Installing the build kit into {home}")
    for name in SKILLS:
        dest = home / "skills" / name
        if dest.exists() and not (dest / MARKER).exists():
            print(f"  skipped skill {name}: you already have one with that name, so it was left alone")
            continue
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(KIT / "skills" / name, dest)
        (dest / MARKER).write_text(f"Installed by the build kit from {KIT}. Delete this folder to remove it.\n")
        print(f"  skill {name}")
    hook_dir().mkdir(parents=True, exist_ok=True)
    for name in HOOK_FILES:
        shutil.copy2(KIT / "hooks" / name, hook_dir() / name)
    print(f"  guards in {hook_dir()}")
    path = home / "settings.json"
    current = load_settings(path)
    new = with_ours(current, handoff_at)
    if new != current:
        write_settings(path, new)
    print(f"  guards registered in settings.json (handoff point {handoff_at // 1000}k tokens)")
    print("Done. The guards switch on in your next Claude Code session.")


def uninstall() -> None:
    home = claude_dir()
    print(f"Removing the build kit from {home}")
    path = home / "settings.json"
    current = load_settings(path)
    new = without_ours(current)
    if new != current:
        write_settings(path, new)
        print("  hook entries removed from settings.json")
    for name in SKILLS:
        dest = home / "skills" / name
        if (dest / MARKER).exists():
            shutil.rmtree(dest)
            print(f"  skill {name} removed")
    if hook_dir().exists():
        shutil.rmtree(hook_dir())
        print("  guards removed")
    print(f"Done. The kit's own copy is still in {KIT}; delete that folder too if you're finished with it.")


def check() -> bool:
    ok = True
    for test in sorted((KIT / "tests").glob("test_*.py")):
        r = subprocess.run([sys.executable, str(test)], capture_output=True, text=True)
        line = (r.stdout.strip().splitlines() or [r.stderr.strip()[-300:]])[-1]
        print(f"  {'ok  ' if r.returncode == 0 else 'FAIL'} {test.name}: {line}")
        ok &= r.returncode == 0
    home = claude_dir()
    for name in SKILLS:
        present = (home / "skills" / name / "SKILL.md").exists()
        print(f"  {'ok  ' if present else 'FAIL'} skill {name} {'installed' if present else 'missing'}")
        ok &= present
    for name in HOOK_FILES:
        same = (hook_dir() / name).exists() and (hook_dir() / name).read_bytes() == (KIT / "hooks" / name).read_bytes()
        print(f"  {'ok  ' if same else 'FAIL'} guard {name} {'up to date' if same else 'missing or out of date'}")
        ok &= same
    hooks = load_settings(home / "settings.json").get("hooks") or {}
    found = sum(1 for groups in hooks.values() if isinstance(groups, list) for g in groups
                if isinstance(g, dict) for h in g.get("hooks") or [] if isinstance(h, dict) and ours(h))
    want = len(registrations(DEFAULT_HANDOFF))
    print(f"  {'ok  ' if found == want else 'FAIL'} {found} of {want} guard entries in settings.json")
    ok &= found == want
    print("All good." if ok else f"Something's wrong: run `{PY} install.py` again, then this check.")
    return ok


def main(argv: list[str]) -> None:
    known = {"--uninstall", "--check", "--handoff-at"}
    if any(a not in known and not (a.isdigit() and argv[i - 1:i] == ["--handoff-at"]) for i, a in enumerate(argv)):
        print(__doc__)  # --help, or a typo: say what it does rather than install anyway
        sys.exit(0 if argv[0] in ("-h", "--help") else 2)
    if "--uninstall" in argv:
        uninstall()
    elif "--check" in argv:
        sys.exit(0 if check() else 1)
    else:
        handoff = DEFAULT_HANDOFF
        if "--handoff-at" in argv:
            i = argv.index("--handoff-at")
            if i + 1 >= len(argv) or not argv[i + 1].isdigit() or int(argv[i + 1]) < 20_000:
                sys.exit("--handoff-at needs a number of tokens, at least 20000, e.g. --handoff-at 300000")
            handoff = int(argv[i + 1])
        install(handoff)


if __name__ == "__main__":
    main(sys.argv[1:])
