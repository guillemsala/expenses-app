"""
Financial calculations module.

This module contains all business logic for computing expenses, splits,
savings, and aggregations.
"""

import pandas as pd
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class PersonFinancials:
    """Financial data for a single person for a given period."""
    salary: float
    bonus: float
    total_income: float
    shared_expenses: float
    personal_expenses: float
    total_expenses: float
    net_savings: float
    savings_rate: float
    split_rate: float  # Average split rate for shared expenses


@dataclass
class PeriodFinancials:
    """Complete financial data for a period."""
    period: str
    guillem: PersonFinancials
    vero: PersonFinancials
    total_shared_expenses: float
    combined_income: float
    combined_savings: float
    combined_savings_rate: float


class FinancialCalculator:
    """Handles all financial calculations and aggregations."""
    
    @staticmethod
    def calculate_split_amounts(row: pd.Series) -> pd.Series:
        """
        Calculate how an expense is split between people.
        
        Args:
            row: DataFrame row with expense data
            
        Returns:
            Series with guillem_final, vero_final, total_final
        """
        total_amount = row['amount'] * row['units']
        
        if row['split_type'] == 'salary_weighted':
            total_salary = row['guillem_salary'] + row['vero_salary']
            if total_salary > 0:
                guillem_share = (row['guillem_salary'] / total_salary) * total_amount
                vero_share = (row['vero_salary'] / total_salary) * total_amount
            else:
                guillem_share = vero_share = 0
                
        elif row['split_type'] == 'custom_absolute':
            guillem_share = row.get('guillem_amount', 0) * row['units']
            vero_share = row.get('vero_amount', 0) * row['units']
            
        elif row['split_type'] == 'custom_relative':
            guillem_share = row.get('guillem_ratio', 0) * total_amount
            vero_share = row.get('vero_ratio', 0) * total_amount
            
        else:
            guillem_share = vero_share = 0
        
        return pd.Series({
            'guillem_final': guillem_share,
            'vero_final': vero_share,
            'total_final': total_amount
        })
    
    @staticmethod
    def apply_split_calculations(df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply split calculations to entire DataFrame.
        
        Args:
            df: DataFrame with expense data
            
        Returns:
            DataFrame with added split columns
        """
        amounts = df.apply(FinancialCalculator.calculate_split_amounts, axis=1)
        return pd.concat([df, amounts], axis=1)
    
    @staticmethod
    def calculate_period_financials(
        period_data: pd.DataFrame,
        period: str
    ) -> PeriodFinancials:
        """
        Calculate complete financial metrics for a period.
        
        Args:
            period_data: DataFrame filtered to a single period
            period: Period label (e.g., "January 2025")
            
        Returns:
            PeriodFinancials object with all metrics
        """
        # Get salaries and bonuses (assuming consistent within period)
        guillem_salary = period_data['guillem_salary'].iloc[0] if len(period_data) > 0 else 0
        vero_salary = period_data['vero_salary'].iloc[0] if len(period_data) > 0 else 0
        guillem_bonus = period_data['guillem_bonus'].iloc[0] if 'guillem_bonus' in period_data.columns and len(period_data) > 0 else 0
        vero_bonus = period_data['vero_bonus'].iloc[0] if 'vero_bonus' in period_data.columns and len(period_data) > 0 else 0
        
        # Total income
        guillem_total_income = guillem_salary + guillem_bonus
        vero_total_income = vero_salary + vero_bonus
        
        # Separate shared vs personal expenses
        shared_expenses = period_data[period_data['type'] != 'personal']
        personal_expenses = period_data[period_data['type'] == 'personal']
        
        # Shared expenses
        guillem_shared = shared_expenses['guillem_final'].sum()
        vero_shared = shared_expenses['vero_final'].sum()
        total_shared = shared_expenses['total_final'].sum()
        
        # Calculate split rates
        guillem_split_rate = (guillem_shared / total_shared * 100) if total_shared > 0 else 0
        vero_split_rate = (vero_shared / total_shared * 100) if total_shared > 0 else 0
        
        # Personal expenses
        personal_guillem = personal_expenses['guillem_final'].sum()
        personal_vero = personal_expenses['vero_final'].sum()
        
        # Total expenses and savings
        total_expenses_guillem = guillem_shared + personal_guillem
        total_expenses_vero = vero_shared + personal_vero
        
        net_savings_guillem = guillem_total_income - total_expenses_guillem
        net_savings_vero = vero_total_income - total_expenses_vero
        
        savings_rate_guillem = (net_savings_guillem / guillem_total_income * 100) if guillem_total_income > 0 else 0
        savings_rate_vero = (net_savings_vero / vero_total_income * 100) if vero_total_income > 0 else 0
        
        # Combined metrics
        combined_income = guillem_total_income + vero_total_income
        combined_savings = net_savings_guillem + net_savings_vero
        combined_savings_rate = (combined_savings / combined_income * 100) if combined_income > 0 else 0
        
        return PeriodFinancials(
            period=period,
            guillem=PersonFinancials(
                salary=guillem_salary,
                bonus=guillem_bonus,
                total_income=guillem_total_income,
                shared_expenses=guillem_shared,
                personal_expenses=personal_guillem,
                total_expenses=total_expenses_guillem,
                net_savings=net_savings_guillem,
                savings_rate=savings_rate_guillem,
                split_rate=guillem_split_rate
            ),
            vero=PersonFinancials(
                salary=vero_salary,
                bonus=vero_bonus,
                total_income=vero_total_income,
                shared_expenses=vero_shared,
                personal_expenses=personal_vero,
                total_expenses=total_expenses_vero,
                net_savings=net_savings_vero,
                savings_rate=savings_rate_vero,
                split_rate=vero_split_rate
            ),
            total_shared_expenses=total_shared,
            combined_income=combined_income,
            combined_savings=combined_savings,
            combined_savings_rate=combined_savings_rate
        )
    
    @staticmethod
    def aggregate_totals(period_financials_list: list) -> Tuple[Dict, Dict]:
        """
        Aggregate totals across multiple periods.
        
        Args:
            period_financials_list: List of PeriodFinancials objects
            
        Returns:
            Tuple of (guillem_totals, vero_totals) dictionaries
        """
        guillem_totals = {
            'net_salary': 0,
            'shared_expenses': 0,
            'personal_expenses': 0,
            'net_savings': 0
        }
        
        vero_totals = {
            'net_salary': 0,
            'shared_expenses': 0,
            'personal_expenses': 0,
            'net_savings': 0
        }
        
        for pf in period_financials_list:
            guillem_totals['net_salary'] += pf.guillem.total_income
            guillem_totals['shared_expenses'] += pf.guillem.shared_expenses
            guillem_totals['personal_expenses'] += pf.guillem.personal_expenses
            guillem_totals['net_savings'] += pf.guillem.net_savings
            
            vero_totals['net_salary'] += pf.vero.total_income
            vero_totals['shared_expenses'] += pf.vero.shared_expenses
            vero_totals['personal_expenses'] += pf.vero.personal_expenses
            vero_totals['net_savings'] += pf.vero.net_savings
        
        return guillem_totals, vero_totals
    
    @staticmethod
    def prepare_chart_data(period_financials_list: list) -> pd.DataFrame:
        """
        Prepare data for time series charts.
        
        Args:
            period_financials_list: List of PeriodFinancials objects
            
        Returns:
            DataFrame sorted by period with all metrics
        """
        chart_data = []
        
        for pf in period_financials_list:
            chart_data.append({
                'period': pf.period,
                'Guillem Net Salary': pf.guillem.total_income,
                'Guillem Shared Expenses': pf.guillem.shared_expenses,
                'Guillem Personal Expenses': pf.guillem.personal_expenses,
                'Guillem Net Savings': pf.guillem.net_savings,
                'Vero Net Salary': pf.vero.total_income,
                'Vero Shared Expenses': pf.vero.shared_expenses,
                'Vero Personal Expenses': pf.vero.personal_expenses,
                'Vero Net Savings': pf.vero.net_savings
            })
        
        df = pd.DataFrame(chart_data)
        
        # Sort by period
        def parse_period(period_str: str) -> Tuple[int, int]:
            parts = period_str.split()
            month_name = parts[0]
            year = int(parts[1])
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
            month_num = months.index(month_name) + 1
            return (year, month_num)
        
        df['sort_key'] = df['period'].apply(parse_period)
        df = df.sort_values('sort_key')
        
        return df
