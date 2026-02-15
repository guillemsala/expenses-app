# Quick Start Guide

Welcome to your modularized Financial Dashboard! Here's how to get started.

## Installation

```bash
cd financial_dashboard

# Option 1: Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Option 2: Using pip
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

## Running the App

```bash
# Make sure you're in the financial_dashboard directory
streamlit run app.py
```

The app will automatically look for `expenses.csv` on your Desktop. If not found, you can upload a file through the interface.

## Testing Your Setup

Try the sample data:
```bash
# Copy sample data to your desktop
cp data/sample_expenses.csv ~/Desktop/expenses.csv

# Run the app
streamlit run app.py
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_calculations.py -v
```

## Project Structure

```
expenses-app/
├── app.py                  # Main application - run this!
├── src/
│   ├── data_loader.py      # Handles CSV loading
│   ├── calculations.py     # Financial calculations
│   ├── visualizations.py   # Chart generation
│   └── ui_components.py    # UI widgets
├── tests/                  # Unit tests
├── data/                   # Sample data and schema docs
├── docs/                   # User guide
├── pyproject.toml          # Dependencies
└── README.md              # Full documentation
```

## Key Improvements in This Version

1. **Modular Architecture**: Code split into logical modules
2. **Type Safety**: All functions have type hints
3. **Testability**: Comprehensive unit tests included
4. **Documentation**: README, user guide, and schema docs
5. **Scalability**: Easy to extend and maintain
6. **Separation of Concerns**: Data, logic, and UI are separate

## Next Steps

1. Read the full README.md for detailed documentation
2. Check out data/schema.md for data format details
3. Explore docs/user_guide.md for usage instructions
4. Run the tests to verify everything works
5. Start entering your own financial data!

## Common Commands

```bash
# Format code
uv run black src/ tests/

# Lint code
uv run flake8 src/ tests/

# Type check
uv run mypy src/

# Run specific test
uv run pytest tests/test_calculations.py::test_salary_weighted_split -v
```

