# Career OS

A full career agent that lives inside Muse. It knows every candidate
personally, hunts jobs proactively across far more boards than the static
ATS lists, drafts outreach and applications, preps interviews — and bridges
every gap for candidates who don't know how the hiring game works.

Built by [Jewel / W3JDev](https://github.com/W3JDev) — shared with the
community. Fork it, use it, improve it.

## What it does

- **Knows the candidate.** Conversational intake builds a real profile —
  target roles, skills, comp, deal-breakers, work authorization. No forms.
- **Scans proactively.** Greenhouse, Lever, Ashby (public APIs), RemoteOK,
  We Work Remotely, YC Jobs, HN "Who is hiring" — plus LinkedIn, Wellfound,
  Indeed and Glassdoor through a logged-in browser session. Coverage grows:
  point it at any company's careers page and it learns that company's board.
- **Scores matches 0–100** on role fit, skills, seniority, location, comp
  signal, company quality. Pings only above your threshold (default 75).
- **Drafts outreach.** Tailored application notes, recruiter messages, referral
  asks — written, never sent. Every send needs your explicit one-tap approval.
- **Preps interviews.** Company research, likely questions, STAR stories built
  from YOUR experience, questions to ask them.
- **Hire mode.** On the other side of the table? Scorecards, calibrated
  question sets, red-flag detectors, debrief templates.
- **Bridges gaps.** Explains ATS, STAR, total comp in plain words. Writes the
  CV with you if you don't have one. Coaches negotiation.

## The one rule

**Nothing ever sends without the candidate's explicit approval of that exact
draft.** The agent does all the work; the human makes the calls. A standing
"apply to everything" instruction is never treated as approval.

## Install (any Muse workspace)

```bash
# copy this folder into your workspace skills
cp -r career-os ~/workspace/skills/career-os

# test the scanner (no keys needed)
cd ~/workspace/skills/career-os
python3 scripts/scan.py --query "ai engineer" --remote-only --out /tmp/jobs.json
```

## Onboard your first candidate

Talk to Muse — it runs the intake as a conversation, then:

```bash
python3 scripts/new_candidate.py --name "Aisha Rahman" \
  --roles "AI Engineer,Backend Engineer" --skills "Python,LLMs,FastAPI" \
  --work-mode remote --locations "Kuala Lumpur" --seniority senior \
  --deal-breakers "F&B"

python3 scripts/score.py --profile candidates/aisha/profile.yml \
  --jobs /tmp/jobs.json --out candidates/aisha/matches.json

python3 scripts/outreach.py --candidate candidates/aisha --top 5
```

Say "scan daily and ping me above 75" and Muse sets up the recurring loop.

## LinkedIn — the honest version

LinkedIn has no public API and blocks scraping hard. Career OS handles it
three ways: a logged-in browser session (paced, ≤1 session/day), LinkedIn job
alert emails parsed from Gmail (zero risk), and Google-indexed LinkedIn
postings as fallback. Full details in `references/linkedin-playbook.md`.

## Layout

```
SKILL.md                  operating contract (Muse reads this)
references/               job-boards, linkedin, outreach, interviewer playbooks
scripts/                  scan.py  score.py  outreach.py  new_candidate.py
data/boards.yml           companies to scan — add yours, coverage compounds
candidates/<slug>/        profile.yml, cv.md, matches.json, outreach/, log.md
```

Candidate data stays on your machine. Nothing leaves it.
