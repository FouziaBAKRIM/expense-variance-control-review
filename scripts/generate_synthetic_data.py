#!/usr/bin/env python3
"""Generate a synthetic retail expense ledger for an educational variance review.

WARNING
-------
This script produces **synthetic educational data only**. It does not contain,
and must never be used with, real employer, client, bank, payroll or personal
financial data. Output is not an audit opinion, assurance engagement or
financial advice.

The dataset is deterministic for a given seed, so the same CSV can be
regenerated and verified by a reviewer.

Usage
-----
    python scripts/generate_synthetic_data.py --rows 450 --seed 20261122
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUT = BASE_DIR / "data" / "synthetic_retail_expenses.csv"

LABEL = "SYNTHETIC_EDUCATIONAL"
CURRENCY = "EUR"
PERIOD_START = date(2026, 1, 1)
PERIOD_END = date(2026, 6, 30)
MONTHS = [(2026, m) for m in range(1, 7)]

DEPARTMENT_WEIGHTS = {
    "Store Operations": 0.30,
    "Marketing": 0.18,
    "Finance & Admin": 0.16,
    "IT & Systems": 0.18,
    "Logistics & Supply": 0.18,
}

# Budget ranges are illustrative monthly values in EUR, per transaction.
# "drift" is the average actual-vs-budget gap baked into the scenario.
CATEGORIES = {
    "Payroll & Overtime": {
        "weight": 0.14,
        "budget": (6000, 14000),
        "drift": -0.025,
        "departments": [
            "Store Operations",
            "Marketing",
            "Finance & Admin",
            "IT & Systems",
            "Logistics & Supply",
        ],
        "vendors": ["ADP Payroll Services", "Randstad Temp Staffing", "internal payroll team"],
        "details": [
            "Monthly payroll allocation - store staff",
            "Weekend overtime - peak trading",
            "Temporary staff - seasonal cover",
            "Shift premium - night replenishment",
            "Agency cover - absence",
        ],
    },
    "Utilities & Rent": {
        "weight": 0.14,
        "budget": (3500, 9000),
        "drift": 0.03,
        "departments": ["Store Operations", "Finance & Admin", "Logistics & Supply"],
        "vendors": ["Engie Pro Energy", "Veolia Water", "Klepierre Retail Leases"],
        "details": [
            "Store lease - monthly",
            "Electricity consumption - stores",
            "Gas & heating",
            "Water & waste",
            "Service charge - retail park",
        ],
    },
    "Freight & Delivery": {
        "weight": 0.13,
        "budget": (1800, 6000),
        "drift": 0.14,
        "departments": ["Logistics & Supply", "Store Operations"],
        "vendors": ["DHL Freight Europe", "Geodis Logistics", "Chronopost Pro"],
        "details": [
            "Inbound freight - regional hub",
            "Outbound delivery - last mile",
            "Pallet transfer - cross dock",
            "Return logistics - reverse flow",
            "Carrier fuel surcharge",
        ],
    },
    "Digital Ads & Promo": {
        "weight": 0.10,
        "budget": (1500, 5500),
        "drift": -0.05,
        "departments": ["Marketing"],
        "vendors": ["Google Ads EMEA", "Meta Ads Ireland", "JCDecaux Retail Display"],
        "details": [
            "Paid search - brand keywords",
            "Paid social - campaign flight",
            "Retail media - in-store screens",
            "Affiliate commission",
            "Programmatic display",
        ],
    },
    "Software & Cloud": {
        "weight": 0.12,
        "budget": (1200, 5000),
        "drift": 0.06,
        "departments": ["IT & Systems", "Finance & Admin", "Marketing"],
        "vendors": ["Snowflake Inc", "Salesforce EMEA", "Microsoft Azure", "Datadog Cloud"],
        "details": [
            "Cloud compute & storage",
            "SaaS subscription - CRM",
            "Data warehouse consumption",
            "Licence renewal - BI platform",
            "Cyber security tooling",
        ],
    },
    "Maintenance & Repairs": {
        "weight": 0.13,
        "budget": (700, 4000),
        "drift": 0.08,
        "departments": ["Store Operations", "Logistics & Supply", "IT & Systems"],
        "vendors": ["Johnson Controls HVAC", "Otis Elevators", "Rexel Electrical"],
        "details": [
            "Preventive HVAC inspection",
            "Refrigeration repair - store",
            "Lighting & electrical maintenance",
            "Dock door repair",
            "Lift servicing",
        ],
    },
    "Professional Services": {
        "weight": 0.12,
        "budget": (2000, 7000),
        "drift": 0.10,
        "departments": ["Finance & Admin", "IT & Systems", "Marketing"],
        "vendors": ["Deloitte Advisory", "Baker Legal", "Talent Partners", "ProcessWorks Consulting"],
        "details": [
            "External audit support",
            "Legal advisory - leases",
            "Recruitment agency fees",
            "Consulting - process improvement",
            "Tax compliance support",
        ],
    },
    "Office & Supplies": {
        "weight": 0.12,
        "budget": (250, 1500),
        "drift": -0.03,
        "departments": [
            "Store Operations",
            "Marketing",
            "Finance & Admin",
            "IT & Systems",
            "Logistics & Supply",
        ],
        "vendors": ["Staples Business", "VistaPrint", "Amazon Business", "CityPost"],
        "details": [
            "Stationery & consumables",
            "Printing - store signage",
            "IT peripherals",
            "Cleaning supplies",
            "Uniform & PPE",
        ],
    },
}

# Seasonality applied to both budget and actual (so it does not create variance).
MONTH_FACTORS = {
    ("Freight & Delivery", 5): 1.15,
    ("Freight & Delivery", 6): 1.10,
    ("Software & Cloud", 4): 1.12,
    ("Maintenance & Repairs", 3): 1.08,
    ("Utilities & Rent", 1): 1.10,
    ("Utilities & Rent", 2): 1.08,
    ("Digital Ads & Promo", 6): 1.10,
    ("Professional Services", 3): 1.06,
}

PAIRS: list[tuple[str, str]] = []
PAIR_WEIGHTS: list[float] = []
for _cat, _cfg in CATEGORIES.items():
    for _dept in _cfg["departments"]:
        PAIRS.append((_dept, _cat))
        PAIR_WEIGHTS.append(DEPARTMENT_WEIGHTS[_dept] * _cfg["weight"])

COLUMNS = [
    "txn_id",
    "date",
    "department",
    "category",
    "description",
    "budget",
    "actual_amount",
    "data_source",
]


def build_base_rows(rng: random.Random, target: int) -> list[dict]:
    rows: list[dict] = []
    for _ in range(target):
        dept, cat = rng.choices(PAIRS, weights=PAIR_WEIGHTS, k=1)[0]
        cfg = CATEGORIES[cat]
        year, month = rng.choice(MONTHS)
        txn_date = date(year, month, rng.randint(1, 28))

        lo, hi = cfg["budget"]
        month_factor = MONTH_FACTORS.get((cat, month), 1.0)
        budget = round(rng.uniform(lo, hi) * month_factor, 2)

        noise = rng.gauss(0.0, 0.05)
        actual = round(max(budget * (1.0 + cfg["drift"] + noise), 0.0), 2)

        detail = rng.choice(cfg["details"])
        vendor = rng.choice(cfg["vendors"])
        rows.append(
            {
                "txn_id": "",
                "date": txn_date.isoformat(),
                "department": dept,
                "category": cat,
                "description": f"{detail} - {vendor}",
                "budget": budget,
                "actual_amount": actual,
                "data_source": LABEL,
            }
        )
    return rows


def inject_anomalies(rng: random.Random, rows: list[dict]) -> list[dict]:
    """Plant realistic data-quality defects and return an anomaly register."""
    register: list[dict] = []
    base_indices = list(range(len(rows)))
    used: set[int] = set()

    def take(pool: list[int], n: int) -> list[int]:
        available = [i for i in pool if i not in used]
        if len(available) < n:
            raise RuntimeError(f"Not enough rows to plant anomaly (need {n}, have {len(available)})")
        chosen = rng.sample(available, n)
        used.update(chosen)
        return chosen

    by_cat: dict[str, list[int]] = {}
    for i, row in enumerate(rows):
        by_cat.setdefault(row["category"], []).append(i)

    # 1. Inconsistent category labels: casing, whitespace, typos, synonyms.
    variants = [
        ("Freight & Delivery", "freight & delivery"),
        ("Freight & Delivery", "FREIGHT & DELIVERY"),
        ("Freight & Delivery", " Freight & Delivery "),
        ("Freight & Delivery", "Freight and Delivery"),
        ("Freight & Delivery", "Logisitcs & Freight"),
        ("Software & Cloud", "software  & cloud"),
    ]
    for base_cat, variant in variants:
        i = take(by_cat[base_cat], 1)[0]
        original = rows[i]["category"]
        rows[i]["category"] = variant
        register.append(
            {
                "type": "inconsistent_category",
                "row_index": i,
                "note": f"Category '{original}' recorded as '{variant}'",
            }
        )

    # 2. Exact duplicates: full copy of an existing row (new txn_id only).
    for i in take(base_indices, 2):
        rows.append(dict(rows[i]))
        register.append(
            {
                "type": "exact_duplicate",
                "row_index": len(rows) - 1,
                "note": f"Exact copy of row {i}: {rows[i]['description']}",
            }
        )

    # 3. Near duplicates: same amount/description, date shifted by 1-2 days.
    for i in take(base_indices, 2):
        clone = dict(rows[i])
        original_date = date.fromisoformat(rows[i]["date"])
        clone["date"] = (original_date + timedelta(days=rng.choice([1, 2]))).isoformat()
        rows.append(clone)
        register.append(
            {
                "type": "near_duplicate",
                "row_index": len(rows) - 1,
                "note": f"Same amount/description as row {i}, date shifted",
            }
        )

    # 4. Missing dates.
    for i in take(base_indices, 4):
        original = rows[i]["date"]
        rows[i]["date"] = ""
        register.append(
            {"type": "missing_date", "row_index": i, "note": f"Date blank (was {original})"}
        )

    # 5. Malformed / non-ISO dates.
    malformed = ["31/02/2026", "2026-13-05", "15-Jan-26", "2026/04/31"]
    for i, bad in zip(take(base_indices, 4), malformed):
        original = rows[i]["date"]
        rows[i]["date"] = bad
        register.append(
            {"type": "malformed_date", "row_index": i, "note": f"Date '{bad}' (was {original})"}
        )

    # 6. Credit notes / refunds (negative actual, legitimate business event).
    credit_pool = [
        i
        for i in base_indices
        if rows[i]["category"] in {"Freight & Delivery", "Professional Services", "Software & Cloud", "Utilities & Rent"}
    ]
    for i in take(credit_pool, 4):
        amount = round(rng.uniform(400, 2500), 2)
        rows[i]["actual_amount"] = -amount
        rows[i]["description"] = f"Credit note - {rows[i]['description']}"
        register.append(
            {
                "type": "negative_actual",
                "row_index": i,
                "note": f"Credit note of -{amount:,.2f} EUR",
            }
        )

    # 7. Negative budget (entry error).
    i = take(base_indices, 1)[0]
    rows[i]["budget"] = -2500.00
    rows[i]["description"] = "Budget correction entry - negative value (review)"
    register.append(
        {
            "type": "negative_budget",
            "row_index": i,
            "note": "Budget of -2,500.00 EUR",
        }
    )

    # 8. Extreme outliers (realistic one-off operational events).
    outliers = [
        ("Freight & Delivery", 4.2, "Expedited air freight - unplanned replenishment"),
        ("Software & Cloud", 3.5, "Annual licence renewal - billed in one month"),
        ("Maintenance & Repairs", 5.0, "Emergency chiller replacement - store 04"),
    ]
    for cat, factor, note in outliers:
        pool = [
            i
            for i, row in enumerate(rows)
            if row["category"] == cat and i not in used and i in base_indices
        ]
        i = take(pool, 1)[0]
        rows[i]["actual_amount"] = round(rows[i]["actual_amount"] * factor, 2)
        rows[i]["description"] = note
        register.append(
            {
                "type": "extreme_outlier",
                "row_index": i,
                "note": f"{note} (x{factor} actual)",
            }
        )

    # 9. Zero-budget, unbudgeted spend.
    for i in take(base_indices, 3):
        rows[i]["budget"] = 0.00
        rows[i]["actual_amount"] = round(rng.uniform(1500, 6000), 2)
        rows[i]["description"] = f"Unbudgeted spend - {rows[i]['description']}"
        register.append(
            {"type": "zero_budget", "row_index": i, "note": "Budget 0.00 with positive actual"}
        )

    # 10. Tiny budget (denominator not meaningful).
    for i in take(base_indices, 2):
        rows[i]["budget"] = 1.00
        rows[i]["actual_amount"] = round(rng.uniform(800, 2200), 2)
        register.append(
            {"type": "tiny_budget", "row_index": i, "note": "Budget 1.00 EUR"}
        )

    # 11. Out-of-period dates.
    for i, out_date in zip(take(base_indices, 2), ["2025-12-28", "2026-07-03"]):
        original = rows[i]["date"]
        rows[i]["date"] = out_date
        register.append(
            {
                "type": "out_of_period_date",
                "row_index": i,
                "note": f"Date {out_date} (was {original})",
            }
        )

    # 12. Blank descriptions.
    for i in take(base_indices, 2):
        rows[i]["description"] = ""
        register.append(
            {"type": "blank_description", "row_index": i, "note": "Description empty"}
        )

    return register


def assign_ids(rows: list[dict]) -> None:
    for i, row in enumerate(rows):
        row["txn_id"] = f"TXN-{2001 + i:04d}"


def resolve_register(register: list[dict], rows: list[dict]) -> None:
    for entry in register:
        entry["txn_id"] = rows[entry.pop("row_index")]["txn_id"]


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_metadata(path: Path, rows: list[dict], register: list[dict], seed: int) -> None:
    counts = Counter(entry["type"] for entry in register)
    total_budget = round(sum(r["budget"] for r in rows), 2)
    total_actual = round(sum(r["actual_amount"] for r in rows), 2)
    metadata = {
        "dataset_name": "synthetic_retail_expenses",
        "label": LABEL,
        "disclaimer": (
            "Synthetic educational data generated for the Finance, Accounting & Audit "
            "project playbook. Contains no real employer, client, bank, payroll or "
            "personal financial data. Not an audit opinion, assurance engagement or "
            "financial advice."
        ),
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "generator": "scripts/generate_synthetic_data.py",
        "seed": seed,
        "currency": CURRENCY,
        "amount_basis": "VAT-exclusive (net)",
        "reporting_period": {"start": PERIOD_START.isoformat(), "end": PERIOD_END.isoformat()},
        "row_count": len(rows),
        "columns": COLUMNS,
        "totals": {
            "budget": total_budget,
            "actual_amount": total_actual,
            "variance": round(total_actual - total_budget, 2),
        },
        "planted_anomalies": dict(sorted(counts.items())),
        "anomaly_register": register,
    }
    path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=450, help="Number of clean base rows (default: 450)")
    parser.add_argument("--seed", type=int, default=20261122, help="Random seed (default: 20261122)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output CSV path")
    args = parser.parse_args()

    if args.rows < 50:
        parser.error("--rows must be at least 50")

    rng = random.Random(args.seed)
    rows = build_base_rows(rng, args.rows)
    register = inject_anomalies(rng, rows)
    assign_ids(rows)
    resolve_register(register, rows)
    rng.shuffle(rows)

    write_csv(args.out, rows)
    metadata_path = args.out.with_suffix(".metadata.json")
    write_metadata(metadata_path, rows, register, args.seed)

    total_budget = sum(r["budget"] for r in rows)
    total_actual = sum(r["actual_amount"] for r in rows)
    variance = total_actual - total_budget
    variance_pct = variance / total_budget * 100 if total_budget else 0.0

    print(f"Wrote {args.out}")
    print(f"Wrote {metadata_path}")
    print(f"Rows: {len(rows)}")
    print(f"Total budget: EUR {total_budget:,.2f}")
    print(f"Total actual: EUR {total_actual:,.2f}")
    print(f"Variance:     EUR {variance:+,.2f} ({variance_pct:+.2f}%)")
    print("Planted anomalies:")
    for anomaly_type, count in sorted(Counter(e["type"] for e in register).items()):
        print(f"  {anomaly_type:<24} {count}")


if __name__ == "__main__":
    main()
