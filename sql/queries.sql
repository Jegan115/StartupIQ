-- ============================================================================
-- StartupIQ Analytics Query Library
-- Purpose: 50 production-style SQL queries for KPI monitoring, portfolio review,
--          and BI reporting against the star schema.
-- Database target: SQLite-compatible ANSI SQL.
-- ============================================================================

-- -----------------------------------------------------------------------------
-- Executive KPIs
-- -----------------------------------------------------------------------------

-- 1) Business purpose: Establish the portfolio base size.
SELECT COUNT(*) AS total_startups
FROM fact_startups;

-- 2) Business purpose: Measure the share of startups reaching a successful exit.
SELECT ROUND(100.0 * SUM(CASE WHEN o.is_successful = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate_pct
FROM fact_startups f
JOIN dim_outcome o ON o.outcome_key = f.outcome_key;

-- 3) Business purpose: Measure how much of the portfolio ended in failure.
SELECT ROUND(100.0 * SUM(CASE WHEN o.outcome_name = 'Failure' THEN 1 ELSE 0 END) / COUNT(*), 2) AS failure_rate_pct
FROM fact_startups f
JOIN dim_outcome o ON o.outcome_key = f.outcome_key;

-- 4) Business purpose: Track how often companies are raising capital.
SELECT ROUND(AVG(funding_rounds), 2) AS average_funding_rounds
FROM fact_startups;

-- 5) Business purpose: Monitor average business revenue levels across the portfolio.
SELECT ROUND(AVG(revenue_usd), 2) AS average_revenue_usd
FROM fact_startups;

-- 6) Business purpose: Highlight average cash burn intensity.
SELECT ROUND(AVG(burn_rate_usd), 2) AS average_burn_rate_usd
FROM fact_startups;

-- -----------------------------------------------------------------------------
-- Funding Analysis
-- -----------------------------------------------------------------------------

-- 7) Business purpose: Compare funding activity across industries.
SELECT i.industry_name,
       COUNT(*) AS startup_count,
       ROUND(AVG(f.funding_rounds), 2) AS avg_funding_rounds
FROM fact_startups f
JOIN dim_industry i ON i.industry_key = f.industry_key
GROUP BY i.industry_name
ORDER BY avg_funding_rounds DESC;

-- 8) Business purpose: Identify whether geographic regions differ in funding behavior.
SELECT c.country_name,
       COUNT(*) AS startup_count,
       ROUND(AVG(f.funding_rounds), 2) AS avg_funding_rounds
FROM fact_startups f
JOIN dim_country c ON c.country_key = f.country_key
GROUP BY c.country_name
ORDER BY avg_funding_rounds DESC;

-- 9) Business purpose: Understand whether successful outcomes require more funding rounds.
SELECT o.outcome_name,
       COUNT(*) AS startup_count,
       ROUND(AVG(f.funding_rounds), 2) AS avg_funding_rounds
FROM fact_startups f
JOIN dim_outcome o ON o.outcome_key = f.outcome_key
GROUP BY o.outcome_name
ORDER BY avg_funding_rounds DESC;

-- 10) Business purpose: Surface the most heavily funded startups for executive review.
SELECT startup_id,
       revenue_usd,
       funding_rounds,
       market_size_billion
FROM fact_startups
ORDER BY funding_rounds DESC, revenue_usd DESC
LIMIT 15;

-- 11) Business purpose: Examine whether funding rounds correlate with outcome success.
SELECT o.outcome_name,
       ROUND(AVG(f.funding_rounds), 2) AS avg_rounds,
       ROUND(AVG(f.revenue_usd), 2) AS avg_revenue_usd
FROM fact_startups f
JOIN dim_outcome o ON o.outcome_key = f.outcome_key
GROUP BY o.outcome_name;

-- 12) Business purpose: Compare average funding intensity by investor type.
SELECT inv.investor_type,
       COUNT(*) AS startup_count,
       ROUND(AVG(f.funding_rounds), 2) AS avg_funding_rounds
FROM fact_startups f
LEFT JOIN dim_investor inv ON inv.investor_key = f.investor_key
GROUP BY inv.investor_type
ORDER BY avg_funding_rounds DESC;

-- 13) Business purpose: Rank industries by average funding rounds.
SELECT i.industry_name,
       ROUND(AVG(f.funding_rounds), 2) AS avg_funding_rounds,
       RANK() OVER (ORDER BY AVG(f.funding_rounds) DESC) AS funding_rank
FROM fact_startups f
JOIN dim_industry i ON i.industry_key = f.industry_key
GROUP BY i.industry_name;

-- 14) Business purpose: Highlight the top funded startups by market size and revenue.
SELECT startup_id,
       funding_rounds,
       market_size_billion,
       revenue_usd,
       DENSE_RANK() OVER (ORDER BY funding_rounds DESC, revenue_usd DESC) AS funding_density_rank
