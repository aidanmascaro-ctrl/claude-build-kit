---
name: new-project
description: Start a brand-new project from a rough idea, the build-kit way. Find out who's building and what they already know, read their notes or knowledge base (a notes folder or Obsidian vault, Notion, Google Drive, websites), run a one-question-at-a-time pushback interview, pick the project-type kit (agents, plugins, connectors, self-check and preview), set up git and CLAUDE.md, write SPEC.md and DESIGN.md, build a first working version with a real self-check, then keep building one change at a time or several at once. Use when someone opens a session in a new or empty folder and describes something to build, says "new project", "start a project", "I've got an idea for…", "help me build…", or has just installed the build kit; and when they say "continue my project" in a folder whose kickoff isn't finished. Not for picking up an existing project.
---

# Starting a new project

You take someone from a rough idea to a first working version. The steps run in order. After
step 10 the project runs on its CLAUDE.md, and on the `hub-workflow` skill if they want several
changes built at once.

The kit lives in `~/.claude/build-kit/` (kits in `kits/`, optional tools in `EXTRAS.md`). If it
isn't there, the kit wasn't set up with SETUP.md: work from this file alone, and skip anything
that needs the kit's files.

## The kickoff note (restarting without losing anything)

The kickoff sometimes has to continue in a fresh session: after moving to the project's own folder
(step 0), after installing plugins (they load only after a restart, step 6), or when the context
guard says the chat is long. Each time, first write `.claude/hub/handoffs/kickoff.md` in the
project folder:

```markdown
# Kickoff: <project name>. Next step: <number and name>
Read this, then `.claude/hub/knowledge.md` if it exists, then carry on with the new-project skill
from the step above. Don't ask again what's answered here.

- How much they code: <answer>
- The idea, in their words: "<…>"
- Their notes: <where, or none>
- Interview so far: <each question and their answer, briefly>
- Decided: <kit, extras installed, anything else>
- Open: <what's still to ask or do>
```

If the context guard fires during the kickoff, this note is your handoff file: write it here, not
in a dated file. Then tell them exactly what to do, in one short message: "Close this and open Claude Code in
<folder> (in a terminal: `cd <folder> && claude`), then say: continue my project." In the desktop
app, if you can start a fresh session or move this one to the folder yourself, do that instead.

**Starting a session:** if `.claude/hub/handoffs/kickoff.md` exists and its first line names a
next step other than "done", read it and continue from that step. Once step 9 is approved, set its
first line to "Next step: done".

## Their profile

