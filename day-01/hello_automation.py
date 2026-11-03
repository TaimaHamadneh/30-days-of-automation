"""
Day 1 - #30DaysOfAutomation
My first automation: a script that runs on a schedule and logs the time.

It is simple on purpose. The idea is the same one behind every real bot:
a TRIGGER (a schedule) starts a TASK (here: writing a log line) with no human clicking anything.

Usage:
    python3 hello_automation.py              # run once
    python3 hello_automation.py --every 10   # run every 10 seconds (Ctrl + C to stop)
"""

import argparse
import time
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent / "automation_log.txt"


def task() -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{now}  Hello! The bot ran by itself."
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)


def main() -> None:
    parser = argparse.ArgumentParser(description="My first scheduled automation.")
    parser.add_argument("--every", type=int, help="Repeat every N seconds")
    args = parser.parse_args()

    if args.every:
        print(f"Running every {args.every} seconds. Press Ctrl + C to stop.")
        runs = 0
        try:
            while True:
                task()
                runs += 1
                time.sleep(args.every)
        except KeyboardInterrupt:
            print(f"\nStopped after {runs} runs. Check {LOG_FILE.name}")
    else:
        task()


if __name__ == "__main__":
    main()
