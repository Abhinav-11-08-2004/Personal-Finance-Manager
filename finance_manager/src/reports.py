"""
reports.py - Report generation and data analysis functions.

Border math:
  Border width  = 2(indent) + 1(╔) + 68(═) + 1(╗) = 72 chars total
  Row inner     = 2( ) + sum(col_widths) + (N-1)*5(  │  ) + 2( ) = 68
  => sum(col_widths) = 64 - (N-1)*5
    N=2 → 59   N=3 → 54   N=4 → 49   N=5 → 44
"""

import os
from collections import defaultdict
from datetime import datetime

from expense import CATEGORIES
from file_manager import export_to_csv
from utils import format_currency, format_month


REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")

W   = 68   # inner dashes (border chars are outside this)
SEP = "│"


def _ensure_reports_dir():
    os.makedirs(REPORTS_DIR, exist_ok=True)


# ─── Drawing primitives ───────────────────────────────────────────────────────

def _top():
    print("  ╔" + "═" * W + "╗")

def _bot():
    print("  ╚" + "═" * W + "╝")

def _mid():
    print("  ╠" + "═" * W + "╣")

def _div():
    print("  ├" + "─" * W + "┤")

def _row(*cells):
    """
    Render one row. Cells = (text, width, align '<'|'>').
    Rule: sum(widths) must equal 64 - (N-1)*5  for N = len(cells).
    Content between the two border │ chars = 2 + sum + (N-1)*5 + 2 = 68 ✓
    """
    parts = []
    for text, width, align in cells:
        s = str(text)
        if len(s) > width:
            s = s[:width - 1] + "…"
        parts.append(f"{s:>{width}}" if align == ">" else f"{s:<{width}}")
    print("  │  " + "  │  ".join(parts) + "  │")

def _title(label):
    _top()
    print("  │" + label.center(W) + "│")
    _mid()

def _section(label):
    """A labelled divider row inside an open table."""
    _div()
    print("  │  " + label.ljust(W - 4) + "  │")
    _div()


# ─── Aggregation helpers ──────────────────────────────────────────────────────

def total_expenses(expenses):
    return sum(e.amount for e in expenses)

def average_expense(expenses):
    return total_expenses(expenses) / len(expenses) if expenses else 0.0

def expenses_by_category(expenses):
    grouped = defaultdict(list)
    for e in expenses:
        grouped[e.category].append(e)
    return dict(grouped)

def expenses_by_month(expenses):
    grouped = defaultdict(list)
    for e in expenses:
        grouped[e.get_month()].append(e)
    return dict(grouped)

def category_totals(expenses):
    grouped = expenses_by_category(expenses)
    totals = [(c, sum(e.amount for e in es)) for c, es in grouped.items()]
    return sorted(totals, key=lambda x: x[1], reverse=True)

def monthly_totals(expenses):
    grouped = expenses_by_month(expenses)
    totals = [(m, sum(e.amount for e in es)) for m, es in grouped.items()]
    return sorted(totals, key=lambda x: x[0])


# ─── View All Expenses ────────────────────────────────────────────────────────
# N=5 cols → sum = 44
# #=4, Date=12, Category=16, Amount=12 → fixed=44, Description=44-4-12-16-12=0 ✗
# Use N=5: fixed 4+10+14+12 = 40 → Desc = 44-40 = 4  — too small
# Better: drop # as separate col, use wider table approach:
# #=3, Date=10, Category=13, Amount=11 → 37, Desc=44-37=7 — still tight
# Let's compute properly:
# N=5, sum=44. Allocate: #=3, Date=10, Category=13, Amount=12 → 38, Desc=6 tight
# Better N=4 for expenses: combine or go N=4
# Actually let's just pick good values that sum correctly.
# N=5: #=4, Date=10, Category=13, Amount=12, Desc=5 → sum=44 ✓ (Desc is tight)
# Let's use N=4 by merging Date into description col? No, keep 5 cols but wider W.
# Instead: increase W to 76 so border = 2+1+76+1 = 80 cols.
# N=5 sum = 76 - 4 - (4)*5 = 72 - 20 = 52 → much better
# #=4, Date=12, Category=14, Amount=12, Desc=10 → 52 ✓

W2 = 76   # wider table for expense list only

def _top2():  print("  ╔" + "═" * W2 + "╗")
def _bot2():  print("  ╚" + "═" * W2 + "╝")
def _mid2():  print("  ╠" + "═" * W2 + "╣")
def _div2():  print("  ├" + "─" * W2 + "┤")

def _row2(*cells):
    parts = []
    for text, width, align in cells:
        s = str(text)
        if len(s) > width:
            s = s[:width - 1] + "…"
        parts.append(f"{s:>{width}}" if align == ">" else f"{s:<{width}}")
    print("  │  " + "  │  ".join(parts) + "  │")


