"""
Day 4 - #30DaysOfAutomation
Morning Briefing Bot: calls 3 free APIs and writes one short daily briefing.

  Weather       -> Open-Meteo   (https://open-meteo.com)
  Prayer times  -> Aladhan      (https://aladhan.com/prayer-times-api)
  Exchange rate -> Frankfurter  (https://frankfurter.dev)

If one API fails, the briefing is still written, with "not available" for that part.

"""
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

# ---------------- Settings: change these ----------------
CITY = "Nablus"
COUNTRY = "Palestine"
LAT, LON = 32.22, 35.26
TIMEZONE = "Asia/Hebron"
CURRENCIES = ["ILS", "EUR"]          # USD -> ILS is the main one; EUR -> ILS is calculated
PRAYER_METHOD = None            
GITHUB_REPO = "TaimaHamadneh/30-days-of-automation"  

BASE_DIR = Path(__file__).parent
OUT_DIR = BASE_DIR / "briefings"
TIMEOUT = 10

# ---------------- One small helper for every API call ----------------
def get_json(url:str, params:dict = None, headers: dict = None):
    """Return the JSON, or None if anything goes wrong (no internet, 404, 500, bad JSON...)."""
    try:
        response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        print(f"  ! API problem with {url}: {error}")
        return None

#---------------- 1. Weather ----------------
def get_weather():
    data = get_json("https://api.open-meteo.com/v1/forecast", params={
        "latitude": LAT,
        "longitude": LON,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max",
        "timezone": TIMEZONE,
        "forecast_days": 1,
    })
    try:
        daily = data["daily"]
        return {
            "max": round(daily["temperature_2m_max"][0]),
            "min": round(daily["temperature_2m_min"][0]),
            "rain": daily["precipitation_probability_max"][0],
            "wind": daily["wind_speed_10m_max"][0],
        }
    except (TypeError, KeyError, IndexError):
        return None

#---------------- 2. Prayer times ----------------
def get_prayer_times():
    data = {"city": CITY, "country": COUNTRY}
    if PRAYER_METHOD is not None:
        data["method"] = PRAYER_METHOD
    data = get_json("https://api.aladhan.com/v1/timingsByCity", params=data)
    try:
        timings = data["data"]["timings"]
        names = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
        return {name: timings[name].split()[0] for name in names}
    except (TypeError, KeyError):
        return None

# ---------------- 3. Exchange rates ----------------
def get_rates():
    # Time-series call: last 7 days in ONE request, so we can compare today with the day before.
    start = (date.today() - timedelta(days=7)).isoformat()
    data = get_json(f"https://api.frankfurter.dev/v1/{start}..",
                    params={"base": "USD", "symbols": ",".join(CURRENCIES)})
    try:
        days = sorted(data["rates"])
        today, before = data["rates"][days[-1]], data["rates"][days[-2]]
        return {
            "date": days[-1],
            "usd_ils": today["ILS"],
            "change": (today["ILS"] - before["ILS"]) / before["ILS"] * 100,
            "eur_ils": today["ILS"] / today["EUR"],
        }
    except (TypeError, KeyError, IndexError, ZeroDivisionError):
        return None


# ---------------- 5. Build the text ----------------
def smart_tip(w):
    if w["rain"] >= 50:
        return "Rain likely today, take an umbrella ☔"
    if w["min"] <= 10:
        return "Cold morning, wear a jacket 🧥"
    if w["max"] >= 32:
        return "Hot day, drink lots of water 💧"
    if w["wind"] >= 35:
        return "Very windy today 🌬️"
    return "Nice day, no umbrella needed ☀️"


def build_briefing(weather, prayers, rates) -> str:
    lines = [f"# Good morning! Briefing for {CITY}",
             f"{date.today():%A, %d %B %Y}", ""]

    lines.append("## Weather")
    if weather:
        lines += [f"{weather['min']}°C – {weather['max']}°C · Rain chance: {weather['rain']}% · "
                  f"Wind: {weather['wind']} km/h", f"→ {smart_tip(weather)}"]
    else:
        lines.append("Weather not available right now.")

    lines += ["", "## Prayer times"]
    lines.append(" · ".join(f"{k} {v}" for k, v in prayers.items()) if prayers
                 else "Prayer times not available right now.")

    lines += ["", "## Money"]
    if rates:
        arrow = "▲" if rates["change"] > 0 else "▼" if rates["change"] < 0 else "="
        lines += [f"1 USD = {rates['usd_ils']:.3f} ILS ({arrow} {abs(rates['change']):.2f}% since the day before)",
                  f"1 EUR = {rates['eur_ils']:.3f} ILS",
                  f"(rates from {rates['date']})"]
    else:
        lines.append("Exchange rates not available right now.")


    return "\n".join(lines) + "\n"


def main():
    print("Calling APIs...")
    weather, prayers, rates = get_weather(), get_prayer_times(), get_rates()

    text = build_briefing(weather, prayers, rates)
    OUT_DIR.mkdir(exist_ok=True)
    out_file = OUT_DIR / f"{date.today().isoformat()}.md"
    out_file.write_text(text, encoding="utf-8")   # same day = same file name = overwritten, no duplicates

    print("\n" + text)
    working = sum(x is not None for x in (weather, prayers, rates))
    print(f"Saved to briefings/{out_file.name}  ({working}/3 APIs worked)")


if __name__ == "__main__":
    main()
