"""
utils.py - Utility functions and validation helpers.
"""

import re
from datetime import datetime

from expense import CATEGORIES


# ─── Validation ──────────────────────────────────────────────────────────────

def validate_amount(value):
    """
    Validate that a string represents a positive float amount.

    Args:
        value (str): The raw input string.

    Returns:
        tuple: (is_valid: bool, amount: float or None, error_msg: str or None)
    """
    try:
        amount = float(value)
        if amount <= 0:
            return False, None, "Amount must be greater than zero."
        return True, amount, None
    except ValueError:
        return False, None, "Invalid amount. Please enter a numeric value (e.g. 150 or 99.99)."


def validate_date(value):
    """
    Validate a date string in YYYY-MM-DD format.

    Args:
        value (str): The raw input string.

    Returns:
        tuple: (is_valid: bool, date_str: str or None, error_msg: str or None)
    """
    value = value.strip()
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
        if dt > datetime.now():
            return False, None, "Date cannot be in the future."
        return True, value, None
    except ValueError:
        return False, None, "Invalid date. Use YYYY-MM-DD format (e.g. 2024-06-15)."


def validate_category(value):
    """
    Validate that a category is in the allowed list.

    Args:
        value (str): The raw input string.

    Returns:
        tuple: (is_valid: bool, category: str or None, error_msg: str or None)
    """
    value = value.strip().capitalize()
    if value in CATEGORIES:
        return True, value, None
    cats = "/".join(CATEGORIES)
    return False, None, f"Invalid category. Choose from: {cats}"


def validate_description(value):
    """
    Validate that a description is non-empty and reasonably short.

    Args:
        value (str): The raw input string.

    Returns:
        tuple: (is_valid: bool, desc: str or None, error_msg: str or None)
    """
    value = value.strip()
    if not value:
        return False, None, "Description cannot be empty."
    if len(value) > 100:
        return False, None, "Description must be 100 characters or fewer."
    return True, value, None


# ─── Formatting ───────────────────────────────────────────────────────────────

def format_currency(amount):
    """Format a float as a currency string with ₹ symbol."""
    return f"₹{amount:,.2f}"


def format_month(month_str):
    """Convert YYYY-MM to a human-readable month (e.g., 'January 2024')."""
    try:
        dt = datetime.strptime(month_str, "%Y-%m")
        return dt.strftime("%B %Y")
    except ValueError:
        return month_str


def today_str():
    """Return today's date as a YYYY-MM-DD string."""
    return datetime.now().strftime("%Y-%m-%d")


# ─── Input Helpers ────────────────────────────────────────────────────────────

def prompt_with_validation(prompt_text, validator_fn, max_attempts=5):
    """
    Prompt the user repeatedly until valid input is received.

    Args:
        prompt_text (str): The prompt to show the user.
        validator_fn (callable): A function(value) -> (bool, value_or_none, error_msg).
        max_attempts (int): Max number of retries before giving up.

    Returns:
        The validated value, or None if max attempts exceeded.
    """
    for attempt in range(1, max_attempts + 1):
        raw = input(prompt_text).strip()
        is_valid, value, error = validator_fn(raw)
        if is_valid:
            return value
        print(f"  ⚠️  {error}")
        if attempt < max_attempts:
            print(f"  (Attempt {attempt}/{max_attempts - 1} remaining)\n")
    print("  ❌ Too many invalid attempts. Returning to menu.")
    return None
