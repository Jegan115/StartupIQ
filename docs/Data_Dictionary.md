# Data Dictionary: StartupIQ Data Models

This document outlines the data model attributes used in the **StartupIQ** data cleaning, SQL modeling, and machine learning pipelines.

---

## 1. Table: `startups`
Primary entities representing the evaluated startup companies.

| Column Name | Data Type | Key Type | Description / Constraints | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `startup_id` | `VARCHAR(50)` | Primary Key | Unique alphanumeric identifier for each startup. | `ST-8902` |
| `company_name` | `VARCHAR(100)` | - | Name of the startup entity. | `SaaSify.io` |
| `status` | `VARCHAR(20)` | - | Current state of startup. Allowed: `Operating`, `Closed`, `Acquired`, `IPO`. | `Operating` |
| `founded_year` | `INTEGER` | - | Year the startup was incorporated. | `2021` |
| `industry` | `VARCHAR(50)` | - | Industry sector categorization. | `FinTech` |
| `employee_count` | `INTEGER` | - | Latest recorded number of employees. | `42` |
| `city` | `VARCHAR(50)` | - | City where the startup is headquartered. | `San Francisco` |
| `country` | `VARCHAR(50)` | - | Country where the startup is headquartered. | `United States` |

---

## 2. Table: `funding_rounds`
Captures historical investment events. Multiple funding rounds map to a single startup.

| Column Name | Data Type | Key Type | Description / Constraints | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `round_id` | `VARCHAR(50)` | Primary Key | Unique identifier for the funding event. | `R-5532` |
| `startup_id` | `VARCHAR(50)` | Foreign Key | Links to `startups(startup_id)`. | `ST-8902` |
| `funding_stage` | `VARCHAR(20)` | - | Stage of funding. E.g., `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Grant`. | `Series A` |
| `funding_amount_usd` | `DECIMAL(15,2)` | - | Amount raised in US Dollars. | `1500000.00` |
| `funding_date` | `DATE` | - | Date the investment round was closed. | `2023-04-12` |
| `investor_count` | `INTEGER` | - | Number of participating investors in the round. | `3` |

---

## 3. Table: `financial_metrics`
Holds standard performance metrics used to evaluate runway, burn rate, and financial risk.

| Column Name | Data Type | Key Type | Description / Constraints | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `metric_id` | `VARCHAR(50)` | Primary Key | Unique identifier for financial metrics log. | `FM-1102` |
| `startup_id` | `VARCHAR(50)` | Foreign Key | Links to `startups(startup_id)`. | `ST-8902` |
| `monthly_revenue` | `DECIMAL(12,2)` | - | Average monthly recurring revenue (MRR) in USD. | `45000.00` |
| `monthly_expenses` | `DECIMAL(12,2)` | - | Average monthly expenses (operating cash out) in USD. | `65000.00` |
| `cash_balance` | `DECIMAL(15,2)` | - | Current cash reserve in bank in USD. | `300000.00` |
| `cac_usd` | `DECIMAL(10,2)` | - | Customer Acquisition Cost in USD. | `120.00` |
| `ltv_usd` | `DECIMAL(10,2)` | - | Lifetime Value per Customer in USD. | `450.00` |

---

## 4. Table: `founder_profiles`
Details biographical indicators of the founding team.

| Column Name | Data Type | Key Type | Description / Constraints | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `founder_id` | `VARCHAR(50)` | Primary Key | Unique identifier for the founder profile. | `FD-3321` |
| `startup_id` | `VARCHAR(50)` | Foreign Key | Links to `startups(startup_id)`. | `ST-8902` |
| `founder_experience_years` | `INTEGER` | - | Combined relevant startup/industry experience of founders. | `7` |
| `has_prior_exits` | `BOOLEAN` | - | True if any founder has successfully sold/exited a prior startup. | `1` |
| `education_level` | `VARCHAR(30)` | - | Highest educational degree among founding team. | `Masters` |
