"""
Visualization module for financial dashboard.

This module handles creation of charts and graphs using Plotly.
"""

import plotly.graph_objects as go
import pandas as pd
from typing import List


class ChartGenerator:
    """Generates interactive Plotly charts for financial data."""

    METRIC_OPTIONS = {
        "Net Salary": ["Guillem Net Salary", "Vero Net Salary"],
        "Shared Expenses": ["Guillem Shared Expenses", "Vero Shared Expenses"],
        "Personal Expenses": ["Guillem Personal Expenses", "Vero Personal Expenses"],
        "Net Savings": ["Guillem Net Savings", "Vero Net Savings"],
    }

    COLOR_SCHEME = {
        "Guillem": "#1f77b4",  # Blue
        "Vero": "#ff7f0e",  # Orange
    }

    @staticmethod
    def create_trend_line_chart(
        df: pd.DataFrame, selected_metric: str, height: int = 500
    ) -> go.Figure:
        """
        Create a line chart showing trends over time.

        Args:
            df: DataFrame with period and metric columns
            selected_metric: Which metric to display
            height: Chart height in pixels

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        metric_columns = ChartGenerator.METRIC_OPTIONS.get(selected_metric, [])

        for person_metric in metric_columns:
            person_name = person_metric.split()[0]
            color = ChartGenerator.COLOR_SCHEME.get(person_name, "#333333")

            fig.add_trace(
                go.Scatter(
                    x=df["period"],
                    y=df[person_metric],
                    mode="lines+markers",
                    name=person_name,
                    line=dict(width=3, color=color),
                    marker=dict(size=8, color=color),
                    hovertemplate=f"<b>{person_name}</b><br>"
                    + "Period: %{x}<br>"
                    + "Amount: CHF %{y:,.0f}<br>"
                    + "<extra></extra>",
                )
            )

        fig.update_layout(
            title=f"{selected_metric} Over Time",
            xaxis_title="Period",
            yaxis_title="Amount (CHF)",
            hovermode="x unified",
            height=height,
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )

        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(128,128,128,0.2)",
        )

        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(128,128,128,0.2)",
        )

        return fig

    @staticmethod
    def create_stacked_bar_chart(
        df: pd.DataFrame, person: str = "Guillem"
    ) -> go.Figure:
        """
        Create a stacked bar chart showing expense breakdown.

        Args:
            df: DataFrame with period and expense columns
            person: Which person's data to show

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=df["period"],
                y=df[f"{person} Shared Expenses"],
                name="Shared Expenses",
                marker_color="lightblue",
            )
        )

        fig.add_trace(
            go.Bar(
                x=df["period"],
                y=df[f"{person} Personal Expenses"],
                name="Personal Expenses",
                marker_color="lightcoral",
            )
        )

        fig.update_layout(
            barmode="stack",
            title=f"{person}'s Expense Breakdown",
            xaxis_title="Period",
            yaxis_title="Amount (CHF)",
            height=400,
            showlegend=True,
        )

        return fig

    @staticmethod
    def create_savings_rate_chart(period_financials_list: List) -> go.Figure:
        """
        Create a line chart comparing savings rates.

        Args:
            period_financials_list: List of PeriodFinancials objects

        Returns:
            Plotly Figure object
        """
        periods = [pf.period for pf in period_financials_list]
        guillem_rates = [pf.guillem.savings_rate for pf in period_financials_list]
        vero_rates = [pf.vero.savings_rate for pf in period_financials_list]

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=periods,
                y=guillem_rates,
                mode="lines+markers",
                name="Guillem",
                line=dict(width=3, color=ChartGenerator.COLOR_SCHEME["Guillem"]),
                marker=dict(size=8),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=periods,
                y=vero_rates,
                mode="lines+markers",
                name="Vero",
                line=dict(width=3, color=ChartGenerator.COLOR_SCHEME["Vero"]),
                marker=dict(size=8),
            )
        )

        fig.update_layout(
            title="Savings Rate Over Time",
            xaxis_title="Period",
            yaxis_title="Savings Rate (%)",
            hovermode="x unified",
            height=400,
            showlegend=True,
        )

        return fig

    @staticmethod
    def get_metric_options() -> List[str]:
        """Get list of available metrics for selection."""
        return list(ChartGenerator.METRIC_OPTIONS.keys())
