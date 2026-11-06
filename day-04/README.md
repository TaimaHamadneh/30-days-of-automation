# Day 04 – Morning Briefing Bot (3 APIs → 1 daily briefing)

Part of my **#30DaysOfAutomation** challenge.

## The problem
Every morning I open 3–4 apps: weather, prayer times, and the dollar rate. That's small, but it happens every single day.

## The solution
A Python bot that calls **3 free APIs**, combines the answers, adds a smart tip, and saves one short briefing file per day.

```
Open-Meteo  (weather)       ┐
Aladhan     (prayer times)  ├──► morning_briefing.py ──► briefings/2026-11-07.md
Frankfurter (exchange rate) ┘
```

## Example output
```
# Good morning! Briefing for Hebron
Saturday, 06 November 2026

## Weather
12°C – 22°C · Rain chance: 65% · Wind: 14 km/h
→ Rain likely today, take an umbrella ☔

## Prayer times
Fajr 04:41 · Dhuhr 11:28 · Asr 14:30 · Maghrib 16:52 · Isha 18:10

## Money
1 USD = 3.711 ILS (▲ 0.30% since the day before)
1 EUR = 4.261 ILS
```

## Features
- **3 APIs combined** into one result
- **Fails gracefully**: if one API is down, the briefing is still written, with "not available" for that part
- **Smart tip** based on the data (rain, cold, heat, wind)
- Timeout on every request
- Same day = same file, so no duplicates
- Settings (city, coordinates, currencies) at the top of the file


## Tech used
Python 3 · `requests` · `pathlib` · `datetime` · [Open-Meteo](https://open-meteo.com) · [Aladhan](https://aladhan.com/prayer-times-api) · [Frankfurter](https://frankfurter.dev) 

## How to run
```bash
pip install -r requirements.txt
python3 morning_briefing.py
```


## Result
<img width="502" height="244" alt="Screenshot 2026-11-07 at 12 47 07 AM" src="https://github.com/user-attachments/assets/c263a8a7-4441-491e-8482-fa59de658f7e" />

## What I learned
- How to read nested JSON (`data["daily"]["temperature_2m_max"][0]`)
- One helper function for all API calls keeps the code clean
- Real automation must expect failures: APIs go down, networks drop

