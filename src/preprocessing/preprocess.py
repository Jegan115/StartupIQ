# -*- coding: utf-8 -*-
"""
StartupIQ Preprocessing Module
------------------------------
This module prepares cleaned startup datasets for input into Scikit-Learn
classification models. Includes categorical encoding, feature scaling,
and training split routines.
"""

import pandas as pd
import numpy as np
import logging
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def split_features_target(df, target_column='status'):
    """
    Splits dataset into features matrix (X) and target vector (y).
    """
    if target_column not in df.columns:
        logger.error(f"Target column '{target_column}' is missing from DataFrame.")
        raise KeyError(f"Missing target: {target_column}")
    
    X = df.drop(columns=[target_column])
    y = df[target_column]
    logger.info(f"Split completed: Features shape = {X.shape}, Target shape = {y.shape}")
    return X, y

def build_transform_pipeline(numeric_features, categorical_features):
    """
    Creates a preprocessor pipeline using Scikit-Learn ColumnTransformer.
    - Scales numeric variables (StandardScaler).
    - Encodes categorical variables (OneHotEncoder).
    
    Returns:
        ColumnTransformer: Instantiated transformation pipeline.
    """
    logger.info("Configuring ColumnTransformer preprocessing pipeline...")
    
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )
    
    logger.info("Transformation pipeline created successfully.")
    return preprocessor

def prepare_train_test_data(df, target_column='status', test_size=0.2, random_state=42):
    """
    Partitions dataset and returns training and testing sets.
    """
    X, y = split_features_target(df, target_column)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    logger.info(f"Data partitioned with test size = {test_size}. Training rows: {len(X_train)}, Test rows: {len(X_test)}")
    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    print("StartupIQ Preprocessing module initialized.")
