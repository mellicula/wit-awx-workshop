SUPPORTED_CURRENCIES = {"AUD", "USD", "EUR", "GBP", "JPY", "SGD", "CNY", "HKD"}

# All rates expressed relative to AUD as the base currency
RATES = {
    "AUD": 1.00,
    "USD": 0.64,
    "EUR": 0.59,
    "GBP": 0.51,
    "JPY": 96.50,
    "SGD": 0.87,
    "CNY": 4.65,
    "HKD": 5.01,
}


def convert(amount: float, from_currency: str, to_currency: str) -> float:
    """Convert an amount from one currency to another. Returns result rounded to 2 decimal places."""
    if from_currency not in SUPPORTED_CURRENCIES:
        raise ValueError(f"Unsupported currency: {from_currency}")
    if to_currency not in SUPPORTED_CURRENCIES:
        raise ValueError(f"Unsupported currency: {to_currency}")
    if amount < 0:
        raise ValueError("Amount cannot be negative")

    if from_currency == to_currency:
        return round(amount, 2)

    aud_amount = amount / RATES[from_currency]
    return round(aud_amount * RATES[to_currency], 2)


def format_amount(amount: float, currency: str) -> str:
    """Return a human-readable string like 'USD 12.50'."""
    if currency not in SUPPORTED_CURRENCIES:
        raise ValueError(f"Unsupported currency: {currency}")
    return f"{currency} {amount:.2f}"
