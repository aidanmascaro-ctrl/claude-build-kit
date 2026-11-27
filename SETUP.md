# Setup: instructions for Claude

Someone pasted this repository's link and asked you to set it up. Assume they're new to building
things: they may never have used a terminal, installed a developer tool or connected an app to
Claude. Your job is to get their computer ready and walk them through it so it feels easy.

**How to talk to them during setup**
- Before each step, say in a sentence or two what it is, why it's needed, and what they'll see.
  Afterwards, say it worked. Short and friendly; no jargon (or explain it in five words).
- One thing at a time. Ask with AskUserQuestion cards: 2 to 4 options, your recommendation first.
- Do everything you can yourself. Only ask for their hands when you have to (clicking Install,
  typing their computer password, signing in to an account), and then say exactly where to click,
  what they'll see, and what to tell you when it's done.
- Never ask them to type their password, or paste a key or token, into this chat. Passwords go
  only into their computer's own prompts and the sign-in pages of the apps themselves.
- If something fails, say plainly what happened and what you'll try next. Never leave them stuck.

## Already set up?

Run `test -f ~/.claude/build-kit/profile.md && echo yes`. If it says yes, they've done the
first-time setup before: skip to "Already set up" at the end. Otherwise do the first-time setup.

---

## First-time setup

### Step 1. Welcome

Send this (in your own words if you like):

> Welcome! Before we build anything, I'll get your computer ready. It takes about 10 to 15 minutes,
> and only the first time. Here's the plan:
> 1. Check your computer has the basic tools, and install any that are missing
> 2. Install the build kit: the instructions and safety guards I'll follow
> 3. Add a starter pack of extra skills
> 4. Connect apps you'd like me to read from, like Notion or Google Drive (optional)
> 5. One restart, and then you tell me your idea
>
> I'll do most of it myself. When I need you to click something or type your computer's password,
> I'll tell you exactly where and what you'll see.

Then ask one question: "How much do you code?" with *Not at all* / *A little* / *I'm a developer*.
If they're a developer, you can be brisker for the rest of setup. Keep their answer for step 6.

### Step 2. Check the computer

Work out the system (`uname -s`: `Darwin` is a Mac, `Linux` is Linux, and `MINGW…` or `MSYS…`
is Windows; if `uname` isn't found at all, it's Windows too). Then check each tool:

```bash
git --version; python3 --version; node --version; claude --version
python --version   # Windows: use this one. There, `python3` is often a stub that opens the Microsoft Store
brew --version || /opt/homebrew/bin/brew --version || /usr/local/bin/brew --version   # Mac only
```

Tell them what you found as a short list, with one line on what each tool is for:
- **git:** saves checkpoints of your project, so work is never lost.
- **Python:** runs the kit's installer and safety guards.
- **Node.js:** runs websites while we build them, and some of the starter tools.
- **Claude Code's command-line tool:** lets me install plugins for you. (Often missing if you only
  use the desktop app; that's normal.)
- **Homebrew** (Mac only): an app store for developer tools, so I can install everything else
  without bothering you.

Then install what's missing, in this order.

**On a Mac**
1. **git or Python missing:** run `xcode-select --install`. Tell them: "A window will pop up asking
   to install the *command line developer tools*. Click **Install**, then **Agree**. It takes 5 to
   15 minutes. Tell me when it says the software was installed." Check again afterwards.
2. **Homebrew missing:** it needs their password, so they run it themselves. Tell them:
   > Open the **Terminal** app: press Cmd + Space, type *Terminal*, press Return. Paste this line
   > and press Return:
   > `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
   > When it asks for your password, type your Mac password and press Return. Nothing appears as
   > you type: that's normal. If it says "Press RETURN to continue", press Return. It takes a few
   > minutes. Tell me when it finishes.

   Afterwards, Homebrew prints "Next steps" with lines that add it to the PATH. Do those yourself:
   for an Apple-silicon Mac, append `eval "$(/opt/homebrew/bin/brew shellenv)"` to
   `~/.zprofile` (Intel Macs: `/usr/local/bin/brew`). In this session, call brew by its full path.
   If they'd rather not use Homebrew, skip it and use the installer from nodejs.org in the next
   step instead (they download it and click through).
3. **Node.js missing:** `brew install node` (you run it; a minute or two).
4. **Claude Code's command-line tool missing:** `curl -fsSL https://claude.ai/install.sh | bash`
   (you run it; no password needed). If `claude` still isn't found, use `~/.local/bin/claude`.

