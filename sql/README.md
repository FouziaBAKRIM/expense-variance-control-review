# SQL Layer — Run Guide and Verified Results

PostgreSQL implementation of the H1 2026 expense review. It mirrors the Python
pipeline: 454 audited rows load into `fact_expenses`, and every analysis filters
on `included`, so quarantined and out-of-period rows stay visible but out of the
totals.

> **Boundary.** Synthetic educational data. Not an audit, assurance engagement,
> audit opinion or financial advice.

---

## Files and run order

| Order | File | Purpose |
|---|---|---|
| 1 | `01_create_tables.sql` | Drops/creates `stg_expenses`, `fact_expenses`, 5 views and 4 indexes |
| 2 | `03_load_data.sql` | `TRUNCATE`, `\copy` the CSV, insert into the fact table, load check |
| 3 | `02_variance_and_dq_queries.sql` | 13 analysis queries (A–M): category, month, line items, DQ, reconciliation |
| 4 | `04_control_tests.sql` | 9 detective tests (T01–T09) plus a note on untestable controls |

The numeric prefix is the dependency order, not the reading order: the load runs
before the analysis even though its filename sorts second.

---

## Prerequisites

- PostgreSQL 14 or later (verified on 19.0).
- The `psql` client. The load uses `\copy`, which is a psql meta-command and does
  not exist in the server-side `COPY` grammar, so a plain driver cannot run
  `03_load_data.sql` unchanged.
- Run everything from the repository root: `\copy` resolves the CSV path relative
  to the client's working directory.

`psql` is not always on `PATH`. On Windows it is typically at
`C:\Program Files\PostgreSQL\<version>\bin\psql.exe`; the runner finds it there
automatically.

---

## Recommended: the runner

```bash
python scripts/run_sql.py --host localhost --port 5432 --user postgres
```

What it does:

1. Locates `psql` (PATH, `--psql`, or the standard Windows install directory).
2. Connects to the `postgres` maintenance database and creates `finance_review`
   if it does not exist.
3. Runs the four scripts with `ON_ERROR_STOP=1`.
4. Writes each script's full output to `sql/output/<script>.txt`.

Options: `--database`, `--password` (or `PGPASSWORD`), `--psql`. Host, port, user
and database also fall back to `PGHOST`, `PGPORT`, `PGUSER` and `PGDATABASE`.

---

## Manual equivalent

```bash
createdb finance_review
psql -d finance_review -f sql/01_create_tables.sql
psql -d finance_review -f sql/03_load_data.sql
psql -d finance_review -f sql/02_variance_and_dq_queries.sql
psql -d finance_review -f sql/04_control_tests.sql
```

---

## Throwaway cluster (no password, no admin)

If the installed server is password-protected and you do not want to touch it,
initialise a separate cluster in a temp directory. This is how the verified run
below was produced.

```powershell
$bin  = 'C:\Program Files\PostgreSQL\19\bin'
$root = "$env:LOCALAPPDATA\Temp\opencode\finance_pg"
$data = "$root\data"

# One-off: trust auth, UTF-8, isolated data directory
& "$bin\initdb.exe" -D $data -U postgres --auth=trust --encoding=UTF8 --locale=C

# Start on 5433 (Start-Process keeps the server detached)
Start-Process -FilePath "$bin\postgres.exe" `
  -ArgumentList @('-D', $data, '-p', '5433') -WindowStyle Hidden

python scripts/run_sql.py --host 127.0.0.1 --port 5433 --user postgres

# Stop when finished
& "$bin\pg_ctl.exe" -D $data -m fast stop
```

This cluster listens on localhost only, uses trust authentication and lives
outside the repository. Do not use it for anything other than this exercise.

---

## Verified run — 2026-11-23

Environment: PostgreSQL 19.0 (Windows x64), UTF-8, locale `C`, throwaway cluster
on `127.0.0.1:5433`, database created empty before the run.

| Script | Observed result |
|---|---|
| `01_create_tables.sql` | 2 tables, 5 views, 4 indexes |
| `03_load_data.sql` | `COPY 454`, `INSERT 0 454`, totals match the CSV |
| `02_variance_and_dq_queries.sql` | all 13 queries return rows; figures match the Python pipeline |
| `04_control_tests.sql` | T01–T09 return the expected populations |

Load check:

| rows_loaded | total_budget_eur | total_actual_eur | total_variance_eur |
|---:|---:|---:|---:|
| 454 | 2,094,168.45 | 2,161,268.43 | 67,099.98 |

Reconciliation (section K):

| Layer | Rows | Budget (EUR) | Actual (EUR) |
|---|---:|---:|---:|
| Raw file | 454 | 2,094,168.45 | 2,161,268.43 |
| Less: excluded (quarantine + out of period) | 12 | 67,110.91 | 74,831.01 |
| Clean ledger | 442 | 2,027,057.54 | 2,086,437.42 |
| **CHECK (raw − excluded − clean)** | **0** | **0.00** | **0.00** |

Control-test populations:

| Test | Expected | Observed |
|---|---|---|
| T01 exact duplicates | 2 pairs | 2 pairs (`TXN-2364/2451`, `TXN-2348/2452`) |
| T02 near duplicates | 2 pairs | 2 pairs |
| T03 out of period | 2 rows | 2 rows (2025-12-28, 2026-07-03) |
| T04 negative budget | 1 row | 1 row (`TXN-2198`) |
| T05 category compliance | 0 rows | 0 rows |
| T06 unbudgeted spend | 3 rows | 3 rows (€10,421.61) |
| T07 credit notes | 4 rows | 4 rows (€5,293.69) |
| T08 review threshold | 19 rows | 19 rows |
| T09 reconciliation | 0 / 0.00 / 0.00 | 0 / 0.00 / 0.00 |

Category totals also match the workbook and Markdown commentary: Freight
+€30,829.24, Maintenance +€25,775.53, Software +€21,188.71, Payroll −€26,110.47.

Full psql output is committed under `sql/output/`.

---

## What execution caught

The first version of the reconciliation query subtracted clean from raw and
labelled the result "Difference (must be 0)". That is wrong: raw − clean is the
excluded population, so it returned 12 rows / €67,110.91 / €74,831.01 and failed
its own label.

It now computes raw − excluded − clean, which is genuinely zero. Both section K
and T09 were corrected. This is the kind of defect that only appears when the
SQL is actually run against a database.

---

## Design notes

- **All rows are loaded.** `fact_expenses` holds 454 rows; `included = FALSE`
  marks the 12 quarantined or out-of-period rows. Views filter on `included`, so
  nothing is silently deleted.
- **Variance is constrained.** `chk_variance` enforces
  `ROUND(actual_eur - budget_eur, 2) = variance_eur`, so a miscomputed row cannot
  be inserted.
- **Month allows `UNKNOWN`.** Rows with missing or invalid dates still load;
  `chk_month` accepts `YYYY-MM` or `UNKNOWN`.
- **Variance % is guarded.** The views compute it only when the budget is at
  least €100, matching the Python rule; otherwise the column is `NULL`.
- **Booleans load as text.** The CSV writes `True`/`False`, which PostgreSQL
  accepts as boolean input.

---

## Limits

- These tests cover **recording**, not payment or approval. There is no supplier,
  invoice number, PO, approval, payment date or bank record in the dataset, so
  duplicate-payment, approval-compliance and supplier-master tests cannot be run
  as queries. See `docs/risk_control_matrix.md`.
- Verified on PostgreSQL 19.0 only. The SQL uses standard features and should work
  on 14+, but that is untested.
- The cluster used for verification was temporary and is not part of the
  repository.
