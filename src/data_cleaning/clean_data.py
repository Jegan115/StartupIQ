# -*- coding: utf-8 -*-
"""
StartupIQ Data Cleaning Pipeline
--------------------------------
This module implements production-quality data cleaning and preparation
functions for the raw StartupIQ dataset. It standardizes financial units,
validates values, checks data constraints, generates key derived metrics,
and saves the output to a staging folder.
"""

import os
import pathlib
import logging
import pandas as pd
import numpy as np

# Setup module-level logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("StartupIQ_ETL")

def get_raw_dataset_path(raw_dir_path):
    """
    Scans the raw data directory and locates the first available CSV file.
    
    Parameters:
        raw_dir_path (str or Path): Path to the data/raw directory.
    Returns:
        Path: Path to the target raw CSV.
    """
    raw_path = pathlib.Path(raw_dir_path)
    csv_files = list(raw_path.glob("*.csv"))
    if not csv_files:
        logger.error(f"No raw CSV datasets found in directory: {raw_path.resolve()}")
        raise FileNotFoundError(f"No raw CSV datasets found in directory: {raw_path}")
    logger.info(f"Target raw dataset identified: {csv_files[0].name}")
    return csv_files[0]

def validate_types_and_structure(df):
    """
    Validates column datatypes and non-null properties.
    
    Parameters:
        df (pd.DataFrame): Dataframe to validate.
    Returns:
        dict: Summary of types and checks.
    """
    logger.info("Running datatype and structural validations...")
    expected_numeric_cols = [
        'funding_rounds', 'founder_experience_years', 'team_size', 
        'market_size_billion', 'product_traction_users', 
        'burn_rate_million', 'revenue_million'
    ]
    expected_categorical_cols = ['investor_type', 'sector', 'founder_background', 'outcome']
    
    for col in expected_numeric_cols:
        if col in df.columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                logger.warning(f"Column '{col}' is expected to be numeric but is of type {df[col].dtype}")
                
    for col in expected_categorical_cols:
        if col in df.columns:
            if not pd.api.types.is_object_dtype(df[col]) and not pd.api.types.is_categorical_dtype(df[col]):
                logger.warning(f"Column '{col}' is expected to be categorical/object but is of type {df[col].dtype}")
                
    logger.info("Datatype validations completed successfully.")
    return True

def standardize_financial_metrics(df):
    """
    Standardizes scaling metrics for financial representation.
    Based on preliminary observations:
      - revenue_million values are stored in single USD.
      - burn_rate_million values are stored in millions of USD.
    
    This function converts both to standardized absolute USD and renames columns:
      - revenue_usd = revenue_million
      - burn_rate_usd = burn_rate_million * 1,000,000
    
    Parameters:
        df (pd.DataFrame): Input dataframe.
    Returns:
        pd.DataFrame: Dataframe with standardized financial columns.
    """
    logger.info("Standardizing financial scales to absolute USD...")
    df_clean = df.copy()
    
    # Check column existence
    if 'revenue_million' not in df_clean.columns or 'burn_rate_million' not in df_clean.columns:
        logger.error("Financial columns 'revenue_million' or 'burn_rate_million' are missing.")
        raise KeyError("Missing core financial columns for standardization.")
        
    # Transformations
    df_clean['revenue_usd'] = df_clean['revenue_million'].astype(float)
    df_clean['burn_rate_usd'] = df_clean['burn_rate_million'].astype(float) * 1_000_000.0
    
    # Keep track of old column drop to maintain tidiness
    df_clean = df_clean.drop(columns=['revenue_million', 'burn_rate_million'])
    
    logger.info("Financial unit standardization complete. Columns added: 'revenue_usd', 'burn_rate_usd'.")
    return df_clean

def check_impossible_values(df):
    """
    Verifies that numeric columns do not contain logical or business constraints violations.
    Constraints:
      - funding_rounds >= 0
      - founder_experience_years >= 0
      - team_size > 0
      - market_size_billion > 0
      - product_traction_users >= 0
      - burn_rate_usd >= 0
      - revenue_usd >= 0
      
    Parameters:
        df (pd.DataFrame): Dataframe with standardized columns.
    Returns:
        pd.DataFrame: Dataframe with validated/filtered records.
    """
    logger.info("Auditing dataset for impossible business values...")
    df_valid = df.copy()
    initial_rows = len(df_valid)
    
    # Define check conditions (True if row is anomalous)
    anomalous_conditions = {
        'negative_funding': df_valid['funding_rounds'] < 0,
        'negative_founder_exp': df_valid['founder_experience_years'] < 0,
        'invalid_team_size': df_valid['team_size'] <= 0,
        'invalid_market_size': df_valid['market_size_billion'] <= 0,
        'negative_traction': df_valid['product_traction_users'] < 0,
        'negative_burn_rate': df_valid['burn_rate_usd'] < 0,
        'negative_revenue': df_valid['revenue_usd'] < 0
    }
    
    total_anomalies = 0
    for key, condition in anomalous_conditions.items():
        anomalies_count = condition.sum()
        if anomalies_count > 0:
            logger.warning(f"Anomalous constraint '{key}' triggered for {anomalies_count} rows.")
            total_anomalies += anomalies_count
            # Filter out anomalies
            df_valid = df_valid[~condition]
            
    final_rows = len(df_valid)
    if total_anomalies > 0:
        logger.info(f"Filtered out {initial_rows - final_rows} anomalous records from the dataset.")
    else:
        logger.info("Zero impossible business values or constraint violations detected.")
        
    return df_valid

