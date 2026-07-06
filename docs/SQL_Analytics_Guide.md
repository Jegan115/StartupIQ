# StartupIQ SQL Analytics Guide

## 1. Why This Schema Was Chosen

The StartupIQ warehouse uses a star schema because it is optimized for analytical workloads. BI tools such as Power BI perform best when dimensions are denormalized and facts are stored at a clear grain. This reduces join complexity and improves readability for business users.

## 2. BI Best Practices Applied

- Use a single fact table at the startup grain
- Keep dimensions compact and descriptive
- Use surrogate keys for stable joins and easier maintenance
- Store measures in the fact table and descriptors in dimensions
- Keep the schema intuitive for dashboard authors

## 3. Query Optimization Techniques

- Create indexes on foreign keys and high-filter columns
- Use simple joins and avoid unnecessary subqueries in large dashboards
- Aggregate in SQL where possible before returning data to BI tools
- Use consistent naming conventions and business-friendly aliases

## 4. Indexing Strategy

The schema includes indexes on:

- fact_startups.industry_key
- fact_startups.country_key
- fact_startups.outcome_key
- fact_startups.founder_key
- fact_startups.investor_key
- fact_startups.revenue_usd
- fact_startups.burn_ratio

These support common analytical filters such as industry, country, outcome, revenue, and burn behavior.

## 5. Power BI Connectivity

Power BI can connect to this warehouse using either:

- direct SQL connection to a relational database such as PostgreSQL or SQL Server
- import mode for smaller datasets
- DirectQuery mode for near-real-time analysis

Recommended approach:

- Use fact_startups as the primary fact table
- Import dimensions and facts into Power BI model
- Create measures for KPIs such as success rate, average revenue, and burn ratio

## 6. Example BI Measures

- Total Startups = COUNT(fact_startups[startup_id])
- Success Rate = DIVIDE(COUNTROWS(FILTER(dim_outcome, dim_outcome[is_successful] = TRUE)), COUNTROWS(fact_startups))
- Average Revenue = AVERAGE(fact_startups[revenue_usd])
- Average Burn Ratio = AVERAGE(fact_startups[burn_ratio])
