# Methodology & Assumptions

## H1 2026 Expense Variance Review — Synthetic Educational Dataset

> **Professional boundary.** This is an educational data-analysis exercise. It is
> **not** a statutory audit, assurance engagement, audit opinion or financial
> advice. The dataset is synthetic and contains no real employer, client, bank,
> payroll or personal financial data. No conclusion about fraud or error is drawn
> anywhere in this project.

| Document control | |
|---|---|
| Version | 1.0 |
| Date | 2026-11-24 |
| Prepared by | Project analyst (educational exercise) |
| Status | Complete — educational exercise |
| Applies to | `data/synthetic_retail_expenses.csv` |
| Supersedes | Earlier 273-row draft (not retained) |

---

## 1. Purpose and scope

The purpose is to review H1 2026 budget-versus-actual expense performance for a
fictional retailer, identify data-quality defects, quantify variances, and select
a small number of items for follow-up. The output is management information, not
assurance.

**In scope**

- Expense lines dated 2026-01-01 to 2026-06-30.
- Budget and actual amounts recorded at transaction-line level.
- Data-quality assessment, variance analysis, follow-up selection and reporting.

**Out of scope**

- Revenue, margin, cash flow, balance sheet and tax filings.
- Supplier payments, bank reconciliations and approval workflows (no data).
- Any conclusion on fraud, error or management intent.
- Prior-year comparatives, forecasting and statutory reporting.

---

## 2. Dataset provenance

| Item | Value |
|---|---|
| File | `data/synthetic_retail_expenses.csv` |
| Rows | 454 (450 clean base rows + 4 duplicate clones) |
| Columns | 8 |
| Generator | `scripts/generate_synthetic_data.py` |
| Seed | `20261122` (deterministic) |
| Generated (UTC) | 2026-11-22T11:45:07+00:00 |
| SHA-256 | `DB792D4E1F014899D70755C7631F6570622FDD7C82EDF8FBB0A8678C11F3195B` |
| Currency | EUR |
| Amount basis | VAT-exclusive (net) |
| Label | Every row carries `data_source = SYNTHETIC_EDUCATIONAL` |

Regenerate with:

```bash
python scripts/generate_synthetic_data.py --rows 450 --seed 20261122
```

The generator plants **35 documented defects**: 31 modified base rows and 4 added
duplicate rows. The full register (transaction ID, defect type, note) is stored in
`data/synthetic_retail_expenses.metadata.json`.

---

## 3. Assumptions register

This is the authoritative list. Any later analysis that contradicts a row here is
a defect in the analysis, not a new assumption.

| ID | Assumption | Value adopted | Status | Impact if wrong |
|---|---|---|---|---|
| A01 | Reporting period | 2026-01-01 to 2026-06-30 inclusive | Given by brief | Period totals and month buckets change |
| A02 | Currency | EUR, single currency, no FX translation | Given by design | Non-EUR lines would need conversion |
| A03 | Tax treatment | Amounts are **VAT-exclusive (net)** | **Assumed — confirm with Finance** | VAT-inclusive data distorts variance % where VAT rates differ |
| A04 | Categories | 8 canonical categories (section 6) | Defined here | Category totals and comparisons change |
| A05 | Budget grain | One budget per transaction line | Design choice | Overstates precision; see section 7 |
| A06 | Variance sign | `variance = actual − budget`; **positive = adverse** | Definition | A reversed sign inverts the whole narrative |
| A07 | Variance % guard | Calculate only when `abs(budget) ≥ 100 EUR` | Analytical judgement | More/fewer null percentages |
| A08 | Review threshold | `abs(variance) ≥ 1,000 EUR` **and** `abs(variance %) ≥ 10%` | Prioritisation rule | Changes the follow-up shortlist |
| A09 | Rounding | 2 decimal places for presentation | Convention | ±0.01 EUR rounding differences |
| A10 | Duplicate rule | Keep the earliest `txn_id`; quarantine later copies | Judgement | Count and totals change |
| A11 | Negative actual | Credit note / refund; include in totals | Judgement | Excluding credits overstates net spend |
| A12 | Negative budget | Data-entry error; quarantine | Judgement | Including it corrupts the denominator |
| A13 | Outliers | Flag for review; never auto-exclude | Judgement | Silent exclusion hides the main story |
| A14 | Data source | Synthetic educational data | Given | — |

---

## 4. Reporting period and cut-off

The reporting period is **1 January 2026 to 30 June 2026 inclusive** (H1 2026).
Cut-off is by **transaction date**, not by payment date or posting date (neither
is available).