def generate_derived_metrics(df):
    """
    Generates mathematically sound and logically consistent derived features:
      - burn_ratio = burn_rate_usd / revenue_usd (Handles division by zero)
      - revenue_per_employee = revenue_usd / team_size
      - user_traction_per_employee = product_traction_users / team_size
      - capital_efficiency_ratio = revenue_usd / burn_rate_usd (Handles division by zero)
      
    Parameters:
        df (pd.DataFrame): Dataframe with standardized values.
    Returns:
        pd.DataFrame: Dataframe containing the new derived metrics columns.
    """
    logger.info("Generating derived business metrics...")
    df_derived = df.copy()
    
    # 1. Burn Ratio: Burn rate relative to revenue. Higher ratio indicates heavier reliance on capital.
    # To handle division by zero (or revenue = 0), we use np.where.
    df_derived['burn_ratio'] = np.where(
        df_derived['revenue_usd'] > 0.0,
        df_derived['burn_rate_usd'] / df_derived['revenue_usd'],
        df_derived['burn_rate_usd']  # fallback representation or standard burn if revenue is 0
    )
    
    # 2. Revenue per Employee (Revenue Efficiency)
    df_derived['revenue_per_employee'] = df_derived['revenue_usd'] / df_derived['team_size']
    
    # 3. User Traction per Employee
    df_derived['user_traction_per_employee'] = df_derived['product_traction_users'] / df_derived['team_size']
    
    # 4. Capital Efficiency Ratio: Revenue generated per dollar burned.
    df_derived['capital_efficiency_ratio'] = np.where(
        df_derived['burn_rate_usd'] > 0.0,
        df_derived['revenue_usd'] / df_derived['burn_rate_usd'],
        np.nan
    )
    
    logger.info("Derived metric columns generated successfully.")
    return df_derived

def run_cleaning_pipeline(raw_dir, output_file_path):
    """
    Executes the entire cleaning pipeline.
    
    Parameters:
        raw_dir (str or Path): Path to raw CSV folder.
        output_file_path (str or Path): Destination path for the clean file.
    Returns:
        pd.DataFrame: Cleaned and prepared dataframe.
    """
    logger.info("Starting StartupIQ cleaning ETL pipeline run...")
    
    # 1. Locate and load raw file
    raw_file = get_raw_dataset_path(raw_dir)
    df = pd.read_csv(raw_file)
    logger.info(f"Loaded {len(df):,} rows from raw data source.")
    
    # 2. Validate types
    validate_types_and_structure(df)
    
    # 3. Handle duplicates and nulls
    nulls_count = df.isnull().sum().sum()
    dups_count = df.duplicated().sum()
    logger.info(f"Pre-cleaning audit: Nulls count = {nulls_count}, Duplicates count = {dups_count}")
    
    # Filter duplicates and nulls if any exist
    if dups_count > 0:
        df = df.drop_duplicates()
        logger.info(f"Dropped {dups_count} duplicate rows.")
    if nulls_count > 0:
        df = df.dropna()
        logger.info("Dropped null values.")
        
    # 4. Standardize financial units
    df = standardize_financial_metrics(df)
    
    # 5. Check impossible values
    df = check_impossible_values(df)
    
    # 6. Generate derived columns
    df = generate_derived_metrics(df)
    
    # 7. Save file
    output_path = pathlib.Path(output_file_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"ETL pipeline run complete. Saved output file to: {output_path.resolve()}")
    
    return df

if __name__ == "__main__":
    # Test path execution
    test_raw_dir = r"c:\Users\Bhuvaneshwar\OneDrive\Desktop\STARTUPIQ\data\raw"
    test_out = r"c:\Users\Bhuvaneshwar\OneDrive\Desktop\STARTUPIQ\data\cleaned\startup_cleaned.csv"
    if os.path.exists(test_raw_dir):
        run_cleaning_pipeline(test_raw_dir, test_out)
