-- ============================================================================
-- StartupIQ Star Schema for BI and Power BI Connectivity
-- Grain: one row per startup (fact_startups)
-- Database target: SQLite, compatible with PostgreSQL and MySQL conventions
-- ============================================================================

PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS fact_startups;
DROP TABLE IF EXISTS dim_investor;
DROP TABLE IF EXISTS dim_founder;
DROP TABLE IF EXISTS dim_outcome;
DROP TABLE IF EXISTS dim_country;
DROP TABLE IF EXISTS dim_industry;

PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------------------------
-- Dimension: dim_industry
-- Purpose: Standardizes industry categories for slicing and grouping.
-- -----------------------------------------------------------------------------
CREATE TABLE dim_industry (
    industry_key INTEGER PRIMARY KEY,
    industry_name VARCHAR(50) NOT NULL UNIQUE,
    industry_group VARCHAR(30),
    is_high_growth BOOLEAN NOT NULL DEFAULT 0
);

-- -----------------------------------------------------------------------------
-- Dimension: dim_country
-- Purpose: Supports geographic analysis. The cleaned dataset does not include
--          country values, so a default "Unknown" row is used until richer
--          source data is available.
-- -----------------------------------------------------------------------------
CREATE TABLE dim_country (
    country_key INTEGER PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL UNIQUE,
    country_code VARCHAR(10),
    is_known BOOLEAN NOT NULL DEFAULT 0
);

-- -----------------------------------------------------------------------------
-- Dimension: dim_outcome
-- Purpose: Encodes startup lifecycle results for outcome-based analysis.
-- -----------------------------------------------------------------------------
CREATE TABLE dim_outcome (
    outcome_key INTEGER PRIMARY KEY,
    outcome_name VARCHAR(30) NOT NULL UNIQUE,
    outcome_group VARCHAR(20) NOT NULL,
    is_successful BOOLEAN NOT NULL DEFAULT 0
);

-- -----------------------------------------------------------------------------
-- Dimension: dim_founder
-- Purpose: Captures founder profile characteristics that affect startup behavior.
-- -----------------------------------------------------------------------------
CREATE TABLE dim_founder (
    founder_key INTEGER PRIMARY KEY,
    founder_background VARCHAR(50) NOT NULL,
    founder_experience_years INTEGER NOT NULL DEFAULT 0,
    experience_band VARCHAR(20) NOT NULL,
    founder_profile_label VARCHAR(100) NOT NULL,
    UNIQUE (founder_background, founder_experience_years, experience_band)
);

-- -----------------------------------------------------------------------------
-- Dimension: dim_investor
-- Purpose: Standardizes investor participation and supports funding analysis.
-- -----------------------------------------------------------------------------
CREATE TABLE dim_investor (
    investor_key INTEGER PRIMARY KEY,
    investor_type VARCHAR(30) NOT NULL UNIQUE,
    investor_tier VARCHAR(20) NOT NULL,
    is_active_investor BOOLEAN NOT NULL DEFAULT 0
);

-- -----------------------------------------------------------------------------
-- Fact table: fact_startups
-- Purpose: Stores one row per startup with business metrics used by BI tools.
-- -----------------------------------------------------------------------------
CREATE TABLE fact_startups (
    startup_id VARCHAR(50) PRIMARY KEY,
    industry_key INTEGER NOT NULL,
    country_key INTEGER NOT NULL,
    outcome_key INTEGER NOT NULL,
    founder_key INTEGER NOT NULL,
    investor_key INTEGER,
    startup_count INTEGER NOT NULL DEFAULT 1,
    funding_rounds INTEGER NOT NULL DEFAULT 0,
    team_size INTEGER NOT NULL DEFAULT 0,
    market_size_billion DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    product_traction_users INTEGER NOT NULL DEFAULT 0,
    revenue_usd DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    burn_rate_usd DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    burn_ratio DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
    revenue_per_employee DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
    user_traction_per_employee DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
    capital_efficiency_ratio DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
    source_row_number INTEGER,
    FOREIGN KEY (industry_key) REFERENCES dim_industry(industry_key),
    FOREIGN KEY (country_key) REFERENCES dim_country(country_key),
    FOREIGN KEY (outcome_key) REFERENCES dim_outcome(outcome_key),
    FOREIGN KEY (founder_key) REFERENCES dim_founder(founder_key),
    FOREIGN KEY (investor_key) REFERENCES dim_investor(investor_key),
    CHECK (funding_rounds >= 0),
    CHECK (team_size >= 0),
    CHECK (product_traction_users >= 0)
);

-- -----------------------------------------------------------------------------
-- Indexes for analytics performance
-- -----------------------------------------------------------------------------
CREATE INDEX idx_fact_industry ON fact_startups(industry_key);
CREATE INDEX idx_fact_country ON fact_startups(country_key);
CREATE INDEX idx_fact_outcome ON fact_startups(outcome_key);
CREATE INDEX idx_fact_founder ON fact_startups(founder_key);
CREATE INDEX idx_fact_investor ON fact_startups(investor_key);
CREATE INDEX idx_fact_revenue ON fact_startups(revenue_usd);
CREATE INDEX idx_fact_burn_ratio ON fact_startups(burn_ratio);
CREATE INDEX idx_fact_revenue_outcome ON fact_startups(outcome_key, revenue_usd);
