# 💰 Personal Finance Manager

A comprehensive command-line personal finance management system built in Python.
Track expenses, generate reports, analyze spending patterns, and manage backups — all from your terminal.

---

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [How to Run](#how-to-run)
- [Using the Application](#using-the-application)
- [Code Architecture](#code-architecture)
- [Data Storage](#data-storage)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

| Feature | Description |
|---|---|
| ➕ Add Expense | Record amount, category, date, and description with full validation |
| 📋 View All | Tabular view of all expenses sorted by date |
| 🔍 Search | Find expenses by keyword, category, or month |
| 🗑️ Delete | Remove any recorded expense after confirmation |
| 📊 Reports | Category summary, monthly breakdown, all-time stats |
| 📤 Export | Save filtered reports to CSV files |
| 💾 Backup | Timestamped backups of your expense data |
| ♻️ Restore | Restore any previous backup with one command |

**Expense Categories:** Food · Transport · Entertainment · Shopping · Health · Utilities · Education · Other

---

## 📁 Project Structure

```
finance_manager/
│
├── main.py                  ← Entry point — run this to start
├── requirements.txt         ← Dependencies (all stdlib)
├── README.md
│
├── src/
│   ├── expense.py           ← Expense class and category constants
│   ├── file_manager.py      ← CSV save/load, backup/restore
│   ├── reports.py           ← Report generation and analysis
│   ├── menu.py              ← CLI menus and user interaction
│   └── utils.py             ← Validation, formatting, input helpers
│
├── data/
│   ├── expenses.csv         ← Main data file (auto-created)
│   └── backups/             ← Timestamped backup files
│
├── reports/                 ← Exported CSV reports
│
├── tests/
│   └── test_finance_manager.py  ← 28 unit tests
│
└── docs/
    └── user_guide.md        ← Detailed user manual
```

---

## ⚙️ Setup & Installation

### Requirements

- Python **3.8 or higher**
- No third-party packages required — uses the Python Standard Library only

### Steps

```bash
# 1. Clone or download the project
git clone https://github.com/your-username/finance-manager.git
cd finance-manager

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows

# 3. No pip install needed — stdlib only!
#    If you want to run tests with pytest:
pip install pytest
```

---

## ▶️ How to Run

```bash
python main.py
```

You will see the main menu:

```
====================================================
           PERSONAL FINANCE MANAGER
====================================================

  Loaded 30 expense(s)

  MAIN MENU:
  1. Add New Expense
  2. View All Expenses
  3. Search Expenses
  4. Delete an Expense
  5. Reports & Analysis
  6. Backup & Restore
  7. Exit

  Enter your choice (1-7):
```

---

## 📖 Using the Application

### Adding an Expense

Select **1** from the main menu. You'll be prompted for:

```
  Enter amount (₹): 1500
  Categories: Food, Transport, Entertainment, ...
  Enter category: Food
  Enter date [press Enter for today]: 2024-03-15
  Enter description: Weekly grocery run

  ✅ Expense added successfully!
  2024-03-15 | Food            ₹   1500.00  -  Weekly grocery run
```

All inputs are validated — invalid entries are rejected with a helpful error message and you get up to 5 attempts per field.

### Viewing Reports

Select **5 → Reports & Analysis** for:

- **Category Summary** — visual bar chart of spending by category
- **Monthly Report** — all entries for a chosen month with totals
- **All-Time Summary** — overall statistics including highest/lowest expense
- **Export to CSV** — save a month's data to `reports/report_YYYY-MM.csv`

### Backup & Restore

Select **6 → Backup & Restore**:

- Backups are saved to `data/backups/` with timestamps  
  e.g. `expenses_backup_20240315_143022.csv`
- Restore any backup; you'll be asked to confirm before overwriting

---

## 🏗️ Code Architecture

### `expense.py` — Data Model

```python
class Expense:
    def __init__(self, amount, category, date, description):
        self.amount = float(amount)   # Always stored as float
        self.category = category
        self.date = date              # YYYY-MM-DD string
        self.description = description

    def get_month(self):              # Returns 'YYYY-MM'
    def to_dict(self):                # For CSV serialization
    @classmethod from_dict(cls, row): # For CSV deserialization
```

### `utils.py` — Validation Pattern

Every validator returns a 3-tuple `(is_valid, value, error_message)`:

```python
ok, amount, err = validate_amount("150")
# ok=True, amount=150.0, err=None

ok, amount, err = validate_amount("-5")
# ok=False, amount=None, err="Amount must be greater than zero."
```

`prompt_with_validation()` wraps any validator for interactive use with automatic retry.

### `file_manager.py` — Persistence

- `save_expenses(expenses)` — writes list to `data/expenses.csv`
- `load_expenses()` — reads CSV and returns `list[Expense]`
- `backup_data()` — copies current file to `data/backups/` with timestamp
- `restore_data(filename)` — copies backup over current data file

### `reports.py` — Analysis

Pure functions that operate on `list[Expense]`:

```
total_expenses()       → float
average_expense()      → float
expenses_by_category() → dict[str, list[Expense]]
category_totals()      → list[(category, total)] sorted desc
monthly_totals()       → list[(month_str, total)] sorted asc
```

---

## 💾 Data Storage

Expenses are stored in `data/expenses.csv` with the following columns:

```
Date,Category,Amount,Description
2024-01-15,Food,1500.00,Grocery shopping
2024-01-08,Transport,200.00,Metro card recharge
```

- File is created automatically on first use
- Each save writes the complete file (simple, no partial writes)
- Backups are identical CSV snapshots with timestamps in the filename

---

## 🧪 Testing

28 unit tests covering the core modules:

```bash
# Run with Python's built-in unittest
python tests/test_finance_manager.py

# Or with pytest (if installed)
pytest tests/ -v
```

Test coverage:
- `TestExpense` — constructor, `__str__`, `to_dict`, `from_dict`, helpers
- `TestValidation` — all validators with valid, zero, negative, and edge cases
- `TestUtils` — currency/month formatting
- `TestReports` — totals, averages, grouping, sorting

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Make sure you run `python main.py` from the project root, not from `src/` |
| Data not saving | Check that the `data/` folder exists and you have write permissions |
| Date rejected | Use the exact format `YYYY-MM-DD`, e.g. `2024-06-15` |
| Category not accepted | Check spelling; categories are case-insensitive but must be exact |
| Backup not found | Backups are in `data/backups/`. Run option 6 → 3 to list them |

---

## 👨‍💻 Author

Built as a Python learning project following OOP, file handling, and CLI design best practices.

---

## 📄 License

MIT License — free to use, modify, and distribute.
