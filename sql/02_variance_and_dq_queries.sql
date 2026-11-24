-- ============================================================================
-- 02_variance_and_dq_queries.sql
-- Analysis queries for the H1 2026 expense review.
-- Run after 01_create_tables.sql and 03_load_data.sql.
--
-- Sign convention: positive variance = adverse (actual above budget).
-- ============================================================================


-- ============================================================================
-- A. CATEGORY SUMMARY WITH ADVERSE / FAVOURABLE RANKS
-- Expected: Freight +30,829.24 is the largest adverse;
--           Payroll -26,110.47 is the largest favourable.
-- ============================================================================
WITH category_totals AS (
    SELECT
        category,
        COUNT(*)                AS txn_count,
        SUM(budget_eur)         AS budget_eur,
        SUM(actual_eur)         AS actual_eur,
        SUM(variance_eur)       AS variance_eur
    FROM fact_expenses
    WHERE included
    GROUP BY category
)
SELECT
    category,
    txn_count,
    ROUND(budget_eur, 2)        AS budget_eur,
    ROUND(actual_eur, 2)        AS actual_eur,
    ROUND(variance_eur, 2)      AS variance_eur,
    CASE
        WHEN budget_eur >= 100
        THEN ROUND(variance_eur / budget_eur * 100, 2)
    END                         AS variance_pct,
    RANK() OVER (ORDER BY variance_eur DESC) AS rank_adverse,
    RANK() OVER (ORDER BY variance_eur ASC)  AS rank_favourable
FROM category_totals
ORDER BY variance_eur DESC;


-- ============================================================================
-- B. MONTHLY SUMMARY WITH CUMULATIVE H1 SPEND
-- Expected: total variance +59,379.88 (+2.93%).
-- ============================================================================
WITH monthly_totals AS (
    SELECT
        month,
        COUNT(*)                AS txn_count,
        SUM(budget_eur)         AS budget_eur,
        SUM(actual_eur)         AS actual_eur,
        SUM(variance_eur)       AS variance_eur
    FROM fact_expenses
    WHERE included
    GROUP BY month
)
SELECT
    month,
    txn_count,
    ROUND(budget_eur, 2)        AS budget_eur,
    ROUND(actual_eur, 2)        AS actual_eur,
    ROUND(variance_eur, 2)      AS variance_eur,
    CASE
        WHEN budget_eur >= 100
        THEN ROUND(variance_eur / budget_eur * 100, 2)
    END                         AS variance_pct,
    ROUND(SUM(actual_eur) OVER (ORDER BY month), 2)   AS cumulative_actual_eur,
    ROUND(SUM(variance_eur) OVER (ORDER BY month), 2) AS cumulative_variance_eur
FROM monthly_totals
ORDER BY month;


-- ============================================================================
-- C. MONTH x CATEGORY — TOP 12 ADVERSE CELLS
-- Expected top cell: 2026-06 Freight +21,340.17 (+44.64%).
-- ============================================================================
SELECT
    month,
    category,
    COUNT(*)                    AS txn_count,
    ROUND(SUM(budget_eur), 2)   AS budget_eur,
    ROUND(SUM(actual_eur), 2)   AS actual_eur,
    ROUND(SUM(variance_eur), 2) AS variance_eur,
    CASE
        WHEN SUM(budget_eur) >= 100
        THEN ROUND(SUM(variance_eur) / SUM(budget_eur) * 100, 2)
    END                         AS variance_pct
FROM fact_expenses
WHERE included
GROUP BY month, category
ORDER BY SUM(variance_eur) DESC
LIMIT 12;


-- ============================================================================
-- D. MONTH x CATEGORY — TOP 12 FAVOURABLE CELLS
-- ============================================================================
SELECT
    month,
    category,
    COUNT(*)                    AS txn_count,
    ROUND(SUM(budget_eur), 2)   AS budget_eur,
    ROUND(SUM(actual_eur), 2)   AS actual_eur,
    ROUND(SUM(variance_eur), 2) AS variance_eur,
    CASE
        WHEN SUM(budget_eur) >= 100
        THEN ROUND(SUM(variance_eur) / SUM(budget_eur) * 100, 2)
    END                         AS variance_pct
FROM fact_expenses
WHERE included
GROUP BY month, category
ORDER BY SUM(variance_eur) ASC
LIMIT 12;


-- ============================================================================
-- E. TOP 15 ADVERSE LINE ITEMS
-- Expected: TXN-2166 +15,077.37; TXN-2326 +12,340.36; TXN-2130 +9,866.75.
-- ============================================================================
SELECT
    txn_id,
    txn_date,
    department,
    category,
    description,
    ROUND(budget_eur, 2)    AS budget_eur,
    ROUND(actual_eur, 2)    AS actual_eur,
    ROUND(variance_eur, 2)  AS variance_eur,
    variance_pct,
    dq_flags
