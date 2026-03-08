"""
tests/test_finance_manager.py
Unit tests for the Personal Finance Manager.

Run with:
    python -m pytest tests/ -v
or from the project root:
    python tests/test_finance_manager.py
"""

import sys
import os
import unittest
import csv
import tempfile

# Make sure src/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from expense import Expense, CATEGORIES
from utils import (
    validate_amount, validate_date, validate_category,
    validate_description, format_currency, format_month, today_str
)
from reports import (
    total_expenses, average_expense,
    expenses_by_category, category_totals, monthly_totals
)


# ─── Expense Tests ─────────────────────────────────────────────────────────────

class TestExpense(unittest.TestCase):

    def setUp(self):
        self.e = Expense(1500.0, "Food", "2024-03-10", "Grocery shopping")

    def test_amount_converted_to_float(self):
        e = Expense("250", "Transport", "2024-03-01", "Bus fare")
        self.assertIsInstance(e.amount, float)
        self.assertAlmostEqual(e.amount, 250.0)

    def test_str_representation(self):
        s = str(self.e)
        self.assertIn("2024-03-10", s)
        self.assertIn("Food", s)
        self.assertIn("1500.00", s)
        self.assertIn("Grocery shopping", s)

    def test_to_dict(self):
        d = self.e.to_dict()
        self.assertEqual(d["date"], "2024-03-10")
        self.assertEqual(d["category"], "Food")
        self.assertAlmostEqual(float(d["amount"]), 1500.0)
        self.assertEqual(d["description"], "Grocery shopping")

    def test_from_dict(self):
        row = {"Date": "2024-01-15", "Category": "Health", "Amount": "750.0", "Description": "Doctor"}
        e = Expense.from_dict(row)
        self.assertEqual(e.category, "Health")
        self.assertAlmostEqual(e.amount, 750.0)

    def test_get_month(self):
        self.assertEqual(self.e.get_month(), "2024-03")

    def test_get_year(self):
        self.assertEqual(self.e.get_year(), "2024")


# ─── Validation Tests ──────────────────────────────────────────────────────────

class TestValidation(unittest.TestCase):

    # Amount
    def test_valid_amount(self):
        ok, val, err = validate_amount("1500")
        self.assertTrue(ok)
        self.assertAlmostEqual(val, 1500.0)

    def test_valid_amount_decimal(self):
        ok, val, _ = validate_amount("99.99")
        self.assertTrue(ok)
        self.assertAlmostEqual(val, 99.99)

    def test_zero_amount_invalid(self):
        ok, _, _ = validate_amount("0")
        self.assertFalse(ok)

    def test_negative_amount_invalid(self):
        ok, _, _ = validate_amount("-50")
        self.assertFalse(ok)

    def test_non_numeric_amount_invalid(self):
        ok, _, _ = validate_amount("abc")
        self.assertFalse(ok)

    # Date
    def test_valid_date(self):
        ok, val, _ = validate_date("2024-01-15")
        self.assertTrue(ok)
        self.assertEqual(val, "2024-01-15")

    def test_invalid_date_format(self):
        ok, _, _ = validate_date("15-01-2024")
        self.assertFalse(ok)

    def test_future_date_invalid(self):
        ok, _, _ = validate_date("2099-12-31")
        self.assertFalse(ok)

    # Category
    def test_valid_category(self):
        ok, val, _ = validate_category("food")
        self.assertTrue(ok)
        self.assertEqual(val, "Food")

    def test_invalid_category(self):
        ok, _, _ = validate_category("Luxury")
        self.assertFalse(ok)

    # Description
    def test_valid_description(self):
        ok, val, _ = validate_description("Grocery shopping")
        self.assertTrue(ok)

    def test_empty_description_invalid(self):
        ok, _, _ = validate_description("   ")
        self.assertFalse(ok)

    def test_too_long_description_invalid(self):
        ok, _, _ = validate_description("x" * 101)
        self.assertFalse(ok)


# ─── Utils Tests ──────────────────────────────────────────────────────────────

class TestUtils(unittest.TestCase):

    def test_format_currency(self):
        self.assertEqual(format_currency(1500.0), "₹1,500.00")
        self.assertEqual(format_currency(0.5), "₹0.50")

    def test_format_month(self):
        self.assertEqual(format_month("2024-01"), "January 2024")
        self.assertEqual(format_month("2024-12"), "December 2024")

    def test_today_str_format(self):
        today = today_str()
        self.assertRegex(today, r"\d{4}-\d{2}-\d{2}")


# ─── Reports Tests ─────────────────────────────────────────────────────────────

class TestReports(unittest.TestCase):

    def setUp(self):
        self.expenses = [
            Expense(500, "Food", "2024-01-10", "Groceries"),
            Expense(200, "Transport", "2024-01-15", "Bus"),
            Expense(1000, "Food", "2024-02-05", "Restaurant"),
            Expense(300, "Health", "2024-02-20", "Pharmacy"),
        ]

    def test_total_expenses(self):
        self.assertAlmostEqual(total_expenses(self.expenses), 2000.0)

    def test_total_empty(self):
        self.assertAlmostEqual(total_expenses([]), 0.0)

    def test_average_expense(self):
        self.assertAlmostEqual(average_expense(self.expenses), 500.0)

    def test_expenses_by_category(self):
        grouped = expenses_by_category(self.expenses)
        self.assertIn("Food", grouped)
        self.assertEqual(len(grouped["Food"]), 2)

    def test_category_totals_sorted(self):
        totals = category_totals(self.expenses)
        # Food should be first (₹1500)
        self.assertEqual(totals[0][0], "Food")
        self.assertAlmostEqual(totals[0][1], 1500.0)

    def test_monthly_totals(self):
        months = monthly_totals(self.expenses)
        self.assertEqual(len(months), 2)
        self.assertEqual(months[0][0], "2024-01")
        self.assertAlmostEqual(months[0][1], 700.0)


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
