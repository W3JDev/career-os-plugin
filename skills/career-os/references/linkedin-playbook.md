# LinkedIn playbook

LinkedIn is the highest-value board and the most hostile to automation. This
is the honest operating procedure — what works, what gets accounts flagged,
and the fallbacks.

## What works reliably

1. **Browser task with a real logged-in session.** The candidate signs in to
   LinkedIn once in the agent's browser (Secure Vault / normal sign-in flow).
   A `browser.spawn_task` then runs job searches exactly like a human would:
   search page → filters (location, remote, date posted, experience level) →
   scroll → open promising postings → extract title, company, location, JD text,
   apply URL.
2. **Pacing.** LinkedIn rate-limits aggressively. Rules:
   - Max ~1 search + 10–15 posting views per session.
   - Sessions spaced ≥ 6 hours apart; one LinkedIn session per day per
     candidate is the safe default.
   - Never run LinkedIn scans in parallel with the candidate actively using
     LinkedIn on another device — concurrent sessions trigger verification.
3. **Job alerts as the primary pipe.** Have the candidate create LinkedIn job
   alerts (keywords + location + remote). LinkedIn emails new matches; the
   gmail skill parses those emails. Zero automation risk, near-real-time.
4. **Recruiter/hiring-manager discovery.** Same browser session: search people
   at target companies ("hiring manager", "talent acquisition"), open profiles,
   note names/titles. Outreach messages are DRAFTED only — see
   outreach-playbook.md.

## What does NOT work / will get flagged

- Scraping `linkedin.com/jobs` logged-out (999 blocks / login walls).
- Hitting `voyager` private APIs with a scraped cookie — works briefly, then
  the account gets restricted. Never do this.
- Sending connection requests or InMails from the agent. Drafts only.
- Applying via Easy Apply from the agent — the application is a legal
  attestation by the candidate. The agent prepares everything; the candidate
  clicks submit (or explicitly approves per-application with full text shown).

## Fallback when LinkedIn is unavailable

1. Google-indexed LinkedIn jobs: `browser.search` for
   `site:linkedin.com/jobs "{role}" "{location}"`. Snippets give title/company;
   full JD needs the session.
2. Cross-reference: a role found on Greenhouse/Lever/Ashby for a company that
   also posts on LinkedIn — apply via the ATS link instead.

## Session hygiene

- Re-auth is the candidate's job: when LinkedIn asks for verification, hand
  the browser to the candidate (takeover), never ask for codes in chat.
- Log every LinkedIn session in the candidate's `log.md`: time, searches run,
  postings viewed. If LinkedIn ever shows a warning, stop LinkedIn automation
  for 7 days and switch to alerts-only.
