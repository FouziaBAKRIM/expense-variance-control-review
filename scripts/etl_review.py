#!/usr/bin/env python3
"""Data-quality and variance pipeline for the synthetic H1 2026 expense review.

Implements the rules documented in ``docs/methodology.md``:

* date parsing and cut-off policy
* category normalisation with an audit trail
* duplicate, negative, unbudgeted and outlier checks
* three-way disposition (include / include-and-flag / quarantine)
* variance and guarded variance %
* reconciliation, DQ summary and analysis extracts

Educational exercise only. Synthetic data; not an audit opinion.

Usage:
    python scripts/etl_review.py
"""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_CSV = BASE_DIR / "data" / "synthetic_retail_expenses.csv"
OUT_DIR = BASE_DIR / "data" / "processed"

PERIOD_START = date(2026, 1, 1)
PERIOD_END = date(2026, 6, 30)
BUDGET_PCT_FLOOR = 100.0
OUTLIER_MULTIPLE = 3.0
REVIEW_AMOUNT_EUR = 1_000.0
REVIEW_PCT = 10.0

CANONICAL_CATEGORIES = [
    "Payroll & Overtime",
    "Utilities & Rent",
    "Freight & Delivery",
    "Digital Ads & Promo",
    "Software & Cloud",
    "Maintenance & Repairs",
    "Professional Services",
    "Office & Supplies",
]

CANONICAL_DEPARTMENTS = [
    "Store Operations",
    "Marketing",
    "Finance & Admin",
    "IT & Systems",
    "Logistics & Supply",
]

CATEGORY_ALIASES = {
    "freight & delivery": "Freight & Delivery",
    "freight and delivery": "Freight & Delivery",
    "logisitcs & freight": "Freight & Delivery",
    "logistics & freight": "Freight & Delivery",
    "software & cloud": "Software & Cloud",
}

INCLUDED_DISPOSITIONS = {"INCLUDE", "CORRECT_AND_INCLUDE", "INCLUDE_FLAGGED"}


def normalise_label(value: object) -> str:
    """Trim and collapse internal whitespace."""
    return re.sub(r"\s+", " ", str(value).strip())


CATEGORY_LOOKUP = {c.lower(): c for c in CANONICAL_CATEGORIES}
CATEGORY_LOOKUP.update(CATEGORY_ALIASES)


def map_category(value: object) -> str | None:
    key = normalise_label(value).lower()
    return CATEGORY_LOOKUP.get(key)


