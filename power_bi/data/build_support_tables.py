#!/usr/bin/env python3
"""Build the three small supporting tables for the Power BI report.

These are convenience extracts so the report can show the control-test
scorecard, the risk matrix and the selected follow-ups without duplicating
long prose. They are derived from, and must stay consistent with:

* ``sql/output/04_control_tests.txt``   -> control_tests.csv
* ``docs/risk_control_matrix.md``        -> risk_matrix.csv
* ``docs/follow_up_items.md``            -> selected_follow_ups.csv

Run from the repository root::

    python power_bi/data/build_support_tables.py

Educational synthetic data only. Not an audit opinion.
"""

from __future__ import annotations

import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent


CONTROL_TESTS = [
    ["test_id", "test_name", "population_rows", "exception_rows", "exception_amount_eur", "outcome", "result", "evidence_gap"],
    ["T01", "Exact duplicate invoice / posting", 454, 2, "7289.32", "Exceptions found",
     "2 exact duplicate pairs: TXN-2364/TXN-2451 and TXN-2348/TXN-2452; later copies quarantined",
     "No payment or bank records, so a duplicate payment cannot be ruled out"],
    ["T02", "Near duplicate", 454, 4, "14459.40", "Exceptions found",
     "2 near-duplicate pairs 1-2 days apart; all 4 rows retained and flagged",
     "No delivery or invoice reference to confirm separate purchases"],
    ["T03", "Out-of-period posting", 454, 2, "23288.60", "Exceptions found",
     "2025-12-28 (TXN-2280) and 2026-07-03 (TXN-2121) excluded from the clean ledger",
     "No accrual schedule or close checklist to test the cut-off control"],
    ["T04", "Negative budget", 454, 1, "2500.00", "Exceptions found",
     "TXN-2198 carries a -EUR 2,500 budget and is quarantined",
     "No approval trail to explain how a negative budget was entered"],
    ["T05", "Category master compliance", 454, 0, "0.00", "Clean after correction",
     "6 non-canonical labels mapped to canonical categories; 0 unmapped labels remain",
     "None for recording; the category policy document is not available"],
    ["T06", "Unbudgeted spend", 454, 3, "10421.61", "Exceptions found",
     "TXN-2040, TXN-2248 and TXN-2336 have zero budget and a positive actual",
     "No budget-approval record to test whether the spend was authorised"],
    ["T07", "Credit notes", 454, 4, "5293.69", "Exceptions found",
     "4 credit notes retained and flagged for matching",
     "No invoice reference, so credits cannot be matched to original invoices"],
    ["T08", "Review-threshold items", 442, 19, "", "Screen populated",
     "19 included lines pass |variance| >= EUR 1,000 and |variance %| >= 10%",
     "Not an exception population; this is a prioritisation screen"],
    ["T09", "Reconciliation", 454, 0, "0.00", "Clean",
     "Raw minus excluded minus clean = 0.00 on rows, budget and actual",
     "None"],
]