FROM fact_expenses
WHERE included
ORDER BY variance_eur DESC
LIMIT 15;


-- ============================================================================
-- F. TOP 15 FAVOURABLE LINE ITEMS
-- Expected: credit notes lead (TXN-2108 -10,545.71, TXN-2142 -10,010.26).
-- ============================================================================
SELECT
    txn_id,
    txn_date,
    department,
    category,
    description,
    ROUND(budget_eur, 2)    AS budget_eur,
    ROUND(actual_eur, 2)    AS actual_eur,
    ROUND(variance_eur, 2)  AS variance_eur,
    variance_pct,
    dq_flags
FROM fact_expenses
WHERE included
ORDER BY variance_eur ASC
LIMIT 15;


-- ============================================================================
-- G. DEPARTMENT SUMMARY
-- ============================================================================
SELECT
    department,
    COUNT(*)                    AS txn_count,
    ROUND(SUM(budget_eur), 2)   AS budget_eur,
    ROUND(SUM(actual_eur), 2)   AS actual_eur,
    ROUND(SUM(variance_eur), 2) AS variance_eur,
    CASE
        WHEN SUM(budget_eur) >= 100
        THEN ROUND(SUM(variance_eur) / SUM(budget_eur) * 100, 2)
    END                         AS variance_pct
FROM fact_expenses
WHERE included
GROUP BY department
ORDER BY SUM(variance_eur) DESC;


-- ============================================================================
-- H. DISPOSITION COUNTS
-- Expected: 417 INCLUDE, 18 INCLUDE_FLAGGED, 7 CORRECT_AND_INCLUDE,
--           10 QUARANTINE, 2 EXCLUDE_OUT_OF_PERIOD.
-- ============================================================================
SELECT
    disposition,
    COUNT(*) AS row_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS share_pct
FROM fact_expenses
GROUP BY disposition
ORDER BY row_count DESC;


-- ============================================================================
-- I. DATA-QUALITY FLAG FREQUENCY
-- ============================================================================
SELECT
    flag,
    COUNT(*) AS row_count
FROM (
    SELECT unnest(string_to_array(dq_flags, '|')) AS flag
    FROM fact_expenses
    WHERE dq_flags <> 'CLEAN'
) AS flags
GROUP BY flag
ORDER BY row_count DESC, flag;


-- ============================================================================
-- J. FOLLOW-UP CANDIDATES (materiality screen)
-- ============================================================================
SELECT *
FROM v_follow_up_candidates
LIMIT 20;


-- ============================================================================
-- K. RECONCILIATION: RAW -> EXCLUDED -> CLEAN
-- Expected: raw - excluded - clean = 0 rows, 0.00 budget, 0.00 actual.
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
SELECT 'Raw file' AS layer, row_count, ROUND(budget, 2) AS budget_eur, ROUND(actual, 2) AS actual_eur
FROM raw
UNION ALL
SELECT 'Less: excluded (quarantine + out of period)', row_count, ROUND(budget, 2), ROUND(actual, 2)
FROM excluded
UNION ALL
SELECT 'Clean ledger', row_count, ROUND(budget, 2), ROUND(actual, 2)
FROM clean
UNION ALL
SELECT
    'CHECK (raw - excluded - clean)',
    raw.row_count - excluded.row_count - clean.row_count,
    ROUND(raw.budget - excluded.budget - clean.budget, 2),
    ROUND(raw.actual - excluded.actual - clean.actual, 2)
FROM raw, excluded, clean;


-- ============================================================================
-- L. CREDIT NOTES AND UNBUDGETED SPEND
-- ============================================================================
SELECT
    txn_id,
    txn_date,
    department,
    category,
    description,
    ROUND(budget_eur, 2)    AS budget_eur,
    ROUND(actual_eur, 2)    AS actual_eur,
    ROUND(variance_eur, 2)  AS variance_eur,
    dq_flags
FROM fact_expenses
WHERE included
  AND (actual_eur < 0 OR (budget_eur = 0 AND actual_eur > 0))
ORDER BY actual_eur;


-- ============================================================================
-- M. LINE ITEMS PASSING THE REVIEW THRESHOLD
--    abs(variance) >= 1,000 EUR AND abs(variance %) >= 10%
-- ============================================================================
SELECT
    txn_id,
    txn_date,
    department,
    category,
    ROUND(budget_eur, 2)    AS budget_eur,
    ROUND(actual_eur, 2)    AS actual_eur,
    ROUND(variance_eur, 2)  AS variance_eur,
    variance_pct
FROM fact_expenses
WHERE included
  AND ABS(variance_eur) >= 1000
  AND ABS(variance_pct) >= 10
ORDER BY variance_eur DESC;
