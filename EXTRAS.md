# Optional extras

Everything here is optional. The `new-project` skill suggests the ones that fit your project (from
its kit in `kits/`) and installs only what you say yes to. You can also ask Claude any time:
"install claude-seo from the build kit's extras".

All of these belong to their own authors. Read what a plugin does before installing it: plugins,
skills and agents become instructions for Claude. For plugins from someone's own marketplace,
Claude reads the repo's README first and tells you in a line what it adds.

## How to install

**Plugins** from Anthropic's official marketplace (already known to Claude Code):
```bash
claude plugin install <name>@claude-plugins-official
```

**Plugins** from someone's own marketplace: add it once, then install.
```bash
claude plugin marketplace add <owner>/<repo>
claude plugin install <name>@<marketplace>
```

Inside a session you can do the same with `/plugin`. New plugins load in your **next** session.
To remove one: `claude plugin uninstall <name>@<marketplace>`.

**Agents** (specialist roles, per project): get the Agency Agents catalogue once, then copy only
the ones a project needs into that project's `.claude/agents/`. Keeping them per project, not in
`~/.claude/agents`, matters: every agent you can see costs tokens in every session, and the whole
catalogue is about 280 agents.
```bash
git clone --depth 1 https://github.com/msitarzewski/agency-agents ~/.claude/agency-agents
cp ~/.claude/agency-agents/engineering/engineering-frontend-developer.md .claude/agents/
```

**Connectors** (Notion, Google Drive, Gmail, Linear and others) are connected in the Claude
desktop app or on claude.ai under **Settings → Connectors**, or with `/mcp` in a terminal. You sign
in yourself; Claude never asks for your password.

## Plugins

The first four (`ponytail`, `mattpocock-skills`, `playwright`, `ui-ux-pro-max`) are the **starter
pack**, with Agency Agents: first-time setup installs them for everyone, unless you skipped it.
They're listed here so you can add one later.

| Plugin | What it does | Good for | Install |
| --- | --- | --- | --- |
| `ponytail` | "Lazy senior developer" mode: keeps every change small and simple, ends each reply with what it skipped, plus `/ponytail-review`. On in every chat; say "normal mode" to switch it off for one chat | Every project (starter pack) | `claude plugin marketplace add DietrichGebert/ponytail` then `claude plugin install ponytail@ponytail` |
| `mattpocock-skills` | `grilling` (the pushback interview), `tdd`, `prototype`, `diagnosing-bugs`, `code-review` | Any code project | `claude plugin install mattpocock-skills@claude-plugins-official` |
| `playwright` | Drives a real browser, so Claude can click through your site and screenshot it | Websites, web apps | `claude plugin install playwright@claude-plugins-official` |
| `ui-ux-pro-max` | Searchable design database (styles, palettes, font pairings, UX rules) that produces a design system | Anything with a screen | `claude plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill` then `claude plugin install ui-ux-pro-max@ui-ux-pro-max-skill` |
| `context7` | Up-to-date docs for code libraries | Code projects using fast-moving libraries | `claude plugin install context7@claude-plugins-official` |
| `claude-seo` | SEO audits, schema, sitemaps, content checks | Sites that need search traffic | `claude plugin marketplace add AgriciDaniel/claude-seo` then `claude plugin install claude-seo@agricidaniel-claude-seo` |
| `cloudflare` | Workers, Pages, Wrangler | Sites hosted on Cloudflare | `claude plugin install cloudflare@claude-plugins-official` |
| `remotion` | Make videos with React code | Motion graphics, explainers | `claude plugin marketplace add remotion-dev/claude-code-plugin` then `claude plugin install remotion@remotion` |
| `hyperframes` | Make videos with HTML: captions, explainers, launch videos | Motion graphics, social video | `claude plugin install hyperframes@claude-plugins-official` |
| `diagram-design` | Clean diagrams; imports Mermaid, draw.io, Excalidraw | Docs, plans, reports | `claude plugin marketplace add cathrynlavery/diagram-design` then `claude plugin install diagram-design@diagram-design` |
| `last30days` | What people said about a topic in the last 30 days | Research, idea checks | `claude plugin marketplace add mvanhorn/last30days-skill` then `claude plugin install last30days@last30days-skill` |
| `coderabbit` | Extra code reviews (needs a CodeRabbit account) | Bigger code projects | `claude plugin install coderabbit@claude-plugins-official` |

## Agents worth knowing (Agency Agents)

Each kit lists its own. These turn up in most of them:

| Agent | File | Job |
| --- | --- | --- |
| Code Reviewer | `engineering/engineering-code-reviewer.md` | Reviews each change |
| AI-Generated Code Security Auditor | `security/security-ai-generated-code-auditor.md` | Finds the security holes AI-written code tends to have |
| Minimal Change Engineer | `engineering/engineering-minimal-change-engineer.md` | Small, careful fixes |
| Reality Checker | `testing/testing-reality-checker.md` | "Is it really done?" |
| Rapid Prototyper | `engineering/engineering-rapid-prototyper.md` | Quick throwaway versions to test an idea |

Browse the rest in `~/.claude/agency-agents/` once it's cloned: there are divisions for
engineering, design, marketing, product, sales, security, testing, game development and more.

## Connectors

| Connector | Use it for |
| --- | --- |
| Notion, Google Drive | Reading your notes and docs during the interview; sharing results |
| Google Sheets, Gmail, Calendar | Projects that work with those (always with your go before anything is sent) |
| Linear, GitHub | Tracking tasks and issues |
| Supabase, Vercel | A database, and hosting websites |

## Tools on your computer

| Tool | Why | Get it |
| --- | --- | --- |
| git | Checkpoints, and the hub's parallel copies | Mac: `xcode-select --install`. Windows: git-scm.com |
| GitHub CLI (`gh`) | Putting a project on GitHub, when you want to | cli.github.com |
| Node.js | Most websites and web apps | nodejs.org, or `brew install node` |
| Python 3 | The kit's installer and guards; lots of scripts | python.org, or `brew install python` |
| ffmpeg | Anything with video or audio | `brew install ffmpeg` |
| An Obsidian vault, or any notes folder | A knowledge base Claude can read | obsidian.md (it's just a folder of Markdown files) |

**Running several task sessions in a terminal?** A terminal with good tabs helps: cmux (Mac, made
for running many Claude sessions side by side), iTerm2, Windows Terminal, or tmux all work.
