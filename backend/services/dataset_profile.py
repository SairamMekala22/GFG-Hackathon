from sqlalchemy import inspect, text


def get_dataset_profile(engine, table_name: str) -> dict:
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    column_names = [column["name"] for column in columns]

    with engine.connect() as connection:
        row_count = connection.execute(
            text(f"SELECT COUNT(*) AS row_count FROM {table_name}")
        ).scalar_one()
        sample_rows = [
            dict(row._mapping)
            for row in connection.execute(text(f"SELECT * FROM {table_name} LIMIT 5"))
        ]

    return {
        "table_name": table_name,
        "row_count": int(row_count),
        "columns": [
            {
                "name": column["name"],
                "type": str(column.get("type", "unknown")),
            }
            for column in columns
        ],
        "sample_rows": sample_rows,
        "has_date_column": any(
            token in column_name.lower()
            for column_name in column_names
            for token in ("date", "time", "month", "year")
        ),
        "numeric_like_columns": [
            column_name
            for column_name in column_names
            if any(token in column_name.lower() for token in ("revenue", "sales", "amount", "count", "value", "cost", "price", "spend"))
        ],
    }
