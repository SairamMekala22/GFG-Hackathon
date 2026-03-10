"""Automatic executive dashboard generation from dataset schema."""

from __future__ import annotations

import pandas as pd

from services.chart_selector import infer_chart_type
from services.dataframe_service import categorical_columns, coerce_datetime, infer_time_column, numeric_columns
from services.insight_generator import generate_insight, generate_summary_cards


def _build_widget(widget_id: str, title: str, data: list[dict], chart_type: str, metadata: dict, source_prompt: str, x: int, y: int, w: int = 6, h: int = 8) -> dict:
    return {
        "widget_id": widget_id,
        "title": title,
        "data": data,
        "chart_type": chart_type,
        "chart_metadata": metadata,
        "source_prompt": source_prompt,
        "layout": {"i": widget_id, "x": x, "y": y, "w": w, "h": h},
    }


def autogenerate_dashboard(dataframe: pd.DataFrame, dataset_name: str) -> dict:
    """Generate KPI cards and starter charts from the uploaded dataset."""
    numeric = [column for column in numeric_columns(dataframe) if column.lower() not in {"id", "index"}]
    categories = categorical_columns(dataframe)
    time_column = infer_time_column(dataframe)
    primary_metric = next((column for column in numeric if "revenue" in column.lower() or "sales" in column.lower()), None)
    primary_metric = primary_metric or (numeric[0] if numeric else None)

    widgets = []
    summary_cards = []

    if primary_metric:
        numeric_series = pd.to_numeric(dataframe[primary_metric], errors="coerce").dropna()
        if len(numeric_series):
            summary_cards.append(
                {
                    "title": f"Total {primary_metric.replace('_', ' ')}",
                    "value": f"{numeric_series.sum():,.0f}",
                    "summary": f"Primary metric aggregated across {len(numeric_series)} rows.",
                }
            )
            summary_cards.append(
                {
                    "title": f"Average {primary_metric.replace('_', ' ')}",
                    "value": f"{numeric_series.mean():,.2f}",
                    "summary": "Mean performance level across the uploaded dataset.",
                }
            )

    if primary_metric and categories:
        top_dimension = categories[0]
        category_frame = (
            dataframe[[top_dimension, primary_metric]]
            .assign(**{primary_metric: pd.to_numeric(dataframe[primary_metric], errors="coerce")})
            .dropna()
            .groupby(top_dimension, as_index=False)[primary_metric]
            .sum()
            .sort_values(primary_metric, ascending=False)
        )
        if len(category_frame):
            top_row = category_frame.iloc[0]
            summary_cards.append(
                {
                    "title": f"Top {top_dimension.replace('_', ' ')}",
                    "value": str(top_row[top_dimension]),
                    "summary": f"Leads with {top_row[primary_metric]:,.0f} {primary_metric.replace('_', ' ')}.",
                }
            )
            widgets.append(
                _build_widget(
                    "autogen-category",
                    f"{primary_metric.replace('_', ' ').title()} by {top_dimension.replace('_', ' ').title()}",
                    category_frame.to_dict(orient="records"),
                    "bar",
                    {"chart_type": "bar", "x_axis": top_dimension, "y_axis": primary_metric},
                    f"Auto-generated view for {dataset_name}",
                    x=0,
                    y=0,
                )
            )

    if primary_metric and time_column:
        timestamps = coerce_datetime(dataframe, time_column)
        trend_frame = dataframe.copy()
        trend_frame[time_column] = timestamps
        trend_frame[primary_metric] = pd.to_numeric(dataframe[primary_metric], errors="coerce")
        trend_frame = (
            trend_frame.dropna(subset=[time_column, primary_metric])
            .groupby(time_column, as_index=False)[primary_metric]
            .sum()
            .sort_values(time_column)
        )
        if len(trend_frame):
            trend_frame[time_column] = trend_frame[time_column].dt.strftime("%Y-%m-%d")
            widgets.append(
                _build_widget(
                    "autogen-trend",
                    f"{primary_metric.replace('_', ' ').title()} over Time",
                    trend_frame.to_dict(orient="records"),
                    "line",
                    {"chart_type": "line", "x_axis": time_column, "y_axis": primary_metric},
                    f"Auto-generated trend for {dataset_name}",
                    x=6,
                    y=0,
                )
            )

    if primary_metric:
        distribution_frame = (
            pd.to_numeric(dataframe[primary_metric], errors="coerce")
            .dropna()
            .reset_index(drop=True)
            .rename(primary_metric)
            .to_frame()
        )
        if len(distribution_frame):
            distribution_frame["bucket"] = pd.cut(distribution_frame[primary_metric], bins=min(8, len(distribution_frame))).astype(str)
            histogram = distribution_frame.groupby("bucket", as_index=False).size().rename(columns={"size": "count"})
            widgets.append(
                _build_widget(
                    "autogen-distribution",
                    f"{primary_metric.replace('_', ' ').title()} distribution",
                    histogram.to_dict(orient="records"),
                    "bar",
                    {"chart_type": "bar", "x_axis": "bucket", "y_axis": "count"},
                    f"Auto-generated distribution for {dataset_name}",
                    x=0,
                    y=8,
                )
            )

    insight_source = widgets[0]["data"] if widgets else dataframe.head(20).to_dict(orient="records")
    return {
        "widgets": widgets,
        "summary_cards": summary_cards,
        "insight": generate_insight(insight_source, f"Auto-generated executive dashboard for {dataset_name}"),
        "dashboard_title": f"{dataset_name} executive starter dashboard",
    }
