"""Business recommendation helpers grounded in current insights."""

from __future__ import annotations

from typing import Any

from services.gemini_service import gemini_service


def _deterministic_recommendations(
    insights: list[str],
    metrics: dict[str, Any] | None = None,
    anomalies: list[dict[str, Any]] | None = None,
    correlations: list[dict[str, Any]] | None = None,
    root_causes: list[str] | None = None,
) -> list[str]:
    metrics = metrics or {}
    recommendations: list[str] = []

    best_case = metrics.get("best_case")
    worst_case = metrics.get("worst_case")
    primary_metric = metrics.get("primary_metric") or "the primary metric"

    if best_case:
        recommendations.append(
            f"Scale the playbook behind {best_case} because it is currently leading {primary_metric}."
        )
    if worst_case:
        recommendations.append(
            f"Review the drivers behind {worst_case} because it is the weakest segment on {primary_metric}."
        )

    if anomalies:
        anomaly = max(anomalies, key=lambda item: item.get("score", 0))
        point_label = anomaly.get("label") or anomaly.get("date") or anomaly.get("period")
        recommendations.append(
            f"Audit the drivers around {point_label or 'the flagged anomaly'} before treating that movement as a sustainable trend."
        )

    for cause in (root_causes or [])[:2]:
        if "decline" in cause.lower() or "drop" in cause.lower() or "underperform" in cause.lower():
            recommendations.append(f"Prioritize corrective action on this driver: {cause}")
            break

    strong_positive = next((item for item in (correlations or []) if item.get("value", 0) >= 0.65), None)
    if strong_positive:
        recommendations.append(
            f"Use {strong_positive['metric_a']} as a planning lever for {strong_positive['metric_b']}, since they move together strongly."
        )

    if not recommendations and insights:
        recommendations.append(
            f"Use the latest insight as the working decision frame: {insights[0]}"
        )

    if not recommendations:
        recommendations.append(
            "No strong automated recommendation is available yet; narrow the question or isolate a clearer business metric."
        )

    seen: set[str] = set()
    unique: list[str] = []
    for recommendation in recommendations:
        if recommendation not in seen:
            unique.append(recommendation)
            seen.add(recommendation)
    return unique[:5]


def generate_recommendations(
    insights: list[str],
    metrics: dict[str, Any] | None = None,
    anomalies: list[dict[str, Any]] | None = None,
    correlations: list[dict[str, Any]] | None = None,
    root_causes: list[str] | None = None,
) -> dict[str, Any]:
    """Return actionable recommendations grounded in the current analysis."""
    recommendations = _deterministic_recommendations(
        insights=insights,
        metrics=metrics,
        anomalies=anomalies,
        correlations=correlations,
        root_causes=root_causes,
    )

    if gemini_service.is_configured():
        prompt = (
            "You are a business strategy advisor.\n"
            "Rewrite the grounded actions below into 3-5 crisp executive recommendations.\n"
            "Use only the supplied facts. Return JSON with a key named recommendations.\n\n"
            f"Insights: {insights}\n"
            f"Metrics: {metrics or {}}\n"
            f"Anomalies: {anomalies or []}\n"
            f"Correlations: {correlations or []}\n"
            f"Root causes: {root_causes or []}\n"
            f"Grounded recommendations: {recommendations}\n"
        )
        try:
            response = gemini_service.generate_json(prompt)
            llm_recommendations = response.get("recommendations")
            if isinstance(llm_recommendations, list) and llm_recommendations:
                recommendations = [str(item) for item in llm_recommendations[:5]]
        except Exception:  # noqa: BLE001
            pass

    return {"recommendations": recommendations}
