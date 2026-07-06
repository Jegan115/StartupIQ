# StartupIQ: Project Configuration & Roadmap

## 1. Project Goals
The primary objective of **StartupIQ** is to construct an end-to-end data analytics and business intelligence platform to analyze the factors influencing startup success and failure. Key goals include:
- **Historical Analysis**: Identify trends, sector performance, and common operational and financial pitfalls leading to startup failure.
- **Relational Data Modeling**: Create a relational database schema (SQLite/PostgreSQL) to store data on funding rounds, financials, founder profiles, and company details.
- **Interactive Dashboards**: Deliver a high-impact Power BI dashboard suite that enables stakeholders (investors, founders, incubators) to drill down into startup performance metrics.
- **Founder Decision Simulator**: Train a predictive model using Scikit-Learn that allows founders to simulate hypothetical scenarios (e.g., funding amounts, runway, sector, founder experience) and estimate their probability of success or failure.

---

## 2. Milestones

| Phase | Milestone Name | Key Deliverables | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Data Ingestion & Understanding** | Exploration of raw datasets, schema design, and baseline documentation. | 📅 Pending |
| **Phase 2** | **Data Cleaning & Pipeline Setup** | Implement Python pipeline (`clean_data.py`) to handle missing data, format standardization, and outlier detection. | 📅 Pending |
| **Phase 3** | **SQL Relational Modeling** | Build SQLite database, import cleaned tables, and execute validation scripts (`queries.sql`). | 📅 Pending |
| **Phase 4** | **Exploratory Data Analysis (EDA)** | Notebook-based EDA, correlation analysis, and feature engineering. | 📅 Pending |
| **Phase 5** | **Power BI Dashboard Design** | Data model design, star-schema creation, DAX measure creation, and visual layouts. | 📅 Pending |
| **Phase 6** | **Founder Decision Simulator** | Model training (logistic regression/random forest), API wrapper, and interactive web dashboard. | 📅 Pending |

---

## 3. KPIs (Key Performance Indicators)

### Financial KPIs
- **Monthly Burn Rate**: The rate at which the startup spends its capital.
  $$\text{Burn Rate} = \frac{\text{Starting Cash} - \text{Ending Cash}}{\text{Months Elapsed}}$$
- **Cash Runway**: The number of months a startup can survive before running out of money.
  $$\text{Runway (Months)} = \frac{\text{Current Cash Balance}}{\text{Monthly Burn Rate}}$$
- **Funding-to-Revenue Ratio**: Measures capital efficiency.
  $$\text{Funding-to-Revenue Ratio} = \frac{\text{Total Funding Raised}}{\text{Annual Recurring Revenue (ARR)}}$$

### Operational & Growth KPIs
- **Customer Acquisition Cost (CAC)**: Total sales & marketing cost divided by new customers acquired.
  $$\text{CAC} = \frac{\text{Total Sales \& Marketing Expenses}}{\text{Number of New Customers Acquired}}$$
- **Customer Lifetime Value (LTV)**: Average revenue generated per customer during their tenure.
  $$\text{LTV} = \frac{\text{Average Monthly Revenue Per Customer} \times \text{Gross Margin}}{\text{Monthly Churn Rate}}$$
- **LTV:CAC Ratio**: Standard measure of business model viability. (Healthy Target: $\ge 3.0$)
- **Churn Rate**: The rate at which customers cancel their subscriptions.
  $$\text{Churn Rate} = \frac{\text{Customers Lost During Period}}{\text{Total Customers at Start of Period}} \times 100\%$$

### Risk & Success KPIs
- **Survival Rate**: The percentage of startups surviving beyond a given time horizon.
  $$\text{Survival Rate (Sector)} = \frac{\text{Active Startups in Sector}}{\text{Total Startups in Sector}} \times 100\%$$
- **Funding Round Conversion Rate**: Probability of transitioning from Seed to Series A, Series A to Series B, etc.

---

## 4. Dashboard Pages

1. **Executive Overview**: High-level KPIs (Total Startups, Survival Rate, Funding Raised, Top Industry Sectors, Geographic Distribution).
2. **Financial Health & Risk Monitor**: Deep dive into burn rates, runway distribution, cash efficiency, and early warning failure indicators.
3. **Founder Decision Simulator Interface**: Embedded machine learning input sliders allowing users to test business scenarios and instantly predict survival probability.
4. **Market & Competitor Intelligence**: Visual comparison of startup dense regions, funding trends over time, and exit paths (IPO vs. Acquisition).
