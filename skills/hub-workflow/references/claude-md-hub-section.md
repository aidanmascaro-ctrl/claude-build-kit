# CLAUDE.md hub section

Add this below the rest of a project's CLAUDE.md when it starts using the hub, and replace every
`<…>`. The rest of CLAUDE.md (commands, how we work, risk, hard rules) comes from the
`new-project` skill's template: `~/.claude/skills/new-project/references/claude-md-template.md`.

````markdown
## Several tasks at once: hub and task sessions

Uses the `hub-workflow` skill. Nothing reaches `main` without the owner's yes, and nothing is
pushed or deployed without their go in their own words.

- **Hub:** the "<Project> hub" session in the project folder, on `main`. It writes everything the
  owner says on the board first, then sorts, plans, opens task sessions, passes messages on and
  merges. It never does a task's work itself.
- **Task sessions:** one per change, each in its own worktree and branch, with an agent from
  `.claude/agents/`.
- **Board:** `.claude/hub/board.md`, with briefs in `.claude/hub/briefs/`, reports in
  `.claude/hub/reports/`, handoffs in `.claude/hub/handoffs/` and research in
  `.claude/hub/research/` (all git-ignored).
- **Caps:** at most <3> tasks building at once, and at most <3> waiting for the owner to try.
- **Hot files** (two tasks never edit these at once): `<file>`, `<file>`, `<file>`.
- **Hot resources** (one task at a time): <the simulator | the database on :5432 | none>.
- **Preview ports:** each task gets its own from <5101–5120>, bound to 127.0.0.1. <Or: one preview
  slot; replace another task's preview only when the owner says so.>

The hub merges one branch at a time, after checking the owner's answer:

```bash
git -C <worktree> rebase main
(cd <worktree> && <build> && <tests>)
git merge --ff-only <branch>
git worktree remove <worktree>        # plain, never --force
git branch -d <branch>
```

If the rebase conflicts in code the owner tried, the task resolves it and they try it again.

## Release

On the owner's go only: `<push command, e.g. git push origin main>`, then `<deploy steps>`.
Afterwards, check every live page and link yourself.
````
