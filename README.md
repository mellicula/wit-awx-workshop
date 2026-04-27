# WIT x Airwallex Workshop — Budget Tracker

A test-driven learning project built for the Women in Tech x Airwallex workshop. You'll explore a personal finance application, write test cases to achieve high code coverage, and then hunt down bugs in intentionally broken code.

---

## What You'll Build

A **Budget Tracker** with four core modules:

| Module | What it does |
|---|---|
| **Wallet** | Manage multi-currency funds — deposit, withdraw, transfer |
| **Expense Tracker** | Record and categorize spending |
| **Budget** | Set spending limits per category and monitor status |
| **Currency Converter** | Convert amounts across 8 supported currencies |

---

## Getting Started

### Prerequisites

- Python 3.12+

### Install dependencies

```bash
pip install -r requirements.txt
```

### Explore the modules interactively

```bash
python cli.py
```

This launches an interactive CLI where you can try out all four modules hands-on before writing tests.

---

## Workshop Flow

### Phase 1 — Write Tests

Your goal is to write pytest test cases for the four modules in `src/`. Tests live in the `tests/` directory. Look at `tests/test_example.py` for examples of how tests are structured.

Run your tests at any time:

```bash
python -m pytest
```

Run with a coverage report to see how much of the code your tests exercise:

```bash
python -m pytest --cov=src --cov-report=term-missing
```

Submit your score to the leaderboard:

```bash
bash run_tests.sh
```

Aim for as high a coverage percentage as possible.

### Phase 2 — Find the Bugs (Reveal)

Once the workshop facilitator activates **reveal mode**, buggy versions of the four modules become available. Run the reveal script to swap them in:

```bash
bash reveal.sh
```

Then re-run your tests against the broken code:

```bash
bash run_tests.sh
```

Your score switches from coverage % to **number of bugs caught** (out of 4). Good tests will catch bugs that manual inspection might miss.

---

## Project Structure

```
wit-awx-workshop/
├── cli.py                # Interactive CLI to explore the modules
├── run_tests.sh          # Runs tests and submits score to leaderboard
├── reveal.sh             # Swaps in buggy code for Phase 2
├── requirements.txt      # Python dependencies
├── pytest.ini            # Pytest configuration
│
├── src/                  # The modules you're testing
│   ├── wallet.py
│   ├── expense.py
│   ├── budget.py
│   └── currency.py
│
├── src_broken/           # Intentionally buggy versions (used in Phase 2)
│
├── tests/
│   ├── test_example.py   # Example tests to get you started
│   └── ...               # Add your own test files here
│
└── server/               # Leaderboard server (Flask)
```

---

## Module Reference

### Currency (`src/currency.py`)

Supported currencies: `AUD`, `USD`, `EUR`, `GBP`, `JPY`, `SGD`, `CNY`, `HKD`

```python
from src.currency import convert, format_amount

convert(100, "USD", "AUD")       # float
format_amount(12.5, "USD")       # "USD 12.50"
```

### Wallet (`src/wallet.py`)

```python
from src.wallet import Wallet

wallet = Wallet()
wallet.deposit(500, "AUD")
wallet.withdraw(50, "USD")
wallet.transfer(100, "AUD", "USD")
wallet.get_balance("AUD")        # float
wallet.total_in_aud()            # float — all balances converted to AUD
```

Raises `InsufficientFundsError` on overdraft.

### Expense Tracker (`src/expense.py`)

Valid categories: `food`, `transport`, `accommodation`, `entertainment`, `shopping`, `other`

```python
from src.expense import ExpenseTracker

tracker = ExpenseTracker()
tracker.add_expense(25.0, "AUD", "food", "Lunch")
tracker.get_by_category("food")        # list of Expense objects
tracker.total_by_category("food")      # float in AUD
tracker.total_in_aud()                 # float — all expenses in AUD
```

### Budget (`src/budget.py`)

```python
from src.budget import Budget

budget = Budget(tracker)               # pass an ExpenseTracker instance
budget.set_limit("food", 200.0)        # AUD
budget.get_remaining("food")           # float
budget.get_over_budget_categories()    # list of category names
budget.get_summary()                   # dict of status per category
```

---

## Writing Tests

Follow the **Arrange → Act → Assert** pattern:

```python
from src.currency import convert

def test_usd_to_aud():
    # Arrange
    amount = 100
    # Act
    result = convert(amount, "USD", "AUD")
    # Assert
    assert result > 0

def test_invalid_currency_raises_error():
    import pytest
    with pytest.raises(ValueError):
        convert(100, "USD", "XYZ")
```

Tips:
- Test both the happy path and edge cases (zero amounts, invalid inputs, insufficient funds)
- Use `pytest.raises()` to assert that errors are raised when expected
- Higher coverage = more bugs caught in Phase 2

---

## Leaderboard

The leaderboard is hosted at [wit-awx-workshop.onrender.com](https://wit-awx-workshop.onrender.com) and auto-refreshes every 5 seconds.

- **Phase 1**: ranked by test coverage %
- **Phase 2**: ranked by bugs caught, then coverage %

---

## Running the Leaderboard Server (Facilitators)

```bash
pip install -r server/requirements.txt
gunicorn server.main:app --bind 0.0.0.0:8000
```

### Admin endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/admin/reveal` | POST | Switch to Phase 2 (reveal mode) |
| `/admin/reset` | POST | Clear all scores, return to Phase 1 |

Both require the `ADMIN_KEY` header set via environment variable.

---

## Dependencies

| Package | Purpose |
|---|---|
| `pytest` | Test runner |
| `pytest-cov` | Coverage reporting |
| `flask` | Leaderboard server |
| `gunicorn` | Production WSGI server |
