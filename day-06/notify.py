import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(text, parse_mode=None):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: Telegram credentials are missing from .env")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }

    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=10
        )

        data = response.json()

        if data.get("ok") is True:
            print("Telegram message sent successfully!")
            return True

        print(f"Telegram API Error: {data}")
        return False

    except requests.exceptions.Timeout:
        print("Error: Telegram request timed out.")
        return False

    except requests.exceptions.RequestException as error:
        print(f"Network Error: {error}")
        return False

    except ValueError:
        print("Error: Telegram returned an invalid response.")
        return False

if __name__ == "__main__":
    send_telegram("✅ Test from my automation bot")