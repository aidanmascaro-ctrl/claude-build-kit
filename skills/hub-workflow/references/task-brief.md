# Task brief template

The hub writes one of these to `<project>/.claude/hub/briefs/<name>.md`, then opens the task
(SKILL.md, "Opening a task session"). A fresh session knows only this file and the project's
CLAUDE.md, so keep it tight and complete. Replace every `<…>`.

```markdown
# Task: <name>

You are a <Project> task session. Your role is **<agent name>** (`.claude/agents/<agent-file>`),
<already in your instructions | read that file first>. <Or: no special role.> Read CLAUDE.md first.
Work only in your own worktree, on your own branch (`task/<name>` or the one the app gave you).
Your hub is the "<Project> hub" session: message it with SendMessage if you can; otherwise write
`<full path to project>/.claude/hub/reports/<name>.md` and tell the owner "Tell the hub: <name> is
ready". Risk label: **<low-risk | hands-on>** (<one-line reason>).

The owner (<date>): "<their request, in their own words>"

<One paragraph: what exists today, with file paths. What's wrong or missing, and what they want
instead. What has already been decided.>

## Deliver
1. <First deliverable. For design work, often "options first: show them, they pick".>
2. <Then build the chosen one.>

## Files and neighbours
- You'll touch: <files>.
- Other tasks are editing: <file> (<task>). Stay out of those, or keep to <region> and rebase
  before the merge.
- Hot resources you need: <none | the simulator, the database, …>. <"It's yours" | "Wait until the
  hub says it's free.">

## Self-check (before asking the owner anything)
<What to exercise, which states (desktop and phone, light and dark, empty and full, errors) and
which throwaway data to use. The self-check command from CLAUDE.md. What must never be touched.>

## Show it
- Preview on your own port: `<preview command using port N>`, bound to 127.0.0.1. Never use
  another task's port.
- Send the captioned screenshots and the preview link (SendUserFile if you have it, otherwise the
  full paths). Links go in plain message text, not inside a question card.

## Review
Run these as subagents and fix what they find: <a security reviewer, always (the kit's security
agent, or a general subagent told to check for leaked secrets, unsafe input handling, broken
sign-in and permission checks, and anything that deletes or uploads)>, <the kit's code reviewer>.
Explain the result in plain English.

## Ask the owner ONE question
- low-risk: "Merge on this evidence?" with *Merge* / *Change something*;
- hands-on: what to try and what they should see, with *Works* / *Doesn't work* / *Couldn't try*.
If the work turns out riskier than the label, raise it to hands-on and say why. Never lower it.

## Rules
- Don't merge, push, deploy, or touch another task's files, port or preview. The hub merges.
- <Project hard rules that apply here.>
- Commit only after the owner's answer, on your branch only.
- Delete by moving to the Trash or Bin, after the owner's yes to "OK to delete <what>?". Nothing
  that can't be undone without their yes in their own words.

## Done when
- <Concrete result the owner can try.>
- Build, tests and the self-check pass, with screenshots you've looked at.
- The owner answered your one question. You committed and told the hub:
  `Ready to merge: <branch>` with the worktree path, the commit, the checks run, the files touched
  and anything still open.

## Handoff
If the context guard tells you to hand off: write `.claude/hub/handoff-<n>.md` in this worktree
(first line: "Continue task `<name>`: read `<this brief's path>`, then this"), tell the hub
"handing over", and start the fresh session in this same worktree, as the guard describes.
```

## Messages the hub sends later

- **Main moved:** "Main is now `<sha>`, with `<what>`. It touched `<files>`. Rebase before you ask
  the owner to try anything."
- **Resource free:** "`<file or resource>` is yours now: `<task>` has merged."
- **Approval passed on:** "The owner answered in the hub: '<their exact words>'."
- **Overlap:** "`<task>` is also fixing `<thing>` in `<file>`. It merges first. Drop your version of
  that part and rebase on top of it."
- **Merged:** "merged `<sha>`. Stop your preview; you're done."
