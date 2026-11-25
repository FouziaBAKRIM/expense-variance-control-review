# DAX Measure Library — Expense Variance & Control Review

> **Boundary.** Synthetic educational data only. Not an audit, assurance
> engagement, audit opinion or financial advice.

Copy these measures into Power BI Desktop (**Modeling → New measure**). Column
names assume the Power Query rename in
[`POWER_BI_BUILD_GUIDE.md`](POWER_BI_BUILD_GUIDE.md#4-rename-and-type-the-fact-table).
If you keep the raw CSV names, substitute them consistently.

Format strings are suggestions; set them in **Measure tools → Format**.

---

## 0. Naming contract

| Raw CSV column | Renamed column | Type | Notes |
|---|---|---|---|
| `txn_id` | `Txn ID` | Text | Unique line identifier |
| `date` | `Date` | Date | Blank for 7 quarantined rows |
| `month` | `Month` | Text | `YYYY-MM` or `UNKNOWN` |
| `department` | `Department` | Text | 5 values |
| `category` | `Category` | Text | 8 values |
| `category_raw` | `Category Raw` | Text | Before normalisation |
| `description` | `Description` | Text | Free text |
| `budget` | `Budget` | Decimal | EUR, VAT-exclusive |
| `actual_amount` | `Actual` | Decimal | EUR; negative = credit |
| `variance_eur` | `Line Variance` | Decimal | `Actual − Budget` |
| `variance_pct` | `Line Variance % (pts)` | Decimal | Percentage **points** |
| `disposition` | `Disposition` | Text | 5 values |
| `dq_flags` | `DQ Flags` | Text | Pipe-delimited |
| `needs_review` | `Needs Review` | True/False | |
| `included` | `Included` | True/False | Clean-ledger flag |

> The measure names below deliberately differ from the column names
> (`Variance EUR` vs `Line Variance`) so Power BI does not create `… 2` names.

---

## 1. Core financial measures (included rows only)

```dax
Total Budget =
CALCULATE ( SUM ( FactExpenses[Budget] ), FactExpenses[Included] = TRUE )
```
Format: `€#,##0.00`

```dax
Total Actual =
CALCULATE ( SUM ( FactExpenses[Actual] ), FactExpenses[Included] = TRUE )
```
Format: `€#,##0.00`

```dax
Variance EUR = [Total Actual] - [Total Budget]
```
Format: `€#,##0.00; (€#,##0.00); €0.00`

```dax
Variance % =
IF ( [Total Budget] >= 100, DIVIDE ( [Variance EUR], [Total Budget] ), BLANK () )
```
Format: `+0.0%; -0.0%; 0.0%`

```dax
Budget Coverage % =
DIVIDE (
    CALCULATE (
        COUNTROWS ( FactExpenses ),
        FactExpenses[Included] = TRUE,
        FactExpenses[Budget] > 0
    ),
    [Rows Included]
)
```
Format: `0.0%`. Expected ≈ **99.3%** (3 unbudgeted lines).

> **Sign convention:** positive variance = adverse (actual above budget). Never
> invert this in the report.

---

## 2. Row and quality measures

```dax
Rows Raw = COUNTROWS ( FactExpenses )
```
Format: `#,##0`

```dax
Rows Included =
CALCULATE ( COUNTROWS ( FactExpenses ), FactExpenses[Included] = TRUE )
```
Format: `#,##0`

```dax
Rows Excluded = [Rows Raw] - [Rows Included]
```
Format: `#,##0`

```dax
Rows Flagged =
CALCULATE ( COUNTROWS ( FactExpenses ), FactExpenses[Disposition] = "INCLUDE_FLAGGED" )
```
Format: `#,##0`

```dax
Rows Corrected =
CALCULATE ( COUNTROWS ( FactExpenses ), FactExpenses[Disposition] = "CORRECT_AND_INCLUDE" )
```
Format: `#,##0`

```dax
Rows Quarantined =
CALCULATE ( COUNTROWS ( FactExpenses ), FactExpenses[Disposition] = "QUARANTINE" )
```
Format: `#,##0`

```dax
Rows Out of Period =
CALCULATE ( COUNTROWS ( FactExpenses ), FactExpenses[Disposition] = "EXCLUDE_OUT_OF_PERIOD" )
```
Format: `#,##0`

```dax
Rows with DQ Flags =
CALCULATE (
    DISTINCTCOUNT ( FactExpenses[Txn ID] ),
    FactExpenses[DQ Flags] <> "CLEAN"
)
```
Format: `#,##0`. Expected **37** (unique rows, not check hits).

---

## 3. Reconciliation

```dax
Reconciliation Gap =
VAR Raw      = CALCULATE ( SUM ( FactExpenses[Budget] ) )
VAR Excluded = CALCULATE ( SUM ( FactExpenses[Budget] ), FactExpenses[Included] = FALSE )
VAR Clean    = [Total Budget]
RETURN Raw - Excluded - Clean
```
Format: `€#,##0.00; (€#,##0.00); €0.00`. **Must be 0.00.**

```dax
Reconciliation Gap Actual =
VAR Raw      = CALCULATE ( SUM ( FactExpenses[Actual] ) )
VAR Excluded = CALCULATE ( SUM ( FactExpenses[Actual] ), FactExpenses[Included] = FALSE )
VAR Clean    = [Total Actual]
RETURN Raw - Excluded - Clean
```
Format: `€#,##0.00; (€#,##0.00); €0.00`.

```dax
Reconciliation Status =
IF ( ABS ( [Reconciliation Gap] ) < 0.005 && ABS ( [Reconciliation Gap Actual] ) < 0.005,
    "BALANCED", "CHECK" )
```

---

## 4. Time intelligence (requires `DimDate` marked as a date table)

```dax
Cumulative Actual =
TOTALYTD ( [Total Actual], DimDate[Date] )
```
Format: `€#,##0.00`

```dax
Cumulative Variance =
TOTALYTD ( [Variance EUR], DimDate[Date] )
```
Format: `€#,##0.00`

```dax
Variance MoM =
VAR Current = [Variance EUR]
VAR Prior   = CALCULATE ( [Variance EUR], DATEADD ( DimDate[Date], -1, MONTH ) )
RETURN IF ( NOT ISBLANK ( Prior ), Current - Prior )
```
Format: `€#,##0.00; (€#,##0.00); €0.00`

```dax
Actual vs Budget Index =
DIVIDE ( [Total Actual], [Total Budget] )
```
Format: `0.00x` (1.00 = on budget).

---

## 5. Ranking and line-level analysis

```dax
Category Variance Rank =
RANKX ( ALLSELECTED ( FactExpenses[Category] ), [Variance EUR], , DESC, DENSE )
```

```dax
Line Variance Rank =
RANKX ( ALLSELECTED ( FactExpenses[Txn ID] ), [Variance EUR], , DESC, DENSE )
```

```dax
Top 10 Adverse Lines =
CALCULATE (
    [Variance EUR],
    KEEPFILTERS ( FILTER ( ALLSELECTED ( FactExpenses[Txn ID] ), [Line Variance Rank] <= 10 ) )
)
```

> For the **Top 10 table visual**, simpler: put `Txn ID`, `Description`,
> `Category` on rows, add `[Variance EUR]`, and use a visual-level Top N filter
> (Top 10 by `[Variance EUR]`). No measure required.

---

## 6. Conditional formatting and icons

Use **Format → Cell elements → Font color → Field value** and pick the measure.

```dax
Variance Colour =
SWITCH (
    TRUE (),
    [Variance EUR] > 0, "#C0392B",
    [Variance EUR] < 0, "#2E7D32",
    "#6B7280"
)
```

```dax
Variance Arrow =
SWITCH (
    TRUE (),
    [Variance EUR] > 0, "▲",
    [Variance EUR] < 0, "▼",
    "■"
)
```

```dax
Variance Label =
[Variance Arrow] & " " & FORMAT ( [Variance EUR], "€#,##0" ) &
" (" & FORMAT ( [Variance %], "+0.0%;-0.0%;0.0%" ) & ")"
```

```dax
DQ Flag Colour =
SWITCH (
    TRUE (),
    CONTAINSSTRING ( SELECTEDVALUE ( FactExpenses[DQ Flags] ), "EXACT_DUPLICATE" ), "#C0392B",
    CONTAINSSTRING ( SELECTEDVALUE ( FactExpenses[DQ Flags] ), "QUARANTINE" ), "#C0392B",
    SELECTEDVALUE ( FactExpenses[DQ Flags] ) = "CLEAN", "#2E7D32",
    "#E9A23B"
)
```

> A row can carry several flags; the order above puts the most severe first.

---

## 7. Dynamic titles and narrative

```dax
Page Title = "Expense Variance & Control Review — H1 2026"
```

```dax
Overview Subtitle =
"Clean ledger " & [Rows Included] & " of " & [Rows Raw] & " rows  ·  " &
FORMAT ( [Total Actual], "€#,##0" ) & " actual vs " &
FORMAT ( [Total Budget], "€#,##0" ) & " budget  ·  " &
FORMAT ( [Variance EUR], "+€#,##0;-€#,##0;€0" ) & " (" &
FORMAT ( [Variance %], "+0.0%;-0.0%;0.0%" ) & ")"
```

```dax
Reconciliation Caption =
"Raw − excluded − clean = " & FORMAT ( [Reconciliation Gap], "€#,##0.00" )
```

```dax
Top Finding =
VAR WorstCategory =
    TOPN ( 1, ALLSELECTED ( FactExpenses[Category] ), [Variance EUR], DESC )
RETURN
    "Largest adverse category: " &
    CONCATENATEX ( WorstCategory, FactExpenses[Category] ) & " " &
    FORMAT ( MAXX ( WorstCategory, [Variance EUR] ), "+€#,##0" )
```

---

## 8. Data-quality, control and follow-up measures

```dax
DQ Checks = COUNTROWS ( DQSummary )
```

```dax
DQ Check Hits = SUM ( DQSummary[rows_affected] )
```
> **Not additive as unique rows.** A transaction can fail several checks; use
> `[Rows with DQ Flags]` for the unique count (37).

```dax
DQ Amount Affected = SUM ( DQSummary[amount_affected_eur] )
```
> Also not additive across checks. Label it “sum of check amounts” in a tooltip.

```dax
Control Tests = COUNTROWS ( ControlTests )
```

```dax
Control Tests Clean =
CALCULATE ( COUNTROWS ( ControlTests ), ControlTests[outcome] = "Clean" )
```

```dax
Follow-ups Open =
CALCULATE ( COUNTROWS ( SelectedFollowUps ), SelectedFollowUps[status] = "Evidence requested" )
```

```dax
Follow-up Amount at Risk = SUM ( SelectedFollowUps[at_risk_eur] )
```
Format: `€#,##0.00`

```dax
Selected Follow-ups = COUNTROWS ( SelectedFollowUps )
```

---

## 9. Validation measures (put on a hidden or appendix page)

```dax
Budget Check = [Total Budget] - 2027057.54
Actual Check = [Total Actual] - 2086437.42
Variance Check = [Variance EUR] - 59379.88
Included Rows Check = [Rows Included] - 442
```
Each should display **0** / **0.00**. If not, the model or filters are wrong.

---

## 10. Measure display folders (optional but tidy)

In **Model view**, select a measure and set **Display folder**:

| Folder | Measures |
|---|---|
| `01 Financials` | Total Budget, Total Actual, Variance EUR, Variance % |
| `02 Rows` | Rows Raw, Rows Included, Rows Excluded, Rows Flagged, Rows Corrected, Rows Quarantined, Rows Out of Period, Rows with DQ Flags |
| `03 Reconciliation` | Reconciliation Gap, Reconciliation Gap Actual, Reconciliation Status |
| `04 Time` | Cumulative Actual, Cumulative Variance, Variance MoM, Actual vs Budget Index |
| `05 Formatting` | Variance Colour, Variance Arrow, Variance Label, DQ Flag Colour |
| `06 Narrative` | Page Title, Overview Subtitle, Reconciliation Caption, Top Finding |
| `07 Quality` | DQ Checks, DQ Check Hits, DQ Amount Affected, Control Tests, Control Tests Clean, Follow-ups Open, Follow-up Amount at Risk, Selected Follow-ups |
| `08 Validation` | Budget Check, Actual Check, Variance Check, Included Rows Check |
