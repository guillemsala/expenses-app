import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# Set page config
st.set_page_config(page_title="Financial Analysis", layout="wide", page_icon="💰")

# Title
st.title("💰 Financial Analysis Dashboard")

# Try to read from default path first
default_path = Path.home() / "Desktop" / "expenses.csv"
df = None

if default_path.exists():
    try:
        df = pd.read_csv(default_path)
        st.success(f"✅ Loaded data from: {default_path}")
    except Exception as e:
        st.error(f"Error reading from {default_path}: {e}")
        df = None

# If default file not found or failed to load, show file uploader
if df is None:
    st.info(f"📁 Default file not found at: {default_path}")
    uploaded_file = st.file_uploader("Upload financials", type=['csv'])
    
    if uploaded_file is not None:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)

if df is not None:
    # Data preprocessing
    df['for_month'] = pd.Categorical(df['for_month'], 
                                     categories=['January', 'February', 'March', 'April', 'May', 'June',
                                               'July', 'August', 'September', 'October', 'November', 'December'],
                                     ordered=True)
    
    # Calculate actual amounts based on split_type
    def calculate_amounts(row):
        total_amount = row['amount'] * row['units']
        
        if row['split_type'] == 'salary_weighted':
            total_salary = row['guillem_salary'] + row['vero_salary']
            guillem_share = (row['guillem_salary'] / total_salary) * total_amount
            vero_share = (row['vero_salary'] / total_salary) * total_amount
        elif row['split_type'] == 'custom_absolute':
            guillem_share = row['guillem_amount'] * row['units']
            vero_share = row['vero_amount'] * row['units']
        elif row['split_type'] == 'custom_relative':
            guillem_share = row['guillem_ratio'] * total_amount
            vero_share = row['vero_ratio'] * total_amount
        else:
            guillem_share = 0
            vero_share = 0
        
        return pd.Series({'guillem_final': guillem_share, 'vero_final': vero_share, 'total_final': total_amount})
    
    # Apply calculation
    amounts = df.apply(calculate_amounts, axis=1)
    df = pd.concat([df, amounts], axis=1)
    
    # Create period identifier for grouping
    df['period_display'] = df['for_month'].astype(str) + ' ' + df['for_year'].astype(str)
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Create period combinations
    available_periods = df.groupby(['for_year', 'for_month', 'period_display']).size().reset_index()[['for_year', 'for_month', 'period_display']]
    available_periods = available_periods.sort_values(['for_year', 'for_month']).drop_duplicates()
    period_options = list(set(available_periods['period_display'].tolist()))
    
    selected_periods = st.sidebar.multiselect(
        "Select Month/Year Combinations", 
        period_options, 
        default=period_options
    )
    
    # Filter data based on selected periods
    filtered_df = df[df['period_display'].isin(selected_periods)]
    
    # Summary by month
    st.header("📊 Financial Analysis")
    
    if len(filtered_df) > 0:
        # Prepare data structures for totals and charts
        totals_guillem = {
            'net_salary': 0,
            'shared_expenses': 0,
            'personal_expenses': 0,
            'net_savings': 0
        }
        totals_vero = {
            'net_salary': 0,
            'shared_expenses': 0,
            'personal_expenses': 0,
            'net_savings': 0
        }
        
        # Data for line charts
        chart_data = []
        
        # Group by period and calculate metrics
        for period in selected_periods:
            period_data = filtered_df[filtered_df['period_display'] == period]
            
            # Get salaries and bonuses (assuming they're consistent within a period)
            guillem_salary = period_data['guillem_salary'].iloc[0] if len(period_data) > 0 else 0
            vero_salary = period_data['vero_salary'].iloc[0] if len(period_data) > 0 else 0
            guillem_bonus = period_data['guillem_bonus'].iloc[0] if len(period_data) > 0 and 'guillem_bonus' in period_data.columns else 0
            vero_bonus = period_data['vero_bonus'].iloc[0] if len(period_data) > 0 and 'vero_bonus' in period_data.columns else 0
            
            # Total income includes salary + bonus
            guillem_total_income = guillem_salary + guillem_bonus
            vero_total_income = vero_salary + vero_bonus
            
            # Separate shared vs personal expenses based on 'type' column
            shared_expenses = period_data[period_data['type'] != 'personal']
            personal_expenses = period_data[period_data['type'] == 'personal']
            
            guillem_shared = shared_expenses['guillem_final'].sum()
            vero_shared = shared_expenses['vero_final'].sum()
            total_shared = shared_expenses['total_final'].sum()
            
            # Calculate average split rate for shared expenses
            if total_shared > 0:
                guillem_split_rate = (guillem_shared / total_shared) * 100
                vero_split_rate = (vero_shared / total_shared) * 100
            else:
                guillem_split_rate = 0
                vero_split_rate = 0
            
            # Personal expenses (100% to each person for type='personal')
            personal_guillem = personal_expenses['guillem_final'].sum()
            personal_vero = personal_expenses['vero_final'].sum()
            
            # Calculate total expenses and savings
            total_expenses_guillem = guillem_shared + personal_guillem
            total_expenses_vero = vero_shared + personal_vero
            
            net_savings_guillem = guillem_total_income - total_expenses_guillem
            net_savings_vero = vero_total_income - total_expenses_vero
            
            savings_rate_guillem = (net_savings_guillem / guillem_total_income * 100) if guillem_total_income > 0 else 0
            savings_rate_vero = (net_savings_vero / vero_total_income * 100) if vero_total_income > 0 else 0
            
            # Accumulate totals
            totals_guillem['net_salary'] += guillem_total_income
            totals_guillem['shared_expenses'] += guillem_shared
            totals_guillem['personal_expenses'] += personal_guillem
            totals_guillem['net_savings'] += net_savings_guillem
            
            totals_vero['net_salary'] += vero_total_income
            totals_vero['shared_expenses'] += vero_shared
            totals_vero['personal_expenses'] += personal_vero
            totals_vero['net_savings'] += net_savings_vero
            
            # Store data for charts
            chart_data.append({
                'period': period,
                'Guillem Net Salary': guillem_total_income,
                'Guillem Shared Expenses': guillem_shared,
                'Guillem Personal Expenses': personal_guillem,
                'Guillem Net Savings': net_savings_guillem,
                'Vero Net Salary': vero_total_income,
                'Vero Shared Expenses': vero_shared,
                'Vero Personal Expenses': personal_vero,
                'Vero Net Savings': net_savings_vero
            })
        
        # Create two-column layout: monthly details on left, totals and trends on right
        main_col1, main_col2 = st.columns([1, 1])
        
        with main_col1:
            st.subheader("📅 Monthly Financial Summary")
            
            # Display each period's summary
            for period in selected_periods:
                period_data = filtered_df[filtered_df['period_display'] == period]
                
                # Get salaries and bonuses
                guillem_salary = period_data['guillem_salary'].iloc[0] if len(period_data) > 0 else 0
                vero_salary = period_data['vero_salary'].iloc[0] if len(period_data) > 0 else 0
                guillem_bonus = period_data['guillem_bonus'].iloc[0] if len(period_data) > 0 and 'guillem_bonus' in period_data.columns else 0
                vero_bonus = period_data['vero_bonus'].iloc[0] if len(period_data) > 0 and 'vero_bonus' in period_data.columns else 0
                
                guillem_total_income = guillem_salary + guillem_bonus
                vero_total_income = vero_salary + vero_bonus
                
                # Separate shared vs personal expenses
                shared_expenses = period_data[period_data['type'] != 'personal']
                personal_expenses = period_data[period_data['type'] == 'personal']
                
                guillem_shared = shared_expenses['guillem_final'].sum()
                vero_shared = shared_expenses['vero_final'].sum()
                total_shared = shared_expenses['total_final'].sum()
                
                # Calculate split rates
                if total_shared > 0:
                    guillem_split_rate = (guillem_shared / total_shared) * 100
                    vero_split_rate = (vero_shared / total_shared) * 100
                else:
                    guillem_split_rate = 0
                    vero_split_rate = 0
                
                personal_guillem = personal_expenses['guillem_final'].sum()
                personal_vero = personal_expenses['vero_final'].sum()
                
                total_expenses_guillem = guillem_shared + personal_guillem
                total_expenses_vero = vero_shared + personal_vero
                
                net_savings_guillem = guillem_total_income - total_expenses_guillem
                net_savings_vero = vero_total_income - total_expenses_vero
                
                savings_rate_guillem = (net_savings_guillem / guillem_total_income * 100) if guillem_total_income > 0 else 0
                savings_rate_vero = (net_savings_vero / vero_total_income * 100) if vero_total_income > 0 else 0
                
                st.markdown(f"**{period}**")
                
                subcol1, subcol2 = st.columns(2)
                
                with subcol1:
                    st.caption("👤 Guillem")
                    st.write(f"Salary: CHF {guillem_total_income:,.0f}")
                    st.write(f"Shared: CHF {guillem_shared:,.0f} ({guillem_split_rate:.0f}%)")
                    st.write(f"Personal: CHF {personal_guillem:,.0f}")
                    st.write(f"**Savings: CHF {net_savings_guillem:,.0f}** ({savings_rate_guillem:.0f}%)")
                
                with subcol2:
                    st.caption("👤 Vero")
                    st.write(f"Salary: CHF {vero_total_income:,.0f}")
                    st.write(f"Shared: CHF {vero_shared:,.0f} ({vero_split_rate:.0f}%)")
                    st.write(f"Personal: CHF {personal_vero:,.0f}")
                    st.write(f"**Savings: CHF {net_savings_vero:,.0f}** ({savings_rate_vero:.0f}%)")
                
                st.divider()
        
        with main_col2:
            st.subheader("📈 Totals Across Selected Periods")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**👤 Guillem**")
                st.metric("Net Salary", f"CHF {totals_guillem['net_salary']:,.0f}")
                st.metric("Shared Exp.", f"CHF {totals_guillem['shared_expenses']:,.0f}")
                st.metric("Personal Exp.", f"CHF {totals_guillem['personal_expenses']:,.0f}")
                st.metric("Net Savings", f"CHF {totals_guillem['net_savings']:,.0f}")
                total_savings_rate_guillem = (totals_guillem['net_savings'] / totals_guillem['net_salary'] * 100) if totals_guillem['net_salary'] > 0 else 0
                st.caption(f"Rate: {total_savings_rate_guillem:.1f}%")
            
            with col2:
                st.markdown("**👤 Vero**")
                st.metric("Net Salary", f"CHF {totals_vero['net_salary']:,.0f}")
                st.metric("Shared Exp.", f"CHF {totals_vero['shared_expenses']:,.0f}")
                st.metric("Personal Exp.", f"CHF {totals_vero['personal_expenses']:,.0f}")
                st.metric("Net Savings", f"CHF {totals_vero['net_savings']:,.0f}")
                total_savings_rate_vero = (totals_vero['net_savings'] / totals_vero['net_salary'] * 100) if totals_vero['net_salary'] > 0 else 0
                st.caption(f"Rate: {total_savings_rate_vero:.1f}%")
            
            with col3:
                st.markdown("**📊 Combined**")
                combined_income = totals_guillem['net_salary'] + totals_vero['net_salary']
                combined_shared = totals_guillem['shared_expenses'] + totals_vero['shared_expenses']
                combined_personal = totals_guillem['personal_expenses'] + totals_vero['personal_expenses']
                combined_savings = totals_guillem['net_savings'] + totals_vero['net_savings']
                combined_savings_rate = (combined_savings / combined_income * 100) if combined_income > 0 else 0
                
                st.metric("Income", f"CHF {combined_income:,.0f}")
                st.metric("Shared Exp.", f"CHF {combined_shared:,.0f}")
                st.metric("Personal Exp.", f"CHF {combined_personal:,.0f}")
                st.metric("Savings", f"CHF {combined_savings:,.0f}")
                st.caption(f"Rate: {combined_savings_rate:.1f}%")
            
            st.divider()
            
            # Line charts
            st.subheader("📉 Trends Over Time")
            
            # Convert chart data to DataFrame
            chart_df = pd.DataFrame(chart_data)
            
            # Sort by period
            def parse_period(period_str):
                parts = period_str.split()
                month_name = parts[0]
                year = int(parts[1])
                month_num = ['January', 'February', 'March', 'April', 'May', 'June',
                            'July', 'August', 'September', 'October', 'November', 'December'].index(month_name) + 1
                return (year, month_num)
            
            chart_df['sort_key'] = chart_df['period'].apply(parse_period)
            chart_df = chart_df.sort_values('sort_key')
            
            # Metric selector
            metric_options = {
                'Net Salary': ['Guillem Net Salary', 'Vero Net Salary'],
                'Shared Expenses': ['Guillem Shared Expenses', 'Vero Shared Expenses'],
                'Personal Expenses': ['Guillem Personal Expenses', 'Vero Personal Expenses'],
                'Net Savings': ['Guillem Net Savings', 'Vero Net Savings']
            }
            
            selected_metric = st.selectbox("Select metric to visualize:", list(metric_options.keys()))
            
            # Create line chart
            fig = go.Figure()
            
            for person_metric in metric_options[selected_metric]:
                person_name = person_metric.split()[0]
                fig.add_trace(go.Scatter(
                    x=chart_df['period'],
                    y=chart_df[person_metric],
                    mode='lines+markers',
                    name=person_name,
                    line=dict(width=3),
                    marker=dict(size=8)
                ))
            
            fig.update_layout(
                title=f"{selected_metric} Over Time",
                xaxis_title="Period",
                yaxis_title="Amount (CHF)",
                hovermode='x unified',
                height=500,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for the selected periods.")

else:
    st.info("👆 Please upload the financials CSV file to begin analysis")
    
    # Show expected format
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