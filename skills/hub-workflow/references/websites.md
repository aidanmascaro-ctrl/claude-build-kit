# The hub workflow for websites

The workflow is the same as in SKILL.md. Websites differ in four things: each branch can have
its own preview, the self-check is a browser, the review looks at what ships to visitors, and
a deploy can replace everything.

## Hot files

Most site changes touch the same few files, so two tasks editing them run one after the other:

- global styles (`globals.css`, `style.css`, the Tailwind config);
- layout, header, footer and navigation components;
- site config (`next.config.*`, `vercel.json`, `astro.config.*`);
- `package.json` and the lockfile.

A lockfile conflict on rebase: take main's lockfile, re-run the install on the branch, and
commit the result. Never hand-merge a lockfile. Don't commit build output.

## A preview per branch

Unlike a desktop app, every worktree can run its own site at the same time:

- **Local:** each task runs its dev server on the port the hub gave it, bound to 127.0.0.1, e.g.
  `npm run dev -- --host 127.0.0.1 --port 5101`. Tell the owner which address is which change,
  e.g. "Pricing page: http://localhost:5101".
- **Hosted:** a preview deployment per branch, e.g. `vercel deploy` *without* `--prod`, gives a
  unique URL the owner can open on their phone too. A preview is on the internet, though hard to
  guess, so ask the owner once per project whether branch previews may be deployed. Never deploy
  to production from a task session.

## Self-check

Build a scripted checker early in the project. A small Playwright script (e.g.
`scripts/site-check.mjs`) or a browser tool works. For every page the change touches, it:

1. Loads the page at **desktop (1440 px)** and **phone (390 px)**, in **light and dark**, and
   saves a screenshot of each. Use a full-page screenshot when the page scrolls.
2. Checks these, and records PASS/FAIL for each:
   - no console errors and no failed network requests (404s, blocked scripts);
   - no horizontal scroll on the phone (`scrollWidth <= innerWidth`);
   - every image loaded (`complete && naturalWidth > 0`) and has alt text;
   - every internal link and download returns 200;
   - forms, filled with test data, go only to a local or test endpoint;
   - the title, description and og/twitter preview tags are present and the og image loads;
   - pages that change per visitor (logged in or out, empty or full) are checked in each state.
3. Writes a short report and a contact sheet of all the screenshots, so a session can look at
   every one and send them to the owner.

Look at the screenshots yourself; passing checks don't prove it looks right. Never use real
customer data or real accounts, and never send real emails or payments.

## Showing the owner

Send the contact sheet or the key screenshots, captioned. Then ask one question with the
preview address: "Open <address> on your laptop and phone. Does the <page> look and work the
way you want?" Offer *Looks right* / *Needs changes* / *Couldn't check*.

## Review: what ships to visitors

- No secrets in client code, the repo or the build output: API keys, tokens, `.env*`.
- Third-party scripts, fonts and embeds are only the expected ones, and any CSP or security
  headers are unchanged or deliberately updated.
- Forms validate input and post only to the intended endpoint. No personal data goes in URLs.
- External links use `rel="noopener"`. Copied text and images have the rights to be used.
- Basic accessibility: headings in order, labelled controls, visible focus, enough contrast.

## Deploy (hub only, on the owner's go)

1. Deploy from `main` after every approved branch is merged, never from a task branch.
2. Some setups replace the whole site with each deploy, for example a static folder uploaded
   with the CLI. Then the deploy folder must hold *everything* that should stay live,
   including downloads and files not kept in git. Build it in a temp folder from
   `git archive HEAD <site folder>` and add those files.
3. If you link the folder to the host, linking may write secrets files (`vercel link` writes
   `.env.local`). Delete them before or after the deploy, and confirm they return 404 live.
4. Check the live site yourself:
   - every page and asset returns 200, and every download is the right size;
   - the page shows the new content;
   - `.env*`, `.vercel/` and `.git/` return 404;
   - the link preview still renders.
5. Push `main`, and note what went live (commit, URL, date) on the board.
