"""
file_manager.py - CSV read/write operations and backup/restore functionality.
Handles all data persistence for the Personal Finance Manager.
"""

import csv
import os
import shutil
from datetime import datetime

from expense import Expense

# Default file paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
EXPENSES_FILE = os.path.join(DATA_DIR, "expenses.csv")
CSV_HEADERS = ["Date", "Category", "Amount", "Description"]
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.txt")

# Built-in default categories (never removed)
DEFAULT_CATEGORIES = ["Food", "Transport", "Entertainment", "Shopping", "Health", "Utilities", "Education", "Other"]


def load_categories():
    """Load categories from file, merging with defaults. Returns sorted list."""
    ensure_dirs()
    cats = list(DEFAULT_CATEGORIES)
    if os.path.exists(CATEGORIES_FILE):
        try:
            with open(CATEGORIES_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    cat = line.strip()
                    if cat and cat not in cats:
                        cats.append(cat)
        except (IOError, OSError):
            pass
    return cats


def save_categories(categories):
    """Save only the custom (non-default) categories to file."""
    ensure_dirs()
    custom = [c for c in categories if c not in DEFAULT_CATEGORIES]
    try:
        with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
            for cat in custom:
                f.write(cat + "\n")
        return True
    except (IOError, OSError) as e:
        print(f"  ❌ Error saving categories: {e}")
        return False


def ensure_dirs():
    """Ensure the data and backup directories exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)


def save_expenses(expenses, filename=None):
    """
    Save a list of Expense objects to a CSV file.

    Args:
        expenses (list): List of Expense objects.
        filename (str): Optional custom filename. Defaults to EXPENSES_FILE.

    Returns:
        bool: True if saved successfully, False otherwise.
    """
    ensure_dirs()
    filepath = filename or EXPENSES_FILE
    try:
        with open(filepath, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
            writer.writeheader()
            for expense in expenses:
                writer.writerow({
                    "Date": expense.date,
                    "Category": expense.category,
                    "Amount": f"{expense.amount:.2f}",
                    "Description": expense.description,
                })
        return True
    except (IOError, OSError) as e:
        print(f"  ❌ Error saving expenses: {e}")
        return False


def load_expenses(filename=None):
    """
    Load expenses from a CSV file.

    Args:
        filename (str): Optional custom filename. Defaults to EXPENSES_FILE.

    Returns:
        list: List of Expense objects. Empty list if file not found or error.
    """
    ensure_dirs()
    filepath = filename or EXPENSES_FILE
    expenses = []

    if not os.path.exists(filepath):
        return expenses

    try:
        with open(filepath, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    expenses.append(Expense.from_dict(row))
                except (KeyError, ValueError):
                    # Skip malformed rows silently
                    continue
    except (IOError, OSError) as e:
        print(f"  ❌ Error loading expenses: {e}")

    return expenses


def backup_data():
    """
    Create a timestamped backup of the expenses CSV file.

    Returns:
        str: Path to the backup file, or None on failure.
    """
    ensure_dirs()
    if not os.path.exists(EXPENSES_FILE):
        print("  ⚠️  No expense data found to backup.")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"expenses_backup_{timestamp}.csv"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    try:
        shutil.copy2(EXPENSES_FILE, backup_path)
        return backup_path
    except (IOError, OSError) as e:
        print(f"  ❌ Backup failed: {e}")
        return None


def list_backups():
    """
    List all available backup files.

    Returns:
        list: Sorted list of backup filenames (newest first).
    """
    ensure_dirs()
    backups = [
        f for f in os.listdir(BACKUP_DIR)
        if f.startswith("expenses_backup_") and f.endswith(".csv")
    ]
    return sorted(backups, reverse=True)


def restore_data(backup_filename):
    """
    Restore expenses data from a backup file.

    Args:
        backup_filename (str): The backup filename to restore from.

    Returns:
        bool: True if restored successfully, False otherwise.
    """
    ensure_dirs()
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    if not os.path.exists(backup_path):
        print(f"  ❌ Backup file not found: {backup_filename}")
        return False

    try:
        shutil.copy2(backup_path, EXPENSES_FILE)
        return True
    except (IOError, OSError) as e:
        print(f"  ❌ Restore failed: {e}")
        return False


def export_to_csv(expenses, filepath):
    """
    Export a filtered/custom list of expenses to a specified CSV path.

    Args:
        expenses (list): List of Expense objects.
        filepath (str): Full path for the exported file.

    Returns:
        bool: True if exported successfully.
    """
    return save_expenses(expenses, filename=filepath)
