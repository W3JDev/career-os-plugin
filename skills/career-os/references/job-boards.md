# Job boards reference

Every source Career OS scans, how to fetch it, and what breaks.

## Tier 1 — public APIs, no auth, scriptable

These run inside `scripts/scan.py` with plain HTTP. No keys, no login.

### Greenhouse
- `GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=false`
- Returns array of jobs: `title`, `absolute_url`, `location`, `departments`, `metadata`.
- **Board token discovery**: open the company's jobs page
  (`boards.greenhouse.io/{company}` or a custom domain). The token is the path
  segment, e.g. `boards.greenhouse.io/stripe` → token `stripe`. Some companies
  embed Greenhouse on their own domain — view source for `boards.greenhouse.io`.
- Rate limit: generous; add 1s sleep between companies anyway.

### Lever
- `GET https://api.lever.co/v0/postings/{company}`
- Returns array: `text` (title), `categories` (location, team, commitment),
  `hostedUrl`, `applyUrl`, `description` (HTML).
- Token discovery: `jobs.lever.co/{company}` → token `{company}`.
- Note: some companies return `[]` while their site shows jobs — they use
  Lever's hosted pages with a different slug. Fall back to browser fetch.

### Ashby
- `POST https://api.ashbyhq.com/posting-api/job-board/{board_name}`
  with JSON body `{}`.
- Returns `{"jobs": [...]}`: `title`, `department`, `locationName`,
  `employmentType`, `jobUrl`.
- Token discovery: `jobs.ashbyhq.com/{board_name}`.
- **Caution (Sep 2026):** Ashby started 401-gating automated POSTs from some
  networks. `scan.py` degrades gracefully (warn + continue). Until it clears,
  cover Ashby companies through a browser session instead.

### RemoteOK (remote-only)
- `GET https://remoteok.com/api` — returns all live postings, newest first.
- Terms: link back to RemoteOK as the source when resharing. Keep the first
  element (it's a legal notice, not a job — skip index 0).
- Filter client-side by tags.

### We Work Remotely (remote-only)
- RSS: `https://weworkremotely.com/categories/remote-programming-jobs.rss`
  (also `remote-devops-sysadmin-jobs`, `remote-product-jobs`,
  `remote-customer-support-jobs`, `remote-design-jobs`).
- Parse with any feed parser; dedup on `<link>`.

### YC Jobs
- Public API: `https://www.ycombinator.com/api/v4/jobs` with query params
  (`role`, `location`, `remote`, `experience`). Paginate.
- Good for startup roles; includes visa sponsorship flags.

### Hacker News "Who is hiring"
- Monthly thread; search via Algolia:
  `https://hn.algolia.com/api/v1/search?query=Ask%20HN:%20Who%20is%20hiring%3F&tags=story`
  then fetch top story's kids via
  `https://hacker-news.firebaseio.com/v0/item/{id}.json`.
- Parse comment text for role/location/remote/email. Noisy but high-signal for
  startups that post nowhere else.

## Tier 2 — browser session required

Run these through a `browser.spawn_task` with the candidate's (or operator's)
logged-in session. See `linkedin-playbook.md` for LinkedIn specifics.

### LinkedIn Jobs
- Best single source for most white-collar roles. Filters: keywords, location,
  remote, date posted, Easy Apply.
- Also: recruiter discovery — find hiring managers at target companies.

### Wellfound (startups)
- `wellfound.com/jobs` — strong for startup roles, salary/equity transparency.
- Search works logged-out for browsing; applying needs the session.

### Indeed
- RSS feeds are dead (captcha wall since ~2025). Use the browser session with
  the candidate's saved searches/alerts, or `indeed.com/jobs?q=...&l=...`
  rendered pages.
- Indeed email job alerts → candidate's Gmail → Career OS reads them via the
  gmail skill. This is the most reliable Indeed pipe: set up alerts once, parse
  forever.

### Glassdoor
- Useful for comp data and interview intel, weaker as a listings source.
- Interview reviews per company feed directly into interview prep packs.

### Company career pages (custom ATS: Workable, Breezy, Recruitee, Taleo)
- Workable public JSON: `https://{company}.workable.com/api/v3/accounts/{company}/jobs`
  (works for many, not all).
- Others: browser task, one per company, cached HTML parsed for postings.

## Tier 3 — alert pipes (email → skill)

- **Indeed / LinkedIn / Glassdoor job alerts**: candidate creates the alert
  once; Career OS parses the emails via gmail.
- **Wellfound matches**: same pattern.
- **Google Alerts**: `site:lever.co OR site:greenhouse.io "{role}"` — catches
  new postings within a day.

## Adding a company

1. Browser task: open the company's careers page.
2. Identify the ATS (URL pattern or page source).
3. Extract the board token, add to `data/boards.yml`:
   ```yaml
   - name: Stripe
     greenhouse: stripe
   ```
4. Next scan picks it up automatically. Coverage compounds.
