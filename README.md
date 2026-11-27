# Claude Build Kit

Turn an idea into a working project with [Claude Code](https://claude.com/claude-code). Paste this
repo's link into Claude, answer a few questions, and it builds it with you: a website, an app, a
video tool, a research report, whatever you've got in mind.

You don't need to code. Claude writes the code, checks its own work with screenshots, and asks you
one clear question at a time.

## Start

You need Claude Code (the Claude desktop app's **Code** tab, or `claude` in a terminal) on a paid
Claude plan.

1. Make a new, empty folder for your idea and open Claude Code in it.
2. Paste this:
   ```
   Set me up with https://github.com/aidanmascaro-ctrl/claude-build-kit
   ```
3. Answer its questions, then tell it your idea.

Claude reads [SETUP.md](SETUP.md) and takes it from there.

**The first time** takes about 10 to 15 minutes, and Claude walks you through all of it:
1. It checks your computer has the basic tools (git, Python, Node.js) and installs any that are
   missing. You might click **Install** in a pop-up, or type your computer's password once into
   the Terminal app. It tells you exactly where.
2. It installs the build kit: the instructions it follows and the safety guards.
3. It adds a starter pack of plugins (interviewing, design, website testing) and a catalogue of
   specialist agents.
4. If you want, it helps you connect Notion, Google Drive or GitHub, step by step. You sign in
   yourself; it never sees your passwords.
5. One restart, then you tell it your idea.

**After that,** starting a project is just: open a new folder, describe your idea. Claude
remembers your setup and keeps the explanations shorter as you get used to it.

If Claude ever asks you to restart (for example after installing a plugin), open Claude Code in
your project folder again and say **continue my project**. It picks up exactly where it stopped.

## What happens next

1. **It gets to know you.** One question: how much you code, so it pitches everything right.
2. **You describe your idea.** Rough is fine.
3. **It asks about your notes.** Got a notes folder or Obsidian vault, Notion pages, Google Drive
   docs or a website about this? It reads them first, so it doesn't ask what you've already
   written down. It only reads; it never edits your notes. What it learns stays in a file on your
   computer that isn't uploaded anywhere.
4. **It pushes back.** One question at a time: who it's for, what "done" looks like, what to leave
   out. It'll challenge the idea if something's off. For a business idea, you get a verdict: go,
   clarify or stop.
5. **It picks the tools.** Each kind of project has a kit (website, app, video, media pipeline,
   research) of specialist agents and plugins. It suggests the ones that fit, and installs only
   what you say yes to.
6. **It writes the plan.** `SPEC.md` (what it does and doesn't do) and, if there's a screen,
   `DESIGN.md` (how it looks). You approve both.
7. **It builds a first version,** with a self-check that clicks through it and screenshots every
   step. You try it.
8. **It keeps building,** one change at a time, or several at once (below).

## Building several things at once

When you have a list of changes, say "be the hub". That session becomes the project's **hub**:
- you tell it anything, any time: a bug, five ideas at once, a half-thought;
- it writes every item down on a board first, so nothing gets lost;
- it opens a separate **task session** for each change, each in its own copy of the code;
- each task builds, checks itself, gets a security review, and asks you one question: "Here's what
  changed. Merge it?";
- the hub merges what you approve.

In the desktop app the hub opens the task sessions itself, which is the easy way if you don't
code. In a terminal it gives you one line to paste into a new tab for each task. Every task session
uses your plan's usage, so on smaller plans keep it to two at a time.

## What gets installed

All of it goes in your Claude Code folder (`~/.claude`), and the installer backs up your settings
before changing them.

| Piece | What it does |
| --- | --- |
| `new-project` skill | The whole flow above, from idea to first version |
| `hub-workflow` skill | Building several changes at once with a hub and task sessions |
| Secret-leak guards | Stop Claude from printing a password or API key into the chat, or writing one into a file that could end up on GitHub |
| Destructive-command guard | Blocks wiping your home folder or a disk; asks before deleting folders, `git reset --hard`, force-pushing and dropping database tables |
| Context guard | When a chat gets long, Claude writes a handoff note and carries on in a fresh session, instead of losing detail to an automatic summary |

**Starter pack** (recommended at setup; you can skip it):

| Piece | What it does |
| --- | --- |
| `mattpocock-skills` plugin | Lets Claude interview you properly, and test and debug code |
| `ui-ux-pro-max` plugin | A design library, so anything with a screen looks designed, not generic |
| `playwright` plugin | Lets Claude open and click through websites to check its own work |
| Agency Agents catalogue | About 280 specialist roles; each project uses only the few it needs |

**Basic tools,** if they're missing: git, Python, Node.js, Claude Code's command-line tool, and
Homebrew on a Mac.

More extras (SEO, video, research and more) are in [EXTRAS.md](EXTRAS.md). You get asked about
the ones that fit each project.

## Your safety

- Nothing is pushed to GitHub, deployed, posted, sent, bought or deleted for good without your yes.
- Your notes are read, never changed, and what Claude learns from them stays in an ignored file in
  your project.
- Secrets go in a `.env` file that's never committed.
- Claude never signs up, signs in or pays for anything on your behalf.

## Updating and removing

- **Update:** tell Claude "update my build kit".
- **Check it's working:** `python3 ~/.claude/build-kit/install.py --check`
- **Remove it:** `python3 ~/.claude/build-kit/install.py --uninstall` takes out the skills, the
  guards and their settings, and leaves your own settings and skills alone. Then delete the
  `~/.claude/build-kit` folder (and `~/.claude/agency-agents`, if a project cloned it).

## What's in this repo

```
SETUP.md        what Claude does when you paste the link
install.py      installs, checks, updates and removes the kit
skills/         new-project and hub-workflow
hooks/          the four guards
kits/           tools per project type: website, app, video, media-pipeline, research
EXTRAS.md       optional plugins, agents, connectors and tools, with install lines
tests/          self-checks for the guards and the installer (python3 install.py --check)
```

## Credits

The destructive-command guard is a fresh, smaller take on the idea behind gstack's `/careful`.
The agents come from [Agency Agents](https://github.com/msitarzewski/agency-agents). The plugins in
EXTRAS.md belong to their authors. This kit is MIT licensed: use it, change it, share it.
