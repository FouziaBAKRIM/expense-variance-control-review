#!/usr/bin/env python3
"""Quick profile of the synthetic expense dataset.

Prints the checks a reviewer would run first: date quality, category labels,
duplicates, negatives, budget edge cases and outliers. Read-only.

Usage:
    python scripts/profile_synthetic_data.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "synthetic_retail_expenses.csv"

CANONICAL_CATEGORIES = {
    "Payroll & Overtime",
    "Utilities & Rent",
    "Freight & Delivery",
    "Digital Ads & Promo",
    "Software & Cloud",
    "Maintenance & Repairs",
    "Professional Services",
    "Office & Supplies",
}


def main() -> None:
    df = pd.read_csv(CSV_PATH, dtype=str, keep_default_na=False)
    df["budget_num"] = pd.to_numeric(df["budget"], errors="coerce")
    df["actual_num"] = pd.to_numeric(df["actual_amount"], errors="coerce")

    print(f"File    : {CSV_PATH.name}")
    print(f"Rows    : {len(df)}")
    print(f"Columns : {', '.join(df.columns[:8])}")
    print()

    parsed = pd.to_datetime(df["date"], errors="coerce")
    blank = df["date"].str.strip() == ""
    iso_shaped = df["date"].str.match(r"^\d{4}-\d{2}-\d{2}$")
    non_iso = ~iso_shaped & ~blank
    invalid_iso = iso_shaped & parsed.isna()
    unparseable = parsed.isna() & ~blank
    print("--- DATE QUALITY ---")
    print(f"Blank dates             : {blank.sum()}")
    print(f"Non-ISO date strings    : {non_iso.sum()} -> {sorted(set(df.loc[non_iso, 'date']))}")
    print(f"ISO-shaped but invalid  : {invalid_iso.sum()} -> {sorted(set(df.loc[invalid_iso, 'date']))}")
    print(f"Unparseable dates       : {unparseable.sum()}")
    print(f"Parsed range            : {parsed.min().date()} to {parsed.max().date()}")
    print()

    print("--- CATEGORY LABELS (raw values) ---")
    for value, count in df["category"].value_counts().items():
        marker = "" if value in CANONICAL_CATEGORIES else "  <-- non-canonical"
        print(f"{count:>4}  {value!r}{marker}")
    print()

    business_key = ["date", "department", "category", "description", "budget", "actual_amount"]
    exact_dupes = df[df.duplicated(subset=business_key, keep=False)]
    near_key = ["department", "category", "description", "actual_amount"]
    near = df[df.duplicated(subset=near_key, keep=False) & ~df.index.isin(exact_dupes.index)]
    print("--- DUPLICATES ---")
    print(f"Exact business-key duplicates : {len(exact_dupes)} rows")
    print(f"Near duplicates (same dept/category/description/amount, different date) : {len(near)} rows")
    print()

    print("--- VALUE ANOMALIES ---")
    print(f"Negative actual (credits/refunds) : {(df['actual_num'] < 0).sum()}")
    print(f"Negative budget                  : {(df['budget_num'] < 0).sum()}")
    print(f"Zero budget                      : {(df['budget_num'] == 0).sum()}")
    print(f"Tiny budget (< 10 EUR)           : {((df['budget_num'] > 0) & (df['budget_num'] < 10)).sum()}")
    print(f"Blank description                : {(df['description'].str.strip() == '').sum()}")
    print()

    print("--- TOP 5 LARGEST ACTUALS ---")
    top = df.nlargest(5, "actual_num")[["txn_id", "date", "department", "category", "budget", "actual_amount"]]
    print(top.to_string(index=False))
    print()

    total_budget = df["budget_num"].sum()
    total_actual = df["actual_num"].sum()
    variance = total_actual - total_budget
    print("--- TOTALS ---")
    print(f"Budget : EUR {total_budget:,.2f}")
    print(f"Actual : EUR {total_actual:,.2f}")
    print(f"Variance: EUR {variance:+,.2f} ({variance / total_budget * 100:+.2f}%)")


if __name__ == "__main__":
    main()
