"""Natural-language chart configuration editing."""

from __future__ import annotations

import copy


def apply_chart_edit(widget: dict, edit_prompt: str) -> dict:
    """Interpret simple chart edit instructions and return updated widget config."""
    updated = copy.deepcopy(widget)
    prompt = edit_prompt.lower()
    data = updated.get("data", [])
    metadata = updated.get("metadata") or updated.get("chart_metadata") or {}
    y_axis = metadata.get("y_axis")
    x_axis = metadata.get("x_axis")

    if "stacked bar" in prompt or "make this a bar" in prompt:
        updated["chart_type"] = "bar"
        updated["chart_metadata"] = {**metadata, "stacked": True}
    elif "line" in prompt:
        updated["chart_type"] = "line"
    elif "pie" in prompt:
        updated["chart_type"] = "pie"
    elif "table" in prompt:
        updated["chart_type"] = "table"
    elif "scatter" in prompt:
        updated["chart_type"] = "scatter"

    if "sort" in prompt and y_axis and data:
        reverse = "desc" in prompt or "descending" in prompt
        updated["data"] = sorted(data, key=lambda item: item.get(y_axis, 0) or 0, reverse=reverse)

    if "top 5" in prompt and data and y_axis:
        ordered = sorted(data, key=lambda item: item.get(y_axis, 0) or 0, reverse=True)
        updated["data"] = ordered[:5]

    if "cumulative" in prompt and data and y_axis:
        running_total = 0
        cumulative = []
        for row in data:
            running_total += float(row.get(y_axis, 0) or 0)
            next_row = dict(row)
            next_row[y_axis] = running_total
            cumulative.append(next_row)
        updated["data"] = cumulative

    if "filter to" in prompt and x_axis and data:
        tokens = prompt.split("filter to", 1)[-1].strip()
        filtered = [row for row in data if tokens.lower() in str(row.get(x_axis, "")).lower()]
        if filtered:
            updated["data"] = filtered

    updated["metadata"] = updated.get("chart_metadata", metadata)
    return updated
