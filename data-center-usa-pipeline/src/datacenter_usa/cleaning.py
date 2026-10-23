"""Reusable data-cleaning helpers."""

from __future__ import annotations

import re
import unicodedata

import pandas as pd

LATITUDE_CANDIDATES = ("latitude", "lat", "y")
LONGITUDE_CANDIDATES = ("longitude", "lon", "lng", "x")
COORDINATE_CANDIDATES = ("coordinate", "coordinates", "coords")


def _normalize_column_name(column: object) -> str:
    """Convert a column label to lowercase ASCII snake_case."""
    name = unicodedata.normalize("NFKD", str(column).casefold())
    name = "".join(char for char in name if not unicodedata.combining(char))
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def normalize_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with normalized column labels; reject empty/colliding labels."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data doit être un pandas.DataFrame")

    result = data.copy()
    normalized = pd.Index([_normalize_column_name(c) for c in result.columns])

    if (normalized == "").any():
        raise ValueError("La normalisation produit un nom de colonne vide.")

    if normalized.has_duplicates:
        duplicates = normalized[normalized.duplicated(keep=False)].unique().tolist()
        raise ValueError(
            "La normalisation produit des noms de colonnes dupliqués : "
            f"{duplicates}"
        )

    result.columns = normalized
    return result


def extract_coordinates(data: pd.DataFrame) -> pd.DataFrame:
    """Add numeric ``latitude`` and ``longitude`` columns to a copy of a DataFrame."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data doit être un pandas.DataFrame")

    result = data.copy()
    lat_cols = [c for c in LATITUDE_CANDIDATES if c in result.columns]
    lon_cols = [c for c in LONGITUDE_CANDIDATES if c in result.columns]

    if lat_cols and lon_cols:
        result["latitude"] = pd.to_numeric(result[lat_cols[0]], errors="coerce")
        result["longitude"] = pd.to_numeric(result[lon_cols[0]], errors="coerce")
        return result

    normalized_lookup = {str(c).strip().lower(): c for c in result.columns}
    combined_col = next(
        (normalized_lookup[c] for c in COORDINATE_CANDIDATES if c in normalized_lookup),
        None,
    )
    if combined_col is None:
        combined_col = next(
            (c for c in result.columns if "coordinate" in str(c).lower()),
            None,
        )
    if combined_col is None:
        raise ValueError(
            "Impossible de trouver les coordonnées. Aucune paire latitude/longitude "
            "ni colonne de coordonnées n'a été détectée."
        )

    def parse_pair(value: object) -> tuple[float, float] | tuple[float, float]:
        if pd.isna(value):
            return float("nan"), float("nan")
        numbers = re.findall(r"-?\d+(?:\.\d+)?", str(value))
        if len(numbers) < 2:
            return float("nan"), float("nan")
        return float(numbers[0]), float(numbers[1])

    pairs = result[combined_col].map(parse_pair)
    result[["latitude", "longitude"]] = pd.DataFrame(
        pairs.tolist(), index=result.index, columns=["latitude", "longitude"]
    )
    return result


def valid_coordinate_mask(data: pd.DataFrame) -> pd.Series:
    """Return True for rows with numeric latitude/longitude within global bounds."""
    required = {"latitude", "longitude"}
    if not required.issubset(data.columns):
        missing = sorted(required - set(data.columns))
        raise ValueError(f"Colonnes requises pour les coordonnées absentes : {missing}")

    latitude = pd.to_numeric(data["latitude"], errors="coerce")
    longitude = pd.to_numeric(data["longitude"], errors="coerce")
    return latitude.between(-90, 90) & longitude.between(-180, 180)


def filter_valid_coordinates(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy containing only rows with valid geographic coordinates."""
    return data.loc[valid_coordinate_mask(data)].copy()
