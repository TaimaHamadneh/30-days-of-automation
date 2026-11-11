"""
Day 7 - #30DaysOfAutomation
Job Radar Bot: every morning, collect new jobs from free job APIs, keep the ones that
match my skills, skip the ones I've already seen, and send the best to Telegram.

Sources (free, no key): Remotive, Arbeitnow, Jobicy
Each one returns a different JSON shape, so every job is first "normalized" into one format.

Usage:
    python3 job_radar.py            # normal run
    python3 job_radar.py --dry-run  # print the message, don't send, don't update seen/tracker
"""

import argparse
import html
import json
import re
import sys
import time
import warnings
from datetime import date, datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")

import pandas as pd       # noqa: E402
import requests           # noqa: E402

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parent / "day-06"))   # reuse notify.py from Day 6
from notify import send_telegram                   # noqa: E402

# ---------------- Settings: change these ----------------
# Job ROLES I want, grouped (from my CV). A role word in the job TITLE = +3
ROLES = {
    "🤖 Automation & AI": [
        "automation", "rpa", "uipath", "n8n", "power automate", "zapier", "workflow",
        "integration", "ai agent", "ai engineer", "llm", "agentic", "rag",
    ],
    "💻 Software Development": [
        "full stack", "full-stack", "fullstack", "backend", "back-end", "back end",
        "frontend", "front-end", "web developer", "software engineer", "software developer",
        "appian", "low-code", "low code",
    ],
    "📈 Business & Projects": [
        "business development", "project manager", "project management", "program manager",
        "product owner", "scrum master", "proposal", "tender", "bid manager", "pre-sales",
        "presales", "solutions consultant", "partnerships",
    ],
}

# My technical SKILLS (from my CV). Skill in the TITLE = +2, in the TAGS = +1
SKILLS = [
    "python", "django", "fastapi", "c#", ".net", "asp.net", "node.js", "nodejs",
    "javascript", "typescript", "react", "next.js", "nextjs", "php", "laravel", "flutter",
    "sql", "sql server", "postgresql", "mongodb", "rest api", "git", "linux",
]

EXCLUDE = ["senior", "sr.", "lead", "principal", "staff", "head of", "director", "vp", "10+ years"]
REMOTE_ONLY = True
MAX_AGE_DAYS = 14          # ignore jobs older than this (None = no limit)
MIN_SCORE = 2              # lower = more jobs, higher = stricter
TOP_N = 8                  # how many jobs to send per day
ARBEITNOW_PAGES = 3
SOURCES = ["remotive", "arbeitnow", "jobicy"]

SEEN_FILE = BASE / "seen_jobs.json"
TRACKER_FILE = BASE / "job_tracker.xlsx"
TIMEOUT = 20
HEADERS = {"User-Agent": "JobRadarBot/1.0 (personal job search, 1 run per day)"}
SOURCE_NAMES = {"remotive": "Remotive", "arbeitnow": "Arbeitnow", "jobicy": "Jobicy"}
SOURCE_SITES = {"remotive": "remotive.com", "arbeitnow": "arbeitnow.com", "jobicy": "jobicy.com"}


# ============================================================
# 1. Fetch (one function per source)
# ============================================================
def get_json(url: str, params: dict = None):
    response = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def fetch_remotive() -> list:
    return get_json("https://remotive.com/api/remote-jobs").get("jobs", [])


def fetch_arbeitnow() -> list:
    jobs = []
    for page in range(1, ARBEITNOW_PAGES + 1):
        data = get_json("https://www.arbeitnow.com/api/job-board-api", {"page": page})
        jobs += data.get("data", [])
        if not data.get("links", {}).get("next"):
            break
        time.sleep(1)                                    # be polite between pages
    return jobs


def fetch_jobicy() -> list:
    return get_json("https://jobicy.com/api/v2/remote-jobs", {"count": 50}).get("jobs", [])


# ============================================================
# 2. Normalize: every source -> the same shape
# ============================================================
def to_date(value) -> str:
    """Accepts '2026-11-10T08:00:00', '2026-11-10 08:00:00' or a Unix timestamp -> '2026-11-10'."""
    if value in (None, ""):
        return ""
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc).date().isoformat()
    return str(value)[:10]


def clean_list(values) -> list:
    if isinstance(values, str):
        values = [values]
    return [html.unescape(str(v)).strip() for v in (values or []) if v]