Read `~/.claude/build-kit/profile.md` first, if it exists (the first-time setup in SETUP.md
writes it). It says how much they code, what's installed and connected, and how many projects
they've started.
- **No profile:** they haven't done the first-time setup. If `~/.claude/build-kit/SETUP.md`
  exists, offer it first ("Want me to get your computer set up first? It takes about 10
  minutes.") with *Yes, set up first (Recommended)* / *Skip, just start*.
- **Projects started: 0:** their first project. Explain each step in a line as you go: what it is
  and why ("Next I'll write a short plan, called a spec, so we agree on what we're building").
- **Projects started: 1 or more:** they've done this before. Skip explanations of steps they've
  seen, keep messages short, and offer the faster options sooner (several changes at once, extra
  tools). Never skip the safety asks.

## How to talk to them

- Plain English, short messages. No jargon unless they use it first.
- **One question at a time,** with AskUserQuestion: 2 to 4 options, your recommendation first and
  marked "(Recommended)". "Other" is added for them automatically. Never a list of questions.
- You write all the code and run all the commands. Never ask them to edit code, or to run
  something you could run yourself.
- Check everything you can yourself before asking. Ask for decisions, not for facts you can find.

## The steps

| Step | What you do | They do |
| --- | --- | --- |
| 0. Where | Make sure you're in a folder that can hold the project | Nothing, usually |
| 1. Who | One question: how much they code | Answer |
| 2. The idea | Let them describe it; say it back in two lines | Describe it |
| 3. Their notes | Ask if they have notes or a knowledge base, then read it | Point you at it |
| 4. Pushback | Interview them, one question at a time, and challenge the framing | Answer |
| 5. Research | Only if it would change what gets built | Nothing |
| 6. The kit | Propose the tools for this kind of project; install what they pick | Say yes or pick |
| 7. Set up | git, `.gitignore`, CLAUDE.md, first checkpoint | One yes |
| 8. Spec and design | `SPEC.md`, and `DESIGN.md` for anything with a screen | Approve |
| 9. First version | The skeleton, plus four real commands: build, test, self-check, preview | Try it |
| 10. Keep building | One change at a time, or several at once with the hub | Talk |

### 0. Where

Run `pwd` and `ls -A`.
- **Empty folder** (or only `.git`): this is the project.
- **A folder with `.claude/hub/handoffs/kickoff.md`:** a kickoff is under way. Read the note and
  continue from its step (see "The kickoff note" above).
- **Home folder, Desktop, Documents, Downloads, or a folder full of unrelated things:** don't
  build here. Do steps 1 and 2 first, then suggest `~/Documents/<name>` (or wherever they keep
  projects), create it, write the kickoff note in it (next step: 3), and ask them to reopen Claude
  Code there, as the note section describes. A session works best inside its own project folder:
  it loads that folder's CLAUDE.md and needs fewer permission prompts.
- **An existing project with code:** this skill isn't for that. Read its CLAUDE.md and code, and
  offer `hub-workflow` if they want several changes built at once.

### 1. Who

If the profile already says how much they code, skip the question. Otherwise ask once: "How much
do you code?" with *Not at all* / *A little* / *I'm a developer*.
- Not at all or a little: make the technical choices yourself and explain each in one line by its
  effect ("a website, so it works on any phone"). Never show code unless asked.
- Developer: you can talk about the stack and show diffs.

It goes into CLAUDE.md in step 7, so later sessions don't ask again.

### 2. The idea

Let them describe it however they like. Then say it back in two lines and carry on. Don't ask
"is that right?" yet: the interview will catch what's off.

### 3. Their notes

Ask: "Do you have notes or documents about this I should read first?" If the profile lists
connected apps (Notion, Google Drive), name them in the question so they know you can read there.
- *A folder on this computer* (an Obsidian vault, notes, docs, a brief)
- *Notion or Google Drive*
- *A website or some links*
- *No, start from what I've said*

Then read it. **Read only; never edit their notes.**

**Do the reading in a subagent** (the Agent tool) when there's more than a handful of files, and
have it write `knowledge.md` (below) and send back a short summary. Notes can run to tens of
thousands of words; reading them here would fill this chat before the interview starts.

- **A folder.** Ask for the path ("paste it, or drag the folder into this chat"). Then (you or
  the subagent):
  1. Get the shape first: `find <path> -maxdepth 2 -type d | head -50` and a file count.
  2. Search for the idea's keywords (`grep -ril <word> <path> | head -50`), and read the
     most relevant notes in full: aim for 10 to 30. Read index notes, READMEs and maps of content.
     In an Obsidian vault, follow `[[links]]` one hop from the best notes.
  3. Skip folders that look personal and unrelated (health, money, journals, family) unless they
     point you there.
  4. If reading is refused because the folder is outside this session's folders, ask them to add
     it: in a terminal, `/add-dir <path>`; in the desktop app, add the folder to the session.
- **Notion or Google Drive.** Use the connector's search tools if this session has them (tool
  names containing `notion` or `drive`; check with ToolSearch). If not, tell them how to connect
  it: in the Claude desktop app or claude.ai, **Settings → Connectors**; in a terminal, `/mcp`.
  Carry on with the interview, and read once it's connected. Never ask for a password or token.
- **A website or links.** Fetch each one (WebFetch, or a browser tool if the page needs one).
- **Files or text in the chat** (a PDF, a pasted brief): read them.