FROM fact_startups
ORDER BY funding_density_rank
LIMIT 20;

-- -----------------------------------------------------------------------------
-- Revenue Analysis
-- -----------------------------------------------------------------------------

-- 15) Business purpose: Identify industries with the strongest revenue contribution.
SELECT i.industry_name,
       ROUND(AVG(f.revenue_usd), 2) AS avg_revenue_usd
FROM fact_startups f
JOIN dim_industry i ON i.industry_key = f.industry_key
GROUP BY i.industry_name
ORDER BY avg_revenue_usd DESC;

-- 16) Business purpose: Compare revenue by geography.
SELECT c.country_name,
       ROUND(AVG(f.revenue_usd), 2) AS avg_revenue_usd
FROM fact_startups f
JOIN dim_country c ON c.country_key = f.country_key
GROUP BY c.country_name
ORDER BY avg_revenue_usd DESC;

-- 17) Business purpose: Evaluate how revenue scales with funding rounds.
SELECT funding_rounds,
       ROUND(AVG(revenue_usd), 2) AS avg_revenue_usd
FROM fact_startups
GROUP BY funding_rounds
ORDER BY funding_rounds;

-- 18) Business purpose: View how revenue is distributed across the portfolio.
SELECT NTILE(4) OVER (ORDER BY revenue_usd) AS revenue_quartile,
       ROUND(AVG(revenue_usd), 2) AS avg_revenue_usd
FROM fact_startups
GROUP BY revenue_quartile;

-- 19) Business purpose: Rank startups by revenue efficiency per employee.
SELECT startup_id,
       revenue_per_employee,
       RANK() OVER (ORDER BY revenue_per_employee DESC) AS revenue_efficiency_rank
FROM fact_startups
ORDER BY revenue_efficiency_rank
LIMIT 20;

-- 20) Business purpose: Show the highest revenue startups for executive attention.
SELECT startup_id,
       revenue_usd,
       funding_rounds,
       burn_ratio
FROM fact_startups
ORDER BY revenue_usd DESC
LIMIT 15;

-- 21) Business purpose: Explore whether investor type aligns with higher revenue performance.
SELECT inv.investor_type,
       ROUND(AVG(f.revenue_usd), 2) AS avg_revenue_usd
FROM fact_startups f
LEFT JOIN dim_investor inv ON inv.investor_key = f.investor_key
GROUP BY inv.investor_type
ORDER BY avg_revenue_usd DESC;

-- 22) Business purpose: Compare revenue outcomes across startup results.
SELECT o.outcome_name,
       ROUND(AVG(f.revenue_usd), 2) AS avg_revenue_usd,
       ROUND(AVG(f.market_size_billion), 2) AS avg_market_size_billion
FROM fact_startups f
JOIN dim_outcome o ON o.outcome_key = f.outcome_key
GROUP BY o.outcome_name;

-- -----------------------------------------------------------------------------
-- Burn Rate Analysis
-- -----------------------------------------------------------------------------

-- 23) Business purpose: Identify startups with the highest burn burden.
SELECT startup_id,
       burn_rate_usd,
       burn_ratio,
       revenue_usd
FROM fact_startups
ORDER BY burn_ratio DESC
LIMIT 20;

-- 24) Business purpose: Compare burn ratio by startup outcome.
SELECT o.outcome_name,
       ROUND(AVG(f.burn_ratio), 2) AS avg_burn_ratio
FROM fact_startups f
JOIN dim_outcome o ON o.outcome_key = f.outcome_key
GROUP BY o.outcome_name
ORDER BY avg_burn_ratio DESC;

-- 25) Business purpose: Flag companies with elevated burn risk.
SELECT startup_id,
       burn_ratio,
       CASE WHEN burn_ratio > 50 THEN 'High Risk' ELSE 'Manageable' END AS burn_risk_flag
FROM fact_startups
ORDER BY burn_ratio DESC
LIMIT 25;

-- 26) Business purpose: Understand whether some industries burn cash faster than others.
SELECT i.industry_name,
       ROUND(AVG(f.burn_ratio), 2) AS avg_burn_ratio
FROM fact_startups f
JOIN dim_industry i ON i.industry_key = f.industry_key
GROUP BY i.industry_name
ORDER BY avg_burn_ratio DESC;

-- 27) Business purpose: Assess whether founder background aligns with burn discipline.
SELECT fd.founder_background,
       ROUND(AVG(f.burn_ratio), 2) AS avg_burn_ratio
FROM fact_startups f
JOIN dim_founder fd ON fd.founder_key = f.founder_key
GROUP BY fd.founder_background
ORDER BY avg_burn_ratio DESC;

