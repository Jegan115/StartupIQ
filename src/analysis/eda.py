# -*- coding: utf-8 -*-
"""
StartupIQ Exploratory Analysis Module
------------------------------------
This module calculates financial and growth KPIs (e.g., Burn Rate, Runway, LTV:CAC)
and returns statistical metrics grouped by category.
"""

import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_burn_and_runway(df_finance):
    """
    Computes cash burn rates and runway in months.
    
    Parameters:
        df_finance (pd.DataFrame): Financial data with revenue, expenses, and cash.
    Returns:
        pd.DataFrame: DataFrame containing runway metrics.
    """
    logger.info("Calculating cash runway and burn rates...")
    df = df_finance.copy()
    
    # Burn Rate = Expenses - Revenue
    df['burn_rate'] = df['monthly_expenses'] - df['monthly_revenue']
    
    # Runway = Cash Balance / Burn Rate (Only if Burn Rate > 0)
    df['runway_months'] = np.where(
        df['burn_rate'] > 0,
        df['cash_balance'] / df['burn_rate'],
        np.inf # Infinite runway (Cash flow positive)
    )
    
    # Set labels for risk tiers
    conditions = [
        (df['runway_months'] <= 0) | (df['runway_months'] == np.inf),
        (df['runway_months'] > 0) & (df['runway_months'] < 6),
        (df['runway_months'] >= 6) & (df['runway_months'] <= 12),
        (df['runway_months'] > 12) & (df['runway_months'] != np.inf)
    ]
    choices = ['Low Risk (Cash Positive)', 'High Risk (< 6 Months)', 'Medium Risk (6-12 Months)', 'Low Risk (> 12 Months)']
    df['runway_risk_tier'] = np.select(conditions, choices, default='Unknown')
    
    logger.info("Runway calculations completed.")
    return df

def calculate_ltv_cac_ratio(df_finance):
    """
    Computes customer acquisition health ratios.
    """
    df = df_finance.copy()
    if 'cac_usd' in df.columns and 'ltv_usd' in df.columns:
        # Avoid division by zero
        df['ltv_cac_ratio'] = np.where(
            df['cac_usd'] > 0,
            df['ltv_usd'] / df['cac_usd'],
            0.0
        )
        logger.info("LTV-to-CAC ratio calculation completed.")
    else:
        logger.warning("Missing LTV or CAC columns. Calculation skipped.")
        df['ltv_cac_ratio'] = np.nan
    return df

def analyze_sector_survival(df_startups):
    """
    Groups startups by industry to evaluate average survival rate metrics.
    """
    logger.info("Computing sector-level survival distributions...")
    
    # Check status
    df_startups['is_active'] = df_startups['status'].isin(['Operating', 'Acquired', 'IPO']).astype(int)
    
    sector_summary = df_startups.groupby('industry').agg(
        total_startups=('startup_id', 'count'),
        survived_startups=('is_active', 'sum'),
        avg_employee_count=('employee_count', 'mean')
    ).reset_index()
    
    sector_summary['survival_rate'] = (sector_summary['survived_startups'] / sector_summary['total_startups']) * 100
    
    logger.info(f"Sector analysis finished for {len(sector_summary)} industries.")
    return sector_summary.sort_values(by='survival_rate', ascending=False)

if __name__ == "__main__":
    print("StartupIQ EDA analysis module initialized.")
