"""Executive report assembly and export helpers."""

from __future__ import annotations

import base64
import io
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer


def _as_lines(values: list[Any] | None, empty_message: str) -> list[str]:
    items = [str(value) for value in (values or []) if value not in (None, "")]
    return items if items else [empty_message]


def build_executive_report(payload: dict[str, Any]) -> dict[str, Any]:
    """Combine dashboard context into a structured executive report."""
    insight = (payload.get("insight") or "").strip()
    summary_cards = payload.get("summary_cards") or []
    root_cause = payload.get("root_cause") or {}
    anomalies = payload.get("anomalies") or []
    correlations = payload.get("correlations") or []
    recommendations = payload.get("recommendations") or []
    simulation = payload.get("simulation")
    widgets = payload.get("widgets") or []
    dataset = payload.get("dataset") or "active dataset"

    key_insights = [
        f"{card.get('title')}: {card.get('value')} — {card.get('summary')}"
        for card in summary_cards
        if card.get("title")
    ]

    report = {
        "executive_summary": insight or f"This report summarizes the current dashboard built on {dataset}.",
        "key_insights": key_insights or ["No structured insight cards were available."],
        "anomalies": [
            f"{item.get('date') or item.get('period') or item.get('label')}: value {item.get('value')} (score {item.get('score')})"
            for item in anomalies
        ],
        "root_causes": root_cause.get("root_causes") or [],
        "recommendations": recommendations,
        "forecast": [
            f"{simulation.get('scenario')}: {simulation.get('predicted_target_change')} for {simulation.get('target_metric')}"
        ] if simulation else [],
        "widgets": [
            {
                "title": widget.get("title"),
                "chart_type": widget.get("chartType") or widget.get("chart_type"),
                "source_prompt": widget.get("sourcePrompt") or widget.get("source_prompt"),
            }
            for widget in widgets
        ],
        "correlations": [
            f"{item.get('metric_a')} ↔ {item.get('metric_b')}: {item.get('value')}"
            for item in correlations
        ],
    }
    return report


def render_report_markdown(report: dict[str, Any]) -> str:
    """Render the executive report as markdown."""
    sections = [
        "# Executive Report",
        "",
        "## Executive Summary",
        report["executive_summary"],
        "",
        "## Key Insights",
    ]
    sections.extend(f"- {item}" for item in _as_lines(report.get("key_insights"), "No key insights available."))
    sections.extend(["", "## Anomalies"])
    sections.extend(f"- {item}" for item in _as_lines(report.get("anomalies"), "No anomalies flagged."))
    sections.extend(["", "## Root Causes"])
    sections.extend(f"- {item}" for item in _as_lines(report.get("root_causes"), "No root-cause findings available."))
    sections.extend(["", "## Recommendations"])
    sections.extend(f"- {item}" for item in _as_lines(report.get("recommendations"), "No recommendations available."))
    sections.extend(["", "## Forecast / Simulation"])
    sections.extend(f"- {item}" for item in _as_lines(report.get("forecast"), "No simulation results available."))
    sections.extend(["", "## Correlations"])
    sections.extend(f"- {item}" for item in _as_lines(report.get("correlations"), "No strong correlations detected."))
    sections.extend(["", "## Dashboard Widgets"])
    widget_lines = [
        f"- {item.get('title')} ({item.get('chart_type')}) from prompt: {item.get('source_prompt')}"
        for item in report.get("widgets", [])
        if item.get("title")
    ]
    sections.extend(widget_lines or ["- No widgets available."])
    return "\n".join(sections)


def render_report_pdf(report: dict[str, Any]) -> bytes:
    """Render the executive report as a PDF byte stream."""
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()
    story: list[Any] = [
        Paragraph("Executive Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph(report["executive_summary"], styles["BodyText"]),
        Spacer(1, 16),
    ]

    sections = [
        ("Key Insights", report.get("key_insights"), "No key insights available."),
        ("Anomalies", report.get("anomalies"), "No anomalies flagged."),
        ("Root Causes", report.get("root_causes"), "No root-cause findings available."),
        ("Recommendations", report.get("recommendations"), "No recommendations available."),
        ("Forecast / Simulation", report.get("forecast"), "No simulation results available."),
        ("Correlations", report.get("correlations"), "No strong correlations detected."),
    ]

    for title, values, empty_message in sections:
        story.append(Paragraph(title, styles["Heading2"]))
        items = _as_lines(values, empty_message)
        story.append(
            ListFlowable(
                [
                    ListItem(Paragraph(item, styles["BodyText"]), leftIndent=8)
                    for item in items
                ],
                bulletType="bullet",
                bulletColor=colors.HexColor("#1d4ed8"),
            )
        )
        story.append(Spacer(1, 12))

    widget_lines = [
        f"{item.get('title')} ({item.get('chart_type')})"
        for item in report.get("widgets", [])
        if item.get("title")
    ]
    story.append(Paragraph("Dashboard Widgets", styles["Heading2"]))
    story.append(
        ListFlowable(
            [
                ListItem(Paragraph(item, styles["BodyText"]), leftIndent=8)
                for item in _as_lines(widget_lines, "No widgets available.")
            ],
            bulletType="bullet",
            bulletColor=colors.HexColor("#1d4ed8"),
        )
    )

    document.build(story)
    return buffer.getvalue()


def generate_report_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Build report, markdown, and downloadable PDF payload."""
    report = build_executive_report(payload)
    markdown = render_report_markdown(report)
    pdf_bytes = render_report_pdf(report)
    return {
        "report": report,
        "markdown": markdown,
        "pdf_base64": base64.b64encode(pdf_bytes).decode("utf-8"),
        "filename": "executive-report.pdf",
    }
