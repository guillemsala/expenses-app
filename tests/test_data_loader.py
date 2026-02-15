"""
Unit tests for data loader module.
"""

import pytest
import pandas as pd
from pathlib import Path
from src.data_loader import DataLoader


def test_validate_schema_valid():
    """Test schema validation with valid DataFrame."""
    loader = DataLoader()
    
    df = pd.DataFrame({
        'for_month': ['January'],
        'for_year': [2025],
        'type': ['rent'],
        'name': ['Monthly rent'],
        'amount': [2000],
        'units': [1],
        'split_type': ['salary_weighted'],
        'guillem_salary': [6000],
        'vero_salary': [4000]
    })
    
    assert loader._validate_schema(df) is True


def test_validate_schema_missing_columns():
    """Test schema validation with missing columns."""
    loader = DataLoader()
    
    df = pd.DataFrame({
        'for_month': ['January'],
        'amount': [2000]
    })
    
    assert loader._validate_schema(df) is False


def test_preprocess_month_ordering():
    """Test that preprocessing creates proper month ordering."""
    loader = DataLoader()
    
    df = pd.DataFrame({
        'for_month': ['March', 'January', 'February'],
        'for_year': [2025, 2025, 2025],
        'type': ['rent', 'rent', 'rent'],
        'name': ['Rent', 'Rent', 'Rent'],
        'amount': [2000, 2000, 2000],
        'units': [1, 1, 1],
        'split_type': ['salary_weighted', 'salary_weighted', 'salary_weighted'],
        'guillem_salary': [6000, 6000, 6000],
        'vero_salary': [4000, 4000, 4000]
    })
    
    result = loader._preprocess(df)
    
    # Check that months are categorical with proper order
    assert pd.api.types.is_categorical_dtype(result['for_month'])
    assert result['for_month'].cat.ordered is True


def test_preprocess_numeric_conversion():
    """Test that preprocessing converts strings to numeric."""
    loader = DataLoader()
    
    df = pd.DataFrame({
        'for_month': ['January'],
        'for_year': [2025],
        'type': ['rent'],
        'name': ['Rent'],
        'amount': ['2000'],  # String
        'units': ['1'],      # String
        'split_type': ['salary_weighted'],
        'guillem_salary': ['6000'],  # String
        'vero_salary': ['4000']      # String
    })
    
    result = loader._preprocess(df)
    
    assert pd.api.types.is_numeric_dtype(result['amount'])
    assert pd.api.types.is_numeric_dtype(result['units'])
    assert pd.api.types.is_numeric_dtype(result['guillem_salary'])
    assert pd.api.types.is_numeric_dtype(result['vero_salary'])


def test_preprocess_optional_columns():
    """Test that preprocessing handles optional columns with NaN."""
    loader = DataLoader()
    
    df = pd.DataFrame({
        'for_month': ['January'],
        'for_year': [2025],
        'type': ['rent'],
        'name': ['Rent'],
        'amount': [2000],
        'units': [1],
        'split_type': ['salary_weighted'],
        'guillem_salary': [6000],
        'vero_salary': [4000],
        'guillem_bonus': [None],  # Optional column with NaN
        'vero_bonus': [None]
    })
    
    result = loader._preprocess(df)
    
    assert result['guillem_bonus'].iloc[0] == 0
    assert result['vero_bonus'].iloc[0] == 0


def test_preprocess_creates_period_display():
    """Test that preprocessing creates period_display column."""
    loader = DataLoader()
    
    df = pd.DataFrame({
        'for_month': ['January', 'February'],
        'for_year': [2025, 2025],
        'type': ['rent', 'rent'],
        'name': ['Rent', 'Rent'],
        'amount': [2000, 2000],
        'units': [1, 1],
        'split_type': ['salary_weighted', 'salary_weighted'],
        'guillem_salary': [6000, 6000],
        'vero_salary': [4000, 4000]
    })
    
    result = loader._preprocess(df)
    
    assert 'period_display' in result.columns
    assert result['period_display'].iloc[0] == 'January 2025'
    assert result['period_display'].iloc[1] == 'February 2025'


def test_get_available_periods():
    """Test extraction of available periods."""
    df = pd.DataFrame({
        'for_month': pd.Categorical(['January', 'January', 'February'], 
                                   categories=DataLoader.MONTH_ORDER, 
                                   ordered=True),
        'for_year': [2025, 2025, 2025],
        'period_display': ['January 2025', 'January 2025', 'February 2025']
    })
    
    periods = DataLoader.get_available_periods(df)
    
    assert len(periods) == 2
    assert 'January 2025' in periods
    assert 'February 2025' in periods


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