RISK_MATRIX = [
    ["risk_id", "risk", "possible_cause", "proposed_control", "evidence_needed", "test_question", "result_in_dataset", "design_testable", "operating_testable", "priority_rank"],
    [1, "Supplier paid twice / invoice recorded twice",
     "Manual keying, re-submitted invoice, no duplicate check",
     "Duplicate-invoice check before payment; unique invoice reference; three-way match",
     "Invoice number, supplier, amount, payment record, bank statement",
     "Are duplicate invoice numbers or identical amounts flagged before payment?",
     "2 exact duplicate pairs found (EUR 7,289.32); payment status unknown",
     "Yes", "No", 1],
    [2, "Purchase without approval",
     "Limit exceeded, emergency purchase, approval bypassed",
     "Delegated approval matrix; PO required above threshold; system-enforced limits",
     "Purchase order, approval record, workflow log, invoice",
     "Was approval obtained before the purchase, and by the right authority?",
     "Not testable: no PO or approval field. Three unbudgeted lines (EUR 10,421.61) prompt the question but do not prove a bypass",
     "Yes", "No", 8],
    [3, "Incorrect expense coding",
     "Free-text categories, unclear taxonomy, manual coding",
     "Defined category list; mandatory pick-list; periodic coding review",
     "Ledger description, coding policy, category master",
     "Is the category consistent with the policy and the description?",
     "Partly testable: 6 non-canonical labels corrected, 0 unmapped after mapping; 2 blank descriptions (EUR 19,040.17) cannot be coded",
     "Yes", "Partly", 9],
    [4, "Unbudgeted spend",
     "No budget line, mid-year initiative, budget moved elsewhere",
     "Budget coverage check before commitment; supplementary budget process",
     "Budget approval, revised budget, PO",
     "Was a budget approved, and if not, who authorised the spend?",
     "Testable: 3 unbudgeted lines, EUR 10,421.61 (TXN-2040, TXN-2248, TXN-2336)",
     "Yes", "Partly", 4],
    [5, "Capital expenditure treated as repairs",
     "Replacement coded as maintenance; no capitalisation review",
     "Capitalisation policy; capex threshold; asset-register check",
     "Work order, asset register, capitalisation policy, approval",
     "Is the chiller replacement capital or revenue, and who decided?",
     "Not testable from the ledger alone: TXN-2326 (EUR 15,115.25) is the candidate",
     "Yes", "No", 3],
    [6, "Freight cost overrun / rate leakage",
     "Spot rates, fuel surcharge, expedited mode, volume spike",
     "Contracted rate card; shipment approval; monthly freight review",
     "Carrier contract, rate card, shipment log, invoice",
     "Was the invoiced rate consistent with the contract, and was expedited mode approved?",
     "Testable at total level: freight +EUR 30,829 (+16.7%); June +44.6%; one line +EUR 15,077",
     "Yes", "Partly", 2],
    [7, "Credit notes unmatched or mis-periodised",
     "Credit received without original invoice; prior-period credit",
     "Credit-note matching; supplier statement reconciliation; period allocation rule",
     "Credit note, original invoice, supplier statement, accrual schedule",
     "Is each credit matched to an original invoice and allocated to the right period?",
     "Not testable: 4 credit notes (EUR 5,293.69) but no invoice reference field",
     "Yes", "No", 7],
    [8, "Period cut-off error",
     "Late posting, accrual missed, manual journal",
     "Close checklist; date validation; accrual and prepayment review",
     "Ledger date, GRN date, accrual schedule, close checklist",
     "Are there transactions dated outside the period, and were they accrued in the right month?",
     "Testable: 2 out-of-period rows (EUR 23,288.60) dated 2025-12-28 and 2026-07-03",
     "Yes", "Partly", 6],
    [9, "Poor data quality in reporting",
     "Manual uploads, free-text fields, no validation",
     "Upload validation rules; mandatory fields; DQ exception review",
     "DQ log, upload specification, review sign-off",
     "Are exceptions identified, reviewed and resolved before reporting?",
     "Testable: 37 unique flagged rows (7 corrected, 18 flagged, 10 quarantined, 2 out-of-period)",
     "Yes", "Partly", 5],
]


SELECTED_FOLLOW_UPS = [
    ["item_no", "item", "transactions", "date", "department", "category", "budget_eur", "actual_eur", "variance_eur", "variance_pct", "at_risk_eur", "status", "observation", "evidence_required", "next_step"],
    [1, "Expedited air freight", "TXN-2166", "2026-06-16", "Store Operations", "Freight & Delivery", "3865.26", "18942.63", "15077.37", "390.07", "15077.37", "Evidence requested",
     "Single freight line at 4.9x budget; 71% of the June freight overspend; freight adverse in 5 of 6 months",
     "Carrier invoice and booking reference; PO or approval; rate card or spot quote; reason for shipment; proof of delivery; any budget revision",
     "Request the six evidence items from Logistics & Supply and compare the invoice to the rate card"],
    [2, "Emergency chiller replacement", "TXN-2326", "2026-01-12", "Logistics & Supply", "Maintenance & Repairs", "2774.89", "15115.25", "12340.36", "444.72", "12340.36", "Evidence requested",
     "Single maintenance line at 5.4x budget; 88% of the January maintenance overspend; possible capital-versus-revenue question",
     "Work order and fault report; quote, invoice and payment; approval record; asset register and capitalisation policy; repair-or-replace evidence; insurance or warranty",
     "Request the work order, approval and asset-register evidence; reclassify if capital"],
    [3, "Duplicate invoice pair", "TXN-2364 / TXN-2451; TXN-2348 / TXN-2452", "2026-05-03 and 2026-01-16", "Logistics & Supply; IT & Systems", "Payroll & Overtime; Office & Supplies", "", "", "", "", "7289.32", "Evidence requested",
     "Two pairs share date, department, category, description, budget and actual; later copies quarantined; payment status unknown",
     "Invoice image for each; payment record and bank statement; supplier statement; goods-received note; AP posting and approval trail",
     "Match each pair to the payment run; remove the duplicate if only one payment exists, otherwise obtain the second invoice and test the duplicate control"],
]


def write_csv(path: Path, rows: list) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)
    print(f"wrote {path.relative_to(path.parents[2])}  ({len(rows) - 1} data rows)")


def main() -> None:
    write_csv(OUT / "control_tests.csv", CONTROL_TESTS)
    write_csv(OUT / "risk_matrix.csv", RISK_MATRIX)
    write_csv(OUT / "selected_follow_ups.csv", SELECTED_FOLLOW_UPS)


if __name__ == "__main__":
    main()
