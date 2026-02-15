"""
Unit tests for financial calculations module.
"""

import pytest
import pandas as pd
from src.calculations import FinancialCalculator


def test_salary_weighted_split():
    """Test salary-weighted expense splitting."""
    row = pd.Series(
        {
            "amount": 1000,
            "units": 1,
            "split_type": "salary_weighted",
            "guillem_salary": 6000,
            "vero_salary": 4000,
        }
    )

    result = FinancialCalculator.calculate_split_amounts(row)

    assert result["total_final"] == 1000
    assert result["guillem_final"] == 600  # 60% of 1000
    assert result["vero_final"] == 400  # 40% of 1000


def test_custom_absolute_split():
    """Test custom absolute expense splitting."""
    row = pd.Series(
        {
            "amount": 100,
            "units": 2,
            "split_type": "custom_absolute",
            "guillem_amount": 60,
            "vero_amount": 40,
            "guillem_salary": 6000,
            "vero_salary": 4000,
        }
    )

    result = FinancialCalculator.calculate_split_amounts(row)

    assert result["total_final"] == 200
    assert result["guillem_final"] == 120  # 60 * 2
    assert result["vero_final"] == 80  # 40 * 2


def test_custom_relative_split():
    """Test custom relative (ratio) expense splitting."""
    row = pd.Series(
        {
            "amount": 1000,
            "units": 1,
            "split_type": "custom_relative",
            "guillem_ratio": 0.7,
            "vero_ratio": 0.3,
            "guillem_salary": 6000,
            "vero_salary": 4000,
        }
    )

    result = FinancialCalculator.calculate_split_amounts(row)

    assert result["total_final"] == 1000
    assert result["guillem_final"] == 700  # 70% of 1000
    assert result["vero_final"] == 300  # 30% of 1000


def test_zero_salary_split():
    """Test handling of zero total salary."""
    row = pd.Series(
        {
            "amount": 1000,
            "units": 1,
            "split_type": "salary_weighted",
            "guillem_salary": 0,
            "vero_salary": 0,
        }
    )

    result = FinancialCalculator.calculate_split_amounts(row)

    assert result["total_final"] == 1000
    assert result["guillem_final"] == 0
    assert result["vero_final"] == 0


def test_period_financials_calculation():
    """Test complete period financial calculations."""
    # Create sample period data
    data = {
        "for_month": ["January", "January", "January"],
        "for_year": [2025, 2025, 2025],
        "type": ["rent", "groceries", "personal"],
        "amount": [2000, 500, 100],
        "units": [1, 1, 1],
        "guillem_salary": [6000, 6000, 6000],
        "vero_salary": [4000, 4000, 4000],
        "guillem_bonus": [0, 0, 0],
        "vero_bonus": [0, 0, 0],
        "guillem_final": [1200, 300, 100],  # Pre-calculated for this test
        "vero_final": [800, 200, 0],
        "total_final": [2000, 500, 100],
    }

    df = pd.DataFrame(data)

    result = FinancialCalculator.calculate_period_financials(df, "January 2025")

    # Check income
    assert result.guillem.total_income == 6000
    assert result.vero.total_income == 4000

    # Check shared expenses (rent + groceries)
    assert result.guillem.shared_expenses == 1500  # 1200 + 300
    assert result.vero.shared_expenses == 1000  # 800 + 200

    # Check personal expenses
    assert result.guillem.personal_expenses == 100
    assert result.vero.personal_expenses == 0

    # Check savings
    assert result.guillem.net_savings == 4400  # 6000 - 1500 - 100
    assert result.vero.net_savings == 3000  # 4000 - 1000 - 0


def test_aggregate_totals():
    """Test aggregation across multiple periods."""
    from src.calculations import PeriodFinancials, PersonFinancials

    # Create mock period financials
    pf1 = PeriodFinancials(
        period="January 2025",
        guillem=PersonFinancials(
            salary=6000,
            bonus=0,
            total_income=6000,
            shared_expenses=1500,
            personal_expenses=100,
            total_expenses=1600,
            net_savings=4400,
            savings_rate=73.33,
            split_rate=60.0,
        ),
        vero=PersonFinancials(
            salary=4000,
            bonus=0,
            total_income=4000,
            shared_expenses=1000,
            personal_expenses=50,
            total_expenses=1050,
            net_savings=2950,
            savings_rate=73.75,
            split_rate=40.0,
        ),
        total_shared_expenses=2500,
        combined_income=10000,
        combined_savings=7350,
        combined_savings_rate=73.5,
    )

    pf2 = PeriodFinancials(
        period="February 2025",
        guillem=PersonFinancials(
            salary=6000,
            bonus=1000,
            total_income=7000,
            shared_expenses=1600,
            personal_expenses=200,
            total_expenses=1800,
            net_savings=5200,
            savings_rate=74.29,
            split_rate=60.0,
        ),
        vero=PersonFinancials(
            salary=4000,
            bonus=500,
            total_income=4500,
            shared_expenses=1100,
            personal_expenses=100,
            total_expenses=1200,
            net_savings=3300,
            savings_rate=73.33,
            split_rate=40.0,
        ),
        total_shared_expenses=2700,
        combined_income=11500,
        combined_savings=8500,
        combined_savings_rate=73.91,
    )

    guillem_totals, vero_totals = FinancialCalculator.aggregate_totals([pf1, pf2])

    assert guillem_totals["net_salary"] == 13000  # 6000 + 7000
    assert guillem_totals["shared_expenses"] == 3100  # 1500 + 1600
    assert guillem_totals["personal_expenses"] == 300  # 100 + 200
    assert guillem_totals["net_savings"] == 9600  # 4400 + 5200

    assert vero_totals["net_salary"] == 8500  # 4000 + 4500
    assert vero_totals["shared_expenses"] == 2100  # 1000 + 1100
    assert vero_totals["personal_expenses"] == 150  # 50 + 100
    assert vero_totals["net_savings"] == 6250  # 2950 + 3300


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
