# Quick Start Guide

Welcome to Guillem & Vero's expenses app. 

## Installation

```bash
cd expenses-app

# Option 1: Using uv (recommended)
uv init
uv sync

# Make sure you're in the expenses-app directory, then run
uv run streamlit run app.py
```

Currently, you can upload a file through the interface.

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_calculations.py -v
```

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

