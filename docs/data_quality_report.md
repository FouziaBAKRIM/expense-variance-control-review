# Data-Quality Report

## H1 2026 Expense Review — Synthetic Educational Dataset

> **Boundary.** Synthetic data; educational exercise. Not an audit, assurance
> engagement or financial advice. No conclusion on fraud or error is drawn.

| | |
|---|---|
| Version | 1.0 |
| Date | 2026-11-22 |
| Source | `data/synthetic_retail_expenses.csv` |
| Rows | 454 |
| Period | 2026-01-01 to 2026-06-30 |
| Pipeline | `scripts/etl_review.py` |
| Rules | `docs/methodology.md` |

---

## 1. Objective

Establish whether the ledger is fit for variance analysis, correct what can be
corrected with an audit trail, quarantine what cannot be validated, and quantify
every adjustment so the clean ledger reconciles to the raw file.

---

## 2. Method

Seventeen checks were run. Each affected transaction received a machine-readable
flag and one of five dispositions:

| Disposition | Meaning |
|---|---|
| `INCLUDE` | Passes all checks |
| `CORRECT_AND_INCLUDE` | Fixable defect, corrected with a logged before/after value |
| `INCLUDE_FLAGGED` | Legitimate but noteworthy; stays in totals and goes to review |
| `QUARANTINE` | Cannot be validated; excluded and disclosed |
| `EXCLUDE_OUT_OF_PERIOD` | Valid but outside H1 2026; excluded and disclosed |

Full row-level output: `data/processed/expenses_audited_all.csv`,
`data/processed/dq_exceptions_log.csv`, `data/processed/dq_summary.csv`.

---

## 3. Reconciliation

| Step | Rows | Budget (EUR) | Actual (EUR) |
|---|---:|---:|---:|
| Raw file | 454 | 2,094,168.45 | 2,161,268.43 |
| Less: exact duplicates | 2 | 7,439.81 | 7,289.32 |
| Less: missing/invalid dates | 7 | 37,322.10 | 37,781.89 |
| Less: negative budget | 1 | (2,500.00) | 6,471.20 |
| Less: out of period | 2 | 24,849.00 | 23,288.60 |
| **Clean ledger** | **442** | **2,027,057.54** | **2,086,437.42** |
| **Check (raw − exclusions − clean)** | **—** | **0.00** | **0.00** |

The negative-budget row is shown in parentheses because removing a −€2,500 budget
*increases* the clean budget. The bridge balances to the cent.

Clean-ledger variance: **+€59,379.88 (+2.93%)**, i.e. adverse.

---

## 4. Check results

| ID | Check | Rows | Amount (EUR) | Basis | Disposition |
|---|---|---:|---:|---|---|
| DQ01 | Exact duplicate | 2 | 7,289.32 | actual | QUARANTINE |
| DQ02 | Near duplicate | 4 | 14,459.40 | actual | INCLUDE_FLAGGED |
| DQ03 | Missing date | 4 | 24,677.13 | actual | QUARANTINE |
| DQ04 | Invalid date | 3 | 13,104.76 | actual | QUARANTINE |
| DQ05 | Date format normalised | 1 | 796.28 | actual | CORRECT_AND_INCLUDE |
| DQ06 | Out of period | 2 | 23,288.60 | actual | EXCLUDE_OUT_OF_PERIOD |
| DQ07 | Non-canonical category | 6 | 20,719.84 | actual | CORRECT_AND_INCLUDE |
| DQ08 | Invalid category | 0 | 0.00 | actual | QUARANTINE |
| DQ09 | Invalid department | 0 | 0.00 | actual | QUARANTINE |
| DQ10 | Invalid amount | 0 | 0.00 | actual | QUARANTINE |
| DQ11 | Negative budget | 1 | 2,500.00 | budget | QUARANTINE |
| DQ12 | Credit note | 4 | 5,293.69 | actual | INCLUDE_FLAGGED |
| DQ13 | Unbudgeted spend | 3 | 10,421.61 | actual | INCLUDE_FLAGGED |
| DQ14 | Tiny budget | 2 | 2,813.99 | actual | INCLUDE_FLAGGED |
| DQ15 | Extreme outlier | 5 | 44,339.57 | variance | INCLUDE_FLAGGED |
| DQ16 | Blank description | 2 | 19,040.17 | actual | INCLUDE_FLAGGED |
| DQ17 | Zero activity | 0 | 0.00 | actual | QUARANTINE |

