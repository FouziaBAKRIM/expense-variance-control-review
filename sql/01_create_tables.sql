-- ============================================================================
-- 01_create_tables.sql
-- H1 2026 expense review — synthetic educational dataset
-- PostgreSQL 14+
--
-- Run order:
--   1. 01_create_tables.sql
--   2. 03_load_data.sql
--   3. 02_variance_and_dq_queries.sql
--   4. 04_control_tests.sql
-- ============================================================================

DROP VIEW IF EXISTS v_follow_up_candidates;
DROP VIEW IF EXISTS v_category_monthly_variance;
DROP VIEW IF EXISTS v_monthly_variance;
DROP VIEW IF EXISTS v_category_variance;
DROP VIEW IF EXISTS v_dq_exceptions;
DROP TABLE IF EXISTS fact_expenses;
DROP TABLE IF EXISTS stg_expenses;

-- ----------------------------------------------------------------------------
-- Staging table: mirrors the CSV column order for \copy
-- ----------------------------------------------------------------------------
CREATE TABLE stg_expenses (
    txn_id          VARCHAR(12),
    txn_date        DATE,
    month           VARCHAR(7),
    department      VARCHAR(60),
    category        VARCHAR(60),
    category_raw    VARCHAR(60),
    description     TEXT,
    budget          NUMERIC(12, 2),
    actual_amount   NUMERIC(12, 2),
    variance_eur    NUMERIC(12, 2),
    variance_pct    NUMERIC(9, 2),
    disposition     VARCHAR(30),
    dq_flags        VARCHAR(200),
    needs_review    BOOLEAN,
    included        BOOLEAN
);

-- ----------------------------------------------------------------------------
-- Fact table: one row per transaction line, including quarantined rows
-- ----------------------------------------------------------------------------
CREATE TABLE fact_expenses (
    txn_id          VARCHAR(12) PRIMARY KEY,
    txn_date        DATE,
    month           VARCHAR(7) NOT NULL,
    department      VARCHAR(60) NOT NULL,
    category        VARCHAR(60) NOT NULL,
    category_raw    VARCHAR(60),
    description     TEXT,
    budget_eur      NUMERIC(12, 2) NOT NULL,
    actual_eur      NUMERIC(12, 2) NOT NULL,
    variance_eur    NUMERIC(12, 2) NOT NULL,
    variance_pct    NUMERIC(9, 2),
    disposition     VARCHAR(30) NOT NULL,
    dq_flags        VARCHAR(200) NOT NULL,
    needs_review    BOOLEAN NOT NULL DEFAULT FALSE,
    included        BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_disposition CHECK (
        disposition IN (
            'INCLUDE',
            'CORRECT_AND_INCLUDE',
            'INCLUDE_FLAGGED',
            'QUARANTINE',
            'EXCLUDE_OUT_OF_PERIOD'
        )
    ),
    CONSTRAINT chk_month CHECK (month ~ '^([0-9]{4}-[0-9]{2}|UNKNOWN)$'),
    CONSTRAINT chk_variance CHECK (
        ROUND(actual_eur - budget_eur, 2) = variance_eur
    )
);

CREATE INDEX idx_fact_month      ON fact_expenses (month);
CREATE INDEX idx_fact_category   ON fact_expenses (category);
CREATE INDEX idx_fact_department ON fact_expenses (department);
CREATE INDEX idx_fact_included   ON fact_expenses (included);

-- ----------------------------------------------------------------------------
-- Views
-- ----------------------------------------------------------------------------
CREATE VIEW v_dq_exceptions AS
SELECT
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
    dq_flags
FROM fact_expenses
WHERE dq_flags <> 'CLEAN';

CREATE VIEW v_category_variance AS
SELECT
    category,
    COUNT(*)                                   AS txn_count,
    ROUND(SUM(budget_eur), 2)                  AS budget_eur,
    ROUND(SUM(actual_eur), 2)                  AS actual_eur,
    ROUND(SUM(variance_eur), 2)                AS variance_eur,
    CASE
        WHEN SUM(budget_eur) >= 100
        THEN ROUND(SUM(variance_eur) / SUM(budget_eur) * 100, 2)
    END                                        AS variance_pct
FROM fact_expenses
WHERE included
GROUP BY category;

CREATE VIEW v_monthly_variance AS
SELECT
    month,
    COUNT(*)                                   AS txn_count,
    ROUND(SUM(budget_eur), 2)                  AS budget_eur,
    ROUND(SUM(actual_eur), 2)                  AS actual_eur,
    ROUND(SUM(variance_eur), 2)                AS variance_eur,
    CASE
        WHEN SUM(budget_eur) >= 100
        THEN ROUND(SUM(variance_eur) / SUM(budget_eur) * 100, 2)
    END                                        AS variance_pct
FROM fact_expenses
WHERE included
GROUP BY month;

CREATE VIEW v_category_monthly_variance AS
SELECT
    month,
    category,
    department,
    COUNT(*)                                   AS txn_count,
    ROUND(SUM(budget_eur), 2)                  AS budget_eur,
    ROUND(SUM(actual_eur), 2)                  AS actual_eur,
    ROUND(SUM(variance_eur), 2)                AS variance_eur,
    CASE
        WHEN SUM(budget_eur) >= 100
        THEN ROUND(SUM(variance_eur) / SUM(budget_eur) * 100, 2)
    END                                        AS variance_pct
FROM fact_expenses
WHERE included
GROUP BY month, category, department;

CREATE VIEW v_follow_up_candidates AS
SELECT
    txn_id,
    txn_date,
    month,
    department,
    category,
    description,
    budget_eur,
    actual_eur,
    variance_eur,
    variance_pct,
    dq_flags
FROM fact_expenses
WHERE included
  AND (
        ABS(variance_eur) >= 1000
     OR dq_flags LIKE '%UNBUDGETED%'
     OR dq_flags LIKE '%CREDIT_NOTE%'
     OR dq_flags LIKE '%OUTLIER%'
  )
ORDER BY variance_eur DESC;
