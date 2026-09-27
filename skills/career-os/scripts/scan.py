#!/usr/bin/env python3
"""Career OS scanner — pull fresh postings from public boards, no auth needed.

Usage:
  python3 scan.py --boards data/boards.yml --out /tmp/jobs.json
  python3 scan.py --boards data/boards.yml --query "ai engineer" --remote-only --out /tmp/jobs.json

Reads data/boards.yml for configured company ATS tokens, plus always-on
aggregators (RemoteOK, We Work Remotely, HN hiring). Emits a JSON list of jobs.
"""
import argparse, json, re, sys, time, html
import urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}


def fetch(url, method="GET", data=None, timeout=20):
    req = urllib.request.Request(url, data=data, method=method, headers=UA)
    if data:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def norm(text):
    return html.unescape(re.sub(r"<[^>]+>", " ", text or "")).strip()


def greenhouse(token, company):
    jobs = []
    try:
        data = json.loads(fetch(
            f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=false"))
        for j in data.get("jobs", []):
            loc = (j.get("location") or {}).get("name", "")
            jobs.append({
                "source": "greenhouse", "company": company,
                "title": j.get("title", ""), "location": loc,
                "url": j.get("absolute_url", ""),
                "description": "", "posted_at": "",
                "remote": "remote" in loc.lower(),
            })
    except Exception as e:
        print(f"[warn] greenhouse/{token}: {e}", file=sys.stderr)
    return jobs


def lever(token, company):
    jobs = []
    try:
        data = json.loads(fetch(f"https://api.lever.co/v0/postings/{token}"))
        for j in data:
            cats = j.get("categories") or {}
            loc = cats.get("location", "")
            jobs.append({
                "source": "lever", "company": company,
                "title": j.get("text", ""), "location": loc,
                "url": j.get("hostedUrl") or j.get("applyUrl", ""),
                "description": norm(j.get("description", ""))[:4000],
                "posted_at": "",
                "remote": "remote" in loc.lower(),
            })
    except Exception as e:
        print(f"[warn] lever/{token}: {e}", file=sys.stderr)
    return jobs


def ashby(board, company):
    jobs = []
    try:
        data = json.loads(fetch(
            f"https://api.ashbyhq.com/posting-api/job-board/{board}",
            method="POST", data=b"{}"))
        for j in data.get("jobs", []):
            loc = j.get("locationName", "")
            jobs.append({
                "source": "ashby", "company": company,
                "title": j.get("title", ""), "location": loc,
                "url": j.get("jobUrl", ""),
                "description": "", "posted_at": "",
                "remote": "remote" in loc.lower(),
            })
    except Exception as e:
        print(f"[warn] ashby/{board}: {e}", file=sys.stderr)
    return jobs


def remoteok(query="", remote_only=False):
    jobs = []
    try:
        data = json.loads(fetch("https://remoteok.com/api"))
        for j in data[1:]:  # index 0 is the legal notice
            title = j.get("position", "")
            tags = " ".join(j.get("tags", [])).lower()
            blob = f"{title} {tags} {j.get('description','')}".lower()
            if query and query.lower() not in blob:
                continue
            jobs.append({
                "source": "remoteok", "company": j.get("company", ""),
                "title": title, "location": "Remote",
                "url": j.get("url", ""),
                "description": norm(j.get("description", ""))[:4000],
                "posted_at": datetime.fromtimestamp(
                    j.get("epoch", 0), tz=timezone.utc).isoformat(),
                "remote": True,
            })
    except Exception as e:
        print(f"[warn] remoteok: {e}", file=sys.stderr)
    return jobs


def wwr_rss(query=""):
    jobs = []
    feeds = [
        "remote-programming-jobs", "remote-devops-sysadmin-jobs",
        "remote-product-jobs", "remote-design-jobs",
        "remote-customer-support-jobs",
    ]
    for feed in feeds:
        try:
            xml = fetch(f"https://weworkremotely.com/categories/{feed}.rss")
            for item in ET.fromstring(xml).iter("item"):
                title = item.findtext("title") or ""
                link = item.findtext("link") or ""
                desc = norm(item.findtext("description") or "")[:4000]
                blob = f"{title} {desc}".lower()
                if query and query.lower() not in blob:
                    continue
                m = re.match(r"(.*?):\s*(.*)", title)
                company, role = (m.group(1), m.group(2)) if m else ("", title)
                jobs.append({
                    "source": "weworkremotely", "company": company.strip(),
                    "title": role.strip(), "location": "Remote", "url": link,
                    "description": desc, "posted_at": item.findtext("pubDate") or "",
                    "remote": True,
                })
        except Exception as e:
            print(f"[warn] wwr/{feed}: {e}", file=sys.stderr)
    return jobs


def load_boards(path):
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f) or []
    except ImportError:
        # minimal YAML subset fallback: list of {name, greenhouse/lever/ashby}
        boards, cur = [], {}
        with open(path) as f:
            for line in f:
                line = line.rstrip()
                if line.startswith("- name:"):
                    if cur: boards.append(cur)
                    cur = {"name": line.split(":", 1)[1].strip()}
                elif ":" in line and cur is not None:
                    k, v = line.strip().split(":", 1)
                    cur[k.strip()] = v.strip()
        if cur: boards.append(cur)
        return boards
    except FileNotFoundError:
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boards", default="data/boards.yml")
    ap.add_argument("--query", default="")
    ap.add_argument("--remote-only", action="store_true")
    ap.add_argument("--no-aggregators", action="store_true")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    all_jobs = []
    for b in load_boards(args.boards):
        name = b.get("name", "?")
        if b.get("greenhouse"):
            all_jobs += greenhouse(b["greenhouse"], name); time.sleep(1)
        if b.get("lever"):
            all_jobs += lever(b["lever"], name); time.sleep(1)
        if b.get("ashby"):
            all_jobs += ashby(b["ashby"], name); time.sleep(1)

    if not args.no_aggregators:
        all_jobs += remoteok(args.query, args.remote_only)
        all_jobs += wwr_rss(args.query)

    if args.query:
        q = args.query.lower()
        all_jobs = [j for j in all_jobs
                    if q in f"{j['title']} {j['description']}".lower()]
    if args.remote_only:
        all_jobs = [j for j in all_jobs if j["remote"]]

    # dedup on (company, title, location)
    seen, uniq = set(), []
    for j in all_jobs:
        key = (j["company"].lower(), j["title"].lower(), j["location"].lower())
        if key not in seen:
            seen.add(key); uniq.append(j)

    out = json.dumps(uniq, indent=1, ensure_ascii=False)
    if args.out:
        with open(args.out, "w") as f:
            f.write(out)
        print(f"{len(uniq)} jobs -> {args.out}")
    else:
        print(out)


if __name__ == "__main__":
    main()
