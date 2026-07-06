# -*- coding: utf-8 -*-
"""
StartupIQ Visualization Module
------------------------------
Generates standardized plots (distributions, trends, and correlation heatmaps)
using Matplotlib, Seaborn, or Plotly for reports or notebooks.
"""

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def plot_runway_distribution(df_finance, save_path=None):
    """
    Plots a histogram distribution of runway months.
    """
    logger.info("Generating runway distribution plot...")
    
    # Filter out infinite runways for plotting purposes
    plot_data = df_finance[df_finance['runway_months'] != np.inf].copy()
    
    fig = px.histogram(
        plot_data, 
        x="runway_months", 
        nbins=20,
        title="Distribution of Cash Runway (Months)",
        labels={'runway_months': 'Runway (Months)'},
        color_discrete_sequence=['#4B6B94']
    )
    
    fig.update_layout(
        template="plotly_white",
        xaxis_title="Runway (Months)",
        yaxis_title="Count of Startups",
        title_font_size=16
    )
    
    if save_path:
        fig.write_image(save_path)
        logger.info(f"Runway plot exported to: {save_path}")
        
    return fig

def plot_survival_by_industry(df_sector_summary, save_path=None):
    """
    Generates a horizontal bar chart comparing survival rates across sectors.
    """
    logger.info("Generating industry survival rate chart...")
    
    fig = px.bar(
        df_sector_summary,
        y="industry",
        x="survival_rate",
        orientation='h',
        title="Startup Survival Rates by Industry Sector (%)",
        labels={'survival_rate': 'Survival Rate (%)', 'industry': 'Industry'},
        color="survival_rate",
        color_continuous_scale=px.colors.sequential.Teal
    )
    
    fig.update_layout(
        template="plotly_white",
        yaxis={'categoryorder':'total ascending'},
        xaxis_title="Survival Rate (%)",
        yaxis_title="Industry Sector"
    )
    
    if save_path:
        fig.write_image(save_path)
        logger.info(f"Industry survival plot exported to: {save_path}")
        
    return fig

def plot_ltv_cac_efficiency(df_finance, save_path=None):
    """
    Generates a scatter plot comparing LTV vs CAC with a benchmark line.
    """
    logger.info("Generating LTV vs CAC unit economics plot...")
    
    fig = px.scatter(
        df_finance,
        x="cac_usd",
        y="ltv_usd",
        hover_data=['startup_id'],
        title="LTV vs CAC Unit Economics Mapping",
        labels={'cac_usd': 'Customer Acquisition Cost (USD)', 'ltv_usd': 'Lifetime Value (USD)'},
        color_discrete_sequence=['#319F92']
    )
    
    # Add target benchmark line (LTV = 3 * CAC)
    max_cac = df_finance['cac_usd'].max() if not df_finance['cac_usd'].empty else 1000
    fig.add_trace(go.Scatter(
        x=[0, max_cac],
        y=[0, 3 * max_cac],
        mode='lines',
        name='Benchmark (LTV = 3x CAC)',
        line=dict(color='firebrick', width=2, dash='dash')
    ))
    
    fig.update_layout(template="plotly_white")
    
    if save_path:
        fig.write_image(save_path)
        logger.info(f"LTV:CAC plot exported to: {save_path}")
        
    return fig

if __name__ == "__main__":
    print("StartupIQ Visualization module initialized.")
