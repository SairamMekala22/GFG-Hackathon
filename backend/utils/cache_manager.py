"""In-memory cache for reusable dataset intelligence."""

from __future__ import annotations

from threading import Lock
from typing import Any, Callable

from services.anomaly_service import detect_anomalies
from services.correlation_service import discover_correlations
from services.data_quality_service import analyze_data_quality
from services.dataframe_service import load_table_dataframe
from services.dataset_profile import get_dataset_profile

_dataset_cache: dict[str, dict[str, Any]] = {}
_cache_lock = Lock()


def get_cached_dataset_artifact(table_name: str, key: str) -> Any:
    with _cache_lock:
        return _dataset_cache.get(table_name, {}).get(key)


def set_cached_dataset_artifact(table_name: str, key: str, value: Any) -> None:
    with _cache_lock:
        _dataset_cache.setdefault(table_name, {})[key] = value


def invalidate_dataset_cache(table_name: str) -> None:
    with _cache_lock:
        _dataset_cache.pop(table_name, None)


def get_or_compute_cached_artifact(table_name: str, key: str, compute: Callable[[], Any]) -> Any:
    cached = get_cached_dataset_artifact(table_name, key)
    if cached is not None:
        return cached
    value = compute()
    set_cached_dataset_artifact(table_name, key, value)
    return value


def get_or_compute_dataset_profile(engine, table_name: str) -> dict[str, Any]:
    return get_or_compute_cached_artifact(
        table_name,
        "profile",
        lambda: get_dataset_profile(engine, table_name),
    )


def get_or_compute_quality_report(engine, table_name: str) -> dict[str, Any]:
    return get_or_compute_cached_artifact(
        table_name,
        "quality_report",
        lambda: analyze_data_quality(load_table_dataframe(engine, table_name).dataframe),
    )


def get_or_compute_correlations(engine, table_name: str) -> dict[str, Any]:
    return get_or_compute_cached_artifact(
        table_name,
        "correlations",
        lambda: discover_correlations(load_table_dataframe(engine, table_name).dataframe),
    )


def get_or_compute_anomaly_baseline(engine, table_name: str) -> dict[str, Any]:
    return get_or_compute_cached_artifact(
        table_name,
        "anomaly_baseline",
        lambda: detect_anomalies(load_table_dataframe(engine, table_name).dataframe),
    )


def warm_dataset_cache(engine, table_name: str) -> None:
    """Populate commonly reused dataset intelligence entries."""
    set_cached_dataset_artifact(table_name, "profile", get_dataset_profile(engine, table_name))
    context = load_table_dataframe(engine, table_name)
    set_cached_dataset_artifact(table_name, "quality_report", analyze_data_quality(context.dataframe))
    set_cached_dataset_artifact(table_name, "correlations", discover_correlations(context.dataframe))
    set_cached_dataset_artifact(table_name, "anomaly_baseline", detect_anomalies(context.dataframe))
