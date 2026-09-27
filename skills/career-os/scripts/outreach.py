#!/usr/bin/env python3
"""Career OS outreach — build the draft queue for top matches.

Usage:
  python3 outreach.py --candidate candidates/jewel --top 5

Reads <candidate>/matches.json + profile.yml, writes one draft file per match
into <candidate>/outreach/. Drafts are NEVER sent — STATUS: awaiting approval.
"""
import argparse, json, os, re, sys
from datetime import date


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def load_profile(path):
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        return {}


def proof_point(prof):
    exp = prof.get("experience_summary", "") or ""
    sents = re.split(r"(?<=[.!])\s+", exp.strip())
    return sents[0] if sents and sents[0] else "relevant hands-on experience"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--top", type=int, default=5)
    args = ap.parse_args()

    cdir = args.candidate
    prof = load_profile(os.path.join(cdir, "profile.yml"))
    with open(os.path.join(cdir, "matches.json")) as f:
        matches = json.load(f)
    matches = [m for m in matches if m.get("score", 0) > 0][:args.top]

    name = prof.get("name", "there")
    outdir = os.path.join(cdir, "outreach")
    os.makedirs(outdir, exist_ok=True)
    proof = proof_point(prof)
    links = " ".join(filter(None, [
        prof.get("linkedin", ""), prof.get("portfolio", ""), prof.get("github", "")]))

    for m in matches:
        company, role = m.get("company", "?"), m.get("title", "?")
        base = f"{slug(company)}-{slug(role)}"
        why = "; ".join(
            f"{k} {v * 100:.0f}%" for k, v in
            sorted(m.get("score_parts", {}).items(),
                   key=lambda x: -x[1])[:3] if isinstance(v, float))

        app = f"""# Application draft — {role} @ {company}
Score: {m.get('score')} ({why})
Posting: {m.get('url')}
Date: {date.today().isoformat()}

## Cover note
Hi — I'm {name}. {proof[0].upper() + proof[1:] if proof else ''}

This role caught my eye because {role} at {company} lines up directly with
what I do. Happy to walk through specifics on a call.

{links}
— {name}

## Screening answers (prefill from profile; verify before sending)
- Work authorization: {prof.get('work_authorization', 'TBD')}
- Location / remote: {prof.get('preferences', {}).get('work_mode', 'TBD')}
- Notice period: {prof.get('notice_period', 'TBD')}

STATUS: awaiting approval
"""
        rec = f"""# Recruiter outreach — {role} @ {company}
Score: {m.get('score')} ({why})
Date: {date.today().isoformat()}

Hi {{recruiter name}} — saw the {role} opening at {company}. {proof[0].upper() + proof[1:] if proof else ''}

Worth a 15-min chat? {links}
— {name}

STATUS: awaiting approval
"""
        for fname, content in [(f"{base}-application.md", app),
                               (f"{base}-recruiter.md", rec)]:
            p = os.path.join(outdir, fname)
            if not os.path.exists(p):
                with open(p, "w") as f:
                    f.write(content)
                print("drafted", p)


if __name__ == "__main__":
    main()
