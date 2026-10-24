
"""Load raw CSV data into PostgreSQL staging tables."""

from pathlib import Path
import re

import pandas as pd
from sqlalchemy import Engine, Text


def load_csv_to_staging(
    csv_path: str | Path,
    engine: Engine,
    table_name: str = "pnnl_atlas_records",
    schema: str = "staging",
) -> int:
    """Load a CSV into a PostgreSQL staging table without overwriting it.

    All source columns are stored as TEXT to preserve raw values.

    Returns:
        Number of imported rows.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If the table or schema name is invalid.
    """
    path = Path(csv_path)

    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
        raise ValueError(f"Invalid table name: {table_name}")

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", schema):
        raise ValueError(f"Invalid schema name: {schema}")

    dataframe = pd.read_csv(path, dtype=str, keep_default_na=False)

    if len(dataframe.columns) == 0:
        raise ValueError("The CSV contains no columns.")

    if dataframe.empty:
        raise ValueError("The CSV contains no data rows.")

    if not dataframe.columns.is_unique:
        raise ValueError("The CSV contains duplicate column names.")

    # Explicitly store every source column as text in the raw staging layer.
    column_types = {column: Text() for column in dataframe.columns}

    dataframe.to_sql(
        name=table_name,
        con=engine,
        schema=schema,
        if_exists="fail",
        index=False,
        chunksize=1000,
        dtype=column_types,
    )

    return len(dataframe)
