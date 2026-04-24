from dataclasses import dataclass, field
from datetime import date

from src.currency import SUPPORTED_CURRENCIES, convert


VALID_CATEGORIES = {"food", "transport", "accommodation", "entertainment", "shopping", "other"}


@dataclass
class Expense:
    amount: float
    currency: str
    category: str
    description: str
    date: date = field(default_factory=date.today)


class ExpenseTracker:
    def __init__(self):
        self._expenses: list[Expense] = []

    def add_expense(self, amount: float, currency: str, category: str, description: str) -> Expense:
        if amount <= 0:
            raise ValueError("Expense amount must be positive")
        if currency not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}")
        if category not in VALID_CATEGORIES:
            raise ValueError(f"Invalid category: {category}. Must be one of {VALID_CATEGORIES}")

        expense = Expense(amount=amount, currency=currency, category=category, description=description)
        self._expenses.append(expense)
        return expense

    def get_by_category(self, category: str) -> list[Expense]:
        # BUG: != instead of == returns every expense EXCEPT the requested category
        return [e for e in self._expenses if e.category != category]

    def total_by_category(self) -> dict[str, float]:
        totals: dict[str, float] = {}
        for expense in self._expenses:
            totals[expense.category] = totals.get(expense.category, 0.0) + expense.amount
        return totals

    def total_in_aud(self) -> float:
        return round(sum(convert(e.amount, e.currency, "AUD") for e in self._expenses), 2)

    def all_expenses(self) -> list[Expense]:
        return list(self._expenses)
