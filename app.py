"""
Main Streamlit application for Financial Dashboard.

This is the entry point that orchestrates all modules to create
the interactive dashboard.
"""

import streamlit as st
from pathlib import Path

from src.data_loader import DataLoader
from src.calculations import FinancialCalculator
from src.visualizations import ChartGenerator
from src.ui_components import UIComponents


# Set page configuration
st.set_page_config(
    page_title="Financial Analysis",
    layout="wide",
    page_icon="💰"
)


def main():
    """Main application entry point."""
    
    # Title
    st.title("💰 Financial Analysis Dashboard")
    
    # Initialize data loader
    loader = DataLoader(default_path=Path.home() / "Desktop" / "expenses.csv")
    
    # File uploader (only shown if default file not found)
    uploaded_file = st.file_uploader("Upload financials", type=['csv'])
    
    # Load data
    df = loader.load_data(uploaded_file)
    
    if df is not None:
        # Apply split calculations
        df = FinancialCalculator.apply_split_calculations(df)
        
        # Get available periods
        available_periods = loader.get_available_periods(df)
        
        # Sidebar filters
        selected_periods = UIComponents.render_sidebar_filters(available_periods)
        
        # Filter data
        filtered_df = df[df['period_display'].isin(selected_periods)]
        
        # Main analysis section
        st.header("📊 Financial Analysis")
        
        if len(filtered_df) > 0:
            # Calculate financials for each period
            period_financials_list = []
            
            for period in selected_periods:
                period_data = filtered_df[filtered_df['period_display'] == period]
                pf = FinancialCalculator.calculate_period_financials(period_data, period)
                period_financials_list.append(pf)
            
            # Aggregate totals
            guillem_totals, vero_totals = FinancialCalculator.aggregate_totals(
                period_financials_list
            )
            
            # Create two-column layout
            main_col1, main_col2 = st.columns([1, 1])
            
            with main_col1:
                # Monthly summaries
                UIComponents.render_monthly_summaries_section(period_financials_list)
            
            with main_col2:
                # Totals section
                UIComponents.render_totals_section(guillem_totals, vero_totals)
                
                # Trends section
                st.subheader("📉 Trends Over Time")
                
                # Prepare chart data
                chart_df = FinancialCalculator.prepare_chart_data(period_financials_list)
                
                # Metric selector
                metric_options = ChartGenerator.get_metric_options()
                selected_metric = st.selectbox(
                    "Select metric to visualize:",
                    metric_options
                )
                
                # Create and display chart
                fig = ChartGenerator.create_trend_line_chart(
                    chart_df,
                    selected_metric,
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.warning("No data available for the selected periods.")
    
    else:
        UIComponents.render_expected_format_info()


if __name__ == "__main__":
    main()
