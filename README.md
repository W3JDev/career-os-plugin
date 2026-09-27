# Career OS — Plugin

A proactive career agent packaged as a plugin. Know every candidate, scan job
boards, score matches, draft outreach, prep interviews — both sides of the
table.

## What's inside

```
career-os-plugin/
  plugin.json                        manifest (name, version, skills, connectors, profiles)
  skills/career-os/                  the agent skill
    SKILL.md                         operating contract — your agent reads this
    references/                      job-boards, linkedin, outreach, interviewer playbooks
    scripts/                         scan.py, score.py, outreach.py, new_candidate.py
    data/boards.yml                  companies to scan (add yours — coverage compounds)
    candidates/_template/            candidate folder template
  connectors/
    job-boards.connector.json        public job-board APIs: hosts, endpoints, auth (none)
  profiles/
    candidate.template.yml           user profile template
```

## Install (2 minutes)

1. Copy `skills/career-os` into your agent workspace's skills directory.
2. Tell your agent: "read the career-os skill and onboard me as a candidate."
3. It runs intake as a conversation and saves your profile from
   `profiles/candidate.template.yml`.
4. Say "scan daily and ping me above 75" — the proactive loop starts.

No API keys. The `job-boards` connector uses only public endpoints.
LinkedIn / Wellfound / Indeed run through your own logged-in browser session
(see `skills/career-os/references/linkedin-playbook.md`).

## The one rule

Nothing ever sends without your explicit approval of that exact draft. The
agent does all the work; you make the calls.

## Share

Send this whole folder (or the zip) to anyone. Their data stays on their
machine — nothing leaves it.

MIT — by W3JDev. Fork it, improve it.
