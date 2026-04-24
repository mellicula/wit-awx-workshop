#!/usr/bin/env bash
# Run this at the end of the workshop to swap in the broken code.
# Students' tests will then be re-run against it automatically via CI.
set -e

cp src_broken/currency.py src/currency.py
cp src_broken/wallet.py   src/wallet.py
cp src_broken/expense.py  src/expense.py
cp src_broken/budget.py   src/budget.py

echo "Broken code swapped in. Push to trigger CI re-run."