Amounts are absolute values and a row can appear in more than one check, so the
column is **not** additive. DQ02 counts both sides of each near-duplicate pair.

---

## 5. Detailed findings

### 5.1 Duplicates

**Exact duplicates — 2 pairs, €7,289.32**

| Original | Duplicate | Date | Department | Category | Amount |
|---|---|---|---|---|---:|
| TXN-2364 | TXN-2451 | 2026-05-03 | Logistics & Supply | Payroll & Overtime | 6,394.95 |
| TXN-2348 | TXN-2452 | 2026-01-16 | IT & Systems | Office & Supplies | 894.37 |

Both duplicates were quarantined; the originals remain. This is a *recording*
duplicate. Whether a *payment* was also duplicated cannot be tested without
payment records.

**Near duplicates — 2 pairs, €7,229.70 exposure**

| Pair | Date | Department | Category | Amount | Gap |
|---|---|---|---|---|---:|---:|
| TXN-2009 / TXN-2453 | 2026-03-11 / 2026-03-13 | Marketing | Software & Cloud | 2,854.66 | 2 days |
| TXN-2023 / TXN-2454 | 2026-02-01 / 2026-02-02 | Marketing | Digital Ads & Promo | 4,375.04 | 1 day |

Both sides were retained and flagged `NEAR_DUPLICATE`. Two identical deliveries
two days apart can be genuine; removing them without evidence would be an
unsupported assumption.

### 5.2 Dates

| Issue | Rows | Amount (EUR) | Examples |
|---|---:|---:|---|
| Missing date | 4 | 24,677.13 | TXN-2217, TXN-2237, TXN-2411, TXN-2415 |
| Invalid date | 3 | 13,104.76 | TXN-2201, TXN-2393, TXN-2446 |
| Format normalised | 1 | 796.28 | TXN-2387 (`15-Jan-26` → `2026-01-15`) |
| Out of period | 2 | 23,288.60 | TXN-2280 (2025-12-28), TXN-2121 (2026-07-03) |

Missing and invalid dates are quarantined rather than imputed: the dataset has no
invoice reference or posting date, so any imputation would be a guess. The two
out-of-period items are valid transactions outside H1 and are disclosed
separately; they may be accruals or cut-off errors.

### 5.3 Categories

Six labels were mapped to canonical categories and logged in
`data/processed/category_mapping_log.csv`:

| Transaction | Raw label | Canonical |
|---|---|---|
| TXN-2003 | `freight & delivery` | Freight & Delivery |
| TXN-2226 | `software  & cloud` | Software & Cloud |
| TXN-2250 | `Freight and Delivery` | Freight & Delivery |
| TXN-2267 | `Logisitcs & Freight` | Freight & Delivery |
| TXN-2299 | `FREIGHT & DELIVERY` | Freight & Delivery |
| TXN-2439 | ` Freight & Delivery ` | Freight & Delivery |

After mapping there are **zero unmapped categories** and **zero invalid
departments**. The corrections are transparent, not silent overwrites.

### 5.4 Values

**Negative budget — 1 row**

TXN-2198 (2026-04-17, Logistics & Supply, Payroll & Overtime) carries a budget of
−€2,500.00 against €6,471.20 actual. A negative budget is an entry error, not a
credit; the row is quarantined because it corrupts the denominator.

**Credit notes — 4 rows, €5,293.69**

