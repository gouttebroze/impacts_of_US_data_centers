"""Reusable data-quality checks and reports."""

from __future__ import annotations

import pandas as pd


def quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Build one quality-report row per column."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df doit être un pandas.DataFrame")

    return pd.DataFrame(
        {
            "dtype": df.dtypes.astype(str),
            "missing_n": df.isna().sum().astype(int),
            "missing_pct": (df.isna().mean() * 100).round(2),
            "unique_n": df.nunique(dropna=True).astype(int),
        }
    ).sort_values("missing_pct", ascending=False)


def duplicate_count(df: pd.DataFrame) -> int:
    """Count exact duplicate rows."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df doit être un pandas.DataFrame")
    return int(df.duplicated().sum())


def missing_rate(series: pd.Series) -> float:
    """Return the missing-value share from 0 to 1; empty input returns 0."""
    if not isinstance(series, pd.Series):
        raise TypeError("series doit être un pandas.Series")
    return 0.0 if series.empty else float(series.isna().mean())


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: list[str] | tuple[str, ...] | set[str],
) -> None:
    """Raise ValueError if any required columns are missing."""
    missing = sorted(set(required_columns) - set(df.columns))
    if missing:
        raise ValueError(f"Colonnes obligatoires absentes : {missing}")


def duplicate_key_count(df: pd.DataFrame, key: str) -> int:
    """Count rows whose key is duplicated, excluding null keys."""
    if key not in df.columns:
        raise ValueError(f"Colonne clé absente : {key}")
    return int(df.loc[df[key].notna(), key].duplicated().sum())
