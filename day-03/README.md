# Day 03 – Merge Sales CSVs into a Formatted Excel Report

Part of my **#30DaysOfAutomation** challenge.

## The problem
Every month, sales data arrives as separate CSV files (one per month, branch or system). Someone has to copy everything into one Excel file, remove duplicates, calculate totals and format it. That takes about 30 minutes, every time, and it's easy to make mistakes.

## The solution
One command reads all the CSV files, cleans the data, calculates totals and creates a ready-to-send Excel report in **under 1 second**.

```
input/sales_aug.csv ┐
input/sales_sep.csv ├──► clean ──► summarize ──► sales_report_2026-11-04.xlsx
input/sales_oct.csv ┘
```

## What the report contains
**Summary sheet**
- Total revenue, number of orders and date range at the top
- Tables: revenue by month, by region and by product
- Totals rows using real Excel `=SUM()` formulas
- A bar chart of revenue by month

**All Orders sheet**
- Every clean order in one table, with a frozen header, filters and money formatting

## Data cleaning
Real data is messy. The script:
- Removes duplicated orders (same `order_id`)
- Removes rows with a missing quantity
- Converts dates and calculates `revenue = quantity × unit_price`
- Adds a `source_file` column, so every row can be traced back to its file

## Tech used
Python 3 · `pandas` (read, clean, group) · `openpyxl` (formatting, formulas, chart)

## How to run
```bash
pip install -r requirements.txt
python3 generate_sample_data.py   # creates 3 practice CSVs in input/
python3 sales_report.py           # creates the Excel report
```
To use your own data, put any CSV files with the same columns in `input/`.

## Result
<img width="1488" height="811" alt="Screenshot 2026-11-06 at 9 17 04 PM" src="https://github.com/user-attachments/assets/f0f01e07-2256-4ff7-b6d7-d7c98fc2e6d9" />


## What I learned
- `pd.concat` merges many files into one table
- `groupby` + `agg` replaces pivot tables
- pandas writes the data; openpyxl makes it look professional
- Always check for duplicates and missing values before calculating totals
