"""
Day 3 - #30DaysOfAutomation
Merge many monthly sales CSV files into ONE formatted Excel report.

Steps:
  1. Read every CSV in the input/ folder        (pandas)
  2. Clean the data: duplicates, missing values (pandas)
  3. Calculate totals by month, region, product (pandas)
  4. Write a formatted Excel file with a chart  (openpyxl)


"""

from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill

BASE = Path(__file__).parent
INPUT_DIR = BASE / "input"
OUTPUT_FILE = BASE / f"sales_report_{datetime.now():%Y-%m-%d}.xlsx"

MONEY = '"$"#,##0'
HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(bold=True, color="FFFFFF")
TOTAL_FILL = PatternFill("solid", fgColor="DDEBF7")


# ---------- 1. Read ----------
def load_data() -> pd.DataFrame:
    files = sorted(INPUT_DIR.glob("*.csv"))
    if not files:
        raise SystemExit("No CSV files in input/. Run: python3 generate_sample_data.py")
    frames = []
    for file in files:
        df = pd.read_csv(file)
        df["source_file"] = file.name  # remember where each row came from
        frames.append(df)
        print(f"Read {file.name}: {len(df)} rows")
    return pd.concat(frames, ignore_index=True)


# ---------- 2. Clean ----------
def clean(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset="order_id")
    dupes = before - len(df)

    missing = df["quantity"].isna().sum()
    df = df.dropna(subset=["quantity"])

    df["quantity"] = df["quantity"].astype(int)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.strftime("%Y-%m")
    df["revenue"] = df["quantity"] * df["unit_price"]

    print(f"Cleaning: removed {dupes} duplicates and {missing} rows with missing quantity")
    return df


# ---------- 3. Summaries ----------
def summarize(df: pd.DataFrame) -> dict:
    def group(col):
        return (df.groupby(col)
                  .agg(orders=("order_id", "count"), units=("quantity", "sum"), revenue=("revenue", "sum"))
                  .reset_index())

    return {
        "By Month": group("month"),
        "By Region": group("region").sort_values("revenue", ascending=False),
        "By Product": group("product").sort_values("revenue", ascending=False),
    }


# ---------- 4. Write + format Excel ----------
def style_header(ws, row: int, ncols: int, col_start: int = 1) -> None:
    for c in range(col_start, col_start + ncols):
        cell = ws.cell(row=row, column=c)
        cell.fill, cell.font = HEADER_FILL, HEADER_FONT
        cell.alignment = Alignment(horizontal="center")


def write_report(df: pd.DataFrame, summaries: dict) -> None:
    # Summary sheet: the three tables stacked with a gap between them
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        row = 3
        positions = {}
        for title, table in summaries.items():
            # startrow is 0-based, so the header lands on Excel row `row + 1`, under the title
            table.to_excel(writer, sheet_name="Summary", startrow=row, index=False)
            positions[title] = (row, len(table))
            row += len(table) + 5

        cols = ["order_id", "date", "month", "region", "product", "quantity", "unit_price", "revenue", "source_file"]
        df[cols].sort_values("date").to_excel(writer, sheet_name="All Orders", index=False)

    # Re-open with openpyxl to add formatting (pandas only writes plain values)
    wb = load_workbook(OUTPUT_FILE)
    ws = wb["Summary"]

    ws["A1"] = "Sales Report"
    ws["A1"].font = Font(bold=True, size=16)
    ws["A2"] = (f"{df['month'].min()} to {df['month'].max()}  ·  "
                f"Total revenue: ${df['revenue'].sum():,.0f}  ·  {len(df)} orders  ·  "
                f"Generated {datetime.now():%Y-%m-%d %H:%M}")
    ws["A2"].font = Font(italic=True, color="595959")

    for title, (start, n) in positions.items():
        ws.cell(row=start, column=1, value=title).font = Font(bold=True, size=12)
        header = start + 1
        style_header(ws, header, 4)
        first, last = header + 1, header + n
        for r in range(first, last + 1):
            ws.cell(row=r, column=4).number_format = MONEY
        # Totals row with real Excel formulas
        total = last + 1
        ws.cell(row=total, column=1, value="Total")
        for c, letter in [(2, "B"), (3, "C"), (4, "D")]:
            ws.cell(row=total, column=c, value=f"=SUM({letter}{first}:{letter}{last})")
        ws.cell(row=total, column=4).number_format = MONEY
        for c in range(1, 5):
            ws.cell(row=total, column=c).font = Font(bold=True)
            ws.cell(row=total, column=c).fill = TOTAL_FILL

    for letter, width in zip("ABCD", [16, 10, 10, 14]):
        ws.column_dimensions[letter].width = width

    # Bar chart: revenue by month
    start, n = positions["By Month"]
    chart = BarChart()
    chart.title, chart.y_axis.title = "Revenue by Month", "Revenue ($)"
    chart.add_data(Reference(ws, min_col=4, min_row=start + 1, max_row=start + 1 + n), titles_from_data=True)
    chart.set_categories(Reference(ws, min_col=1, min_row=start + 2, max_row=start + 1 + n))
    chart.height, chart.width, chart.legend = 7, 14, None
    ws.add_chart(chart, "F4")

    # All Orders sheet: header style, money format, frozen header, filters, widths
    ws2 = wb["All Orders"]
    style_header(ws2, 1, ws2.max_column)
    ws2.freeze_panes = "A2"
    ws2.auto_filter.ref = ws2.dimensions
    for r in range(2, ws2.max_row + 1):
        ws2.cell(row=r, column=2).number_format = "yyyy-mm-dd"
        ws2.cell(row=r, column=7).number_format = MONEY
        ws2.cell(row=r, column=8).number_format = MONEY
    for letter, width in zip("ABCDEFGHI", [10, 12, 10, 10, 12, 10, 11, 11, 16]):
        ws2.column_dimensions[letter].width = width

    wb.save(OUTPUT_FILE)


def main() -> None:
    df = clean(load_data())
    write_report(df, summarize(df))
    print(f"\nDone! Report saved: {OUTPUT_FILE.name}")
    print(f"Total revenue: ${df['revenue'].sum():,.0f} from {len(df)} orders")


if __name__ == "__main__":
    main()
