from src.currency import SUPPORTED_CURRENCIES, convert


class InsufficientFundsError(Exception):
    pass


class Wallet:
    def __init__(self, owner: str):
        self.owner = owner
        self._balances: dict[str, float] = {}

    def deposit(self, amount: float, currency: str) -> None:
        if currency not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}")
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        self._balances[currency] = self._balances.get(currency, 0.0) + amount

    def withdraw(self, amount: float, currency: str) -> None:
        if currency not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}")
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if self._balances.get(currency, 0.0) < amount:
            raise InsufficientFundsError(
                f"Insufficient {currency} funds: have {self._balances.get(currency, 0.0)}, need {amount}"
            )

        self._balances[currency] = self._balances[currency] - amount

    def balance(self, currency: str) -> float:
        if currency not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}")
        return self._balances.get(currency, 0.0)

    def transfer(self, amount: float, currency: str, recipient: "Wallet") -> None:
        """Withdraw from this wallet and deposit into recipient's wallet."""
        self.withdraw(amount, currency)
        recipient.deposit(amount, currency)

    def total_in_aud(self) -> float:
        """Return the total value of all balances converted to AUD."""
        total = 0.0
        for currency, amount in self._balances.items():
            total += convert(amount, currency, "AUD")
        return round(total, 2)
