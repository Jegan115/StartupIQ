# Strategic Business Questions: StartupIQ Analytics

This document lists the primary business hypotheses and questions driving the **StartupIQ** data model, SQL queries, visualizations, and simulator configurations. These questions are framed from the perspective of various stakeholders: founders, venture capitalists, and incubator managers.

---

## 1. Investor Perspective (Risk & Return)

### Q1.1: What are the primary indicators of a startup's failure within its first 36 months?
*   **Metric**: Survival rate over time, burn rate, cash runway.
*   **Hypothesis**: Startups with less than 6 months of cash runway and a monthly burn rate exceeding 25% of their total funding at any time have a 70% higher probability of closure.

### Q1.2: How does the total capital raised in early stages (Seed / Pre-Seed) affect the probability of raising a Series A?
*   **Metric**: Funding stage transition/conversion rate, average round sizes.
*   **Hypothesis**: Startups that raise a moderate Seed round ($1M - $2.5M) transition to Series A at a higher rate than underfunded (<$500K) or overfunded (>$5M) startups due to capital discipline.

---

## 2. Founder Perspective (Operational Decisions)

### Q2.1: What is the optimal LTV-to-CAC ratio that correlates with steady revenue expansion without burning through capital?
*   **Metric**: LTV:CAC Ratio, annual growth rate, runway.
*   **Hypothesis**: Startups maintaining an LTV:CAC ratio above 3.5 demonstrate sustainable, capital-efficient growth and survive 2x longer than those below 2.0.

### Q2.2: How does founder experience and the presence of prior exits affect the operational survival of the company?
*   **Metric**: Company status (Operating/Closed/Acquired/IPO) grouped by founder experience bins and has_prior_exits flag.
*   **Hypothesis**: Founding teams with at least one prior exit have a 30% higher survival rate and raise larger follow-on rounds.

---

## 3. Incubator/Market Perspective (Regional & Sector Growth)

### Q3.1: Which industry sectors exhibit the highest survival rate and lowest average CAC?
*   **Metric**: Survival rate by industry, average CAC by sector.
*   **Hypothesis**: Enterprise SaaS and FinTech startups show higher long-term survival rates, whereas Consumer Hardware and B2C E-commerce face higher failure rates due to intensive CAC and logistics challenges.

### Q3.2: Does geographic location significantly impact a startup's funding velocity?
*   **Metric**: Funding velocity (days between rounds), average total funding by city/country.
*   **Hypothesis**: Startups located in tier-1 hubs (e.g., San Francisco, London, New York) experience 40% shorter duration between funding stages compared to remote or tier-2 hubs.