**On Windows**
Tell them a box may ask "Do you want to allow this app to make changes?": click **Yes**. Then run,
for whatever's missing:
```
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
winget install --id OpenJS.NodeJS.LTS -e
powershell -c "irm https://claude.ai/install.ps1 | iex"
```
New tools may only be found after a restart of Claude Code. If so, finish what you can, then ask
them to restart and say "continue setup".

For the rest of setup on Windows:
- Type `python` where a step says `python3`.
- If you're running a command in PowerShell rather than Git Bash, write `$HOME` where a step says
  `~`. Older PowerShell hands `~` to other programs as-is, so `git clone … ~/.claude/build-kit`
  would make a folder literally called `~`.
- Where a step says **Terminal**, they open the **Terminal** app (or **PowerShell** on older
  Windows): press the Windows key, type *Terminal*, press Enter. "Return" is the Enter key.

**On Linux**
Give them one line for their package manager to paste into a terminal (it needs their password),
e.g. `sudo apt install git python3 nodejs npm`, and run the Claude Code installer yourself as on a
Mac.

Check everything again and tell them it's all there.

### Step 3. Install the build kit

Say: "Now the build kit itself: three skills that tell me how to run a project with you, and four
guards that keep your work safe."

```bash
git clone --depth 1 https://github.com/aidanmascaro-ctrl/claude-build-kit ~/.claude/build-kit
```
(If the folder already exists: `git -C ~/.claude/build-kit pull --ff-only`.)

Read `~/.claude/build-kit/install.py` before running it: it's short, and it edits their settings.
Then:
```bash
python3 ~/.claude/build-kit/install.py
python3 ~/.claude/build-kit/install.py --check
```
On Windows, type `python` instead of `python3` (and `$HOME` for `~` in PowerShell). If you know this session has a
1M-token context window, add `--handoff-at 300000` to the first command. Every line of the check
should say `ok`; if one fails, fix it (usually by running the installer again) before going on.
If the installer skipped a skill because one with that name already exists, tell them which.

Then explain what they now have, in plain words:
- **Three skills:** one for starting a project (from idea to first version), one for building
  several changes at once, and `unslop`, which makes screens look designed rather than generic.
- **Secret guards:** stop me from ever showing a password or key in the chat, or saving one into
  a file that could end up online.
- **Delete guard:** stops anything that would wipe their files, and asks them first before
  anything risky.
- **Long-chat guard:** when a chat gets long, I save notes and carry on in a fresh session, so
  nothing gets forgotten.

### Step 4. The starter pack

Say: "Plugins are add-ons that give me extra skills. These ones help with almost every project:"
- **mattpocock-skills:** lets me interview you properly about your idea, and test and fix code.
- **ui-ux-pro-max:** a design library, so anything with a screen looks designed, not generic.
- **playwright:** lets me open and click through websites to check my own work.
- **Agency Agents:** a catalogue of about 280 specialist roles (a designer, a security reviewer,
  and so on). A project only uses the few it needs.

