#!/usr/bin/env python3
"""Career OS scorer — score job postings against a candidate profile.

Usage:
  python3 score.py --profile candidates/jewel/profile.yml --jobs /tmp/jobs.json \
      --out candidates/jewel/matches.json --threshold 75

Scoring (0-100), weighted:
  role fit ......... 30   title/keywords vs target roles
  skills ........... 25   required skills present in candidate skills
  seniority ........ 15   level alignment (junior/mid/senior/staff)
  location ......... 15   remote/onsite/hybrid + authorized locations
  comp signal ...... 10   salary mentioned and in range (often unknown -> neutral)
  company quality ..  5   funding/reputation signals in description

Prints top matches; writes full ranked list to --out.
"""
import argparse, json, re, sys

ROLE_SYNONYMS = {
    "ai engineer": ["ai engineer", "ml engineer", "machine learning engineer",
                    "applied ai", "llm engineer", "genai engineer", "ai developer"],
    "backend engineer": ["backend", "back-end", "server engineer", "api engineer"],
    "full stack": ["full stack", "fullstack", "full-stack"],
    "devops": ["devops", "sre", "platform engineer", "infrastructure"],
    "agent engineer": ["agent", "multi-agent", "agentic"],
}

SENIORITY_ORDER = ["intern", "junior", "mid", "senior", "staff", "principal",
                   "lead", "manager", "director", "head", "vp"]


def load_profile(path):
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        # naive subset parser for simple key: value / lists
        prof, key, lst = {}, None, None
        with open(path) as f:
            for line in f:
                if re.match(r"^\w[\w ]*:", line):
                    k, v = line.split(":", 1)
                    key, lst = k.strip(), None
                    v = v.strip()
                    if v:
                        prof[key] = v
                    else:
                        prof[key] = []; lst = prof[key]
                elif line.startswith(("  - ", "    - ")) and lst is not None:
                    lst.append(line.split("-", 1)[1].strip().strip("'\""))
                elif line.startswith("  ") and key and lst is None:
                    prof[key] = (str(prof.get(key, "")) + " " + line.strip()).strip()
        return prof


def blob(job):
    return f"{job.get('title','')} {job.get('description','')} {job.get('company','')}".lower()


def role_score(job, targets):
    b = blob(job)
    best = 0
    for t in targets:
        t = str(t).lower()
        terms = ROLE_SYNONYMS.get(t, [t])
        hits = sum(1 for term in terms if term in b)
        best = max(best, min(1.0, hits / max(1, len(terms) * 0.5)))
    return best


def skills_score(job, skills):
    b = blob(job)
    skills = [str(s).lower() for s in skills]
    if not skills:
        return 0.5
    hits = sum(1 for s in skills if s.lower() in b)
    # diminishing returns: matching 6+ skills is plenty
    return min(1.0, hits / 6)


def seniority_score(job, target_level):
    b = blob(job)
    if not target_level:
        return 0.7
    t = str(target_level).lower()
    t_idx = next((i for i, s in enumerate(SENIORITY_ORDER) if s in t),
                 len(SENIORITY_ORDER) // 2)
    j_idx = next((i for i, s in enumerate(SENIORITY_ORDER) if s in b), None)
    if j_idx is None:
        return 0.7  # no level stated -> neutral
    diff = abs(t_idx - j_idx)
    return max(0.0, 1.0 - diff * 0.3)


def location_score(job, prefs):
    work = str(prefs.get("work_mode", "any")).lower()
    locs = [str(x).lower() for x in prefs.get("locations", [])]
    job_loc = f"{job.get('location','')}".lower()
    is_remote = job.get("remote") or "remote" in job_loc
    if work == "remote":
        return 1.0 if is_remote else 0.1
    if work == "onsite":
        if is_remote:
            return 0.3
        return 1.0 if any(l in job_loc for l in locs) else 0.2
    # hybrid / any
    if is_remote:
        return 1.0
    if any(l in job_loc for l in locs):
        return 1.0
    return 0.5


def comp_score(job, prefs):
    b = blob(job)
    m = re.search(r"\$[\d,]+", b)
    if not m:
        return 0.6  # unknown -> neutral
    nums = [int(n.replace(",", "")) for n in re.findall(r"\$([\d,]+)", b)][:2]
    if not nums:
        return 0.6
    low = min(nums)
    target = prefs.get("target_comp_min")
    try:
        target = int(str(target).replace(",", "").replace("$", ""))
    except (TypeError, ValueError):
        return 0.6
    if low >= target:
        return 1.0
    if low >= target * 0.8:
        return 0.6
    return 0.2


def company_score(job):
    b = blob(job)
    s = 0.5
    for kw in ["series a", "series b", "series c", "funded", "yc ", "y combinator",
               "unicorn", "public"]:
        if kw in b:
            s += 0.1
    return min(1.0, s)


WEIGHTS = {"role": 30, "skills": 25, "seniority": 15,
           "location": 15, "comp": 10, "company": 5}


def score_job(job, prof):
    prefs = prof.get("preferences", prof)
    parts = {
        "role": role_score(job, prof.get("target_roles", [])),
        "skills": skills_score(job, prof.get("skills", [])),
        "seniority": seniority_score(job, prof.get("seniority", "")),
        "location": location_score(job, prefs),
        "comp": comp_score(job, prefs),
        "company": company_score(job),
    }
    total = round(sum(parts[k] * WEIGHTS[k] for k in parts), 1)
    # hard deal-breakers zero it out
    for bad in prof.get("deal_breakers", []) or []:
        if str(bad).lower() in blob(job):
            total = 0.0
            parts["deal_breaker"] = str(bad)
            break
    return total, parts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True)
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--threshold", type=float, default=75)
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()

    prof = load_profile(args.profile)
    with open(args.jobs) as f:
        jobs = json.load(f)

    ranked = []
    for j in jobs:
        total, parts = score_job(j, prof)
        ranked.append({**j, "score": total, "score_parts": parts})
    ranked.sort(key=lambda x: x["score"], reverse=True)

    if args.out:
        with open(args.out, "w") as f:
            json.dump(ranked, f, indent=1, ensure_ascii=False)

    hits = [r for r in ranked if r["score"] >= args.threshold][:args.top]
    print(f"scored {len(ranked)} jobs, {len(hits)} above {args.threshold}")
    for r in hits:
        print(f"{r['score']:5.1f}  {r['title'][:60]:62} @ {r['company'][:30]}")


if __name__ == "__main__":
    main()
