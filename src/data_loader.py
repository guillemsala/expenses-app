"""
Data loading and preprocessing module for financial dashboard.

This module handles reading CSV data, validating schema, and preparing
data structures for analysis.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Tuple
import streamlit as st


class DataLoader:
    """Handles loading and preprocessing of financial data."""
    
    REQUIRED_COLUMNS = [
        'for_month', 'for_year', 'type', 'name', 'amount', 'units',
        'split_type', 'guillem_salary', 'vero_salary'
    ]
    
    MONTH_ORDER = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    VALID_SPLIT_TYPES = ['salary_weighted', 'custom_absolute', 'custom_relative']
    
    def __init__(self, default_path: Optional[Path] = None):
        """
        Initialize DataLoader with optional default file path.
        
        Args:
            default_path: Path to default CSV file (e.g., Desktop/expenses.csv)
        """
        self.default_path = default_path or (Path.home() / "Desktop" / "expenses.csv")
        
    def load_data(self, uploaded_file=None) -> Optional[pd.DataFrame]:
        """
        Load data from default path or uploaded file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            DataFrame if successful, None otherwise
        """
        df = None
        
        # Try default path first
        if self.default_path.exists():
            try:
                df = pd.read_csv(self.default_path)
                st.success(f"✅ Loaded data from: {self.default_path}")
            except Exception as e:
                st.error(f"Error reading from {self.default_path}: {e}")
                df = None
        
        # Fall back to uploaded file
        if df is None:
            st.info(f"📁 Default file not found at: {self.default_path}")
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                except Exception as e:
                    st.error(f"Error reading uploaded file: {e}")
                    return None
        
        # Validate and preprocess
        if df is not None:
            if self._validate_schema(df):
                df = self._preprocess(df)
            else:
                return None
                
        return df
    
    def _validate_schema(self, df: pd.DataFrame) -> bool:
        """
        Validate that DataFrame has required columns.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if valid, False otherwise
        """
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        
        if missing_cols:
            st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
            return False
        
        # Validate split_type values
        invalid_splits = df[~df['split_type'].isin(self.VALID_SPLIT_TYPES)]['split_type'].unique()
        if len(invalid_splits) > 0:
            st.warning(f"⚠️ Invalid split_type values found: {', '.join(invalid_splits)}")
        
        return True
    
    def _preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess DataFrame: convert types, add computed columns.
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        # Convert month to categorical for proper sorting
        df['for_month'] = pd.Categorical(
            df['for_month'], 
            categories=self.MONTH_ORDER,
            ordered=True
        )
        
        # Ensure numeric columns
        numeric_cols = ['amount', 'units', 'guillem_salary', 'vero_salary']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill NaN values for optional columns
        optional_numeric = ['guillem_bonus', 'vero_bonus', 'guillem_amount', 
                           'vero_amount', 'guillem_ratio', 'vero_ratio']
        for col in optional_numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Create period display column
        df['period_display'] = df['for_month'].astype(str) + ' ' + df['for_year'].astype(str)
        
        return df
    
    @staticmethod
    def get_available_periods(df: pd.DataFrame) -> list:
        """
        Get sorted list of available period labels.
        
        Args:
            df: DataFrame with period_display column
            
        Returns:
            Sorted list of period strings
        """
        periods = df.groupby(['for_year', 'for_month', 'period_display']).size().reset_index()
        periods = periods.sort_values(['for_year', 'for_month']).drop_duplicates()
        periods = periods['period_display'].tolist()
        periods = list(set(periods))
        return periods