| Condition | Example | Treatment |
|---|---|---|
| Valid ISO date inside H1 2026 | `2026-03-14` | Include |
| Valid ISO date before 2026-01-01 | `2025-12-28` | Exclude from H1 totals; disclose as prior-period item |
| Valid ISO date after 2026-06-30 | `2026-07-03` | Exclude from H1 totals; disclose as next-period item |
| Unambiguous non-ISO date | `15-Jan-26` | Normalise to `2026-01-15`, include, flag `DATE_FORMAT_NORMALISED` |
| Invalid or ambiguous date | `31/02/2026`, `2026/04/31`, `2026-13-05` | Quarantine; request source document |
| Blank date | `""` | Quarantine; request source document |

Because the dataset has no invoice reference or posting date, missing dates are
**not imputed**. Any imputation would be an unsupported assumption.

---

## 5. Currency, tax and rounding

- **Currency:** euro (EUR). No foreign-currency lines and no FX rates are applied.
- **Tax:** all budget and actual values are treated as **net of VAT** (VAT-exclusive).
  This is an assumption pending confirmation. If the source ledger is
  VAT-inclusive, the review must be restated before any percentage comparison,
  because a different VAT mix across categories would distort variance.
- **Other taxes:** none modelled (no customs duty, excise or withholding tax).
- **Rounding:** amounts are stored to 2 decimals. Percentages are rounded to 2
  decimals for presentation; calculations use the stored 2-decimal amounts.
- **Sign convention:** expenses are positive; credits and refunds are negative.
  A negative actual is a reduction in spend, not an error by definition.

---

## 6. Organisational and category taxonomy

### Departments (5)

`Store Operations`, `Marketing`, `Finance & Admin`, `IT & Systems`, `Logistics & Supply`.

### Categories (8 canonical)

| Category | Includes | Excludes | Example description |
|---|---|---|---|
| Payroll & Overtime | Salaries, wages, overtime, shift premiums, agency and temporary staff | Recruitment fees, external consultants | `Weekend overtime - peak trading` |
| Utilities & Rent | Store and DC rent, service charges, electricity, gas, water, waste | Repairs and maintenance | `Electricity consumption - stores` |
| Freight & Delivery | Inbound and outbound freight, last-mile, cross-dock, fuel surcharge, reverse logistics | Inventory cost (COGS), customs duty | `Inbound freight - regional hub` |
| Digital Ads & Promo | Paid search, paid social, programmatic, affiliate, retail media, campaign production | Print and in-store signage | `Paid social - campaign flight` |
| Software & Cloud | SaaS subscriptions, cloud compute and storage, licences, cyber tooling | Hardware, implementation consulting | `Cloud compute & storage` |
| Maintenance & Repairs | Preventive and reactive maintenance: HVAC, refrigeration, electrical, lifts, dock doors | Capital improvements (capex) | `Preventive HVAC inspection` |
| Professional Services | Legal, tax, audit support, consulting, recruitment agency fees, training | Internal payroll | `Legal advisory - leases` |
| Office & Supplies | Stationery, printing, IT peripherals, cleaning supplies, uniform and PPE, postage | Software licences, freight | `Stationery & consumables` |

### Category normalisation map

The generator plants six non-canonical labels. The ETL must map them and record
the original value, never silently overwrite it.

| Raw value | Canonical value | Rule |
|---|---|---|
| `freight & delivery` | Freight & Delivery | Case normalisation |
| `FREIGHT & DELIVERY` | Freight & Delivery | Case normalisation |
| ` Freight & Delivery ` | Freight & Delivery | Trim whitespace |
| `Freight and Delivery` | Freight & Delivery | Synonym mapping |
| `Logisitcs & Freight` | Freight & Delivery | Typo correction |
| `software  & cloud` | Software & Cloud | Collapse double space |

Anything not on this map and not canonical is quarantined, not guessed.

---

## 7. Budget grain

Each transaction line carries its own budget. This matches the brief, but it is
**not** how a real ledger works: budgets normally sit at
`month × department × category` (cost-centre) level, and actuals are allocated to
it.

Consequences, stated openly:

- The variance of a single line is only meaningful relative to that line's budget.
- Summing line budgets produces a valid **total** budget, but the precision is
  artificial.
- The project therefore also reports a rolled-up view at
  `month × department × category` (step 25), which is the grain a finance reader
  would expect.
- A future iteration should move budget to its own table (star schema). This is a
  documented limitation, not a hidden one.

---

## 8. Variance definitions

```
variance_eur = actual_amount − budget
variance_pct = (variance_eur / budget) × 100     only if abs(budget) ≥ 100 EUR
```

