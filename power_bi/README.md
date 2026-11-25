# Power BI Dashboard — Design Spec (Not Yet Built)

> **Status: planned.** No `.pbix` file is committed. The report must be authored
> and rendered in Power BI Desktop, which is a local GUI application. This folder
> documents the intended model and pages so the build is reproducible, not a
> claim that the dashboard exists.

> **Boundary.** Synthetic educational data only. Not an audit, assurance
> engagement, audit opinion or financial advice. Every report page must carry the
> synthetic-data disclaimer.

---

## Why this is a spec and not a report

A `.pbix` cannot be generated or visually verified from a headless environment:
Power BI Desktop is required to create the data model, write DAX, lay out pages
and render them. Committing an empty or hand-edited scaffold would misrepresent
the project, so the repository ships the design instead and the build stays on
the roadmap.

---

## Data source

Use the same audited extract the Python and SQL layers use:

| Option | Source | Notes |
|---|---|---|
| Flat file | `data/processed/expenses_audited_all.csv` | 454 rows; easiest for a demo |
| PostgreSQL | `fact_expenses` (see `sql/01_create_tables.sql`) | Same 454 rows, typed columns |

Filter `included = TRUE` for every financial page. Keep the 12 excluded rows
visible only on the data-quality page.

---

## Suggested model

A lightweight star around the existing fact table:

- **Fact:** `fact_expenses` (454 rows, one per transaction line).
- **Dimensions (derived):** `dim_date` (month, quarter, year), `dim_category`,
  `dim_department`, `dim_disposition`.
- **Relationships:** one-to-many from each dimension to the fact on the matching
  key. Mark `dim_date` as the date table.

---

## Core measures (DAX)

```dax
Total Budget = CALCULATE ( SUM ( fact_expenses[budget_eur] ), fact_expenses[included] = TRUE )
Total Actual = CALCULATE ( SUM ( fact_expenses[actual_eur] ), fact_expenses[included] = TRUE )
Variance EUR = [Total Actual] - [Total Budget]
Variance % =
    IF ( [Total Budget] >= 100, DIVIDE ( [Variance EUR], [Total Budget] ), BLANK () )
Included Rows = CALCULATE ( COUNTROWS ( fact_expenses ), fact_expenses[included] = TRUE )
Flagged Rows  = CALCULATE ( COUNTROWS ( fact_expenses ), fact_expenses[disposition] = "INCLUDE_FLAGGED" )
Quarantine Rows = CALCULATE ( COUNTROWS ( fact_expenses ), fact_expenses[disposition] = "QUARANTINE" )
Reconciliation Gap =
    VAR Raw      = SUM ( fact_expenses[budget_eur] )
    VAR Excluded = CALCULATE ( SUM ( fact_expenses[budget_eur] ), fact_expenses[included] = FALSE )
    VAR Clean    = [Total Budget]
    RETURN Raw - Excluded - Clean
```

Keep the same conventions as the rest of the project:

- **Positive variance = adverse** (actual above budget).
- **Variance % is blank** when budget < €100 or not meaningful.
- **Reconciliation Gap must equal 0.00** before any figure is published.

---

## Pages

1. **Executive overview** — KPI cards (budget, actual, variance, variance %),
   rows reviewed vs clean, and a one-line boundary statement.
2. **Variance waterfall** — category contributions from budget to actual, with
   the three largest adverse and favourable categories called out.
3. **Category × month matrix** — conditional-formatted variance with the
   guarded variance %; drill-through to line items.
4. **Data-quality exceptions** — 17-check summary, disposition mix, and the
   exception log (quarantined and flagged rows).
5. **Follow-up tracker** — the three selected items with observation, evidence
   required and status (all "evidence requested", none concluded).

---

## Build checklist

- [ ] Connect to `expenses_audited_all.csv` or `fact_expenses`.
- [ ] Create `dim_date`, `dim_category`, `dim_department`, `dim_disposition`.
- [ ] Add the measures above; verify `Reconciliation Gap = 0.00`.
- [ ] Build the five pages; add the synthetic-data disclaimer to each.
- [ ] Cross-check headline figures against `docs/management_summary.md`.
- [ ] Save as `power_bi/expense_variance_control_review.pbix` and commit it.

Until the checklist is complete, the roadmap keeps the dashboard at **Planned**.
