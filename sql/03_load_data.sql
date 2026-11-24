-- ============================================================================
-- 03_load_data.sql
-- Load the pipeline output into PostgreSQL.
--
-- Run from the repository root with psql:
--   psql -d finance_review -f sql/01_create_tables.sql
--   psql -d finance_review -f sql/03_load_data.sql
--
-- \copy reads the file on the client machine, relative to the current
-- working directory. Re-run this file to refresh the data.
-- ============================================================================

TRUNCATE stg_expenses;
TRUNCATE fact_expenses;

\copy stg_expenses (txn_id, txn_date, month, department, category, category_raw, description, budget, actual_amount, variance_eur, variance_pct, disposition, dq_flags, needs_review, included) FROM 'data/processed/expenses_audited_all.csv' WITH (FORMAT csv, HEADER true, NULL '')

INSERT INTO fact_expenses (
    txn_id,
    txn_date,
    month,
    department,
    category,
    category_raw,
    description,
    budget_eur,
    actual_eur,
    variance_eur,
    variance_pct,
    disposition,
    dq_flags,
    needs_review,
    included
)
SELECT
    txn_id,
    txn_date,
    month,
    department,
    category,
    category_raw,
    description,
    budget,
    actual_amount,
    variance_eur,
    variance_pct,
    disposition,
    dq_flags,
    COALESCE(needs_review, FALSE),
    COALESCE(included, TRUE)
FROM stg_expenses;

ANALYZE fact_expenses;

-- Load check: 454 rows, budget 2,094,168.45, actual 2,161,268.43
SELECT
    COUNT(*)                        AS rows_loaded,
    ROUND(SUM(budget_eur), 2)       AS total_budget_eur,
    ROUND(SUM(actual_eur), 2)       AS total_actual_eur,
    ROUND(SUM(variance_eur), 2)     AS total_variance_eur
FROM fact_expenses;