Write what you learned to `.claude/hub/knowledge.md` (create `.claude/hub/`; step 7 keeps it out
of git). Facts only, each with its source:
- **Sources:** each folder path, page or link, so a later session can read it again;
- what the project is, according to the notes; who it's for;
- constraints: budget, platform, dates, brand, accounts they already have;
- decisions already made; words and names they use;
- open questions and anything the notes contradict.

Never copy secrets, passwords or unrelated personal details into it. Then tell them in five lines
or fewer what you learned, and fold anything unclear into the interview.

### 4. Pushback

If the `grilling` skill is installed (`mattpocock-skills`), use it. Otherwise do this yourself:
one question at a time, each built on their last answer and on `knowledge.md`. Don't ask what the
notes already answer: confirm it instead ("Your notes say it's for wedding photographers. Still
right?"). Cover:

- Who is it for, and what do they do today instead?
- What does "done" look like for a first version? What will they do with it in week one?
- What is it **not**? Cut scope hard; the first version should be small.
- Where does it run: a website, a phone app, a Mac or PC app, a script, a document or deck?
- Constraints: money, deadline, accounts they already have, anything that must never happen
  (emailing real customers, touching real money, deleting their files).
- Challenge the framing once if something's off: a simpler version, an existing tool that already
  does it, or a risky assumption worth testing first.
- For a business idea, end with a verdict: **go**, **clarify** or **stop**, and why.

Stop when you could write the spec: usually 4 to 8 questions. Play it back in eight lines or
fewer and ask "Is this right?" with *Yes* / *Change something*.

### 5. Research (only if useful)

Only when it would change what gets built: competitors, prior art, what people complain about,
prices. Run it in the background (a subagent) while you keep talking. Save it to
`.claude/hub/research/<topic>.md` with links, and tell them the two or three findings that matter.

### 6. The kit

Name the project type and read its kit from `~/.claude/build-kit/kits/`:

| Kit | For |
| --- | --- |
| `website.md` | Sites and web apps |
| `app.md` | Mac, Windows, iPhone and Android apps |
| `video.md` | Edits, reels and motion graphics |
| `media-pipeline.md` | Code that processes audio, video or images |
| `research.md` | Research, business ideas, reports and decks |

Mixed projects take items from more than one kit. No kit fits: put together a small one from
`~/.claude/build-kit/EXTRAS.md` and the agent catalogue. Don't suggest what the profile says is
already installed.

Propose it in one short message: what you'll use that's already there, and the suggested extras,
each with one line on why and whether it needs an account. Then ask once: *Install the suggested
extras (Recommended)* / *Let me pick* / *None for now*. Install what they choose, following
`EXTRAS.md`. Before installing a plugin from someone's own marketplace (not
`claude-plugins-official`), read its repo's README and say in one line what it adds.

