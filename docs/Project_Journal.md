# Project Journal: StartupIQ Analytics

This journal is a chronological record of architectural design decisions, ETL revisions, model findings, and BI design iterations throughout the development cycle.

---

## [2026-07-03] - Entry 1: Project Initialization
**Author:** Bhuvaneshwar

### Activities:
- Generated the directory structure for `StartupIQ` portfolio.
- Outlined directory structure including data folders, docs, sql, notebooks, src, reports, images, dashboard, models, and tests.
- Formulated the initial data dictionary, business hypotheses questions, database schema schema DDL, and sample query files.
- Built helper Python script templates for cleaning (`clean_data.py`), preprocessing (`preprocess.py`), analysis (`eda.py`), visualization (`visualizations.py`), and utils (`helper.py`).
- Configured Python environments via `.gitignore` and `requirements.txt`.
- Structured the placeholder notebooks for data cleaning, EDA, business insights, and feature engineering.

### Decisions:
1. **Database Selection**: Standardized SQLite database engine for storage local testing. It is fully cross-platform and requires zero local daemon installation, making it perfect for peer validation of the portfolio project.
2. **Directory Architecture**: Adopted a modular folder structure dividing business exploration (in `notebooks/`) from productionizable utilities (in `src/`). This follows standard production machine learning practices.
3. **Data Security**: Configured `.gitignore` to prevent any Raw, Cleaned, or Final CSV/Excel/SQLite files from being committed. Only `.gitkeep` placeholders will be tracked, ensuring the repository doesn't bloat.

### Next Steps:
- Ingest raw dataset (synthetic or sourced Startup records) into the `data/raw/` directory.
- Complete coding in `src/data_cleaning/clean_data.py` to ingest raw files, perform type conversions, deduplicate records, and handle missing values.

---

## [2026-07-04] - Entry 2: Data Understanding and Initial Profiling
**Author:** Senior Data Analyst

### Activities:
- Scanned raw data files in `data/raw/` and identified the primary dataset: `startup_success_dataset (1).csv` (100,000 records, 11 features).
- Implemented and validated the `01_Data_Understanding.ipynb` notebook to inspect missing counts, duplicate states, statistical descriptions, and value counts.
- Mapped all 11 features into logical business domains (Company Information, Founder Information, Funding Information, Financial Metrics, Startup Outcome, Market Information).

### Findings & Decisions:
1. **Zero Missingness & Duplication**: The dataset is 100% complete and contains no duplicate records, meaning standard imputation is not required.
2. **Units and Scaling Inconsistency**:
   - `revenue_million` contains values on the scale of absolute USD (mean ~782,819.1 USD), whereas the column suffix implies it's in millions.
   - `burn_rate_million` is in millions (mean ~16.78M USD).
   - **Decision**: In the upcoming cleaning phase (`02_Data_Cleaning.ipynb` and `clean_data.py`), we must divide `revenue_million` by 1,000,000 or multiply `burn_rate_million` by 1,000,000 to align their scales for unit-economics and runway modeling.
3. **Outliers**: Identified severe positive skewness in `market_size_billion` (max $1,072B) and `burn_rate_million` (max $357.49M). Robust transformations are recommended.

### Next Steps:
- Code the cleaning pipeline in `src/data_cleaning/clean_data.py` and invoke it via `notebooks/02_Data_Cleaning.ipynb` to output standardized tables.

---

## [2026-07-04] - Entry 3: Data Cleaning and Standardization
**Author:** Senior Data Analyst

### Activities:
- Refactored `src/data_cleaning/clean_data.py` into a production-quality modular ETL pipeline.
- Implemented and generated `02_Data_Cleaning.ipynb` to execute structural checks, unit scaling, validation audits, outlier analysis, and derived column calculations.
- Executed the cleaning ETL pipeline, producing `data/cleaned/startup_cleaned.csv`.

### Findings & Decisions:
1. **Financial Standardisation**: Adjusted scales of all financial properties to absolute USD. Named new fields `revenue_usd` and `burn_rate_usd` to prevent naming confusion.
2. **Business Constraints**: Verified there are 0 negative funding rounds, negative experience indicators, or team size issues.
3. **Outlier Auditing**: Found that ~4.9% of records contain outliers in market size, and ~4.8% contain outliers in burn rate.
   - **Decision**: Retained all outliers. Startup statistics follow highly skewed Pareto/power-law distributions, and filtering outliers would remove high-performing unicorns and distressed firms critical to modeling success.
4. **Derived Metrics Created**: Calculated `burn_ratio`, `revenue_per_employee`, `user_traction_per_employee`, and `capital_efficiency_ratio` for downstream models.

### Next Steps:
- Import cleaned datasets into SQL staging tables.
- Execute Exploratory Data Analysis (`03_Exploratory_Data_Analysis.ipynb`).


