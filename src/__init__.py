"""
Financial Dashboard - A modular application for household expense tracking.
"""

__version__ = "0.1.0"

from src.data_loader import DataLoader
from src.calculations import FinancialCalculator, PeriodFinancials, PersonFinancials
from src.visualizations import ChartGenerator
from src.ui_components import UIComponents

__all__ = [
    "DataLoader",
    "FinancialCalculator",
    "PeriodFinancials",
    "PersonFinancials",
    "ChartGenerator",
    "UIComponents",
]