-- 28) Business purpose: Evaluate whether revenue is supporting burn load.
SELECT startup_id,
       revenue_usd,
       burn_rate_usd,
       ROUND(CASE WHEN revenue_usd > 0 THEN burn_rate_usd / revenue_usd ELSE NULL END, 4) AS burn_to_revenue_ratio
FROM fact_startups
ORDER BY burn_to_revenue_ratio DESC
LIMIT 20;

-- 29) Business purpose: Segment burn profile by risk tier for portfolio monitoring.
SELECT CASE
           WHEN burn_ratio > 100 THEN 'Critical'
           WHEN burn_ratio > 50 THEN 'High'
           WHEN burn_ratio > 20 THEN 'Moderate'
           ELSE 'Low'
       END AS burn_tier,
       COUNT(*) AS startup_count
FROM fact_startups
GROUP BY burn_tier
ORDER BY startup_count DESC;

-- 30) Business purpose: Size the burn-rate distribution across the portfolio.
SELECT NTILE(5) OVER (ORDER BY burn_ratio) AS burn_quintile,
       ROUND(AVG(burn_ratio), 2) AS avg_burn_ratio
FROM fact_startups
GROUP BY burn_quintile;

-- -----------------------------------------------------------------------------
-- Industry Analysis
-- -----------------------------------------------------------------------------

-- 31) Business purpose: Measure industry-level success rates.
SELECT i.industry_name,
       ROUND(100.0 * SUM(CASE WHEN o.is_successful = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate_pct
FROM fact_startups f
JOIN dim_industry i ON i.industry_key = f.industry_key
JOIN dim_outcome o ON o.outcome_key = f.outcome_key
GROUP BY i.industry_name
ORDER BY success_rate_pct DESC;

-- 32) Business purpose: Compare industry funding behavior.
SELECT i.industry_name,
       COUNT(*) AS startup_count,
       ROUND(AVG(f.funding_rounds), 2) AS avg_funding_rounds,
       ROUND(AVG(f.revenue_usd), 2) AS avg_revenue_usd
FROM fact_startups f
JOIN dim_industry i ON i.industry_key = f.industry_key
GROUP BY i.industry_name
ORDER BY avg_funding_rounds DESC;

-- 33) Business purpose: Rank industries by average revenue.
SELECT i.industry_name,
       ROUND(AVG(f.revenue_usd), 2) AS avg_revenue_usd,
       RANK() OVER (ORDER BY AVG(f.revenue_usd) DESC) AS revenue_rank
FROM fact_startups f
JOIN dim_industry i ON i.industry_key = f.industry_key
GROUP BY i.industry_name;

-- 34) Business purpose: Evaluate whether industry economics support efficient growth.
SELECT i.industry_name,
       ROUND(AVG(f.revenue_per_employee), 2) AS avg_revenue_per_employee,
       ROUND(AVG(f.capital_efficiency_ratio), 4) AS avg_capital_efficiency_ratio
FROM fact_startups f
JOIN dim_industry i ON i.industry_key = f.industry_key
GROUP BY i.industry_name
ORDER BY avg_revenue_per_employee DESC;

-- 35) Business purpose: Compare market size and traction across industries.
SELECT i.industry_name,
       ROUND(AVG(f.market_size_billion), 2) AS avg_market_size_billion,
       ROUND(AVG(f.product_traction_users), 2) AS avg_product_traction_users
FROM fact_startups f
JOIN dim_industry i ON i.industry_key = f.industry_key
GROUP BY i.industry_name
ORDER BY avg_product_traction_users DESC;

-- 36) Business purpose: Identify industries that are most capital efficient.
SELECT i.industry_name,
       ROUND(AVG(f.capital_efficiency_ratio), 4) AS avg_capital_efficiency_ratio
FROM fact_startups f
JOIN dim_industry i ON i.industry_key = f.industry_key
GROUP BY i.industry_name
ORDER BY avg_capital_efficiency_ratio DESC;

-- -----------------------------------------------------------------------------
-- Geographic Analysis
-- -----------------------------------------------------------------------------

-- 37) Business purpose: Rank countries by startup counts for portfolio coverage.
SELECT c.country_name,
       COUNT(*) AS startup_count
FROM fact_startups f
JOIN dim_country c ON c.country_key = f.country_key
GROUP BY c.country_name
ORDER BY startup_count DESC;

-- 38) Business purpose: Measure success rates by country.
SELECT c.country_name,
       ROUND(100.0 * SUM(CASE WHEN o.is_successful = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate_pct
FROM fact_startups f
JOIN dim_country c ON c.country_key = f.country_key
JOIN dim_outcome o ON o.outcome_key = f.outcome_key
GROUP BY c.country_name
ORDER BY success_rate_pct DESC;

-- 39) Business purpose: Compare average revenue across countries.
SELECT c.country_name,
       ROUND(AVG(f.revenue_usd), 2) AS avg_revenue_usd
FROM fact_startups f
JOIN dim_country c ON c.country_key = f.country_key
GROUP BY c.country_name;

-- 40) Business purpose: Compare average funding rounds by country.
SELECT c.country_name,
       ROUND(AVG(f.funding_rounds), 2) AS avg_funding_rounds
