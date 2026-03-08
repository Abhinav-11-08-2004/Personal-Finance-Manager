"""
expense.py - Expense class definition
Defines the core Expense data model for the Personal Finance Manager.
"""

from datetime import datetime


# Valid expense categories — populated at startup from file_manager.load_categories()
# This list is mutable so new categories can be added at runtime.
CATEGORIES = ["Food", "Transport", "Entertainment", "Shopping", "Health", "Utilities", "Education", "Other"]


class Expense:
    """
    Represents a single financial expense entry.

    Attributes:
        amount (float): The expense amount in rupees.
        category (str): The category of the expense.
        date (str): The date of the expense in YYYY-MM-DD format.
        description (str): A short description of the expense.
    """

    def __init__(self, amount, category, date, description):
        self.amount = float(amount)
        self.category = category
        self.date = date
        self.description = description

    def __str__(self):
        return f"{self.date} | {self.category:<15} ₹{self.amount:>10.2f}  -  {self.description}"

    def __repr__(self):
        return f"Expense(amount={self.amount}, category='{self.category}', date='{self.date}', description='{self.description}')"

    def to_dict(self):
        """Convert expense to a dictionary."""
        return {
            "date": self.date,
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data):
        """Create an Expense from a dictionary (e.g., a CSV row)."""
        return cls(
            amount=data["Amount"],
            category=data["Category"],
            date=data["Date"],
            description=data["Description"],
        )

    def get_month(self):
        """Return the month string (YYYY-MM) for this expense."""
        return self.date[:7]

    def get_year(self):
        """Return the year (YYYY) for this expense."""
        return self.date[:4]
