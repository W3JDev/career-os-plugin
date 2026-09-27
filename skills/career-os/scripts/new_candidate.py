#!/usr/bin/env python3
"""Scaffold a new candidate folder from intake answers.

Usage:
  python3 new_candidate.py --name "Aisha Rahman" --slug aisha \
      --roles "AI Engineer,Backend Engineer" --skills "Python,LLMs,FastAPI" \
      --work-mode remote --locations "Kuala Lumpur" --seniority senior
"""
import argparse, os, re

TEMPLATE = """# Candidate profile — {name}
name: {name}
email: {email}
phone: {phone}
linkedin: {linkedin}
github: {github}
portfolio: {portfolio}
location: {location}
work_authorization: {auth}

seniority: {seniority}
target_roles:
{roles}
skills:
{skills}
experience_summary: |
  {summary}
target_comp_min: {comp_min}
notice_period: {notice}

preferences:
  work_mode: {work_mode}   # remote | hybrid | onsite | any
  locations:
{locations}
  alert_threshold: 75      # ping me when a match scores >= this

deal_breakers:
{deal_breakers}

notes: |
  {notes}
"""


def main():
    ap = argparse.ArgumentParser()
    for f in ["name", "slug", "email", "phone", "linkedin", "github",
              "portfolio", "location", "auth", "seniority", "roles",
              "skills", "summary", "comp_min", "notice", "work_mode",
              "locations", "deal_breakers", "notes"]:
        ap.add_argument("--" + f.replace("_", "-"), default="")
    args = ap.parse_args()
    d = vars(args)

    slug = d["slug"] or re.sub(r"[^a-z0-9]+", "-", d["name"].lower()).strip("-")
    cdir = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "candidates", slug)
    os.makedirs(os.path.join(cdir, "outreach"), exist_ok=True)

    def lst(key):
        items = [x.strip() for x in d[key].split(",") if x.strip()]
        return "\n".join(f"  - {x}" for x in items) if items else "  - TBD"

    content = TEMPLATE.format(
        name=d["name"] or "TBD", email=d["email"] or "TBD",
        phone=d["phone"] or "TBD", linkedin=d["linkedin"] or "",
        github=d["github"] or "", portfolio=d["portfolio"] or "",
        location=d["location"] or "TBD", auth=d["auth"] or "TBD",
        seniority=d["seniority"] or "TBD", roles=lst("roles"),
        skills=lst("skills"), summary=d["summary"] or "TBD — fill from conversation",
        comp_min=d["comp_min"] or "TBD", notice=d["notice"] or "TBD",
        work_mode=d["work_mode"] or "any", locations=lst("locations"),
        deal_breakers=lst("deal_breakers"), notes=d["notes"] or "")
    with open(os.path.join(cdir, "profile.yml"), "w") as f:
        f.write(content)
    with open(os.path.join(cdir, "cv.md"), "w") as f:
        f.write(f"# CV — {d['name'] or 'TBD'}\n\n_Built from intake conversation. Expand me._\n")
    with open(os.path.join(cdir, "log.md"), "w") as f:
        f.write(f"# Log — {d['name'] or 'TBD'}\n\n")
    print("candidate folder:", cdir)


if __name__ == "__main__":
    main()
