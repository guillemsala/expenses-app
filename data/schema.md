# Data Schema Documentation

## Current Schema (Single File)

The application currently expects a single CSV file with the following structure:

### Core Columns (Required)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `input_date` | date | Date when the expense was recorded | `2025-01-15` |
| `for_month` | string | Month the expense applies to | `January` |
| `for_year` | integer | Year the expense applies to | `2025` |
| `type` | string | Category of expense | `rent`, `groceries`, `personal` |
| `name` | string | Description of the expense | `Monthly Rent` |
| `amount` | float | Base amount of the expense | `2000.00` |
| `units` | integer | Multiplier for the amount | `1` |

### Split Configuration Columns (Required)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `split_type` | string | Method for splitting expense | `salary_weighted`, `custom_absolute`, `custom_relative` |
| `guillem_salary` | float | Guillem's base salary | `6000.00` |
| `vero_salary` | float | Vero's base salary | `4000.00` |

### Split-Specific Columns (Conditional)

#### For `custom_absolute` split type:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `guillem_amount` | float | Fixed amount for Guillem | `100.00` |
| `vero_amount` | float | Fixed amount for Vero | `80.00` |

#### For `custom_relative` split type:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `guillem_ratio` | float | Guillem's share ratio (0-1) | `0.6` |
| `vero_ratio` | float | Vero's share ratio (0-1) | `0.4` |

### Income Columns (Optional)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `guillem_bonus` | float | Guillem's bonus for the month | `1000.00` |
| `vero_bonus` | float | Vero's bonus for the month | `500.00` |

## Split Type Details

### 1. Salary Weighted (`salary_weighted`)

Splits the expense proportionally based on base salaries.

**Formula:**
- Guillem's share = (guillem_salary / (guillem_salary + vero_salary)) × total_amount
- Vero's share = (vero_salary / (guillem_salary + vero_salary)) × total_amount

**Example:** With salaries 6000 and 4000, a 1000 CHF expense splits to 600 and 400.

**Use case:** Shared expenses like rent, utilities, groceries where fair split is proportional to income.

### 2. Custom Absolute (`custom_absolute`)

Each person pays a fixed amount.

**Formula:**
- Guillem's share = guillem_amount × units
- Vero's share = vero_amount × units

**Example:** Guillem's gym (100 CHF) and Vero's yoga (80 CHF) as separate personal expenses.

**Use case:** Personal expenses or expenses where each person pays a known fixed amount.

### 3. Custom Relative (`custom_relative`)

Each person pays a specified percentage.

**Formula:**
- Guillem's share = guillem_ratio × total_amount
- Vero's share = vero_ratio × total_amount

**Example:** With ratios 0.6 and 0.4, a 1000 CHF expense splits to 600 and 400.

**Use case:** When you want a specific percentage split different from salary weighting.

## Special Expense Type

### Personal Expenses (`type='personal'`)

Expenses marked as `personal` are treated as 100% individual expenses and don't contribute to shared expense calculations. The split configuration determines who pays what amount.

**Example:**
```csv
type,name,split_type,guillem_amount,vero_amount
personal,Gym - Guillem,custom_absolute,100,0
personal,Yoga - Vero,custom_absolute,0,80
```

## Data Validation Rules

1. **Required fields:** All core and split configuration columns must be present
2. **Split type values:** Must be one of: `salary_weighted`, `custom_absolute`, `custom_relative`
3. **Numeric fields:** Amount, units, salaries, bonuses must be numeric (or convertible to numeric)
4. **Ratios:** For `custom_relative`, ratios should sum to 1.0
5. **Months:** Must be full month names (January, February, etc.)

## Future Proposed Schema (Multi-File)

For improved scalability and maintainability, consider splitting into:

### 1. `income.csv` (Monthly granularity)
```csv
year,month,guillem_salary,vero_salary,guillem_bonus,vero_bonus
2025,January,6000,4000,0,0
```

### 2. `expenses.csv` (Transaction granularity)
```csv
expense_id,input_date,for_year,for_month,type,name,amount,units
1,2025-01-15,2025,January,rent,Monthly Rent,2000,1
```

### 3. `expense_splits.csv` (Split configuration)
```csv
expense_id,split_type,guillem_amount,vero_amount,guillem_ratio,vero_ratio
1,salary_weighted,0,0,0,0
```

Benefits: normalized structure, easier updates, better audit trail, scalable to multiple people.
