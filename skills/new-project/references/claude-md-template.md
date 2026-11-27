# CLAUDE.md template

The `new-project` skill writes a project's `CLAUDE.md` from this. Replace every `<…>` and delete
lines that don't apply. Keep it short: every session reads it. Commands must be real: run each one
before writing it down.

Never put secrets, or full paths that include someone's user name, in CLAUDE.md: it's committed,
and may end up on GitHub. Those go in `.claude/hub/knowledge.md`, which isn't committed.

````markdown
# <Project name>

<Two or three lines: what it is, who it's for, what the first version does. From SPEC.md.>

## About the owner

- Codes: <not at all | a little | a lot>. <"Plain English; never ask them to edit code or run
  commands." | "Happy to talk stack and read diffs.">
- Local git commits: <yes, as we go (owner, <date>) | ask first>. Pushing always needs its own yes.
- Background notes: `.claude/hub/knowledge.md` (not committed; lists its sources). <Or: none.>

## Commands

```bash
<build>          # e.g. npm run build
<test>           # e.g. npm test
<self-check>     # drives the real thing with throwaway data; screenshots go to <folder>
<preview>        # how the owner tries it, e.g. npm run dev -- --host 127.0.0.1 --port 5173
```

## How we work

- One change at a time, unless the hub is running (see "Several tasks at once" if it's below).
- Each change: build it, run the self-check and look at every screenshot, show the owner the
  result and how to try it, ask ONE question, then commit after their answer.
- Questions: one at a time, with options. Check everything you can yourself first.
- Nothing is pushed, deployed, published, sent, bought or deleted for good without the owner's
  yes in their own words.
- Secrets live in `.env` (never committed). Refer to them by name, never by value.
- Delete by moving to the Trash or Bin where you can. Ask before anything that can't be undone.
- When the context guard says the chat is long, write a handoff and continue in a fresh session.

## Risk

- **Low-risk** (ships on the owner's yes to the screenshots and checks): copy, styling, layout,
  docs, tests, small isolated fixes.
- **Hands-on** (the owner tries it first): <the kit's hands-on list, e.g. forms that send or
  store data, sign-in, payments, anything that deletes, moves or uploads files, releases>.

## Hard rules

- <What must never happen, e.g. "never email real customers from a test", "never touch the
  production database".>
````

When the project uses the hub, `hub-workflow` adds its own section below these: see
`~/.claude/skills/hub-workflow/references/claude-md-hub-section.md`.