def parse_date(value: object) -> tuple[date | None, str | None]:
    raw = "" if pd.isna(value) else str(value).strip()
    if not raw:
        return None, "MISSING_DATE"
    try:
        return date.fromisoformat(raw), None
    except ValueError:
        pass
    for fmt in ("%d-%b-%y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw, fmt).date(), "DATE_FORMAT_NORMALISED"
        except ValueError:
            continue
    return None, "INVALID_DATE"


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW_CSV, dtype=str, keep_default_na=False)
    df.columns = [c.strip().lower() for c in df.columns]
    required = {"txn_id", "date", "department", "category", "description", "budget", "actual_amount"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["budget"] = pd.to_numeric(df["budget"], errors="coerce")
    df["actual_amount"] = pd.to_numeric(df["actual_amount"], errors="coerce")
    return df.sort_values("txn_id").reset_index(drop=True)


def add_checks(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- dates -------------------------------------------------------------
    parsed = df["date"].apply(parse_date)
    df["parsed_date"] = [p[0] for p in parsed]
    df["date_issue"] = [p[1] for p in parsed]
    df["month"] = df["parsed_date"].apply(lambda d: d.strftime("%Y-%m") if d else "UNKNOWN")
    df["out_of_period"] = df["parsed_date"].apply(
        lambda d: bool(d and (d < PERIOD_START or d > PERIOD_END))
    )

    # --- labels ------------------------------------------------------------
    df["category_raw"] = df["category"]
    df["category"] = df["category"].apply(map_category)
    df["category_corrected"] = df["category"].notna() & (df["category_raw"] != df["category"])
    df["invalid_category"] = df["category"].isna()
    df.loc[df["invalid_category"], "category"] = "UNMAPPED"

    df["department"] = df["department"].apply(normalise_label)
    df["invalid_department"] = ~df["department"].isin(CANONICAL_DEPARTMENTS)

    # --- amounts -----------------------------------------------------------
    df["invalid_amount"] = df["budget"].isna() | df["actual_amount"].isna()
    df["negative_budget"] = df["budget"] < 0
    df["credit_note"] = df["actual_amount"] < 0
    df["unbudgeted"] = (df["budget"] == 0) & (df["actual_amount"] > 0)
    df["tiny_budget"] = (df["budget"] > 0) & (df["budget"] < BUDGET_PCT_FLOOR)
    df["zero_activity"] = (df["budget"] == 0) & (df["actual_amount"] == 0)
    df["blank_description"] = df["description"].str.strip() == ""

    # --- outliers (robust, category median) --------------------------------
    median_actual = df.groupby("category")["actual_amount"].transform("median")
    df["outlier"] = df["actual_amount"] > (OUTLIER_MULTIPLE * median_actual)

    # --- exact duplicates (keep earliest txn_id) ---------------------------
    dup_key = ["date", "department", "category_raw", "description", "budget", "actual_amount"]
    df["exact_duplicate"] = df.duplicated(subset=dup_key, keep="first")

    # --- near duplicates (same description and amount, date within 2 days) --
    df["near_duplicate"] = False
    group_cols = ["department", "category", "description", "actual_amount"]
    for _, group in df.groupby(group_cols, dropna=False):
        if len(group) < 2:
            continue
        indices = list(group.index)
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                a, b = indices[i], indices[j]
                date_a, date_b = df.at[a, "parsed_date"], df.at[b, "parsed_date"]
                if pd.isna(date_a) or pd.isna(date_b) or date_a == date_b:
                    continue
                if abs((date_a - date_b).days) <= 2:
                    df.at[a, "near_duplicate"] = True
                    df.at[b, "near_duplicate"] = True

    return df


def build_flags(row: pd.Series) -> str:
    flags: list[str] = []
    if row["exact_duplicate"]:
        flags.append("EXACT_DUPLICATE")
    if row["date_issue"] == "MISSING_DATE":
        flags.append("MISSING_DATE")
    if row["date_issue"] == "INVALID_DATE":
        flags.append("INVALID_DATE")
    if row["date_issue"] == "DATE_FORMAT_NORMALISED":
        flags.append("DATE_FORMAT_NORMALISED")
    if row["out_of_period"]:
        flags.append("OUT_OF_PERIOD_DATE")
    if row["invalid_category"]:
        flags.append("INVALID_CATEGORY")
    if row["category_corrected"]:
        flags.append("CATEGORY_NORMALISED")
    if row["invalid_department"]:
        flags.append("INVALID_DEPARTMENT")
    if row["invalid_amount"]:
        flags.append("INVALID_AMOUNT")
    if row["negative_budget"]:
        flags.append("NEGATIVE_BUDGET")
    if row["credit_note"]:
        flags.append("CREDIT_NOTE")
    if row["unbudgeted"]:
        flags.append("UNBUDGETED")
    if row["tiny_budget"]:
        flags.append("TINY_BUDGET")
    if row["zero_activity"]:
        flags.append("ZERO_ACTIVITY")
    if row["near_duplicate"]:
        flags.append("NEAR_DUPLICATE")
    if row["outlier"]:
        flags.append("OUTLIER")
    if row["blank_description"]:
        flags.append("BLANK_DESCRIPTION")
    return "|".join(flags) if flags else "CLEAN"


def assign_disposition(row: pd.Series) -> str:
    if row["exact_duplicate"]:
        return "QUARANTINE"
    if row["invalid_amount"]:
        return "QUARANTINE"
    if row["date_issue"] in {"MISSING_DATE", "INVALID_DATE"}:
        return "QUARANTINE"
    if row["invalid_category"] or row["invalid_department"]:
        return "QUARANTINE"
    if row["negative_budget"]:
        return "QUARANTINE"
    if row["zero_activity"]:
        return "QUARANTINE"
    if row["out_of_period"]:
        return "EXCLUDE_OUT_OF_PERIOD"
    if (
        row["near_duplicate"]
        or row["credit_note"]
        or row["unbudgeted"]
        or row["tiny_budget"]
        or row["outlier"]
        or row["blank_description"]
    ):
        return "INCLUDE_FLAGGED"
    if row["category_corrected"] or row["date_issue"] == "DATE_FORMAT_NORMALISED":
        return "CORRECT_AND_INCLUDE"
    return "INCLUDE"


def exclusion_bucket(row: pd.Series) -> str:
    if row["disposition"] in INCLUDED_DISPOSITIONS:
        return "Included"
    if row["disposition"] == "EXCLUDE_OUT_OF_PERIOD":
        return "Out of period"
    if row["exact_duplicate"]:
        return "Exact duplicate"
    if row["invalid_amount"]:
        return "Invalid amount"
    if row["date_issue"] in {"MISSING_DATE", "INVALID_DATE"}:
        return "Missing/invalid date"
    if row["negative_budget"]:
        return "Negative budget"
    if row["invalid_category"] or row["invalid_department"]:
        return "Invalid category/department"
    if row["zero_activity"]:
        return "Zero activity"
    return "Other quarantine"


def add_variance(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["variance_eur"] = (df["actual_amount"] - df["budget"]).round(2)
    df["variance_pct"] = pd.NA
    mask = (
        df["budget"].notna()
        & df["actual_amount"].notna()
        & (df["budget"] >= BUDGET_PCT_FLOOR)
    )
    df.loc[mask, "variance_pct"] = (
        (df.loc[mask, "variance_eur"] / df.loc[mask, "budget"]) * 100
    ).round(2)
    return df


def write_reconciliation(df: pd.DataFrame) -> pd.DataFrame:
    order = [
        "Included",
        "Exact duplicate",
        "Missing/invalid date",
        "Negative budget",
        "Out of period",
        "Invalid amount",
        "Invalid category/department",
        "Zero activity",
        "Other quarantine",
    ]
    grouped = (
        df.groupby("exclusion_bucket")
        .agg(rows=("txn_id", "size"), budget_eur=("budget", "sum"), actual_eur=("actual_amount", "sum"))
        .reindex(order)
        .fillna(0)
        .reset_index()
    )
    grouped = grouped.rename(columns={"exclusion_bucket": "bucket"})
    grouped["budget_eur"] = grouped["budget_eur"].round(2)
    grouped["actual_eur"] = grouped["actual_eur"].round(2)

    raw = df.agg({"txn_id": "size", "budget": "sum", "actual_amount": "sum"})
    clean = df[df["disposition"].isin(INCLUDED_DISPOSITIONS)]
    clean_totals = clean.agg({"txn_id": "size", "budget": "sum", "actual_amount": "sum"})

    rows = [{"bucket": "Raw file", "rows": int(raw["txn_id"]), "budget_eur": round(raw["budget"], 2), "actual_eur": round(raw["actual_amount"], 2)}]
    for _, r in grouped.iterrows():
        if r["bucket"] == "Included":
            continue
        if int(r["rows"]) == 0:
            continue
        rows.append(
            {
                "bucket": f"Less: {r['bucket']}",
                "rows": int(r["rows"]),
                "budget_eur": -round(r["budget_eur"], 2),
                "actual_eur": -round(r["actual_eur"], 2),
            }
        )
    rows.append(
        {
            "bucket": "Clean ledger",
            "rows": int(clean_totals["txn_id"]),
            "budget_eur": round(clean_totals["budget"], 2),
            "actual_eur": round(clean_totals["actual_amount"], 2),
        }
    )
    bridge = pd.DataFrame(rows)
    bridge["variance_eur"] = (bridge["actual_eur"] - bridge["budget_eur"]).round(2)

    check_budget = round(bridge["budget_eur"].iloc[:-1].sum() - bridge["budget_eur"].iloc[-1], 2)
    check_actual = round(bridge["actual_eur"].iloc[:-1].sum() - bridge["actual_eur"].iloc[-1], 2)
    bridge.loc[len(bridge)] = {
        "bucket": "CHECK (must be 0.00)",
        "rows": 0,
        "budget_eur": check_budget,
        "actual_eur": check_actual,
        "variance_eur": 0.0,
    }
    bridge.to_csv(OUT_DIR / "reconciliation.csv", index=False)
    return bridge


def write_dq_summary(df: pd.DataFrame) -> None:
    def amount(mask: pd.Series, basis: str) -> float:
        return round(float(df.loc[mask, basis].abs().sum()), 2)

    checks = [
        ("DQ01", "Exact duplicate", "Same date, department, category, description, budget and actual; later txn_id", df["exact_duplicate"], "actual_amount", "QUARANTINE"),
        ("DQ02", "Near duplicate", "Same department, category, description and actual; date within 2 days", df["near_duplicate"], "actual_amount", "INCLUDE_FLAGGED"),
        ("DQ03", "Missing date", "Date field is blank", df["date_issue"] == "MISSING_DATE", "actual_amount", "QUARANTINE"),
        ("DQ04", "Invalid date", "Date is not parseable with the approved formats", df["date_issue"] == "INVALID_DATE", "actual_amount", "QUARANTINE"),
        ("DQ05", "Date format normalised", "Non-ISO but unambiguous date", df["date_issue"] == "DATE_FORMAT_NORMALISED", "actual_amount", "CORRECT_AND_INCLUDE"),
        ("DQ06", "Out of period", "Date outside 2026-01-01 to 2026-06-30", df["out_of_period"], "actual_amount", "EXCLUDE_OUT_OF_PERIOD"),
        ("DQ07", "Non-canonical category", "Label mapped to a canonical category", df["category_corrected"], "actual_amount", "CORRECT_AND_INCLUDE"),
        ("DQ08", "Invalid category", "Label cannot be mapped to a canonical category", df["invalid_category"], "actual_amount", "QUARANTINE"),
        ("DQ09", "Invalid department", "Department outside the approved list", df["invalid_department"], "actual_amount", "QUARANTINE"),
        ("DQ10", "Invalid amount", "Budget or actual is not numeric", df["invalid_amount"], "actual_amount", "QUARANTINE"),
        ("DQ11", "Negative budget", "Budget below zero", df["negative_budget"], "budget", "QUARANTINE"),
        ("DQ12", "Credit note", "Negative actual amount (credit or refund)", df["credit_note"], "actual_amount", "INCLUDE_FLAGGED"),
        ("DQ13", "Unbudgeted spend", "Budget is zero and actual is positive", df["unbudgeted"], "actual_amount", "INCLUDE_FLAGGED"),
        ("DQ14", "Tiny budget", "Budget above zero but below 100 EUR", df["tiny_budget"], "actual_amount", "INCLUDE_FLAGGED"),
        ("DQ15", "Extreme outlier", "Actual above 3x the category median", df["outlier"], "variance_eur", "INCLUDE_FLAGGED"),
        ("DQ16", "Blank description", "Description is empty", df["blank_description"], "actual_amount", "INCLUDE_FLAGGED"),
        ("DQ17", "Zero activity", "Budget and actual are both zero", df["zero_activity"], "actual_amount", "QUARANTINE"),
    ]
    rows = []
    for check_id, name, rule, mask, basis, disposition in checks:
        rows.append(
            {
                "check_id": check_id,
                "check_name": name,
                "rule": rule,
                "rows_affected": int(mask.sum()),
                "amount_affected_eur": amount(mask, basis),
                "amount_basis": basis,
                "disposition": disposition,
            }
        )
    pd.DataFrame(rows).to_csv(OUT_DIR / "dq_summary.csv", index=False)


def write_analysis(df: pd.DataFrame) -> None:
    included = df[df["disposition"].isin(INCLUDED_DISPOSITIONS)].copy()

    def summarise(group_cols: list[str]) -> pd.DataFrame:
        out = (
            included.groupby(group_cols, dropna=False)
            .agg(
                txn_count=("txn_id", "size"),
                budget_eur=("budget", "sum"),
                actual_eur=("actual_amount", "sum"),
                variance_eur=("variance_eur", "sum"),
            )
            .reset_index()
        )
        out["variance_pct"] = pd.NA
        mask = out["budget_eur"] >= BUDGET_PCT_FLOOR
        out.loc[mask, "variance_pct"] = (
            (out.loc[mask, "variance_eur"] / out.loc[mask, "budget_eur"]) * 100
        ).round(2)
        for col in ["budget_eur", "actual_eur", "variance_eur"]:
            out[col] = out[col].round(2)
        return out.sort_values("variance_eur", ascending=False)

    by_category = summarise(["category"])
    by_category["rank_adverse"] = by_category["variance_eur"].rank(ascending=False, method="min").astype(int)
    by_category["rank_favourable"] = by_category["variance_eur"].rank(ascending=True, method="min").astype(int)
    by_category.to_csv(OUT_DIR / "summary_by_category.csv", index=False)

    summarise(["month"]).sort_values("month").to_csv(OUT_DIR / "summary_by_month.csv", index=False)
    summarise(["month", "category"]).to_csv(OUT_DIR / "summary_by_month_category.csv", index=False)
    summarise(["department"]).to_csv(OUT_DIR / "summary_by_department.csv", index=False)

    top = included.sort_values("variance_eur", ascending=False).head(15)[
        ["txn_id", "date", "department", "category", "description", "budget", "actual_amount", "variance_eur", "variance_pct", "dq_flags"]
    ]
    top.to_csv(OUT_DIR / "top_adverse_items.csv", index=False)

    bottom = included.sort_values("variance_eur", ascending=True).head(15)[
        ["txn_id", "date", "department", "category", "description", "budget", "actual_amount", "variance_eur", "variance_pct", "dq_flags"]
    ]
    bottom.to_csv(OUT_DIR / "top_favourable_items.csv", index=False)

    candidates = included[
        (included["variance_eur"].abs() >= REVIEW_AMOUNT_EUR)
        | included["unbudgeted"]
        | included["credit_note"]
        | included["outlier"]
    ].copy()
    candidates["review_reason"] = candidates.apply(
        lambda r: "; ".join(
            reason
            for reason, condition in [
                ("Large adverse variance", r["variance_eur"] >= REVIEW_AMOUNT_EUR),
                ("Large favourable variance", r["variance_eur"] <= -REVIEW_AMOUNT_EUR),
                ("Unbudgeted spend", r["unbudgeted"]),
                ("Credit note", r["credit_note"]),
                ("Statistical outlier", r["outlier"]),
            ]
            if condition
        ),
        axis=1,
    )
    candidates.sort_values("variance_eur", ascending=False).to_csv(
        OUT_DIR / "follow_up_candidates.csv", index=False
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_raw()
    df = add_checks(df)
    df["dq_flags"] = df.apply(build_flags, axis=1)
    df["disposition"] = df.apply(assign_disposition, axis=1)
    df["exclusion_bucket"] = df.apply(exclusion_bucket, axis=1)
    df["needs_review"] = df["disposition"] == "INCLUDE_FLAGGED"
    df["included"] = df["disposition"].isin(INCLUDED_DISPOSITIONS)
    df = add_variance(df)

    df["date"] = df["parsed_date"].apply(lambda d: d.isoformat() if d else "")

    output_cols = [
        "txn_id",
        "date",
        "month",
        "department",
        "category",
        "category_raw",
        "description",
        "budget",
        "actual_amount",
        "variance_eur",
        "variance_pct",
        "disposition",
        "dq_flags",
        "needs_review",
        "included",
    ]
    audited = df[output_cols].sort_values("txn_id")
    audited.to_csv(OUT_DIR / "expenses_audited_all.csv", index=False)

    included = audited[audited["included"]]
    included.to_csv(OUT_DIR / "expenses_clean.csv", index=False)
    exceptions = audited[audited["dq_flags"] != "CLEAN"]
    exceptions.to_csv(OUT_DIR / "dq_exceptions_log.csv", index=False)

    mapping_log = audited[audited["category_raw"] != audited["category"]]
    mapping_log[["txn_id", "category_raw", "category", "disposition"]].to_csv(
        OUT_DIR / "category_mapping_log.csv", index=False
    )

    write_dq_summary(df)
    bridge = write_reconciliation(df)
    write_analysis(df)

    print("Pipeline complete")
    print(f"Rows raw          : {len(audited)}")
    print(f"Rows included     : {len(included)}")
    print(f"Rows quarantined  : {(audited['disposition'] == 'QUARANTINE').sum()}")
    print(f"Rows out of period: {(audited['disposition'] == 'EXCLUDE_OUT_OF_PERIOD').sum()}")
    print(f"Rows flagged      : {int(audited['needs_review'].sum())}")
    print()
    print("Reconciliation:")
    print(bridge.to_string(index=False))
    print()
    print("Totals (included):")
    print(f"  Budget  EUR {included['budget'].sum():,.2f}")
    print(f"  Actual  EUR {included['actual_amount'].sum():,.2f}")
    print(f"  Variance EUR {included['variance_eur'].sum():+,.2f}")


if __name__ == "__main__":
    main()
