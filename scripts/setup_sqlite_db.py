import os
import sqlite3
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / 'data' / 'cleaned' / 'startup_cleaned.csv'
DB_DIR = ROOT / 'data' / 'warehouse'
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / 'startupiq.sqlite'
SCHEMA_PATH = ROOT / 'sql' / 'schema.sql'


def read_source_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    for col in [
        'funding_rounds',
        'founder_experience_years',
        'team_size',
        'market_size_billion',
        'product_traction_users',
        'revenue_usd',
        'burn_rate_usd',
        'burn_ratio',
        'revenue_per_employee',
        'user_traction_per_employee',
        'capital_efficiency_ratio',
    ]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['sector'] = df['sector'].astype(str).str.strip()
    df['investor_type'] = df['investor_type'].astype(str).str.strip()
    df['founder_background'] = df['founder_background'].astype(str).str.strip()
    df['outcome'] = df['outcome'].astype(str).str.strip()
    return df


def create_database(conn: sqlite3.Connection) -> None:
    schema_sql = SCHEMA_PATH.read_text(encoding='utf-8')
    conn.executescript(schema_sql)


def load_dimensions(conn: sqlite3.Connection, df: pd.DataFrame) -> dict:
    cursor = conn.cursor()

    industry_rows = []
    for idx, value in enumerate(sorted(df['sector'].dropna().astype(str).unique()), start=1):
        name = value
        group = 'Emerging' if name in {'AI', 'Crypto', 'Fintech'} else 'Mainstream'
        industry_rows.append((idx, name, group, int(name in {'AI', 'Fintech', 'Crypto'})))
    cursor.executemany(
        'INSERT INTO dim_industry (industry_key, industry_name, industry_group, is_high_growth) VALUES (?, ?, ?, ?)',
        industry_rows,
    )

    cursor.execute(
        'INSERT INTO dim_country (country_key, country_name, country_code, is_known) VALUES (?, ?, ?, ?)',
        (1, 'Unknown', 'UNK', 0),
    )

    outcome_rows = [
        (1, 'Failure', 'Non-Successful', 0),
        (2, 'Acquisition', 'Successful Exit', 1),
        (3, 'IPO', 'Successful Exit', 1),
    ]
    cursor.executemany(
        'INSERT INTO dim_outcome (outcome_key, outcome_name, outcome_group, is_successful) VALUES (?, ?, ?, ?)',
        outcome_rows,
    )

    founder_rows = []
    founder_lookup = {}
    for idx, (background, experience_years) in enumerate(
        df[['founder_background', 'founder_experience_years']].drop_duplicates().itertuples(index=False, name=None),
        start=1,
    ):
        background, experience_years = background, int(experience_years)
        if experience_years < 5:
            band = 'Novice'
        elif experience_years < 15:
            band = 'Experienced'
        else:
            band = 'Veteran'
        label = f'{background} | {band}'
        founder_rows.append((idx, background, experience_years, band, label))
        founder_lookup[(background, experience_years)] = idx
    cursor.executemany(
        'INSERT INTO dim_founder (founder_key, founder_background, founder_experience_years, experience_band, founder_profile_label) VALUES (?, ?, ?, ?, ?)',
        founder_rows,
    )

    investor_rows = [
        (1, 'none', 'No Investor', 0),
        (2, 'angel', 'Angel', 1),
        (3, 'tier1_vc', 'Tier 1 VC', 1),
        (4, 'tier2_vc', 'Tier 2 VC', 1),
    ]
    cursor.executemany(
        'INSERT INTO dim_investor (investor_key, investor_type, investor_tier, is_active_investor) VALUES (?, ?, ?, ?)',
        investor_rows,
    )

    industry_lookup = {name: key for key, name, _, _ in industry_rows}
    investor_lookup = {inv_type: key for key, inv_type, _, _ in investor_rows}
    outcome_lookup = {name: key for key, name, _, _ in outcome_rows}

    return {
        'industry_lookup': industry_lookup,
        'investor_lookup': investor_lookup,
        'outcome_lookup': outcome_lookup,
        'founder_lookup': founder_lookup,
    }


def load_fact_table(conn: sqlite3.Connection, df: pd.DataFrame, lookups: dict) -> None:
    cursor = conn.cursor()
    rows = []
    for idx, row in df.reset_index().iterrows():
        industry_key = lookups['industry_lookup'][row['sector']]
        outcome_key = lookups['outcome_lookup'][row['outcome']]
        founder_key = lookups['founder_lookup'][(row['founder_background'], int(row['founder_experience_years']))]
        investor_key = lookups['investor_lookup'].get(row['investor_type'])
        rows.append(
            (
                f'ST-{idx + 1}',
                industry_key,
                1,
                outcome_key,
                founder_key,
                investor_key,
                1,
                int(row['funding_rounds']),
                int(row['team_size']),
                float(row['market_size_billion']),
                int(row['product_traction_users']),
                float(row['revenue_usd']),
                float(row['burn_rate_usd']),
                float(row['burn_ratio']),
                float(row['revenue_per_employee']),
                float(row['user_traction_per_employee']),
                float(row['capital_efficiency_ratio']),
                idx + 1,
            )
        )
    cursor.executemany(
        '''
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
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        rows,
    )


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f'CSV not found: {CSV_PATH}')

    df = read_source_data()
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    try:
        create_database(conn)
        lookups = load_dimensions(conn, df)
        load_fact_table(conn, df, lookups)
        conn.commit()
        count = conn.execute('SELECT COUNT(*) FROM fact_startups').fetchone()[0]
        print(f'Created database: {DB_PATH}')
        print(f'Loaded {count} startup rows into fact_startups')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