def normalize_remotive(job: dict) -> dict:
    return {
        "id": f"remotive-{job.get('id')}",
        "source": "remotive",
        "title": job.get("title", "").strip(),
        "company": job.get("company_name", ""),
        "location": job.get("candidate_required_location") or "Worldwide",
        "remote": True,                                  # Remotive only lists remote jobs
        "tags": clean_list(job.get("tags")) + clean_list(job.get("category")),
        "url": job.get("url", ""),
        "date": to_date(job.get("publication_date")),
    }


def normalize_arbeitnow(job: dict) -> dict:
    return {
        "id": f"arbeitnow-{job.get('slug')}",
        "source": "arbeitnow",
        "title": job.get("title", "").strip(),
        "company": job.get("company_name", ""),
        "location": job.get("location", ""),
        "remote": bool(job.get("remote")),
        "tags": clean_list(job.get("tags")) + clean_list(job.get("job_types")),
        "url": job.get("url", ""),
        "date": to_date(job.get("created_at")),
    }


def normalize_jobicy(job: dict) -> dict:
    return {
        "id": f"jobicy-{job.get('id')}",
        "source": "jobicy",
        "title": html.unescape(job.get("jobTitle", "")).strip(),
        "company": job.get("companyName", ""),
        "location": job.get("jobGeo") or "Worldwide",
        "remote": True,                                  # Jobicy only lists remote jobs
        "tags": clean_list(job.get("jobIndustry")) + clean_list(job.get("jobType")),
        "url": job.get("url", ""),
        "date": to_date(job.get("pubDate")),
    }


FETCHERS = {
    "remotive": (fetch_remotive, normalize_remotive),
    "arbeitnow": (fetch_arbeitnow, normalize_arbeitnow),
    "jobicy": (fetch_jobicy, normalize_jobicy),
}


def collect_jobs():
    """Return (all normalized jobs, list of sources that failed). One failing source never stops the rest."""
    jobs, failed = [], []
    for name in SOURCES:
        fetch, normalize = FETCHERS[name]
        try:
            raw = fetch()
            normalized = [normalize(j) for j in raw]
            jobs += [j for j in normalized if j["title"] and j["url"]]
            print(f"  {SOURCE_NAMES[name]}: {len(raw)} jobs")
        except (requests.RequestException, ValueError, AttributeError) as error:
            print(f"  ! {SOURCE_NAMES[name]} failed: {error}")
            failed.append(name)
    return jobs, failed


# ============================================================
# 3. Filter + score
# ============================================================
def contains(text: str, word: str) -> bool:
    """Whole-word, case-insensitive match: 'rpa' matches 'RPA Developer' but not 'Sharpaxe'."""
    return re.search(rf"(?<![a-z0-9]){re.escape(word.lower())}(?![a-z0-9])", text) is not None


def score_job(job: dict) -> int:
    """
    0 = not a match. Otherwise:
      role word in title +3, in tags +1 · skill in title +2, in tags +1
    The job must have at least one role or skill IN THE TITLE, so a random job with
    'python' hidden in its tags doesn't make the list.
    Also fills job["category"] and job["matched"] for the message and the tracker.
    """
    title = job["title"].lower()
    tags = " ".join(job["tags"]).lower()
    job["category"], job["matched"] = "", []

    if any(contains(title, word) for word in EXCLUDE):
        return 0
    if REMOTE_ONLY and not job["remote"]:
        return 0
    if MAX_AGE_DAYS and job["date"]:
        try:
            if (date.today() - date.fromisoformat(job["date"])).days > MAX_AGE_DAYS:
                return 0
        except ValueError:
            pass

    score, in_title, best = 0, False, {}
    for group, words in ROLES.items():
        for word in words:
            if contains(title, word):
                score += 3
                in_title = True
                best[group] = best.get(group, 0) + 3
                job["matched"].append(word)
            elif contains(tags, word):
                score += 1
                best[group] = best.get(group, 0) + 1
                job["matched"].append(word)
    for word in SKILLS:
        if contains(title, word):
            score += 2
            in_title = True
            job["matched"].append(word)
        elif contains(tags, word):
            score += 1
            job["matched"].append(word)

    if not in_title or score < MIN_SCORE:
        return 0
    job["category"] = max(best, key=best.get) if best else "💻 Software Development"
    return score


# ============================================================
# 4. Memory (seen_jobs.json) + Excel tracker
# ============================================================
def load_seen() -> set:
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
    return set()


def save_seen(seen: set) -> None:
    SEEN_FILE.write_text(json.dumps(sorted(seen), indent=0), encoding="utf-8")