| Transaction | Date | Category | Actual |
|---|---|---|---:|
| TXN-2108 | 2026-03-04 | Utilities & Rent | −2,416.53 |
| TXN-2142 | 2026-06-02 | Utilities & Rent | −1,745.37 |
| TXN-2368 | 2026-05-27 | Freight & Delivery | −481.48 |
| TXN-2346 | 2026-05-18 | Freight & Delivery | −650.31 |

Credits are legitimate and reduce spend. They are included but flagged because
each should be matched to its original invoice.

**Unbudgeted spend — 3 rows, €10,421.61**

| Transaction | Date | Department | Category | Actual |
|---|---|---|---|---:|
| TXN-2040 | 2026-05-07 | IT & Systems | Office & Supplies | 3,705.08 |
| TXN-2248 | 2026-01-08 | IT & Systems | Office & Supplies | 3,350.01 |
| TXN-2336 | 2026-05-16 | Marketing | Software & Cloud | 3,366.52 |

Budget is zero and actual is positive. These stay in the ledger; variance % is
null because the denominator is not meaningful.

**Tiny budget — 2 rows, €2,813.99**

TXN-2021 (budget €1.00, actual €1,145.39) and TXN-2194 (budget €1.00, actual
€1,668.60). Both are included; variance % is suppressed.

### 5.5 Outliers

Five lines exceed 3× their category median:

| Transaction | Category | Budget | Actual | Variance | Variance % |
|---|---|---:|---:|---:|---:|
| TXN-2166 | Freight & Delivery | 3,865.26 | 18,942.63 | +15,077.37 | +390.07% |
| TXN-2326 | Maintenance & Repairs | 2,774.89 | 15,115.25 | +12,340.36 | +444.72% |
| TXN-2130 | Software & Cloud | 3,847.19 | 13,713.94 | +9,866.75 | +256.47% |
| TXN-2040 | Office & Supplies | 0.00 | 3,705.08 | +3,705.08 | n/a |
| TXN-2248 | Office & Supplies | 0.00 | 3,350.01 | +3,350.01 | n/a |

Three are planted one-off events (freight, chiller, annual licence); two are also
unbudgeted. All are retained and flagged. Statistical size is not evidence of
error.

### 5.6 Blank descriptions

TXN-2100 (Utilities & Rent, €7,505.15) and TXN-2418 (Payroll & Overtime,
€11,535.02). Both are included and flagged; narrative is needed to code and
evidence them.

---

## 6. Disposition summary

| Disposition | Rows | Share |
|---|---:|---:|
| INCLUDE | 417 | 91.9% |
| INCLUDE_FLAGGED | 18 | 4.0% |
| CORRECT_AND_INCLUDE | 7 | 1.5% |
| QUARANTINE | 10 | 2.2% |
| EXCLUDE_OUT_OF_PERIOD | 2 | 0.4% |
| **Total** | **454** | **100%** |

---

## 7. What could not be tested

| Test | Why not possible | What to request |
|---|---|---|
| Duplicate **payment** | No payment or bank records | Payment run, bank statement, supplier statement |
| Approval compliance | No PO or approval field | PO, approval matrix, workflow log |
| Supplier master integrity | No supplier identifier | Supplier master, invoice images |
| VAT treatment | No tax ledger | VAT return, invoice tax codes |
| Accruals and cut-off | No posting or accrual date | Close checklist, accrual schedule |
| Capital vs revenue | No asset register | Asset register, capitalisation policy |

These are design-and-evidence questions, not data-analysis questions, and are
carried into the risk-and-control matrix.

---

## 8. Conclusion

The clean ledger of **442 rows / €2,086,437.42 actual** is fit for variance
analysis. Ten rows (€51,542.41 actual) were quarantined and two (€23,288.60) were
excluded as out of period, with a reconciliation that balances to zero. Eighteen
included lines carry a business flag and are carried forward to the follow-up
review.

No finding in this report establishes fraud, error or mismanagement. Each item is
an observation requiring evidence.
