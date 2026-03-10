def local_follow_up_prompts(user_prompt: str, rows: list[dict], dataset: str) -> list[str]:
    sample = rows[0] if rows else {}
    numeric_keys = [
        key for key, value in sample.items()
        if isinstance(value, (int, float)) and key.lower() not in {"id", "index"}
    ]
    dimension_keys = [
        key for key in sample.keys()
        if key not in numeric_keys and key.lower() not in {"id", "index"}
    ]
    prompts = []

    if dimension_keys and numeric_keys:
        prompts.append(f"Show {numeric_keys[0]} by {dimension_keys[0]} as a ranked comparison")
    if "date" in " ".join(sample.keys()).lower() and numeric_keys:
        prompts.append(f"Show the trend of {numeric_keys[0]} over time")
    if dimension_keys and len(dimension_keys) > 1 and numeric_keys:
        prompts.append(f"Filter {numeric_keys[0]} by {dimension_keys[-1]}")

    prompts.append(f"What are the key columns and metrics available in {dataset}?")
    prompts.append(f"What is the best and worst performing segment in this result?")
    return prompts[:4]


def generate_follow_up_prompts(user_prompt: str, rows: list[dict], dataset: str, context: str = "") -> list[str]:
    return local_follow_up_prompts(user_prompt, rows, dataset)
