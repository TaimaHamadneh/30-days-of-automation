# Day 06 – Morning Briefing to Telegram, Every Day at 7:00

Part of my **#30DaysOfAutomation** challenge.

## The problem
My Day 4 bot created a useful briefing, but I still had to open Terminal and run it myself, then open a file to read it. An automation isn't finished until it **runs by itself** and **delivers the result where I'll see it**.

## The solution
- **Notification:** the briefing is sent to my phone through a Telegram bot.
- **Schedule:** macOS `launchd` runs it every morning at 07:00, with no manual step.
- **Alerts:** if the script crashes, I get a "⚠️ Briefing failed" message instead of silence.

```
07:00 launchd ──► main.py ──► Open-Meteo + Aladhan + Frankfurter
                     │
                     ├──► briefings/2026-11-10.md   (saved first)
                     └──► Telegram Bot API ──► 📱 my phone
```

## Example message
```
☀️ Good Morning! Briefing for Nablus
📅 Tuesday, 10 November 2026

🌤 Weather
🌡 10°C – 19°C
🌧 Rain chance: 0%
💨 Wind: 11.6 km/h
💡 Cold morning, wear a jacket 🧥

🕌 Prayer Times
Fajr: 05:37 · Dhuhr: 12:06 · Asr: 15:06 · Maghrib: 17:27 · Isha: 18:36

💱 Exchange Rates
1 USD = 3.171 ILS (▼ 0.88%)
1 EUR = 3.549 ILS
```

## Files
| File | What it does |
| --- | --- |
| `notify.py` | Reusable `send_telegram(text)` function. Reads the token from `.env`, uses a timeout, checks Telegram's `"ok": true`, and never crashes the main script |
| `main.py` | Calls the 3 APIs, builds the briefing (HTML formatting for Telegram), saves it, sends it, and sends an alert if anything crashes |
| `com.taima.briefing.plist.example` | Example `launchd` job that runs `main.py` daily at 07:00 and writes logs |

## What makes it reliable
- **Save first, send second:** if Telegram is down, the briefing file is still saved
- **One API down ≠ broken briefing:** each section shows "not available" instead of crashing
- **Crash alerts** to Telegram, so failures are never silent
- **Logs** for every scheduled run (`logs/briefing.log`, `logs/briefing-error.log`)
- **Secrets stay secret:** the bot token lives in `.env`, which is in `.gitignore`

## How to run
1. Create a bot with [@BotFather](https://t.me/BotFather) and get your token and chat_id.
2. Create a `.env` file in the project root:
   ```
   TELEGRAM_TOKEN=your_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```
3. Install and test:
   ```bash
   pip install -r requirements.txt
   python3 notify.py     # sends a test message
   python3 main.py       # sends the full briefing
   ```
4. Schedule it: copy the example plist to `~/Library/LaunchAgents/com.taima.briefing.plist`, replace `YOUR_USER` with your username, then:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.taima.briefing.plist
   launchctl start com.taima.briefing    # test now instead of waiting until 7:00
   ```

## Tech used
Python 3 · `requests` · `python-dotenv` · Telegram Bot API · macOS `launchd` · Open-Meteo · Aladhan · Frankfurter

## Result

<img width="738" height="1600" alt="WhatsApp Image 2026-11-10 at 1 50 03 AM" src="https://github.com/user-attachments/assets/c97feb8a-078b-4fd6-84aa-3e7fb9e6ecf6" />



## What I learned
- How a Telegram bot works: BotFather → token → `chat_id` → `sendMessage`
- `launchd` vs `cron`: on a Mac, launchd runs a missed job when the Mac wakes up; cron just skips it
- Scheduled jobs need **full paths**, because they don't know your venv or current folder
- macOS blocks background jobs from reading the Desktop folder ("Operation not permitted"), so I moved the project to `~/Projects`
- A notifier should be a separate, reusable module. I'll use `notify.py` in the next projects
