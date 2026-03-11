"""Background workers for progressive query analysis and dataset cache warming."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pandas as pd

from database.db import engine
from extensions import socketio
from routes.websocket_routes import store_analysis_update
from services.anomaly_service import detect_anomalies
from services.recommendation_service import generate_recommendations
from services.root_cause_service import analyze_root_causes
from utils.cache_manager import get_or_compute_correlations, warm_dataset_cache

executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="analysis-worker")


def new_job_id() -> str:
    return str(uuid4())


def _expanded_insight(
    basic_insight: str,
    anomalies: list[dict],
    root_cause: dict,
    correlations: list[dict],
) -> str:
    parts = [basic_insight] if basic_insight else []
    if root_cause.get("root_causes"):
        parts.append(f"Key driver: {root_cause['root_causes'][0]}")
    elif anomalies:
        anomaly = max(anomalies, key=lambda item: item.get("score", 0))
        label = anomaly.get("date") or anomaly.get("period") or "the flagged point"
        parts.append(f"Anomaly detected around {label}, where the metric moved abnormally.")

    if correlations:
        strongest = correlations[0]
        parts.append(
            f"The strongest numeric relationship in the dataset is {strongest['metric_a']} to {strongest['metric_b']} ({strongest['value']})."
        )
    return " ".join(parts).strip()


def warm_dataset_cache_async(table_name: str) -> None:
    executor.submit(warm_dataset_cache, engine, table_name)


def submit_async_analysis(
    *,
    session_id: str,
    job_id: str,
    widget_id: str,
    prompt: str,
    rows: list[dict],
    chart_metadata: dict,
    basic_insight: str,
    summary_cards: list[dict],
    active_table: str,
) -> None:
    """Run deeper analysis after the immediate chart response is returned."""
    executor.submit(
        _run_async_analysis,
        session_id,
        job_id,
        widget_id,
        prompt,
        rows,
        chart_metadata,
        basic_insight,
        summary_cards,
        active_table,
    )


def _run_async_analysis(
    session_id: str,
    job_id: str,
    widget_id: str,
    prompt: str,
    rows: list[dict],
    chart_metadata: dict,
    basic_insight: str,
    summary_cards: list[dict],
    active_table: str,
) -> None:
    try:
        frame = pd.DataFrame(rows or [])
        anomalies_result = detect_anomalies(
            frame,
            metric=chart_metadata.get("y_axis"),
            time_column=chart_metadata.get("x_axis"),
        )
        anomalies = anomalies_result.get("anomalies", [])

        dataset_frame = pd.read_sql_query(f"SELECT * FROM {active_table}", engine)
        should_run_root_cause = bool(anomalies) or any(
            token in prompt.lower() for token in ("why", "drop", "decline", "spike", "anomaly")
        )
        root_cause = analyze_root_causes(dataset_frame, prompt) if should_run_root_cause else {"root_causes": []}

        correlation_bundle = get_or_compute_correlations(engine, active_table)
        correlations = correlation_bundle.get("correlations", [])

        best_case = next(
            (card.get("value") for card in summary_cards if (card.get("title") or "").lower() == "best case"),
            None,
        )
        worst_case = next(
            (card.get("value") for card in summary_cards if (card.get("title") or "").lower() == "worst case"),
            None,
        )
        recommendations = generate_recommendations(
            insights=[basic_insight],
            metrics={
                "primary_metric": chart_metadata.get("y_axis"),
                "best_case": best_case,
                "worst_case": worst_case,
            },
            anomalies=anomalies,
            correlations=correlations,
            root_causes=root_cause.get("root_causes") or [],
        ).get("recommendations", [])

        payload = {
            "job_id": job_id,
            "widget_id": widget_id,
            "root_cause": root_cause,
            "correlations": correlations,
            "anomalies": anomalies,
            "recommendations": recommendations,
            "insight": _expanded_insight(basic_insight, anomalies, root_cause, correlations),
            "analysis_pending": False,
            "status": "completed",
        }
        store_analysis_update(session_id, payload)
        socketio.emit("analysis_update", payload, room=session_id)
    except Exception as error:  # noqa: BLE001
        payload = {
            "job_id": job_id,
            "widget_id": widget_id,
            "analysis_pending": False,
            "status": "failed",
            "error": str(error),
        }
        store_analysis_update(session_id, payload)
        socketio.emit("analysis_update", payload, room=session_id)
