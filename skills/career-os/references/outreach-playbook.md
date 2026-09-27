# Outreach playbook — proactive reach-out, draft-first

Career OS is proactive: it doesn't wait for the candidate to find roles, it
brings roles AND the first message to them. But proactive never means sending
without permission.

## The draft queue

`scripts/outreach.py` builds, per top match:

1. **Application draft** — tailored cover note / answers to common screening
   questions, referencing the candidate's real experience. Saved as
   `candidates/<slug>/outreach/<company>-<role>-application.md`.
2. **Recruiter outreach** — short message to the recruiter or hiring manager
   (name found via LinkedIn discovery): who the candidate is, why this role,
   one proof point, soft call to action. Saved as
   `candidates/<slug>/outreach/<company>-<role>-recruiter.md`.
3. **Referral ask** (optional) — if the candidate knows someone at the company
   (LinkedIn 1st/2nd-degree), a message they can forward.

Each draft ends with a status line: `STATUS: awaiting approval`.

## Approval flow

- Present the draft in chat with the role, company, and why it scored high.
- Candidate replies yes / edits / no. On yes: mark
  `STATUS: approved <date>` and log it.
- Sending happens through the candidate's own action where the platform
  requires it (Easy Apply, LinkedIn message). Where the agent CAN send
  (email via gmail skill), it still shows the exact text first and sends only
  after explicit approval of that text.
- A "yes to all above 80" standing instruction is never accepted as approval.
  Say so plainly, once.

## Tone rules

- Short. No "I hope this message finds you well".
- One concrete proof point from the candidate's real history per message.
- Never invent experience, titles, or metrics. If the CV doesn't support a
  claim, the draft doesn't make it — flag the gap to the candidate instead
  ("this role wants X, you don't show X — want to address it?").
- Follow-ups: one polite bump after 7 days of silence, then stop. Never
  double-bump.

## Templates

### Recruiter message
```
Hi {name} — saw the {role} opening at {company}. {one-line why: e.g. "I've
shipped production multi-agent systems for two years, most recently {proof}."}
Worth a 15-min chat? {link: LinkedIn/portfolio}
— {candidate}
```

### Hiring manager message
Same skeleton, but lead with the problem their team owns (from the JD), not
with the candidate's biography.

### Referral ask
```
Hey {name} — noticed {company} is hiring for {role} and it lines up with what
I do ({proof}). Any chance you'd be open to referring me? Happy to send over
a blurb. No worries at all if not.
```