def print_expenses_table(expenses):
    # N=5, W2=76: sum = 76 - 4 - 4*5 = 52
    CN = 4   # #
    CD = 10  # Date
    CC = 14  # Category
    CA = 12  # Amount
    CX = 52 - CN - CD - CC - CA  # Description = 12
    # 4+10+14+12+12 = 52 ✓

    sorted_exps = sorted(expenses, key=lambda e: e.date, reverse=True)

    _top2()
    _row2(("#",           CN, "<"), ("Date",        CD, "<"),
          ("Category",    CC, "<"), ("Amount",      CA, ">"),
          ("Description", CX, "<"))
    _div2()
    for i, e in enumerate(sorted_exps, 1):
        _row2((str(i),                   CN, "<"), (e.date,        CD, "<"),
              (e.category,               CC, "<"), (format_currency(e.amount), CA, ">"),
              (e.description,            CX, "<"))
    _div2()
    grand = total_expenses(expenses)
    _row2(("", CN, "<"), ("", CD, "<"), ("", CC, "<"),
          (format_currency(grand),      CA, ">"),
          (f"{len(expenses)} record(s)", CX, "<"))
    _bot2()


# ─── Category Summary ─────────────────────────────────────────────────────────
# N=4, sum=49: Category=18, Total=13, %Share=9, Spend%=9 → 49 ✓

def print_category_summary(expenses):
    if not expenses:
        print("  No expenses to summarize.")
        return

    CC = 18  # Category
    CA = 13  # Total
    CP = 9   # % Share
    CB = 49 - CC - CA - CP  # Spend % bar = 9

    grand_total = total_expenses(expenses)
    totals = category_totals(expenses)

    _top()
    _row(("Category", CC, "<"), ("Total",   CA, ">"),
         ("% Share",  CP, ">"), ("Spend %", CB, "<"))
    _div()
    for cat, total in totals:
        pct = (total / grand_total * 100) if grand_total else 0
        bar = "█" * int(pct / 5)
        _row((cat,                    CC, "<"), (format_currency(total), CA, ">"),
             (f"{pct:.1f}%",          CP, ">"), (bar,                   CB, "<"))
    _div()
    _row(("TOTAL", CC, "<"), (format_currency(grand_total), CA, ">"),
         ("100.0%", CP, ">"), ("", CB, "<"))
    _bot()


# ─── Monthly Report ───────────────────────────────────────────────────────────
# Expense rows: N=4, sum=49: Date=10, Category=14, Amount=13, Desc=12 → 49 ✓
# Stats rows:   N=2, sum=59: Label=24, Value=35 → 59 ✓
# Category breakdown: N=4, sum=49: Cat=18, Total=13, %Share=9, Spend%=9 → 49 ✓

def print_monthly_report(expenses, month=None):
    if month is None:
        month = datetime.now().strftime("%Y-%m")

    month_expenses = [e for e in expenses if e.get_month() == month]

    _title(f"MONTHLY REPORT — {format_month(month)}")

    if not month_expenses:
        print("  │" + f"  No expenses recorded for {format_month(month)}.".ljust(W) + "│")
        _bot()
        return

    # Expense list
    CD = 10   # Date
    CC = 14   # Category
    CA = 13   # Amount
    CX = 49 - CD - CC - CA  # Description = 12

    _row(("Date", CD, "<"), ("Category", CC, "<"),
         ("Amount", CA, ">"), ("Description", CX, "<"))
    _div()
    month_expenses.sort(key=lambda e: e.date)
    for e in month_expenses:
        _row((e.date, CD, "<"), (e.category, CC, "<"),
             (format_currency(e.amount), CA, ">"), (e.description, CX, "<"))

    # Stats
    CL = 24   # label
    CV = 59 - CL  # value = 35
    _section("SUMMARY")
    _row(("Total entries",   CL, "<"), (str(len(month_expenses)),                         CV, ">"))
    _row(("Total spent",     CL, "<"), (format_currency(total_expenses(month_expenses)),  CV, ">"))
    _row(("Average expense", CL, "<"), (format_currency(average_expense(month_expenses)), CV, ">"))

    # Category breakdown: N=4, sum=49
    CC2 = 18
    CA2 = 13
    CP2 = 9
    CB2 = 49 - CC2 - CA2 - CP2  # = 9
    _section("BREAKDOWN BY CATEGORY")
    _row(("Category", CC2, "<"), ("Total",   CA2, ">"),
         ("% Share",  CP2, ">"), ("Spend %", CB2, "<"))
    _div()
    grand = total_expenses(month_expenses)
    for cat, total in category_totals(month_expenses):
        pct = (total / grand * 100) if grand else 0
        bar = "█" * int(pct / 12)
        _row((cat,                    CC2, "<"), (format_currency(total), CA2, ">"),
             (f"{pct:.1f}%",          CP2, ">"), (bar,                   CB2, "<"))
    _bot()


# ─── Annual Report ────────────────────────────────────────────────────────────
# Month table:    N=4, sum=49: Month=18, Entries=8, Total=13, %ofYear=10 → 49 ✓
# Category table: N=4, sum=49: Cat=18, Total=13, %Share=9, Spend%=9 → 49 ✓
# Highlights:     N=2, sum=59: Label=24, Value=35 → 59 ✓

