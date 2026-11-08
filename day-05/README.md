# Day 05 – Web Robot with Playwright

Part of my **#30DaysOfAutomation** challenge.

## The problem
Many websites have no API. To get data from them, or to enter data into them, someone has to click, type, wait and copy by hand.

## The solution
A Python robot that controls a real browser:

1. **Logs in** through a form and checks that the login worked
2. Opens a page that is **built slowly by JavaScript** and waits for the content
3. Clicks **Next** through every page until the end
4. Collects each quote, author and tags
5. Saves everything to **Excel**, prints a summary, and takes a **screenshot** as proof

Practice site: [quotes.toscrape.com](https://quotes.toscrape.com), made for learning scraping.

## Example output
```
Logging in... ✓ logged in
Opening /js-delayed/ (waiting for JavaScript)...
  Page 1: 10 quotes
  ...
  Page 10: 10 quotes

Total: 100 quotes from 50 authors
Top authors: Albert Einstein (10), J.K. Rowling (9), ...
Top tags:    love (14), inspirational (13), ...
Saved quotes.xlsx and proof.png
```

## What makes it reliable
- **No `time.sleep()`**: it waits for real things (`wait_for_selector`, and checks that the page really changed after clicking Next)
- **Login check**: stops with a clear message if the Logout link doesn't appear
- **Stops by itself** when there's no Next button; nothing is hard-coded
- The browser always closes, even after an error
- Options: `--headless` (no window), `--video` (records the run), `--fast`

## Tech used
Python 3 · Playwright · pandas · openpyxl

## How to run
```bash
pip install -r requirements.txt
playwright install chromium
python3 quote_robot.py            # watch it work
python3 quote_robot.py --video    # record a video into videos
```


## What I learned
- Locators and CSS selectors: how to point the robot at the right element
- Pages built by JavaScript need **waiting**, not sleeping
- After a click, wait for the page to actually change
- This is the same idea as RPA: a robot doing what a person does in a browser
