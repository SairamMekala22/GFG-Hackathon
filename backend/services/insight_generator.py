def choose_primary_metric(sample: dict) -> str:
    numeric_keys = [key for key, value in sample.items() if isinstance(value, (int, float))]
    preferred = next(
        (
            key for key in numeric_keys
            if any(token in key.lower() for token in ("revenue", "sales", "conversion", "lead", "click", "impression", "roi", "score", "cost", "customer"))
        ),
        None,
    )
    if preferred:
        return preferred
    non_id = [key for key in numeric_keys if key.lower() not in {"id", "index"}]
    return non_id[0] if non_id else (numeric_keys[0] if numeric_keys else "")


def local_insight(rows, chart_metadata):
    if not rows:
        return "No records were returned for this query, so there is no business insight to summarize."

    x_axis = chart_metadata.get("x_axis")
    y_axis = chart_metadata.get("y_axis") or choose_primary_metric(rows[0])

    if y_axis and all(isinstance(row.get(y_axis), (int, float)) for row in rows):
        peak = max(rows, key=lambda row: row[y_axis])
        trough = min(rows, key=lambda row: row[y_axis])
        if x_axis and any(token in x_axis.lower() for token in ("date", "month", "time", "year")) and len(rows) > 1:
            first = rows[0]
            last = rows[-1]
            change = last[y_axis] - first[y_axis]
            direction = "increased" if change >= 0 else "decreased"
            pct = abs(change / first[y_axis] * 100) if first[y_axis] else 0
            return (
                f"{y_axis.replace('_', ' ').title()} {direction} by {pct:.1f}% from {first.get(x_axis)} to {last.get(x_axis)}. "
                f"The peak occurs at {peak.get(x_axis, 'the strongest point')} with {format_metric_value(peak[y_axis])}, while the low is {format_metric_value(trough[y_axis])}."
            )
        return (
            f"{y_axis.replace('_', ' ').title()} ranges from {format_metric_value(trough[y_axis])} to {format_metric_value(peak[y_axis])}. "
            f"The best-performing segment is {peak.get(x_axis, 'the leading segment')}, while the weakest is {trough.get(x_axis, 'the trailing segment')}."
        )

    return "The returned dataset is ready for exploration. Use follow-up prompts to refine the breakdown or isolate a segment."


def generate_insight(rows, user_prompt: str):
    metadata = {
        "x_axis": next((key for key, value in (rows[0] if rows else {}).items() if not isinstance(value, (int, float))), ""),
        "y_axis": choose_primary_metric(rows[0]) if rows else "",
    }
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
        primary_metric = choose_primary_metric(sample)
        total = sum(float(row.get(primary_metric, 0) or 0) for row in rows)
        cards.append(
            {
                "title": f"Total {primary_metric.replace('_', ' ')}",
                "value": format_metric_value(total),
                "summary": f"Aggregated across {len(rows)} returned records.",
            }
        )

        if dimension_keys:
            dimension = next((key for key in dimension_keys if key.lower() not in {"date"}), dimension_keys[0])
            leader = max(rows, key=lambda row: float(row.get(primary_metric, 0) or 0))
            non_null_rows = [row for row in rows if row.get(dimension) not in (None, "", "None")]
            trailer = min(non_null_rows or rows, key=lambda row: float(row.get(primary_metric, 0) or 0))
            cards.append(
                {
                    "title": "Best case",
                    "value": str(leader.get(dimension, "N/A")),
                    "summary": f"Led with {format_metric_value(leader.get(primary_metric, 0))} {primary_metric.replace('_', ' ')}.",
                }
            )
            cards.append(
                {
                    "title": "Worst case",
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
    return local_summary_cards(rows, user_prompt)