- **Positive variance = adverse** (spend above budget).
- **Negative variance = favourable** (spend below budget).
- `variance_pct` is **null** when:
  - `budget = 0` → flag `UNBUDGETED`;
  - `abs(budget) < 100` → flag `TINY_BUDGET`;
  - `budget < 0` → quarantined before calculation.
- The €100 guard exists because percentages on very small denominators are
  unstable and not decision-useful (a €1 budget turns a €1,000 spend into
  +99,900%). It is a **presentation rule**, not a statistical test.
- Percentage variance is never calculated on a negative denominator.

**Worked example:** budget €4,000, actual €4,600 → variance **+€600 (adverse)**,
variance % **+15.0%**.

---

## 9. Data-quality policy

Every check produces a row in `dq_summary.csv` with: check name, rule, rows
affected, amount affected and disposition. Every affected transaction appears in
`dq_exceptions_log.csv` with a machine-readable flag.

| Disposition | Meaning | Effect on totals |
|---|---|---|
| `INCLUDE` | Passes all checks | Included |
| `INCLUDE_FLAGGED` | Legitimate but noteworthy (credit note, outlier, unbudgeted) | Included, listed for follow-up |
| `CORRECT_AND_INCLUDE` | Fixable defect with an audit trail (category label, date format) | Included after correction |
| `QUARANTINE` | Cannot be validated (blank/invalid date, negative budget) | Excluded, disclosed |
| `EXCLUDE_OUT_OF_PERIOD` | Valid but outside H1 2026 | Excluded, disclosed |

The governing principle: **exclude only what cannot be validated; never exclude a
large variance merely because it is large.** Statistical outliers stay in the
ledger and move to the follow-up list.

### Checks performed (17 automated rules)

| ID | Check | Rule | Disposition |
|---|---|---|---|
| DQ01 | Exact duplicate | Same date, department, category, description, budget and actual; later `txn_id` | `QUARANTINE` |
| DQ02 | Near duplicate | Same department, category, description and actual; date within ±2 days | `INCLUDE_FLAGGED` |
| DQ03 | Missing date | Date field is blank | `QUARANTINE` |
| DQ04 | Invalid date | Date is not parseable with the approved formats | `QUARANTINE` |
| DQ05 | Date format normalised | Non-ISO but unambiguous date | `CORRECT_AND_INCLUDE` |
| DQ06 | Out of period | Date outside 2026-01-01 to 2026-06-30 | `EXCLUDE_OUT_OF_PERIOD` |
| DQ07 | Non-canonical category | Label mapped to a canonical category | `CORRECT_AND_INCLUDE` |
| DQ08 | Invalid category | Label cannot be mapped to a canonical category | `QUARANTINE` |
| DQ09 | Invalid department | Department outside the approved list | `QUARANTINE` |
| DQ10 | Invalid amount | Budget or actual is not numeric | `QUARANTINE` |
| DQ11 | Negative budget | Budget below zero | `QUARANTINE` |
| DQ12 | Credit note | Negative actual amount (credit or refund) | `INCLUDE_FLAGGED` |
| DQ13 | Unbudgeted spend | Budget is zero and actual is positive | `INCLUDE_FLAGGED` |
| DQ14 | Tiny budget | Budget above zero but below €100 | `INCLUDE_FLAGGED` |
| DQ15 | Extreme outlier | Actual above 3× the category median | `INCLUDE_FLAGGED` |
| DQ16 | Blank description | Description is empty | `INCLUDE_FLAGGED` |
| DQ17 | Zero activity | Budget and actual are both zero | `QUARANTINE` |

The row-count and total reconciliation is tested separately in section 14; it is
not one of the 17 row-level checks. Full results are in
`data/processed/dq_summary.csv` and `docs/data_quality_report.md`.

---

## 10. Duplicate policy

| Type | Definition | Action |
|---|---|---|
| Exact duplicate | Same date, department, category, description, budget and actual; different `txn_id` | Keep earliest `txn_id`, quarantine the later copy |
| Near duplicate | Same department, category, description and actual; date within ±2 days | Flag `NEAR_DUPLICATE`, **keep both**, request evidence |
| Description-only match | Same description, different amount/date | No action; descriptions repeat legitimately |

Near duplicates are **not** removed automatically. Two identical deliveries two
days apart can be genuine. Removal without evidence would be an unsupported
assumption.

The dataset contains 2 exact-duplicate pairs and 2 near-duplicate pairs. Because
duplicate detection is on business keys, the exact pairs will appear as 4 rows
(2 originals + 2 copies).

---

## 11. Negative and zero-budget policy

