"""
menu.py - Command-line interface and menu system.
"""

import os
from datetime import datetime

from expense import Expense, CATEGORIES
from file_manager import (
    load_expenses, save_expenses,
    backup_data, list_backups, restore_data,
    load_categories, save_categories, DEFAULT_CATEGORIES
)
from reports import (
    print_category_summary, print_monthly_report,
    print_all_time_summary, export_monthly_report,
    print_annual_report, export_annual_report,
    print_expenses_table
)
from utils import (
    format_currency, format_month, today_str
)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title="PERSONAL FINANCE MANAGER"):
    print()
    print("=" * 52)
    print(f"  {title.center(48)}")
    print("=" * 52)


def press_enter():
    input("\n  Press Enter to continue...")


def cancelled():
    print("  ↩️  Cancelled. Returning to menu.")
    press_enter()


def cancel_hint():
    """Print the cancel hint once, at the top of each feature."""
    print("  (Enter 0 at any prompt to cancel and go back)\n")


# ─── Add Expense ──────────────────────────────────────────────────────────────

def add_expense(expenses):
    print_header("ADD NEW EXPENSE")
    cancel_hint()

    # Amount
    while True:
        raw = input("  Enter amount (₹): ").strip()
        if raw == "0":
            cancelled(); return
        try:
            amount = float(raw)
            if amount <= 0:
                print("  ⚠️  Amount must be greater than zero.")
                continue
            break
        except ValueError:
            print("  ⚠️  Invalid amount. Enter a number e.g. 150 or 99.99.")

    # Category
    print(f"\n  Categories:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"  {i:>2}. {cat}")
    print()
    while True:
        raw = input("  Enter category name or number: ").strip()
        if raw == "0":
            cancelled(); return
        if raw.isdigit() and 1 <= int(raw) <= len(CATEGORIES):
            category = CATEGORIES[int(raw) - 1]
            break
        cap = raw.capitalize()
        if cap in CATEGORIES:
            category = cap
            break
        print("  ⚠️  Invalid category. Type the name or its number from the list.")

    # Date
    default_date = today_str()
    print(f"\n  Date format: YYYY-MM-DD  (default: {default_date})")
    while True:
        raw = input("  Enter date [press Enter for today]: ").strip()
        if raw == "0":
            cancelled(); return
        if raw == "":
            date = default_date; break
        try:
            dt = datetime.strptime(raw, "%Y-%m-%d")
            if dt > datetime.now():
                print("  ⚠️  Date cannot be in the future.")
                continue
            date = raw; break
        except ValueError:
            print("  ⚠️  Invalid date. Use YYYY-MM-DD format e.g. 2024-06-15.")

    # Description
    while True:
        raw = input("\n  Enter description: ").strip()
        if raw == "0":
            cancelled(); return
        if not raw:
            print("  ⚠️  Description cannot be empty.")
            continue
        if len(raw) > 100:
            print("  ⚠️  Description must be 100 characters or fewer.")
            continue
        description = raw; break

    expense = Expense(amount, category, date, description)
    expenses.append(expense)

    if save_expenses(expenses):
        print(f"\n  ✅ Expense added successfully!")
        print(f"  {expense}")
    else:
        print("\n  ⚠️  Expense added to session but could not be saved to disk.")

    press_enter()


# ─── View Expenses ────────────────────────────────────────────────────────────

def view_all_expenses(expenses):
    print_header("ALL EXPENSES")
    if not expenses:
        print("  No expenses recorded yet.")
        press_enter()
        return
    print_expenses_table(expenses)
    press_enter()


# ─── Search Expenses ──────────────────────────────────────────────────────────

def search_expenses(expenses):
    print_header("SEARCH EXPENSES")
    cancel_hint()
    print("  Search by:")
    print("  1. Keyword (description)")
    print("  2. Category")
    print("  3. Month (YYYY-MM)")
    print("  0. Back")

    choice = input("\n  Enter choice: ").strip()
    results = []

    if choice == "0":
        return

    elif choice == "1":
        while True:
            keyword = input("  Enter keyword: ").strip()
            if keyword == "0":
                cancelled(); return
            if not keyword:
                print("  ⚠️  Keyword cannot be empty.")
                continue
            break
        results = [e for e in expenses if keyword.lower() in e.description.lower()]
        label = f"keyword '{keyword}'"

    elif choice == "2":
        print(f"\n  Categories:")
        for i, cat in enumerate(CATEGORIES, 1):
            print(f"  {i:>2}. {cat}")
        print()
        while True:
            raw = input("  Enter category name or number: ").strip()
            if raw == "0":
                cancelled(); return
            if raw.isdigit() and 1 <= int(raw) <= len(CATEGORIES):
                cat = CATEGORIES[int(raw) - 1]; break
            cap = raw.capitalize()
            if cap in CATEGORIES:
                cat = cap; break
            print("  ⚠️  Invalid category.")
        results = [e for e in expenses if e.category == cat]
        label = f"category '{cat}'"

    elif choice == "3":
        while True:
            raw = input("  Enter month (YYYY-MM): ").strip()
            if raw == "0":
                cancelled(); return
            try:
                datetime.strptime(raw, "%Y-%m"); break
            except ValueError:
                print("  ⚠️  Invalid format. Use YYYY-MM e.g. 2024-03.")
        results = [e for e in expenses if e.get_month() == raw]
        label = f"month {format_month(raw)}"

    else:
        print("  ⚠️  Invalid choice.")
        press_enter(); return

    print_header(f"SEARCH RESULTS — {label.upper()}")
    if not results:
        print(f"  No expenses found for {label}.")
    else:
        print_expenses_table(results)
        print(f"\n  {len(results)} result(s)  |  Total: {format_currency(sum(e.amount for e in results))}")

    press_enter()


# ─── Delete Expense ───────────────────────────────────────────────────────────

def delete_expense(expenses):
    print_header("DELETE AN EXPENSE")
    cancel_hint()

    if not expenses:
        print("  No expenses to delete.")
        press_enter(); return

    print_expenses_table(expenses)
    print()

    while True:
        raw = input("  Enter number to delete: ").strip()
        if raw == "0":
            cancelled(); return
        try:
            idx = int(raw)
        except ValueError:
            print("  ⚠️  Please enter a valid number.")
            continue
        sorted_exps = sorted(expenses, key=lambda e: e.date, reverse=True)
        if not (1 <= idx <= len(sorted_exps)):
            print(f"  ⚠️  Number out of range. Enter 1–{len(sorted_exps)}.")
            continue
        break

    sorted_exps = sorted(expenses, key=lambda e: e.date, reverse=True)
    target = sorted_exps[idx - 1]
    print(f"\n  Selected: {target}")
    confirm = input("  Confirm delete? (yes/no): ").strip().lower()
    if confirm == "0":
        cancelled(); return
    if confirm == "yes":
        expenses.remove(target)
        if save_expenses(expenses):
            print("  ✅ Expense deleted successfully.")
        else:
            print("  ⚠️  Deleted from session but could not save to disk.")
    else:
        print("  ❌ Deletion cancelled.")

    press_enter()


# ─── Backup & Restore ─────────────────────────────────────────────────────────

def backup_restore_menu(expenses):
    while True:
        print_header("BACKUP & RESTORE")
        cancel_hint()
        print("  1. Create Backup")
        print("  2. Restore from Backup")
        print("  3. List Backups")
        print("  0. Back to Main Menu")

        choice = input("\n  Enter choice: ").strip()

        if choice == "0":
            return

        elif choice == "1":
            path = backup_data()
            if path:
                print(f"\n  ✅ Backup created: {os.path.basename(path)}")
            press_enter()

        elif choice == "2":
            backups = list_backups()
            if not backups:
                print("\n  ⚠️  No backups available.")
                press_enter(); continue

            print("\n  Available backups:")
            for i, b in enumerate(backups, 1):
                print(f"  {i}. {b}")

            while True:
                raw = input("\n  Enter number to restore: ").strip()
                if raw == "0":
                    break
                try:
                    idx = int(raw)
                except ValueError:
                    print("  ⚠️  Invalid number."); continue
                if not (1 <= idx <= len(backups)):
                    print(f"  ⚠️  Enter 1–{len(backups)}."); continue
                confirm = input(f"\n  Restore '{backups[idx-1]}'?\n  This will overwrite current data. (yes/no): ").strip().lower()
                if confirm == "0":
                    break
                if confirm == "yes":
                    if restore_data(backups[idx - 1]):
                        expenses.clear()
                        expenses.extend(load_expenses())
                        print("  ✅ Data restored successfully.")
                    else:
                        print("  ❌ Restore failed.")
                else:
                    print("  ❌ Restore cancelled.")
                press_enter(); break

        elif choice == "3":
            backups = list_backups()
            if not backups:
                print("\n  No backups found.")
            else:
                print(f"\n  Found {len(backups)} backup(s):")
                for b in backups:
                    print(f"    • {b}")
            press_enter()

        else:
            print("  ⚠️  Invalid choice.")
            press_enter()


# ─── Monthly Report ───────────────────────────────────────────────────────────

def monthly_report_menu(expenses):
    print_header("GENERATE MONTHLY REPORT")
    cancel_hint()
    current = datetime.now().strftime("%Y-%m")
    while True:
        raw = input(f"  Enter month (YYYY-MM) [Enter for {current}]: ").strip()
        if raw == "0":
            cancelled(); return
        if raw == "":
            month = current; break
        try:
            datetime.strptime(raw, "%Y-%m")
            month = raw; break
        except ValueError:
            print("  ⚠️  Invalid format. Use YYYY-MM e.g. 2024-03.")

    print_monthly_report(expenses, month=month)

    export = input("  Export this report to CSV? (yes/no): ").strip().lower()
    if export == "yes":
        path = export_monthly_report(expenses, month=month)
        if path:
            print(f"  ✅ Exported to: {path}")
        else:
            print("  ⚠️  No data for that month or export failed.")
    press_enter()


# ─── Annual Report ────────────────────────────────────────────────────────────

def annual_report_menu(expenses):
    print_header("GENERATE ANNUAL REPORT")
    cancel_hint()
    current_year = datetime.now().strftime("%Y")
    while True:
        raw = input(f"  Enter year (YYYY) [Enter for {current_year}]: ").strip()
        if raw == "0":
            cancelled(); return
        if raw == "":
            year = current_year; break
        if raw.isdigit() and len(raw) == 4:
            year = raw; break
        print("  ⚠️  Invalid year. Use 4-digit format e.g. 2024.")

    print_annual_report(expenses, year=year)

    export = input("  Export this report to CSV? (yes/no): ").strip().lower()
    if export == "yes":
        path = export_annual_report(expenses, year=year)
        if path:
            print(f"  ✅ Exported to: {path}")
        else:
            print("  ⚠️  No data for that year or export failed.")
    press_enter()


# ─── Manage Categories ────────────────────────────────────────────────────────

def manage_categories():
    while True:
        print_header("MANAGE CATEGORIES")
        cancel_hint()
        print(f"  Current categories ({len(CATEGORIES)}):")
        print()
        for i, cat in enumerate(CATEGORIES, 1):
            tag = "  (default)" if cat in DEFAULT_CATEGORIES else "  (custom)"
            print(f"  {i:>2}. {cat}{tag}")
        print()
        print("  1. Add a new category")
        print("  2. Delete a custom category")
        print("  0. Back to Main Menu")
        print()
        choice = input("  Enter choice: ").strip()

        if choice == "0":
            return

        elif choice == "1":
            print()
            while True:
                raw = input("  Enter new category name: ").strip()
                if raw == "0":
                    break
                if not raw:
                    print("  ⚠️  Category name cannot be empty."); continue
                if len(raw) > 30:
                    print("  ⚠️  Category name must be 30 characters or fewer."); continue
                if raw.capitalize() in CATEGORIES:
                    print(f"  ⚠️  '{raw.capitalize()}' already exists."); continue
                new_cat = raw.capitalize()
                if "Other" in CATEGORIES:
                    CATEGORIES.insert(CATEGORIES.index("Other"), new_cat)
                else:
                    CATEGORIES.append(new_cat)
                save_categories(CATEGORIES)
                print(f"  ✅ Category '{new_cat}' added successfully!")
                break
            press_enter()

        elif choice == "2":
            custom = [c for c in CATEGORIES if c not in DEFAULT_CATEGORIES]
            if not custom:
                print("\n  ⚠️  No custom categories to delete.")
                press_enter(); continue
            print("\n  Custom categories:")
            for i, cat in enumerate(custom, 1):
                print(f"  {i}. {cat}")
            print()
            while True:
                raw = input("  Enter number to delete: ").strip()
                if raw == "0":
                    break
                try:
                    idx = int(raw)
                except ValueError:
                    print("  ⚠️  Invalid number."); continue
                if not (1 <= idx <= len(custom)):
                    print(f"  ⚠️  Enter 1–{len(custom)}."); continue
                target = custom[idx - 1]
                confirm = input(f"  Delete category '{target}'? (yes/no): ").strip().lower()
                if confirm == "0":
                    break
                if confirm == "yes":
                    CATEGORIES.remove(target)
                    save_categories(CATEGORIES)
                    print(f"  ✅ Category '{target}' deleted.")
                else:
                    print("  ❌ Cancelled.")
                break
            press_enter()

        else:
            print("  ⚠️  Invalid choice.")
            press_enter()


# ─── Main Menu ────────────────────────────────────────────────────────────────

def main_menu():
    loaded_cats = load_categories()
    CATEGORIES.clear()
    CATEGORIES.extend(loaded_cats)

    expenses = load_expenses()

    while True:
        clear_screen()
        print_header()
        print(f"\n  Loaded {len(expenses)} expense(s)\n")
        print("  MAIN MENU:")
        print("  1. Add New Expense")
        print("  2. View All Expenses")
        print("  3. View Category-wise Summary")
        print("  4. Generate Monthly Report")
        print("  5. Generate Annual Report")
        print("  6. Search Expenses")
        print("  7. Delete An Expense")
        print("  8. Backup Data")
        print("  9. Manage Categories")
        print("  10. Exit")
        print()

        choice = input("  Enter your choice (1-10): ").strip()

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            view_all_expenses(expenses)
        elif choice == "3":
            print_header("CATEGORY-WISE SUMMARY")
            print_category_summary(expenses)
            press_enter()
        elif choice == "4":
            monthly_report_menu(expenses)
        elif choice == "5":
            annual_report_menu(expenses)
        elif choice == "6":
            search_expenses(expenses)
        elif choice == "7":
            delete_expense(expenses)
        elif choice == "8":
            backup_restore_menu(expenses)
        elif choice == "9":
            manage_categories()
        elif choice == "10":
            print("\n  👋 Thank you for using Personal Finance Manager. Goodbye!\n")
            break
        else:
            print("  ⚠️  Invalid choice. Please enter a number from 1 to 10.")
            press_enter()
