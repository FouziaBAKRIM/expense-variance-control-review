-- ============================================================================
-- 04_control_tests.sql
-- Detective tests a reviewer would run on the expense ledger.
--
-- Each test returns the exception population. An empty result is the
-- expected outcome for a clean control; here the synthetic data is seeded,
-- so results are stated in the comments.
--
-- These tests cover RECORDING. They do not prove that payment or approval
-- controls operated; see the risk-and-control matrix.
-- ============================================================================


-- ============================================================================
-- T01. EXACT DUPLICATE INVOICE / POSTING
-- Rule: same date, department, category, description, budget and actual.
-- Expected: 2 pairs (TXN-2364/2451 and TXN-2348/2452).
-- ============================================================================
SELECT
    txn_date,
    department,
    category,
    description,
    budget_eur,
    actual_eur,
    COUNT(*)        AS copies,
    STRING_AGG(txn_id, ', ' ORDER BY txn_id) AS txn_ids
FROM fact_expenses
GROUP BY txn_date, department, category, description, budget_eur, actual_eur
HAVING COUNT(*) > 1
ORDER BY actual_eur DESC;


-- ============================================================================
-- T02. NEAR DUPLICATE
-- Rule: same department, category, description and actual; date 1-2 days apart.
-- Expected: 2 pairs (TXN-2009/2453 and TXN-2023/2454).
-- ============================================================================
SELECT
    a.txn_id        AS txn_a,
    b.txn_id        AS txn_b,
    a.department,
    a.category,
    a.actual_eur,
    a.txn_date      AS date_a,
    b.txn_date      AS date_b,
    ABS(a.txn_date - b.txn_date) AS days_apart
FROM fact_expenses a
JOIN fact_expenses b
  ON a.txn_id < b.txn_id
 AND a.department = b.department
 AND a.category = b.category
 AND a.description = b.description
 AND a.actual_eur = b.actual_eur
 AND a.txn_date IS NOT NULL
 AND b.txn_date IS NOT NULL
 AND ABS(a.txn_date - b.txn_date) BETWEEN 1 AND 2
ORDER BY a.actual_eur DESC;


-- ============================================================================
-- T03. OUT-OF-PERIOD POSTING
-- Rule: transaction date outside 2026-01-01 to 2026-06-30.
-- Expected: 2 rows (2025-12-28 and 2026-07-03).
-- ============================================================================
SELECT
    txn_id,
    txn_date,
    department,
    category,
    actual_eur,
    dq_flags
FROM fact_expenses
WHERE txn_date < DATE '2026-01-01'
   OR txn_date > DATE '2026-06-30'
ORDER BY txn_date;


-- ============================================================================
-- T04. NEGATIVE BUDGET
-- Rule: budget below zero.
-- Expected: 1 row (TXN-2198, -2,500.00).
-- ============================================================================
SELECT
    txn_id,
    txn_date,
    department,
    category,
    budget_eur,
    actual_eur,
    dq_flags
FROM fact_expenses
WHERE budget_eur < 0;


-- ============================================================================
-- T05. CATEGORY MASTER COMPLIANCE
-- Rule: every category must be one of the eight approved values.
-- Expected: 0 rows.
-- ============================================================================
SELECT
    category,
    COUNT(*) AS row_count
FROM fact_expenses
WHERE category NOT IN (
    'Payroll & Overtime',
    'Utilities & Rent',
    'Freight & Delivery',
    'Digital Ads & Promo',
    'Software & Cloud',
    'Maintenance & Repairs',
    'Professional Services',
    'Office & Supplies'
)
GROUP BY category;


-- ============================================================================
-- T06. UNBUDGETED SPEND
-- Rule: budget = 0 and actual > 0.
-- Expected: 3 rows, 10,421.61 total.
-- ============================================================================
SELECT
    txn_id,
    txn_date,
    department,
    category,
    budget_eur,
    actual_eur,
    variance_eur
FROM fact_expenses
WHERE budget_eur = 0
  AND actual_eur > 0
ORDER BY actual_eur DESC;


-- ============================================================================
-- T07. CREDIT NOTES
-- Rule: negative actual amount.
-- Expected: 4 rows, 5,293.69 total credit.
-- ============================================================================
SELECT
    txn_id,
    txn_date,
    department,
    category,
    actual_eur,
    budget_eur,
    variance_eur
FROM fact_expenses
WHERE actual_eur < 0
ORDER BY actual_eur;


-- ============================================================================
-- T08. REVIEW-THRESHOLD ITEMS
-- Rule: abs(variance) >= 1,000 and abs(variance %) >= 10.
-- Expected: the three follow-up outliers plus smaller lines.
-- ============================================================================
SELECT
    txn_id,
    txn_date,
    department,
    category,
    budget_eur,
    actual_eur,
    variance_eur,
    variance_pct
FROM fact_expenses
WHERE included
  AND ABS(variance_eur) >= 1000
  AND ABS(variance_pct) >= 10
ORDER BY variance_eur DESC;


-- ============================================================================
-- T09. RECONCILIATION
-- Rule: raw staging = excluded population + clean ledger.
-- Expected: difference = 0 rows, 0.00 budget, 0.00 actual.
-- ============================================================================
WITH raw AS (
    SELECT
        COUNT(*)                        AS row_count,
        COALESCE(SUM(budget), 0)        AS budget,
        COALESCE(SUM(actual_amount), 0) AS actual
    FROM stg_expenses
),
clean AS (
    SELECT
        COUNT(*)                        AS row_count,
        COALESCE(SUM(budget_eur), 0)    AS budget,
        COALESCE(SUM(actual_eur), 0)    AS actual
    FROM fact_expenses
    WHERE included
),
excluded AS (
    SELECT
        COUNT(*)                        AS row_count,
        COALESCE(SUM(budget_eur), 0)    AS budget,
        COALESCE(SUM(actual_eur), 0)    AS actual
    FROM fact_expenses
    WHERE NOT included
)
SELECT
    raw.row_count - excluded.row_count - clean.row_count AS row_difference,
    ROUND(raw.budget - excluded.budget - clean.budget, 2) AS budget_difference,
    ROUND(raw.actual - excluded.actual - clean.actual, 2) AS actual_difference
FROM raw, excluded, clean;


-- ============================================================================
-- T10. TESTS THAT CANNOT BE RUN WITH THIS DATASET
-- The ledger has no purchase order, approval, supplier master, invoice
-- number, payment date or bank record. The following questions are
-- therefore evidence requests, not queries:
--
--   * Was approval obtained before the purchase?
--   * Was the invoice paid twice?
--   * Is the supplier a valid, active vendor?
--   * Was VAT correctly applied?
--   * Is the item capital or revenue?
--
-- Documented in docs/risk_control_matrix.md and docs/follow_up_items.md.
-- ============================================================================