Ask: *Install the starter pack (Recommended)* / *Let me pick* / *Skip for now*. Then (using
`~/.local/bin/claude` if `claude` isn't on the PATH):

```bash
claude plugin install mattpocock-skills@claude-plugins-official
claude plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
claude plugin install ui-ux-pro-max@ui-ux-pro-max-skill
claude plugin install playwright@claude-plugins-official
git clone --depth 1 https://github.com/msitarzewski/agency-agents ~/.claude/agency-agents
claude plugin list
```

`ui-ux-pro-max` comes from its author's own marketplace: glance at its README on GitHub first and
say in a line what it adds. Check `claude plugin list` shows all three. If one fails, tell them,
carry on without it, and note it in the profile. If the command-line tool asks them to sign in,
ask them to run `claude` once in Terminal and sign in with their Claude account.

Mention that more extras (SEO, video tools, research tools) get suggested later, only if their
project needs them.

### Step 5. Connect their apps (optional)

Say: "Connectors let me read from apps you already use, so I can learn about your idea from your
own notes and documents. I only read what's relevant, and you can disconnect any time. If your notes
are in Obsidian or a folder on this computer, there's nothing to connect: you'll just show me the
folder when we start."

Ask (allow several answers): *Notion* / *Google Drive* / *GitHub (to back up and share projects)* /
*None for now*. Then walk them through each one they picked, one at a time.

**Notion or Google Drive**
- **In the Claude desktop app:** "Click your name or initials in the bottom-left corner, then
  **Settings**, then **Connectors**. Find **Notion** (or **Google Drive**) and click **Connect**. A
  browser window opens: sign in, then click **Allow**. Notion lets you choose which pages to share:
  pick the ones about your ideas, or all of them. Come back and tell me when it's done."
- **In a terminal:** the same steps on claude.ai in their web browser (Settings → Connectors),
  signed in with the same Claude account. Connectors added there show up in Claude Code too, from
  the next session.
- **Check it:** if this session can already see the connector's tools (search with ToolSearch for
  `notion` or `drive`), run one harmless search and tell them it works. If not, it'll load after
  the restart in step 7: check it then.

**GitHub** (only needed to back up or share projects online)
1. They need a free account at github.com. They make it themselves (you never create accounts).
2. Install GitHub's tool: `brew install gh` on a Mac, `winget install --id GitHub.cli -e` on
   Windows.
3. Signing in is interactive, so they run it in Terminal. Tell them:
   > In Terminal, paste `gh auth login` and press Return. Then use the arrow keys and Return to
   > pick: **GitHub.com**, then **HTTPS**, then **Yes** (to use it with git), then **Login with a
   > web browser**. It shows an 8-character code: copy it, press Return, paste the code into the
   > page that opens, and click **Authorize**. Tell me when it says you're logged in.
4. Check with `gh auth status`. Then set their git name and their private GitHub "no-reply" email,
   so their real email never appears in public projects:
   ```bash
   git config --global user.name "$(gh api user --jq .login)"
   git config --global user.email "$(gh api user --jq '"\(.id)+\(.login)@users.noreply.github.com"')"
   ```
   Tell them that's what you did and why.

Never ask for passwords, codes or tokens in the chat.

### Step 6. Save their profile

Write `~/.claude/build-kit/profile.md` (it isn't part of the kit's files, and updates leave it
alone). Later sessions read it, so they don't repeat setup or ask the same questions again:

```markdown
# Build kit profile
- First setup: <date>
- Computer: <Mac | Windows | Linux>
- Codes: <not at all | a little | developer>
- Installed: <basics installed today>, starter pack: <which plugins>, Agency Agents: <yes | no>
- Connected: <Notion, Google Drive, GitHub | none>
- Didn't work: <anything that failed, or nothing>
- Projects started: 0
```

No passwords, keys or tokens in it.

### Step 7. Restart, then the idea

If plugins or connectors were added, a restart loads them (and switches the guards on). Tell them:

> All set! One restart loads everything we just installed:
> - **Desktop app:** start a new session in the folder you want to build in.
> - **Terminal:** type `/exit`, then `claude`, in the folder you want to build in.
>
> Then just tell me your idea, as rough as you like. A few phrases that always work:
> - "continue my project": pick up where we left off
> - "be the hub": build several things at once, once the first version works
> - "update my build kit": get the latest version
> - "what does that mean?": any time I say something unclear

If nothing new needs loading (they skipped the starter pack and connectors), skip the restart: read
`~/.claude/skills/new-project/SKILL.md` and start it now, from step 0.

---

## Already set up

They've done this before, so keep it short. Update quietly:
```bash
git -C ~/.claude/build-kit pull --ff-only
python3 ~/.claude/build-kit/install.py
python3 ~/.claude/build-kit/install.py --check
```
(On Windows: `python` instead of `python3`, and `$HOME` for `~` in PowerShell.)
Tell them in two or three lines what changed (`git -C ~/.claude/build-kit log --oneline -10`), and
mention anything in the profile's "Didn't work" line that they might want to try again. Then read
`~/.claude/skills/new-project/SKILL.md` and follow it from step 0.

To remove everything later: `python3 ~/.claude/build-kit/install.py --uninstall`, then delete the
`~/.claude/build-kit` folder.