| Case | Interpretation | Treatment |
|---|---|---|
| Negative actual | Credit note or refund | Include; flag `CREDIT_NOTE`; request credit note |
| Negative budget | Data-entry error | Quarantine; exclude from budget and denominator |
| Budget = 0, actual > 0 | Unbudgeted spend | Include actual; variance % null; flag `UNBUDGETED` |
| 0 < budget < €100 | Denominator not meaningful | Include; variance % null; flag `TINY_BUDGET` |
| Budget = 0, actual = 0 | No economic substance | Exclude from analysis; disclose |

---

## 12. Outlier policy

An outlier is flagged when `actual_amount > 3 × median(actual_amount)` for its
category. Outliers are **never excluded on statistical grounds**. A large freight
invoice or an emergency repair is usually a real business event and is exactly
what the review should surface.

---

## 13. Review threshold (follow-up selection)

A line is a candidate for follow-up when **both**:

- `abs(variance) ≥ €1,000`, and
- `abs(variance %) ≥ 10%` (where the denominator is valid).

This is a **prioritisation rule for management attention**, not an audit
materiality and not a conclusion. Items below the threshold remain in the data and
in the dashboard; they are simply not shortlisted.

The three selected follow-up items (step 26) must each pass this screen and be
chosen for a stated business reason, not only because they are the largest.

---

## 14. Reconciliation requirement

No number reaches the management summary unless the bridge below balances to the
cent. It is produced in step 23 as `data/processed/reconciliation.csv`.

| Step | Rows | Budget (EUR) | Actual (EUR) |
|---|---|---|---|
| Raw file | 454 | 2,094,168.45 | 2,161,268.43 |
| Less: exact duplicates | 2 | (7,439.81) | (7,289.32) |
| Less: missing/invalid dates | 7 | (37,322.10) | (37,781.89) |
| Less: negative budget | 1 | 2,500.00 | (6,471.20) |
| Less: out of period | 2 | (24,849.00) | (23,288.60) |
| **Clean ledger** | **442** | **2,027,057.54** | **2,086,437.42** |
| **Check: raw − exclusions = clean** | **0** | **0.00** | **0.00** |

The negative-budget line shows a positive budget adjustment because removing a
−€2,500 budget *increases* the clean budget. This is the same bridge as
`data/processed/reconciliation.csv`, and it balances to the cent.

---

## 15. Data dictionary

| Column | Type | Null allowed | Description | Validation |
|---|---|---|---|---|
| `txn_id` | text | No | Unique transaction identifier (`TXN-2001`…) | Unique, pattern `TXN-\d{4}` |
| `date` | text | Yes | Transaction date, intended ISO `YYYY-MM-DD` | Parsed per section 4 |
| `department` | text | No | Cost centre | Must be one of the 5 approved values |
| `category` | text | No | Expense category | Mapped to 8 canonical values |
| `description` | text | Yes | Free-text narrative including vendor | Blank flagged |
| `budget` | decimal | No | Line budget, EUR, VAT-exclusive | Numeric; negative quarantined |
| `actual_amount` | decimal | No | Actual spend, EUR, VAT-exclusive | Numeric; negative = credit |
| `data_source` | text | No | Always `SYNTHETIC_EDUCATIONAL` | Constant |

---

## 16. Limitations

1. **Synthetic data.** 454 rows over six months is illustrative, not representative.
2. **No supplier, invoice, PO, approval or payment fields.** Duplicate *payment*,
   approval compliance and supplier-master checks cannot be tested; they can only
   be designed and requested as evidence.
3. **No quantity or unit price.** Price/volume decomposition of variance is not possible.
4. **Per-line budget.** Not a true cost-centre budget (section 7).
5. **No tax ledger or FX.** VAT is assumed, not evidenced.
6. **No accruals or prepayments.** Timing effects cannot be separated from
   genuine overspend.
7. **No prior-year comparatives.** Seasonality cannot be validated.
8. **Category mapping is judgemental.** The mapping table is documented so it can
   be challenged.
9. **No external confirmations.** Nothing here is verified against a third party.
10. **No conclusion on fraud or error.** Variances are signals for follow-up, not findings.

---

## 17. Change log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | 2026-11-22 | Initial assumptions for the 454-row synthetic dataset; supersedes the 273-row draft | Project analyst |
| 1.0 | 2026-11-24 | Final methodology: 17 checks, verified reconciliation bridge, completed status | Project analyst |

---

## 18. Sign-off

| Role | Name | Date | Status |
|---|---|---|---|
| Prepared by | Project analyst (educational) | 2026-11-24 | Complete |
| Reviewed by | Self-review against the 17 checks and reconciliation | 2026-11-24 | Complete |
| Approved by | — | — | Not applicable (educational exercise) |
