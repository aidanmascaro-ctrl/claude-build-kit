# Kit: website

Sites and web apps: landing pages, portfolios, shops, dashboards, small SaaS apps.

## Agents (from Agency Agents, copied into `.claude/agents/`)

| Agent | File | Job |
| --- | --- | --- |
| Frontend Developer | `engineering/engineering-frontend-developer.md` | Builds pages and components |
| UI Designer | `design/design-ui-designer.md` | Layout, visual design, DESIGN.md |
| Minimal Change Engineer | `engineering/engineering-minimal-change-engineer.md` | Small fixes |
| Code Reviewer | `engineering/engineering-code-reviewer.md` | Reviews each change |
| AI-Generated Code Security Auditor | `security/security-ai-generated-code-auditor.md` | Security review of each change |
| Evidence Collector | `testing/testing-evidence-collector.md` | "Is it really done?", from screenshots |
| Backend Architect | `engineering/engineering-backend-architect.md` | Only if there's a database or API |

## Plugins (see EXTRAS.md for install lines)

- **Recommended:** `ui-ux-pro-max` (a design system instead of defaults). The kit's own `unslop`
  skill polishes each screen once it works.
- **Optional:** `playwright` (lets Claude click around the site by hand, beyond the scripted
  self-check), `claude-seo` (if search traffic matters), `cloudflare` (if it's hosted there),
  `mattpocock-skills`, `ponytail`.

## Tools

Node.js (`node -v`). The self-check uses the Playwright library from npm, so it needs no plugin:
`npm i -D playwright && npx playwright install chromium`.

## Connectors and accounts

Hosting: Vercel, Netlify, Cloudflare Pages or GitHub Pages (all have free tiers; the owner makes
the account). A database only if it needs one: Supabase is the usual pick.

## Self-check

A Playwright script (`scripts/site-check.mjs`) that loads every changed page at 1440 px and 390 px,
light and dark, screenshots each, and checks console errors, failed requests, phone overflow,
images, links and meta tags. Full recipe: `~/.claude/skills/hub-workflow/references/websites.md`.

## Preview

`npm run dev -- --host 127.0.0.1 --port <port>`, opened in a browser. On the owner's phone: a
hosted preview deployment (e.g. `vercel deploy` without `--prod`), only if they've said yes for
this project.

## Hot files and resources

Hot files: global styles and Tailwind config, layout/header/footer/nav, site config
(`next.config.*`, `vercel.json`, `astro.config.*`), `package.json` and the lockfile.
Hot resources: none locally (every task has its own port). The production deploy is hub-only.

## `.gitignore` additions

`node_modules/`, `.next/`, `dist/`, `.vercel/`, `.netlify/`, test screenshots folder.

## Hands-on (not approved from evidence alone)

Forms that send or store data, sign-in, payments, analytics and tracking scripts, DNS and deploy
settings.
