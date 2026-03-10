import json

from services.gemini_service import gemini_service


def local_insight(rows, chart_metadata):
    if not rows:
        return "No records were returned for this query, so there is no business insight to summarize."

    x_axis = chart_metadata.get("x_axis")
    y_axis = chart_metadata.get("y_axis")

    if y_axis and all(isinstance(row.get(y_axis), (int, float)) for row in rows):
        values = [row[y_axis] for row in rows]
        peak = max(rows, key=lambda row: row[y_axis])
        trough = min(rows, key=lambda row: row[y_axis])
        return (
            f"{y_axis.title()} ranges from {trough[y_axis]:,.0f} to {peak[y_axis]:,.0f}. "
            f"The strongest result appears at {peak.get(x_axis, 'the leading segment')}, while "
            f"the weakest result appears at {trough.get(x_axis, 'the trailing segment')}."
        )

    return "The returned dataset is ready for exploration. Use follow-up prompts to refine the breakdown or isolate a segment."


def generate_insight(rows, user_prompt: str):
    chart_data = json.dumps(rows[:30], default=str)
    if not gemini_service.is_configured():
        metadata = {"x_axis": next(iter(rows[0].keys()), ""), "y_axis": list(rows[0].keys())[-1] if rows else ""}
        return local_insight(rows, metadata)

    prompt = f"""
You are a business analyst.

User prompt:
{user_prompt}

Data:
{chart_data}

Generate a 2-3 sentence executive summary highlighting trends, anomalies, or key insights.
"""
    try:
        return gemini_service.generate_text(prompt)
    except Exception:  # noqa: BLE001
        metadata = {"x_axis": next(iter(rows[0].keys()), ""), "y_axis": list(rows[0].keys())[-1] if rows else ""}
        return local_insight(rows, metadata)


def format_metric_value(value):
    if isinstance(value, (int, float)):
        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        if abs(value) >= 1_000:
            return f"{value:,.0f}"
        if isinstance(value, float):
            return f"{value:.2f}"
        return str(value)
    return str(value)


def local_summary_cards(rows, user_prompt: str):
    if not rows:
        return []

    sample = rows[0]
    numeric_keys = [key for key, value in sample.items() if isinstance(value, (int, float))]
    dimension_keys = [key for key in sample.keys() if key not in numeric_keys]
    cards = []

    if numeric_keys:
        primary_metric = numeric_keys[0]
        total = sum(float(row.get(primary_metric, 0) or 0) for row in rows)
        cards.append(
            {
                "title": f"Total {primary_metric.replace('_', ' ')}",
                "value": format_metric_value(total),
                "summary": f"Aggregated across {len(rows)} returned records.",
            }
        )

        if dimension_keys:
            dimension = dimension_keys[0]
            leader = max(rows, key=lambda row: float(row.get(primary_metric, 0) or 0))
            trailer = min(rows, key=lambda row: float(row.get(primary_metric, 0) or 0))
            cards.append(
                {
                    "title": f"Top {dimension.replace('_', ' ')}",
                    "value": str(leader.get(dimension, "N/A")),
                    "summary": f"Led with {format_metric_value(leader.get(primary_metric, 0))} {primary_metric.replace('_', ' ')}.",
                }
            )
            cards.append(
                {
                    "title": f"Lowest {dimension.replace('_', ' ')}",
                    "value": str(trailer.get(dimension, "N/A")),
                    "summary": f"Trailing segment at {format_metric_value(trailer.get(primary_metric, 0))}.",
                }
            )

        if len(rows) > 1:
            first_value = float(rows[0].get(primary_metric, 0) or 0)
            last_value = float(rows[-1].get(primary_metric, 0) or 0)
            delta = last_value - first_value
            direction = "Up" if delta >= 0 else "Down"
            pct = (delta / first_value * 100) if first_value else 0
            cards.append(
                {
                    "title": f"{primary_metric.replace('_', ' ').title()} trend",
                    "value": f"{direction} {abs(pct):.1f}%",
                    "summary": f"Moved from {format_metric_value(first_value)} to {format_metric_value(last_value)} across the sequence.",
                }
            )

    if not cards:
        cards.append(
            {
                "title": "Dataset overview",
                "value": f"{len(rows)} rows",
                "summary": f"The prompt '{user_prompt}' returned records ready for review.",
            }
        )

    return cards[:5]


def generate_summary_cards(rows, user_prompt: str):
    if not rows:
        return []

    if not gemini_service.is_configured():
        return local_summary_cards(rows, user_prompt)

    prompt = f"""
You are an executive analytics assistant.

User prompt:
{user_prompt}

Data:
{json.dumps(rows[:40], default=str)}

Create 3 to 5 relevant summary cards for this result.
Return JSON only in this exact format:
{{
  "cards": [
    {{
      "title": "short label",
      "value": "headline number or takeaway",
      "summary": "one short business-relevant sentence"
    }}
  ]
}}

Requirements:
- Make the cards specific to the actual result data.
- Prefer totals, leaders, growth, changes, coverage, ratios, or anomalies when supported.
- Avoid generic filler.
"""
    try:
        raw = gemini_service.generate_json(prompt)
        cards = raw.get("cards", [])
        normalized_cards = []
        for card in cards:
          if card.get("title") and card.get("value") and card.get("summary"):
              normalized_cards.append(
                  {
                      "title": str(card["title"]).strip()[:80],
                      "value": str(card["value"]).strip()[:160],
                      "summary": str(card["summary"]).strip()[:220],
                  }
              )
        return normalized_cards[:5] or local_summary_cards(rows, user_prompt)
    except Exception:  # noqa: BLE001
        return local_summary_cards(rows, user_prompt)
