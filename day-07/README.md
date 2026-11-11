
# Day 07 – Job Radar Bot 🎯

Part of my **#30DaysOfAutomation** challenge. This is the Week 1 project: it combines everything I built in Days 1–6.

## The problem
I'm looking for an automation job. Checking job boards every day takes time, most jobs don't match my skills, and I keep seeing the same posts again.

## The solution
A bot that runs **every morning at 9:00**, collects jobs from **3 free job APIs**, keeps only the ones that match my skills, skips jobs it already showed me, and sends the best 5 to my **Telegram**. Every match is also saved to an **Excel tracker** where I mark what I applied to.

```
09:00 launchd ──► job_radar.py
                    │
   Remotive  ───────┤
   Arbeitnow ───────┼──► normalize ──► filter + score ──► skip seen ──► top 5
   Jobicy    ───────┘                                                    │
                                              ┌──────────────────────────┤
                                              ▼                          ▼
                                       📱 Telegram              job_tracker.xlsx
```

## First real run
```
Collecting jobs...
  Remotive: 13 jobs
  Arbeitnow: 900 jobs
  Jobicy: 50 jobs
Checked 856 jobs · ... new matches
Telegram message sent successfully!
```
From **856 jobs**, only a few matched my filters. That's the point: the bot reads everything so I only look at what's relevant.

## How it works
| Step | What happens |
| --- | --- |
| **Collect** | One fetch function per API. Arbeitnow is paginated (3 pages) |
| **Normalize** | Each API returns a different JSON shape. One function per source turns every job into the same format: `id, source, title, company, location, remote, tags, url, date` |
| **Filter** | Remote only, posted in the last 14 days, no senior/lead/director roles |
| **Score** | +2 for each keyword in the title, +1 for each keyword in the tags. Whole-word matching, so "rpa" doesn't match inside another word |
| **Remember** | `seen_jobs.json` stores jobs already sent, so I never get the same job twice |
| **Send** | Top 5 to Telegram, each with "via Remotive / Arbeitnow / Jobicy" |
| **Track** | Every match goes into `job_tracker.xlsx`, with a Status column I fill in ("Applied", "Interview"). The bot keeps my notes on every run |

## What makes it reliable
- **One source down ≠ no message.** If an API fails, the others still work, and the message says "⚠️ Unavailable today: …"
- **No lost jobs.** `seen_jobs.json` is updated only after Telegram confirms delivery. Matches that weren't in the top 5 stay available for the next days
- **Respectful of the sources:** one run per day, timeouts, a pause between pages, and credit to each job board
- **Crash alerts** to Telegram, so it never fails silently
- `--dry-run` mode to preview the message without sending or saving anything

## Settings
At the top of `job_radar.py`:
```python
KEYWORDS = ["automation", "rpa", "uipath", "n8n", "python", "integration", "ai agent", "workflow", ...]
EXCLUDE = ["senior", "lead", "principal", "staff", "head of", "director", "10+ years"]
REMOTE_ONLY = True
MAX_AGE_DAYS = 14
TOP_N = 5
```

## How to run
```bash
pip install -r requirements.txt
python3 job_radar.py --dry-run   # preview only
python3 job_radar.py             # send to Telegram
```
Needs `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`, and `notify.py` from [Day 6](../day-06).

**Schedule it every day at 9:00 (macOS):**
```bash
cp com.taima.jobradar.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.taima.jobradar.plist
launchctl start com.taima.jobradar    # test now
```

## Tech used
Python 3 · `requests` · `pandas` · `openpyxl` · Telegram Bot API · macOS `launchd`
Job data from [Remotive](https://remotive.com), [Arbeitnow](https://www.arbeitnow.com) and [Jobicy](https://jobicy.com).

## Result

<img width="545" height="1648" alt="WhatsApp Image 2026-11-11 at 6 47 04 PM" src="https://github.com/user-attachments/assets/c098828e-85f7-4bb8-9664-5834a80bad57" />


## What I learned
- **Normalizing data** from different APIs into one format is most of the work in integration projects. After that, the filter, score and send logic doesn't care where a job came from
- Simple keyword matching needs care: "ai" also matches "email", so whole-word matching matters
- Save state only after success, so a failure never hides data
- Respect free APIs: one request a day is enough, and they ask for credit

## Week 1 skills used
| Day | Skill | Used for |
| --- | --- | --- |
| 2 | files, logging | `seen_jobs.json`, logs |
| 3 | pandas + Excel | the job tracker |
| 4 | REST APIs + JSON | 3 job APIs |
| 5 | scraping ethics | official APIs instead of scraping LinkedIn |
| 6 | Telegram + launchd | daily message at 9:00 |
