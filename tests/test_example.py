"""
Example tests — read these before writing your own.

Each test follows the same pattern:
  1. Arrange  — set up the data you need
  2. Act      — call the function you're testing
  3. Assert   — check the result is what you expected

Your job: write tests for currency.py, wallet.py, expense.py, and budget.py.
Think about the happy path first, then ask: what could go wrong?
"""

from src.currency import convert, format_amount
from src.wallet import Wallet


# ── A simple test ──────────────────────────────────────────────────────────────

def test_convert_aud_to_usd():
    # Arrange
    amount = 100.0

    # Act
    result = convert(amount, "AUD", "USD")

    # Assert
    assert result == 64.0


# ── Testing that an error is raised ───────────────────────────────────────────

def test_convert_raises_for_unsupported_currency():
    import pytest

    with pytest.raises(ValueError):
        convert(100.0, "AUD", "XYZ")


# ── Testing a class ───────────────────────────────────────────────────────────

def test_wallet_balance_starts_at_zero():
    wallet = Wallet("Alice")

    assert wallet.balance("AUD") == 0.0


def test_wallet_balance_reflects_deposit():
    # Arrange
    wallet = Wallet("Alice")

    # Act
    wallet.deposit(50.0, "AUD")

    # Assert
    assert wallet.balance("AUD") == 50.0