def update_tracker(matches: list) -> int:
    """Add new matches to job_tracker.xlsx. Old rows (and the Status you typed) are kept."""
    columns = ["id", "date_found", "score", "category", "title", "company", "matched",
               "location", "source", "url", "status"]
    new = pd.DataFrame([{
        "id": j["id"], "date_found": date.today().isoformat(), "score": j["score"],
        "category": j["category"][2:].strip(), "title": j["title"], "company": j["company"],
        "matched": ", ".join(j["matched"]), "location": j["location"],
        "source": SOURCE_NAMES[j["source"]], "url": j["url"], "status": "",
    } for j in matches], columns=columns)

    if TRACKER_FILE.exists():
        old = pd.read_excel(TRACKER_FILE, dtype={"status": str}).fillna("")
        old = old.reindex(columns=columns, fill_value="")   # older trackers had fewer columns
        new = new[~new["id"].isin(old["id"])]            # never add the same job twice
        table = pd.concat([old, new], ignore_index=True)
    else:
        table = new

    table = table.sort_values(["date_found", "score"], ascending=[False, False])
    with pd.ExcelWriter(TRACKER_FILE, engine="openpyxl") as writer:
        table.to_excel(writer, index=False, sheet_name="Jobs")
        sheet = writer.sheets["Jobs"]
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for col, width in zip("ABCDEFGHIJK", [26, 12, 7, 22, 45, 25, 30, 20, 11, 50, 14]):
            sheet.column_dimensions[col].width = width
    return len(new)


# ============================================================
# 5. Telegram message
# ============================================================
def build_messages(top: list, total_checked: int, total_matches: int, failed: list) -> list:
    e = html.escape
    today = date.today().strftime("%d %b %Y")
    header = f"🎯 <b>Job Radar · {today}</b>\n"

    if top:
        header += f"{total_matches} new matches, showing the top {len(top)} (checked {total_checked} jobs)"
    else:
        header += f"No new matching jobs today (checked {total_checked} jobs)."
    if failed:
        header += "\n⚠️ Unavailable today: " + ", ".join(SOURCE_NAMES[s] for s in failed)

    blocks = [header]
    for i, j in enumerate(top, 1):
        loc = j["location"] if j["location"].lower() not in ("", "remote") else ""
        place = "🌍 Remote" + (f", {e(loc)}" if loc else "")
        blocks.append(
            f"{i}. <b>{e(j['title'])}</b> · {e(j['company'])}\n"
            f"   {place} · score {j['score']}\n"
            f"   {j['category']} · matched: {e(', '.join(j['matched'][:5]))}\n"
            f"   {e(j['url'])}\n"
            f"   via {SOURCE_NAMES[j['source']]} ({SOURCE_SITES[j['source']]})"
        )

    # Split into messages under Telegram's 4,096-character limit, never inside a job
    messages, current = [], ""
    for block in blocks:
        if current and len(current) + len(block) + 2 > 4000:
            messages.append(current)
            current = block
        else:
            current = f"{current}\n\n{block}" if current else block
    messages.append(current)
    return messages


# ============================================================
# Main
# ============================================================
def main() -> None:
    parser = argparse.ArgumentParser(description="Job Radar Bot")
    parser.add_argument("--dry-run", action="store_true", help="Print only: don't send or save")
    args = parser.parse_args()

    print("Collecting jobs...")
    jobs, failed = collect_jobs()

    # Same job can appear twice in one source: keep the first
    unique = {j["id"]: j for j in reversed(jobs)}
    jobs = list(unique.values())

    seen = load_seen()
    matches = []
    for job in jobs:
        if job["id"] in seen:
            continue
        job["score"] = score_job(job)
        if job["score"] > 0:
            matches.append(job)
    matches.sort(key=lambda j: (j["score"], j["date"]), reverse=True)
    top = matches[:TOP_N]
    print(f"Checked {len(jobs)} jobs · {len(matches)} new matches · sending {len(top)}")

    messages = build_messages(top, len(jobs), len(matches), failed)

    if args.dry_run:
        print("\n----- DRY RUN: message preview -----\n")
        print("\n\n".join(re.sub(r"</?b>", "", m) for m in messages))
        return

    sent = all(send_telegram(m, parse_mode="HTML") for m in messages)

    if sent:
        save_seen(seen | {j["id"] for j in top})        # only jobs you actually received
        added = update_tracker(matches) if matches else 0
        print(f"Sent. seen_jobs.json updated. {added} new rows in {TRACKER_FILE.name}")
    else:
        print("Telegram failed: seen_jobs.json NOT updated, so no job is lost.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:                          # never fail silently
        print(f"Job Radar crashed: {error}")
        if "--dry-run" not in sys.argv:
            send_telegram(f"⚠️ Job Radar failed: {html.escape(str(error))}", parse_mode="HTML")
        raise
