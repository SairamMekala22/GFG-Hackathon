import io
import re
from pathlib import Path

import pandas as pd

from database.db import engine

ALLOWED_EXTENSIONS = {".csv"}
SUPPORTED_ENCODINGS = ("utf-8-sig", "utf-8", "cp1252", "latin-1")


def sanitize_table_name(filename: str) -> str:
    stem = Path(filename).stem.lower()
    table_name = re.sub(r"[^a-z0-9_]+", "_", stem).strip("_")
    return table_name[:48] or "uploaded_dataset"


def validate_csv_file(filename: str) -> None:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only CSV uploads are supported.")


def read_csv_with_fallbacks(file_storage):
    raw_bytes = file_storage.read()
    if not raw_bytes:
        raise ValueError("The uploaded CSV is empty.")

    if raw_bytes.startswith(b"bplist00"):
        raise ValueError("This file is not a valid CSV. It appears to be an Apple plist/web archive export.")

    last_error = None
    for encoding in SUPPORTED_ENCODINGS:
        try:
            text = raw_bytes.decode(encoding)
            stripped = text.lstrip()
            if stripped.startswith("<!DOCTYPE html") or stripped.startswith("<html"):
                raise ValueError("This file is HTML, not a CSV. Export the data again as CSV and retry.")
            return pd.read_csv(io.StringIO(text)), encoding
        except UnicodeDecodeError as error:
            last_error = error
        except pd.errors.ParserError as error:
            last_error = error
        except ValueError:
            raise

    raise ValueError(
        "Unable to read this CSV encoding. Save the file as UTF-8 CSV and try again."
    ) from last_error


def validate_dataframe(dataframe: pd.DataFrame) -> None:
    if dataframe.empty:
        raise ValueError("The uploaded CSV is empty.")

    suspicious_columns = [str(column).lower() for column in dataframe.columns]
    if len(suspicious_columns) == 1 and (
        suspicious_columns[0].startswith("bplist00") or "webmainresource" in suspicious_columns[0]
    ):
        raise ValueError("The uploaded file is not a usable CSV table. Export the source data as a real CSV with rows and columns.")

    non_empty_columns = [column for column in dataframe.columns if str(column).strip()]
    if not non_empty_columns:
        raise ValueError("The uploaded CSV does not contain valid column headers.")


def load_csv_to_sqlite(file_storage):
    validate_csv_file(file_storage.filename)
    table_name = sanitize_table_name(file_storage.filename)
    dataframe, encoding = read_csv_with_fallbacks(file_storage)
    validate_dataframe(dataframe)

    dataframe.columns = [re.sub(r"[^a-zA-Z0-9_]+", "_", column).strip("_").lower() for column in dataframe.columns]
    dataframe.to_sql(table_name, engine, if_exists="replace", index=False)
    return {
        "table_name": table_name,
        "columns": dataframe.columns.tolist(),
        "encoding": encoding,
        "row_count": int(len(dataframe)),
    }
