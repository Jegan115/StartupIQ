# -*- coding: utf-8 -*-
"""
StartupIQ Helper & Utilities Module
-----------------------------------
Provides general support utilities such as custom logging format setup,
directory creation checks, and database session generation.
"""

import os
import logging
from sqlalchemy import create_engine

def get_project_logger(name, level=logging.INFO):
    """
    Standardizes logger layout format across modules.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = get_project_logger("StartupIQ_Utils")

def ensure_directory_exists(directory_path):
    """
    Helper function to verify folder structure before file writes.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logger.info(f"Created missing directory pathway: {directory_path}")
    else:
        logger.debug(f"Directory already exists: {directory_path}")

def get_sqlite_engine(db_path):
    """
    Returns a SQLAlchemy database engine instance for SQLite.
    """
    parent_dir = os.path.dirname(db_path)
    if parent_dir:
        ensure_directory_exists(parent_dir)
        
    db_uri = f"sqlite:///{db_path}"
    logger.info(f"Generating SQLite database connection engine for: {db_uri}")
    engine = create_engine(db_uri, echo=False)
    return engine

if __name__ == "__main__":
    print("StartupIQ Utilities module initialized.")
