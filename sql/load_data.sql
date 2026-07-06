-- ============================================================================
-- StartupIQ Star Schema Load Script
-- Purpose: Populate the warehouse dimensions and fact table from the cleaned CSV
--          dataset so Power BI and BI tools can query the warehouse directly.
-- ============================================================================

-- -----------------------------------------------------------------------------
-- Assumptions
-- 1. The cleaned dataset is available at data/cleaned/startup_cleaned.csv.
-- 2. Country information is not present in the cleaned file, so all rows are
--    mapped to a default 'Unknown' country dimension row.
-- 3. This script is written to be compatible with SQLite and PostgreSQL.
-- -----------------------------------------------------------------------------

-- Load dimension values from the source data.
-- SQLite-compatible approach: insert distinct values using SELECT DISTINCT.

INSERT OR IGNORE INTO dim_industry (industry_key, industry_name, industry_group, is_high_growth)
SELECT ROW_NUMBER() OVER (ORDER BY industry_name) AS industry_key,
       industry_name,
       CASE
           WHEN industry_name IN ('AI', 'Crypto', 'Fintech') THEN 'Emerging'
           ELSE 'Mainstream'
       END AS industry_group,
       CASE
           WHEN industry_name IN ('AI', 'Fintech', 'Crypto') THEN 1 ELSE 0
       END AS is_high_growth
FROM (
    SELECT DISTINCT sector AS industry_name
    FROM temp_startup_source
);

INSERT OR IGNORE INTO dim_country (country_key, country_name, country_code, is_known)
SELECT 1, 'Unknown', 'UNK', 0;

INSERT OR IGNORE INTO dim_outcome (outcome_key, outcome_name, outcome_group, is_successful)
SELECT 1, 'Failure', 'Non-Successful', 0
UNION ALL
SELECT 2, 'Acquisition', 'Successful Exit', 1
UNION ALL
SELECT 3, 'IPO', 'Successful Exit', 1;

INSERT OR IGNORE INTO dim_founder (founder_key, founder_background, founder_experience_years, experience_band, founder_profile_label)
SELECT ROW_NUMBER() OVER (ORDER BY founder_background, founder_experience_years, experience_band) AS founder_key,
       founder_background,
       founder_experience_years,
       CASE
           WHEN founder_experience_years < 5 THEN 'Novice'
           WHEN founder_experience_years < 15 THEN 'Experienced'
           ELSE 'Veteran'
       END AS experience_band,
       founder_background || ' | ' || CASE
           WHEN founder_experience_years < 5 THEN 'Novice'
           WHEN founder_experience_years < 15 THEN 'Experienced'
           ELSE 'Veteran'
       END AS founder_profile_label
FROM (
    SELECT DISTINCT founder_background, founder_experience_years
    FROM temp_startup_source
);

INSERT OR IGNORE INTO dim_investor (investor_key, investor_type, investor_tier, is_active_investor)
SELECT 1, 'none', 'No Investor', 0
UNION ALL
SELECT 2, 'angel', 'Angel', 1
UNION ALL
SELECT 3, 'tier1_vc', 'Tier 1 VC', 1
UNION ALL
SELECT 4, 'tier2_vc', 'Tier 2 VC', 1;

-- -----------------------------------------------------------------------------
-- Load the fact table from the cleaned source data.
-- -----------------------------------------------------------------------------
INSERT INTO fact_startups (
    startup_id,
    industry_key,
    country_key,
    outcome_key,
    founder_key,
    investor_key,
    startup_count,
    funding_rounds,
    team_size,
    market_size_billion,
    product_traction_users,
    revenue_usd,
    burn_rate_usd,
    burn_ratio,
    revenue_per_employee,
    user_traction_per_employee,
    capital_efficiency_ratio,
    source_row_number
)
SELECT
    'ST-' || CAST(ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS VARCHAR(20)) AS startup_id,
    di.industry_key,
    dc.country_key,
    do.outcome_key,
    df.founder_key,
    dinv.investor_key,
    1 AS startup_count,
    CAST(s.funding_rounds AS INTEGER) AS funding_rounds,
    CAST(s.team_size AS INTEGER) AS team_size,
    CAST(s.market_size_billion AS DECIMAL(12,2)) AS market_size_billion,
    CAST(s.product_traction_users AS INTEGER) AS product_traction_users,
    CAST(s.revenue_usd AS DECIMAL(15,2)) AS revenue_usd,
    CAST(s.burn_rate_usd AS DECIMAL(15,2)) AS burn_rate_usd,
    CAST(s.burn_ratio AS DECIMAL(12,4)) AS burn_ratio,
    CAST(s.revenue_per_employee AS DECIMAL(12,4)) AS revenue_per_employee,
    CAST(s.user_traction_per_employee AS DECIMAL(12,4)) AS user_traction_per_employee,
    CAST(s.capital_efficiency_ratio AS DECIMAL(12,4)) AS capital_efficiency_ratio,
    ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS source_row_number
FROM temp_startup_source s
JOIN dim_industry di ON di.industry_name = s.sector
JOIN dim_country dc ON dc.country_name = 'Unknown'
JOIN dim_outcome do ON do.outcome_name = s.outcome
JOIN dim_founder df ON df.founder_background = s.founder_background AND df.founder_experience_years = s.founder_experience_years
LEFT JOIN dim_investor dinv ON dinv.investor_type = s.investor_type;

-- -----------------------------------------------------------------------------
-- Optional: create a staging view or table for the source CSV.
-- For SQLite, a temporary table is used so the load script remains self-contained.
-- -----------------------------------------------------------------------------
CREATE TEMP TABLE temp_startup_source AS
SELECT
    sector,
    investor_type,
    founder_background,
    founder_experience_years,
    outcome,
    funding_rounds,
    team_size,
    market_size_billion,
    product_traction_users,
    revenue_usd,
    burn_rate_usd,
    burn_ratio,
    revenue_per_employee,
    user_traction_per_employee,
    capital_efficiency_ratio
FROM CSVREAD('data/cleaned/startup_cleaned.csv');
