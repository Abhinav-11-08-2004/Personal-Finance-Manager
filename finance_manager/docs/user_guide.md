# 📘 Personal Finance Manager — User Guide

## Quick Start

```bash
python main.py
```

---

## Menu Reference

### 1. Add New Expense

Prompts for amount, category, date (defaults to today), and description.  
All inputs are validated; you get up to 5 retries per field.

**Example session:**
```
  Enter amount (₹): 1500
  Categories: Food, Transport, Entertainment, Shopping, Health, Utilities, Education, Other
  Enter category: Food
  Enter date [press Enter for today]: 2024-03-15
  Enter description: Weekly grocery run
  ✅ Expense added successfully!
```

---

### 2. View All Expenses

Displays all recorded expenses in a numbered table sorted by date (newest first).  
Shows grand total at the bottom.

---

### 3. Search Expenses

Three search modes:

| Mode | Input | Example |
|---|---|---|
| Keyword | Any word in description | `grocery` |
| Category | One of the 8 categories | `Food` |
| Month | YYYY-MM format | `2024-03` |

Results show matching expenses and their total.

---

### 4. Delete an Expense

Displays all expenses numbered. Enter the number to delete.  
Asks for `yes` confirmation before deleting. Enter `0` to cancel.

---

### 5. Reports & Analysis

| Sub-option | What it shows |
|---|---|
| Category Summary | Totals per category with % share and bar chart |
| Monthly Report (current) | All entries this month, daily average, category breakdown |
| Monthly Report (choose) | Same for any past month |
| All-Time Summary | Total, average, highest/lowest expense, busiest month |
| Export to CSV | Saves month's data to `reports/report_YYYY-MM.csv` |

---

### 6. Backup & Restore

| Sub-option | What it does |
|---|---|
| Create Backup | Copies `data/expenses.csv` → `data/backups/expenses_backup_TIMESTAMP.csv` |
| Restore from Backup | Overwrites current data with a chosen backup |
| List Backups | Shows all available backup files |

---

## Data File Formats

### `data/expenses.csv` (main data)
```
Date,Category,Amount,Description
2024-03-15,Food,1500.00,Weekly grocery run
```

### `data/backups/expenses_backup_YYYYMMDD_HHMMSS.csv` (backups)
Same format as the main file.

### `reports/report_YYYY-MM.csv` (exports)
Same format, filtered to one month.

---

## Tips

- Press **Enter** when prompted for a date to use today's date automatically.
- Categories are **case-insensitive** — `food`, `FOOD`, and `Food` all work.
- Create a backup before making large changes.
- Use the **Export** feature to share monthly data with a spreadsheet.