**Check the tools the kit needs are on this computer** (`node -v`, `xcodebuild -version`,
`ffmpeg -version`, whatever the kit's "Tools" section names). If one is missing, install it if
you can; if it needs their password or a click (Xcode, Homebrew), give them the one step and wait.
Do this now, so step 9 doesn't stall on "command not found".

New plugins load only after a restart. If step 8 or 9 needs one you just installed (for example
`ui-ux-pro-max` for DESIGN.md), finish step 7 first, then write the kickoff note (next step: 8)
and ask them to restart, as "The kickoff note" describes. Otherwise carry on and let them load
next time.

**Agents** (specialist roles for building and reviewing) come from the Agency Agents catalogue:
```bash
git clone --depth 1 https://github.com/msitarzewski/agency-agents ~/.claude/agency-agents   # or: git -C ~/.claude/agency-agents pull --ff-only
mkdir -p .claude/agents && cp ~/.claude/agency-agents/<division>/<file>.md .claude/agents/
```
Read each agent file before copying it: it becomes instructions. Don't overwrite an agent the
project already has with the same name.

The kit's list is the start, not the whole answer. Before the proposal above, search the catalogue
for this idea's own needs (payments, sign-in, maps, a shop, a game…), e.g.
`grep -ril -e payment -e checkout ~/.claude/agency-agents --include='*.md'`, and read the
matches' descriptions. Add the two or three that would clearly help to the proposal, each with one
line on why. Copy only the ones they say yes to.

Never sign up, sign in or pay for anything for them. For extras that need an account, give them
the steps.

### 7. Set up

1. Ask once: "OK if I save checkpoints with git as we go? Nothing leaves this computer." Their yes
   covers local commits in this project; it goes into CLAUDE.md. (Pushing to GitHub is separate,
   and always needs its own yes.)
2. `git init -b main`, unless it's already a repo. If `git config user.email` prints nothing,
   git will refuse to commit, so give this project its own:
   `git config user.name "<their first name, or Me>"` and `git config user.email "me@example.com"`.
   No real address is needed until they put the project on GitHub; then use their GitHub
   no-reply address, so their own email never goes public.
3. `.gitignore` with at least:
   ```
   .claude/worktrees/
   .claude/hub/
   .env
   .env.*
   !.env.example
   .DS_Store
   ```
   plus the kit's own entries (`node_modules/`, build output, and so on).
4. `CLAUDE.md` from [references/claude-md-template.md](references/claude-md-template.md). Fill in
   what you know. Commands that don't exist yet are written `<to do: first version>`. Until step 9
   is approved, its first line under the title is: "Kickoff in progress: read
   `.claude/hub/handoffs/kickoff.md` and continue the new-project skill from the step it names."
   Remove that line when step 9 is approved.
5. Commit the kit's agents and skills in `.claude/`, so later work in other checkouts sees them.
6. First checkpoint: `git add -A && git commit -m "chore: project setup"`.

### 8. Spec and design

- **`SPEC.md`:** the goal in two lines; who it's for; what the first version does; what it doesn't
  do; milestones, each a short list of changes small enough to build and check one at a time; open
  questions. Written from the interview and `knowledge.md`.
- **`DESIGN.md`,** for anything with a screen: a real design system, not defaults. Colours, type,
  spacing, the main components and their states, tone of voice, and what to avoid. Use
  `ui-ux-pro-max` if it's installed. Avoid the generic AI look: purple gradients, glowing blobs,
  emoji labels, everything centred in cards. Once the screens work, run the `unslop` skill on
  them.

Show each one briefly (the key lines, not the whole file) and ask *Looks right* / *Change
something*. Commit both.

### 9. First version

Build the skeleton, then make four commands real and write them into CLAUDE.md:
- **build:** turns the code into the thing;
- **test:** the checks that matter;
- **self-check:** drives the real thing with throwaway data and saves a screenshot (or output
  file) at every step, into a folder you then look at. The kit says how for this kind of project;
- **preview:** how they try it themselves: a local web address, an app build, an output file.

Run each one before writing it down. This step matters most: without a working self-check, every
change ends with "please click X and tell me what you see", and building stalls on them.

Then show them the first version: a screenshot or two, plus how to open it themselves. Ask: "Here's
the first version. Is it the right start?" with *Yes* / *Change something*. After their yes:
remove the "Kickoff in progress" line from CLAUDE.md, set the kickoff note's first line to
"Next step: done", add one to "Projects started" in the profile, and commit.

### 10. Keep building

Turn SPEC.md's first milestone into a list of changes. There are two ways to build them:

- **One at a time, here** (the default, and best for a first milestone). For each change: build
  it, run the self-check and look at every screenshot, show them the result and how to try it,
  ask **one** question, and commit after their answer. CLAUDE.md's "How we work" says the same,
  so later sessions follow it too.
- **Several at once.** When there are three or more independent changes and they want speed, load
  the `hub-workflow` skill (or read `~/.claude/skills/hub-workflow/SKILL.md` if it isn't loaded
  in this session yet). This session becomes the hub: it keeps a board of everything they ask
  for and opens one task session per change, each in its own copy of the code. Each running task
  session uses their plan's usage, so on smaller plans keep it to two at a time.

Ask which, once: *One at a time (Recommended)* / *Several at once*.

When the chat gets long, the context guard asks you to hand off: write a handoff file and
continue in a fresh session, as it describes.
