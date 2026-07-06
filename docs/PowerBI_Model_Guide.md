# Power BI Model Mapping Guide

## Overview

This guide explains how to connect the StartupIQ warehouse to Power BI.

## Recommended Connection

- Use the SQLite database generated at data/warehouse/startupiq.sqlite
- Import or DirectQuery the tables from the warehouse into Power BI

## Suggested Power BI Model

### Fact Table
- fact_startups

### Dimension Tables
- dim_industry
- dim_country
- dim_outcome
- dim_founder
- dim_investor

## Relationships

- fact_startups[industry_key] -> dim_industry[industry_key]
- fact_startups[country_key] -> dim_country[country_key]
- fact_startups[outcome_key] -> dim_outcome[outcome_key]
- fact_startups[founder_key] -> dim_founder[founder_key]
- fact_startups[investor_key] -> dim_investor[investor_key]

## Recommended Measures

- Total Startups = COUNT(fact_startups[startup_id])
- Success Rate = DIVIDE(CALCULATE(COUNT(fact_startups[startup_id]), dim_outcome[is_successful] = TRUE), COUNT(fact_startups[startup_id]))
- Average Revenue = AVERAGE(fact_startups[revenue_usd])
- Average Burn Ratio = AVERAGE(fact_startups[burn_ratio])
- Average Funding Rounds = AVERAGE(fact_startups[funding_rounds])

## BI Design Tips

- Use slicers for industry, outcome, investor type, founder background, and country
- Build a KPI card visual for executive reporting
- Add trend or comparison visuals for funding, revenue, and burn ratio
- Use matrix visuals for industry and outcome comparisons
