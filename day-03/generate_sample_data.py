"""
Day 3 - #30DaysOfAutomation
Creates 3 fake monthly sales CSV files to practice with.
(In a real job, these would come from different branches, systems or people.)

The data is a little messy on purpose, like real data:
- one duplicated order
- one row with a missing quantity
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)  # same "random" data every time

PRODUCTS = {"Laptop": 850, "Monitor": 220, "Keyboard": 45, "Mouse": 25, "Headphones": 90}
REGIONS = ["North", "South", "Center"]
MONTHS = [(2026, 8, "sales_aug.csv"), (2026, 9, "sales_sep.csv"), (2026, 10, "sales_oct.csv")]

out_dir = Path(__file__).parent / "input"
out_dir.mkdir(exist_ok=True)

order_id = 1000
for year, month, filename in MONTHS:
    rows = []
    for _ in range(random.randint(40, 60)):
        order_id += 1
        product = random.choice(list(PRODUCTS))
        day = date(year, month, 1) + timedelta(days=random.randint(0, 27))
        rows.append({
            "order_id": order_id,
            "date": day.isoformat(),
            "region": random.choice(REGIONS),
            "product": product,
            "quantity": random.randint(1, 5),
            "unit_price": PRODUCTS[product],
        })

    rows.append(dict(rows[0]))      # messy data: a duplicated order
    rows[5]["quantity"] = ""        # messy data: a missing value

    with open(out_dir / filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Created input/{filename} ({len(rows)} rows)")
