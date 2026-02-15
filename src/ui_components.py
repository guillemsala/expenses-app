"""
UI components module for Streamlit dashboard.

This module contains reusable UI components and layout functions.
"""

import streamlit as st
from typing import Dict, List
from src.calculations import PeriodFinancials, PersonFinancials


class UIComponents:
    """Reusable UI components for the dashboard."""
    
    @staticmethod
    def render_person_metrics(
        person_name: str,
        financials: PersonFinancials,
        show_bonus: bool = False
    ):
        """
        Render financial metrics for a single person.
        
        Args:
            person_name: Name to display
            financials: PersonFinancials object
            show_bonus: Whether to show bonus breakdown
        """
        st.caption(f"👤 {person_name}")
        st.write(f"Salary: CHF {financials.total_income:,.0f}")
        if show_bonus and financials.bonus > 0:
            st.caption(f"(Base: {financials.salary:,.0f} + Bonus: {financials.bonus:,.0f})")
        st.write(f"Shared: CHF {financials.shared_expenses:,.0f} ({financials.split_rate:.0f}%)")
        st.write(f"Personal: CHF {financials.personal_expenses:,.0f}")
        st.write(f"**Savings: CHF {financials.net_savings:,.0f}** ({financials.savings_rate:.0f}%)")
    
    @staticmethod
    def render_period_summary(period_financials: PeriodFinancials):
        """
        Render a compact summary for one period.
        
        Args:
            period_financials: PeriodFinancials object
        """
        st.markdown(f"**{period_financials.period}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            UIComponents.render_person_metrics("Guillem", period_financials.guillem)
        
        with col2:
            UIComponents.render_person_metrics("Vero", period_financials.vero)
        
        st.divider()
    
    @staticmethod
    def render_totals_column(
        person_name: str,
        totals: Dict[str, float]
    ):
        """
        Render total metrics for a person.
        
        Args:
            person_name: Name to display
            totals: Dictionary with net_salary, shared_expenses, personal_expenses, net_savings
        """
        st.markdown(f"**👤 {person_name}**")
        st.metric("Net Salary", f"CHF {totals['net_salary']:,.0f}")
        st.metric("Shared Exp.", f"CHF {totals['shared_expenses']:,.0f}")
        st.metric("Personal Exp.", f"CHF {totals['personal_expenses']:,.0f}")
        st.metric("Net Savings", f"CHF {totals['net_savings']:,.0f}")
        
        savings_rate = (totals['net_savings'] / totals['net_salary'] * 100) if totals['net_salary'] > 0 else 0
        st.caption(f"Rate: {savings_rate:.1f}%")
    
    @staticmethod
    def render_combined_totals(
        guillem_totals: Dict[str, float],
        vero_totals: Dict[str, float]
    ):
        """
        Render combined totals for both people.
        
        Args:
            guillem_totals: Guillem's totals dictionary
            vero_totals: Vero's totals dictionary
        """
        st.markdown("**📊 Combined**")
        
        combined_income = guillem_totals['net_salary'] + vero_totals['net_salary']
        combined_shared = guillem_totals['shared_expenses'] + vero_totals['shared_expenses']
        combined_personal = guillem_totals['personal_expenses'] + vero_totals['personal_expenses']
        combined_savings = guillem_totals['net_savings'] + vero_totals['net_savings']
        combined_savings_rate = (combined_savings / combined_income * 100) if combined_income > 0 else 0
        
        st.metric("Income", f"CHF {combined_income:,.0f}")
        st.metric("Shared Exp.", f"CHF {combined_shared:,.0f}")
        st.metric("Personal Exp.", f"CHF {combined_personal:,.0f}")
        st.metric("Savings", f"CHF {combined_savings:,.0f}")
        st.caption(f"Rate: {combined_savings_rate:.1f}%")
    
    @staticmethod
    def render_monthly_summaries_section(period_financials_list: List[PeriodFinancials]):
        """
        Render the monthly summaries section.
        
        Args:
            period_financials_list: List of PeriodFinancials objects
        """
        st.subheader("📅 Monthly Financial Summary")
        
        for pf in period_financials_list:
            UIComponents.render_period_summary(pf)
    
    @staticmethod
    def render_totals_section(
        guillem_totals: Dict[str, float],
        vero_totals: Dict[str, float]
    ):
        """
        Render the totals across periods section.
        
        Args:
            guillem_totals: Guillem's totals dictionary
            vero_totals: Vero's totals dictionary
        """
        st.subheader("📈 Totals Across Selected Periods")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            UIComponents.render_totals_column("Guillem", guillem_totals)
        
        with col2:
            UIComponents.render_totals_column("Vero", vero_totals)
        
        with col3:
            UIComponents.render_combined_totals(guillem_totals, vero_totals)
        
        st.divider()
    
    @staticmethod
    def render_sidebar_filters(available_periods: List[str]) -> List[str]:
        """
        Render sidebar filters and return selected periods.
        
        Args:
            available_periods: List of available period strings
            
        Returns:
            List of selected period strings
        """
        st.sidebar.header("Filters")
        
        selected_periods = st.sidebar.multiselect(
            "Select Month/Year Combinations",
            available_periods,
            default=available_periods
        )
        
        return selected_periods
    
    @staticmethod
    def render_expected_format_info():
        """Render information about expected CSV format."""
        st.info("👆 Please upload the financials CSV file to begin analysis")
        
        st.subheader("Expected File Format")
        st.markdown("""
        The CSV file should contain the following columns:
        - `input_date`: Date when data was entered
        - `for_month`: Month the expense applies to (January, February, etc.)
        - `for_year`: Year the expense applies to (2025, 2026, etc.)
        - `type`: Category of expense (or 'personal' for 100% personal expenses)
        - `name`: Description of expense
        - `amount`: Base amount
        - `units`: Multiplier (1, 2, 3, etc.)
        - `split_type`: How the expense is split (salary_weighted, custom_absolute, custom_relative)
        - `guillem_amount`: Guillem's amount (for custom_absolute)
        - `vero_amount`: Vero's amount (for custom_absolute)
        - `guillem_ratio`: Guillem's ratio (for custom_relative)
        - `vero_ratio`: Vero's ratio (for custom_relative)
        - `guillem_salary`: Guillem's base salary (used for shared expense splits)
        - `vero_salary`: Vero's base salary (used for shared expense splits)
        - `guillem_bonus`: Guillem's bonus (added to income, not used for splits)
        - `vero_bonus`: Vero's bonus (added to income, not used for splits)
        """)
