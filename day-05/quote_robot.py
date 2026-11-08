"""
Day 5 - #30DaysOfAutomation
Web robot with Playwright: log in, wait for a slow JavaScript page, go through
every page, collect the data, save it to Excel, and take a screenshot as proof.

Practice site: https://quotes.toscrape.com (made for learning scraping)

Usage:
    python3 quote_robot.py                 # watch the browser do it
    python3 quote_robot.py --headless      # no window (for servers)
    python3 quote_robot.py --video         # record a video into videos
    python3 quote_robot.py --fast          # use the normal /js/ page instead of the slow one
"""

import argparse
from collections import Counter
from pathlib import Path

import pandas as pd
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

BASE_URL = "https://quotes.toscrape.com"
USERNAME = "taima"      
PASSWORD = "automation"

HERE = Path(__file__).parent
OUTPUT_FILE = HERE / "quotes.xlsx"
PROOF_FILE = HERE / "proof.png"


def log_in(page) -> None:
    print("Logging in...", end=" ", flush=True)
    page.goto(f"{BASE_URL}/login")
    page.fill("#username", USERNAME)
    page.fill("#password", PASSWORD)
    page.click("input[type=submit]")

    # Check it really worked: a logged-in page shows a "Logout" link
    try:
        page.get_by_role("link", name="Logout").wait_for(timeout=10_000)
    except PlaywrightTimeout:
        raise SystemExit("Login failed: no 'Logout' link found. Check the selectors or the site.")
    print("✓ logged in")


def read_quotes_on_page(page) -> list[dict]:
    # Wait until the JavaScript has actually drawn the quotes (no time.sleep!)
    page.wait_for_selector("div.quote", timeout=30_000)

    quotes = []
    for box in page.locator("div.quote").all():
        quotes.append({
            "text": box.locator("span.text").inner_text().strip("“”\""),
            "author": box.locator("small.author").inner_text(),
            "tags": ", ".join(box.locator("a.tag").all_inner_texts()),
        })
    return quotes


def scrape_all_pages(page, start_path: str) -> list[dict]:
    print(f"Opening {start_path} (waiting for JavaScript)...")
    page.goto(f"{BASE_URL}{start_path}")

    all_quotes, page_number = [], 1
    while True:
        quotes = read_quotes_on_page(page)
        all_quotes.extend(quotes)
        print(f"  Page {page_number}: {len(quotes)} quotes")

        next_button = page.locator("li.next a")
        if next_button.count() == 0:          # no Next button = last page
            break
        first_quote = quotes[0]["text"]
        next_button.click()
        # Wait until the page really changed (the first quote is different), not just "some time"
        page.wait_for_function(
            "old => { const q = document.querySelector('div.quote span.text');"
            " return q && !q.innerText.includes(old); }",
            arg=first_quote[:40], timeout=30_000)
        page_number += 1

    page.screenshot(path=str(PROOF_FILE), full_page=True)
    return all_quotes


def save_and_summarize(quotes: list[dict]) -> None:
    df = pd.DataFrame(quotes)
    df.index += 1
    df.to_excel(OUTPUT_FILE, index_label="#")

    authors = Counter(df["author"])
    tags = Counter(t for row in df["tags"] for t in row.split(", ") if t)

    print(f"\nTotal: {len(df)} quotes from {len(authors)} authors")
    print("Top authors:", ", ".join(f"{a} ({n})" for a, n in authors.most_common(5)))
    print("Top tags:   ", ", ".join(f"{t} ({n})" for t, n in tags.most_common(5)))
    print(f"Saved {OUTPUT_FILE.name} and {PROOF_FILE.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Playwright web robot for quotes.toscrape.com")
    parser.add_argument("--headless", action="store_true", help="Run without opening a window")
    parser.add_argument("--video", action="store_true", help="Record a video into videos/")
    parser.add_argument("--fast", action="store_true", help="Use /js/ instead of the slow /js-delayed/")
    args = parser.parse_args()

    with sync_playwright() as p:            # closes everything properly, even after an error
        browser = p.chromium.launch(headless=args.headless, slow_mo=0 if args.headless else 150)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=str(HERE / "videos") if args.video else None,
        )
        page = context.new_page()
        try:
            log_in(page)
            quotes = scrape_all_pages(page, "/js/" if args.fast else "/js-delayed/")
        finally:
            context.close()                 # the video file is saved when the context closes
            browser.close()

    save_and_summarize(quotes)
    if args.video:
        print("Video saved in videos/")


if __name__ == "__main__":
    main()
