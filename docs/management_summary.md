# H1 2026 Expense Variance Review — Management Summary

**Synthetic educational dataset · Not an audit, assurance engagement or financial advice**

| Budget | Actual | Variance | Variance % |
|---:|---:|---:|---:|
| €2,027,058 | €2,086,437 | **+€59,380** | **+2.93%** |

*Clean ledger: 442 of 454 lines. Ten rows (€51,542) quarantined; two out-of-period
rows (€23,289) excluded; 18 included lines flagged for review. Reconciliation
balances to zero.*

## What we found

**1. Freight is the largest adverse category: +€30,829 (+16.7%).**
June alone is +€21,340 (+44.6%), driven by one expedited air-freight line:
€18,943 actual against €3,865 budget (+€15,077, +390%). Even excluding that line,
June freight is still +€6,263 (+14.3%) once that line and its budget are removed,
so this is not only a one-off.

**2. Maintenance is second: +€25,776 (+16.5%).**
January accounts for +€14,081 (+61.7%), including an emergency chiller
replacement at €15,115 against €2,775 budget (+€12,340, +445%). The description
says "replacement", which raises a capital-versus-revenue question as well as a
cost question.

**3. Data quality is material to the numbers.**
Two exact duplicate pairs (€7,289), six mislabelled categories, three unbudgeted
lines (€10,422) and four credit notes (€5,294) were identified. Payment
duplication cannot be tested without payment records. The clean ledger is
reconciled, but 18 lines remain flagged.

## Questions for management

1. What operational event drove the June air freight, was it approved before
   dispatch, and was the invoiced amount consistent with the contracted rate?
2. Was the chiller a repair or a capital replacement, who approved it, and how
   should it be classified?
3. Were both invoices in each duplicate pair paid, or was one a double posting?
4. Are the payroll underspends (−€26,110) due to vacancies or timing, and do the
   utilities credit notes relate to the current period?

## Recommended next steps

1. Obtain the evidence listed in `docs/follow_up_items.md` for the three
   selected items.
2. Match the duplicate pairs to the payment run and confirm whether cash moved.
3. Confirm the VAT basis (currently assumed VAT-exclusive) before restating any
   percentage.
4. Correct the category master data and add upload validation for category,
   date, description and non-negative budget.
5. Add a period-close date scan and a budget-coverage check before commitment.
6. Re-run the analysis when evidence is received; restate only what the evidence
   supports.

## What this is not

This is a first-pass analytical review of synthetic data. It does not express an
audit opinion, provide assurance, or conclude that any variance is an error or
fraud. Each item is a question requiring evidence, not an accusation.

---

*Prepared 2026-11-22 · Version 1.0 · PDF: `docs/management_summary.pdf` · Sources:
`docs/methodology.md`, `docs/data_quality_report.md`,
`docs/variance_commentary.md`, `docs/follow_up_items.md`,
`docs/risk_control_matrix.md`*
