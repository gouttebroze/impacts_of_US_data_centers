"""Composable local ingestion, cleaning, and data-quality pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from datacenter_usa.cleaning import (
    extract_coordinates,
    normalize_columns,
    valid_coordinate_mask,
)
from datacenter_usa.ingestion import load_csv
from datacenter_usa.quality import (
    duplicate_count,
    duplicate_key_count,
    quality_report,
    validate_required_columns,
)

PNNL_REQUIRED_COLUMNS = (
    "id", "layer", "state", "state_abb", "county", "operator", "name", "sqft", "lat", "lon"
)


@dataclass(frozen=True)
class PipelineResult:
    """Outputs from a local CSV ingestion and validation run."""

    data: pd.DataFrame
    quality_report: pd.DataFrame
    summary: dict[str, Any]


def prepare_dataset(
    source: str | Path,
    *,
    required_columns: tuple[str, ...] | list[str] = PNNL_REQUIRED_COLUMNS,
    coordinate_policy: str = "drop",
    read_csv_kwargs: dict[str, Any] | None = None,
) -> PipelineResult:
    """Load, normalize, validate, and prepare a CSV for analysis.

    ``coordinate_policy`` is either ``"drop"`` (remove rows with invalid numeric
    coordinates from the analysis dataset) or ``"keep"`` (retain them but count
    them in the summary). The quality report is computed before this filtering.
    """
    if coordinate_policy not in {"drop", "keep"}:
        raise ValueError("coordinate_policy doit être 'drop' ou 'keep'.")

    df_raw = load_csv(source, **(read_csv_kwargs or {}))
    df = normalize_columns(df_raw)
    validate_required_columns(df, required_columns)
    df = extract_coordinates(df)

    coord_mask = valid_coordinate_mask(df)
    report = quality_report(df)
    exact_duplicates = duplicate_count(df)
    duplicate_ids = duplicate_key_count(df, "id") if "id" in df.columns else None

    summary: dict[str, Any] = {
        "source": str(source),
        "rows_loaded": int(len(df_raw)),
        "columns_loaded": int(len(df_raw.columns)),
        "columns_after_normalization": int(len(df.columns)),
        "exact_duplicate_rows": exact_duplicates,
        "duplicate_ids": duplicate_ids,
        "states_observed": int(df["state"].nunique(dropna=True)) if "state" in df else None,
        "valid_coordinate_rows": int(coord_mask.sum()),
        "invalid_coordinate_rows": int((~coord_mask).sum()),
        "coordinate_policy": coordinate_policy,
        "rows_returned": int(coord_mask.sum()) if coordinate_policy == "drop" else int(len(df)),
    }

    output_data = df.loc[coord_mask].copy() if coordinate_policy == "drop" else df.copy()
    return PipelineResult(data=output_data, quality_report=report, summary=summary)
