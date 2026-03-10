from collections import Counter


def infer_chart_type(rows):
    if not rows:
        return {"chart_type": "bar", "x_axis": "", "y_axis": ""}

    sample = rows[0]
    keys = list(sample.keys())
    numeric_keys = [key for key, value in sample.items() if isinstance(value, (int, float))]
    text_keys = [key for key in keys if key not in numeric_keys]

    x_axis = text_keys[0] if text_keys else keys[0]
    y_axis = numeric_keys[0] if numeric_keys else keys[-1]

    if x_axis and any(token in x_axis.lower() for token in ["date", "month", "year", "time"]):
        chart_type = "line"
    elif any("percent" in key.lower() or "share" in key.lower() for key in keys):
        chart_type = "pie"
    elif len(numeric_keys) > 1:
        chart_type = "scatter"
    elif len(set(row.get(x_axis) for row in rows if x_axis in row)) <= 8:
        chart_type = "bar"
    else:
        chart_type = "bar"

    if chart_type == "bar" and len(numeric_keys) == 1:
        values = [row[y_axis] for row in rows if isinstance(row.get(y_axis), (int, float))]
        if values:
            repeated = Counter(int(value) // 10 for value in values)
            if len(repeated) < len(values) / 2 and len(values) > 12:
                chart_type = "histogram"

    if chart_type == "histogram":
        chart_type = "bar"

    return {
        "chart_type": chart_type,
        "x_axis": x_axis,
        "y_axis": y_axis,
    }