FROM fact_startups f
JOIN dim_country c ON c.country_key = f.country_key
GROUP BY c.country_name;

-- 41) Business purpose: Surface any country-level differences in burn risk profile.
SELECT c.country_name,
       ROUND(AVG(f.burn_ratio), 2) AS avg_burn_ratio
FROM fact_startups f
JOIN dim_country c ON c.country_key = f.country_key
GROUP BY c.country_name
ORDER BY avg_burn_ratio DESC;

-- -----------------------------------------------------------------------------
-- Startup Outcome Analysis
-- -----------------------------------------------------------------------------

-- 42) Business purpose: Review the overall distribution of startup outcomes.
SELECT o.outcome_name,
       COUNT(*) AS startup_count
FROM fact_startups f
JOIN dim_outcome o ON o.outcome_key = f.outcome_key
GROUP BY o.outcome_name
ORDER BY startup_count DESC;

-- 43) Business purpose: Test whether higher funding rounds correspond to successful exits.
SELECT CASE WHEN funding_rounds >= 3 THEN '3+ Rounds' ELSE 'Under 3 Rounds' END AS funding_band,
       ROUND(100.0 * SUM(CASE WHEN o.is_successful = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate_pct
FROM fact_startups f
JOIN dim_outcome o ON o.outcome_key = f.outcome_key
GROUP BY funding_band;

-- 44) Business purpose: Compare success rates by industry.
SELECT i.industry_name,
       ROUND(100.0 * SUM(CASE WHEN o.is_successful = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate_pct
FROM fact_startups f
JOIN dim_industry i ON i.industry_key = f.industry_key
JOIN dim_outcome o ON o.outcome_key = f.outcome_key
GROUP BY i.industry_name
ORDER BY success_rate_pct DESC;

-- 45) Business purpose: Assess whether founder background is associated with stronger outcomes.
SELECT fd.founder_background,
       ROUND(100.0 * SUM(CASE WHEN o.is_successful = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate_pct
FROM fact_startups f
JOIN dim_founder fd ON fd.founder_key = f.founder_key
JOIN dim_outcome o ON o.outcome_key = f.outcome_key
GROUP BY fd.founder_background
ORDER BY success_rate_pct DESC;

-- 46) Business purpose: Review whether investor involvement is linked to outcome quality.
SELECT inv.investor_type,
       ROUND(100.0 * SUM(CASE WHEN o.is_successful = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate_pct
FROM fact_startups f
LEFT JOIN dim_investor inv ON inv.investor_key = f.investor_key
JOIN dim_outcome o ON o.outcome_key = f.outcome_key
GROUP BY inv.investor_type
ORDER BY success_rate_pct DESC;

-- -----------------------------------------------------------------------------
-- Advanced Analytics
-- -----------------------------------------------------------------------------

-- 47) Business purpose: Rank startups by revenue using a window function.
SELECT startup_id,
       revenue_usd,
       DENSE_RANK() OVER (ORDER BY revenue_usd DESC) AS revenue_dense_rank
FROM fact_startups
ORDER BY revenue_dense_rank
LIMIT 20;

-- 48) Business purpose: Show running totals of startup count by funding rounds.
WITH ranked AS (
    SELECT funding_rounds,
           COUNT(*) AS startup_count
    FROM fact_startups
    GROUP BY funding_rounds
)
SELECT funding_rounds,
       startup_count,
       SUM(startup_count) OVER (ORDER BY funding_rounds) AS running_total_startups
FROM ranked
ORDER BY funding_rounds;

-- 49) Business purpose: Bucket startups into burn percentiles for risk segmentation.
WITH ordered_burn AS (
    SELECT burn_ratio,
           NTILE(10) OVER (ORDER BY burn_ratio) AS burn_percentile
    FROM fact_startups
)
SELECT burn_percentile,
       ROUND(AVG(burn_ratio), 2) AS avg_burn_ratio,
       COUNT(*) AS startup_count
FROM ordered_burn
GROUP BY burn_percentile
ORDER BY burn_percentile;

-- 50) Business purpose: Create a rolling average of revenue by funding-round band.
SELECT funding_rounds,
       ROUND(AVG(revenue_usd), 2) AS avg_revenue_usd,
       ROUND(AVG(AVG(revenue_usd)) OVER (ORDER BY funding_rounds ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS moving_avg_revenue
FROM fact_startups
GROUP BY funding_rounds
ORDER BY funding_rounds;