def print_annual_report(expenses, year=None):
    if year is None:
        year = datetime.now().strftime("%Y")

    year_expenses = [e for e in expenses if e.get_year() == year]

    _title(f"ANNUAL REPORT — {year}")

    if not year_expenses:
        print("  │" + f"  No expenses recorded for {year}.".ljust(W) + "│")
        _bot()
        return

    grand_total = total_expenses(year_expenses)
    months      = monthly_totals(year_expenses)

    # Month-by-month table: N=4, sum=49
    CM = 18   # Month name
    CE = 8    # Entries
    CA = 13   # Total
    CY = 49 - CM - CE - CA  # % of Year = 10

    _row(("Month",     CM, "<"), ("Entries", CE, ">"),
         ("Total",     CA, ">"), ("% of Year", CY, ">"))
    _div()
    for month_str, month_total in months:
        month_exps = [e for e in year_expenses if e.get_month() == month_str]
        pct = (month_total / grand_total * 100) if grand_total else 0
        _row((format_month(month_str),     CM, "<"), (str(len(month_exps)), CE, ">"),
             (format_currency(month_total), CA, ">"), (f"{pct:.1f}%",       CY, ">"))
    _div()
    _row(("TOTAL",                    CM, "<"), (str(len(year_expenses)), CE, ">"),
         (format_currency(grand_total), CA, ">"), ("100.0%",              CY, ">"))

    # Category breakdown: N=4, sum=49
    CC2 = 18
    CA2 = 13
    CP2 = 9
    CB2 = 49 - CC2 - CA2 - CP2  # Spend % = 9
    _section(f"CATEGORY BREAKDOWN — {year}")
    _row(("Category", CC2, "<"), ("Total",   CA2, ">"),
         ("% Share",  CP2, ">"), ("Spend %", CB2, "<"))
    _div()
    for cat, total in category_totals(year_expenses):
        pct = (total / grand_total * 100) if grand_total else 0
        bar = "█" * int(pct / 12)
        _row((cat,                    CC2, "<"), (format_currency(total), CA2, ">"),
             (f"{pct:.1f}%",          CP2, ">"), (bar,                   CB2, "<"))

    # Highlights: N=2, sum=59
    CL = 24
    CV = 59 - CL  # = 35
    sorted_exps  = sorted(year_expenses, key=lambda e: e.amount)
    avg_monthly  = grand_total / len(months) if months else 0
    best_month   = max(months, key=lambda x: x[1]) if months else None

    _section("HIGHLIGHTS")
    _row(("Lowest expense",    CL, "<"), (f"{format_currency(sorted_exps[0].amount)}  ({sorted_exps[0].description})",   CV, "<"))
    _row(("Highest expense",   CL, "<"), (f"{format_currency(sorted_exps[-1].amount)}  ({sorted_exps[-1].description})", CV, "<"))
    _row(("Avg monthly spend", CL, "<"), (format_currency(avg_monthly),                                                  CV, "<"))
    if best_month:
        _row(("Highest month", CL, "<"), (f"{format_month(best_month[0])}  —  {format_currency(best_month[1])}",         CV, "<"))
    _bot()


# ─── All-time Summary ─────────────────────────────────────────────────────────
# N=2, sum=59: Label=24, Value=35 → 59 ✓

def print_all_time_summary(expenses):
    if not expenses:
        print("  No expenses recorded yet.")
        return

    _title("ALL-TIME SUMMARY")

    CL = 24
    CV = 59 - CL  # = 35

    sorted_exps = sorted(expenses, key=lambda e: e.amount)
    months  = monthly_totals(expenses)
    busiest = max(months, key=lambda x: x[1]) if months else None

    _row(("Total records",   CL, "<"), (str(len(expenses)),                         CV, "<"))
    _row(("Total spent",     CL, "<"), (format_currency(total_expenses(expenses)),  CV, "<"))
    _row(("Average expense", CL, "<"), (format_currency(average_expense(expenses)), CV, "<"))
    _div()
    _row(("Lowest expense",  CL, "<"), (f"{format_currency(sorted_exps[0].amount)}  ({sorted_exps[0].description})",   CV, "<"))
    _row(("Highest expense", CL, "<"), (f"{format_currency(sorted_exps[-1].amount)}  ({sorted_exps[-1].description})", CV, "<"))
    if busiest:
        _row(("Highest month", CL, "<"), (f"{format_month(busiest[0])}  —  {format_currency(busiest[1])}", CV, "<"))
    _bot()


# ─── Export helpers ───────────────────────────────────────────────────────────

def export_monthly_report(expenses, month=None):
    _ensure_reports_dir()
    if month is None:
        month = datetime.now().strftime("%Y-%m")
    month_expenses = [e for e in expenses if e.get_month() == month]
    if not month_expenses:
        return None
    filepath = os.path.join(REPORTS_DIR, f"report_{month}.csv")
    return filepath if export_to_csv(month_expenses, filepath) else None


def export_annual_report(expenses, year=None):
    _ensure_reports_dir()
    if year is None:
        year = datetime.now().strftime("%Y")
    year_expenses = [e for e in expenses if e.get_year() == year]
    if not year_expenses:
        return None
    filepath = os.path.join(REPORTS_DIR, f"report_{year}_annual.csv")
    return filepath if export_to_csv(year_expenses, filepath) else None
