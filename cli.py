#!/usr/bin/env python3
"""Interactive CLI for exploring the budget tracker modules."""

from src.wallet import Wallet, InsufficientFundsError
from src.expense import ExpenseTracker, VALID_CATEGORIES
from src.budget import Budget
from src.currency import SUPPORTED_CURRENCIES, convert, format_amount

wallet = Wallet("you")
tracker = ExpenseTracker()
budget = Budget()


def divider():
    print("-" * 40)


def pause():
    input("\nPress Enter to continue...")


# ── Wallet ────────────────────────────────────────────────────────────────────

def wallet_menu():
    while True:
        print("\n=== Wallet ===")
        print(f"  Owner: {wallet.owner}")
        print("  1. Deposit")
        print("  2. Withdraw")
        print("  3. Transfer to another wallet")
        print("  4. Check balance")
        print("  5. Total in AUD")
        print("  0. Back")
        choice = input("> ").strip()

        if choice == "1":
            amount = float(input(f"Amount ({', '.join(sorted(SUPPORTED_CURRENCIES))}): "))
            currency = input("Currency: ").strip().upper()
            try:
                wallet.deposit(amount, currency)
                print(f"Deposited {format_amount(amount, currency)}")
            except (ValueError, KeyError) as e:
                print(f"Error: {e}")

        elif choice == "2":
            currency = input(f"Currency ({', '.join(sorted(SUPPORTED_CURRENCIES))}): ").strip().upper()
            amount = float(input("Amount: "))
            try:
                wallet.withdraw(amount, currency)
                print(f"Withdrew {format_amount(amount, currency)}")
            except (ValueError, InsufficientFundsError) as e:
                print(f"Error: {e}")

        elif choice == "3":
            recipient_name = input("Recipient name: ").strip()
            recipient = Wallet(recipient_name)
            currency = input(f"Currency ({', '.join(sorted(SUPPORTED_CURRENCIES))}): ").strip().upper()
            amount = float(input("Amount: "))
            try:
                wallet.transfer(amount, currency, recipient)
                print(f"Transferred {format_amount(amount, currency)} to {recipient_name}")
                print(f"  Their new balance: {format_amount(recipient.balance(currency), currency)}")
            except (ValueError, InsufficientFundsError) as e:
                print(f"Error: {e}")

        elif choice == "4":
            currency = input(f"Currency ({', '.join(sorted(SUPPORTED_CURRENCIES))}): ").strip().upper()
            try:
                bal = wallet.balance(currency)
                print(f"Balance: {format_amount(bal, currency)}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "5":
            print(f"Total across all currencies: AUD {wallet.total_in_aud():.2f}")

        elif choice == "0":
            break
        else:
            print("Invalid choice.")
        pause()


# ── Expenses ──────────────────────────────────────────────────────────────────

def expense_menu():
    while True:
        print("\n=== Expenses ===")
        print("  1. Add expense")
        print("  2. List all expenses")
        print("  3. Filter by category")
        print("  4. Totals by category")
        print("  5. Grand total in AUD")
        print("  0. Back")
        choice = input("> ").strip()

        if choice == "1":
            amount = float(input("Amount: "))
            currency = input(f"Currency ({', '.join(sorted(SUPPORTED_CURRENCIES))}): ").strip().upper()
            print(f"Categories: {', '.join(sorted(VALID_CATEGORIES))}")
            category = input("Category: ").strip().lower()
            description = input("Description: ").strip()
            try:
                expense = tracker.add_expense(amount, currency, category, description)
                print(f"Added: {expense}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            expenses = tracker.all_expenses()
            if not expenses:
                print("No expenses recorded yet.")
            else:
                divider()
                for e in expenses:
                    print(f"  [{e.category}] {format_amount(e.amount, e.currency)} — {e.description} ({e.date})")
                divider()

        elif choice == "3":
            print(f"Categories: {', '.join(sorted(VALID_CATEGORIES))}")
            category = input("Category: ").strip().lower()
            expenses = tracker.get_by_category(category)
            if not expenses:
                print(f"No expenses in '{category}'.")
            else:
                divider()
                for e in expenses:
                    print(f"  {format_amount(e.amount, e.currency)} — {e.description} ({e.date})")
                divider()

        elif choice == "4":
            totals = tracker.total_by_category()
            if not totals:
                print("No expenses recorded yet.")
            else:
                divider()
                for cat, total in sorted(totals.items()):
                    print(f"  {cat}: {total:.2f}")
                divider()

        elif choice == "5":
            print(f"Grand total: AUD {tracker.total_in_aud():.2f}")

        elif choice == "0":
            break
        else:
            print("Invalid choice.")
        pause()


# ── Budget ────────────────────────────────────────────────────────────────────

def budget_menu():
    while True:
        print("\n=== Budget ===")
        print("  1. Set limit for a category")
        print("  2. Check remaining budget")
        print("  3. Check if over budget")
        print("  4. Full summary (uses current expense totals)")
        print("  0. Back")
        choice = input("> ").strip()

        if choice == "1":
            print(f"Categories: {', '.join(sorted(VALID_CATEGORIES))}")
            category = input("Category: ").strip().lower()
            amount = float(input("Limit (AUD): "))
            try:
                budget.set_limit(category, amount)
                print(f"Set {category} limit to AUD {amount:.2f}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            category = input("Category: ").strip().lower()
            spent = float(input("Amount spent so far: "))
            result = budget.remaining(category, spent)
            if result is None:
                print(f"No limit set for '{category}'.")
            elif result < 0:
                print(f"Over budget by AUD {abs(result):.2f}")
            else:
                print(f"Remaining: AUD {result:.2f}")

        elif choice == "3":
            category = input("Category: ").strip().lower()
            spent = float(input("Amount spent so far: "))
            over = budget.is_over_budget(category, spent)
            limit = budget.get_limit(category)
            if limit is None:
                print(f"No limit set for '{category}'.")
            else:
                status = "OVER BUDGET" if over else "within budget"
                print(f"{category}: {status} (limit AUD {limit:.2f}, spent {spent:.2f})")

        elif choice == "4":
            spent_by_category = tracker.total_by_category()
            summary = budget.summary(spent_by_category)
            if not summary:
                print("No budget limits set yet.")
            else:
                divider()
                for cat, info in sorted(summary.items()):
                    flag = " *** OVER BUDGET ***" if info["over_budget"] else ""
                    print(f"  {cat}: limit={info['limit']:.2f}, spent={info['spent']:.2f}, remaining={info['remaining']:.2f}{flag}")
                divider()

        elif choice == "0":
            break
        else:
            print("Invalid choice.")
        pause()


# ── Currency ──────────────────────────────────────────────────────────────────

def currency_menu():
    while True:
        print("\n=== Currency Converter ===")
        print(f"  Supported: {', '.join(sorted(SUPPORTED_CURRENCIES))}")
        print("  1. Convert amount")
        print("  0. Back")
        choice = input("> ").strip()

        if choice == "1":
            amount = float(input("Amount: "))
            from_c = input("From currency: ").strip().upper()
            to_c = input("To currency: ").strip().upper()
            try:
                result = convert(amount, from_c, to_c)
                print(f"  {format_amount(amount, from_c)} = {format_amount(result, to_c)}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "0":
            break
        else:
            print("Invalid choice.")
        pause()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 40)
    print("   Budget Tracker — Interactive CLI")
    print("=" * 40)
    print("All data resets when you exit.")

    while True:
        print("\n=== Main Menu ===")
        print("  1. Wallet")
        print("  2. Expenses")
        print("  3. Budget")
        print("  4. Currency Converter")
        print("  0. Quit")
        choice = input("> ").strip()

        if choice == "1":
            wallet_menu()
        elif choice == "2":
            expense_menu()
        elif choice == "3":
            budget_menu()
        elif choice == "4":
            currency_menu()
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
