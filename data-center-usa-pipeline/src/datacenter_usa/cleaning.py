"""Cleaning and validation helpers for the US data center project."""

from __future__ import annotations

import re

import pandas as pd


LATITUDE_CANDIDATES = ("latitude", "lat", "y")
LONGITUDE_CANDIDATES = ("longitude", "lon", "lng", "x")
COORDINATE_CANDIDATES = ("coordinate", "coordinates", "coords")


def _find_coordinate_column(columns: pd.Index) -> str | None:
    """Return the first column that looks like a combined coordinate field."""
    normalized = {str(column).strip().lower(): column for column in columns}

    for candidate in COORDINATE_CANDIDATES:
        if candidate in normalized:
            return normalized[candidate]

    for column in columns:
        name = str(column).strip().lower()
        if "coordinate" in name:
            return column

    return None


def _parse_coordinate_pair(value: object) -> tuple[float, float] | tuple[None, None]:
    """Extract two decimal numbers from a combined coordinate value."""
    if pd.isna(value):
        return None, None

    numbers = re.findall(r"-?\d+(?:\.\d+)?", str(value))

    if len(numbers) < 2:
        return None, None

    return float(numbers[0]), float(numbers[1])


def extract_coordinates(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of *data* with numeric ``latitude`` and ``longitude`` columns.

    The function first looks for separate latitude/longitude columns. If they are
    unavailable, it looks for a combined coordinate column such as ``coordinates``
    or ``coords``.

    Parameters
    ----------
    data:
        Input data frame.

    Returns
    -------
    pandas.DataFrame
        A copy of the input with normalized ``latitude`` and ``longitude`` columns.

    Raises
    ------
    TypeError
        If ``data`` is not a pandas DataFrame.
    ValueError
        If no usable coordinate columns can be detected.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data doit être un pandas.DataFrame")

    result = data.copy()

    lat_columns = [c for c in LATITUDE_CANDIDATES if c in result.columns]
    lon_columns = [c for c in LONGITUDE_CANDIDATES if c in result.columns]

    if lat_columns and lon_columns:
        result["latitude"] = pd.to_numeric(result[lat_columns[0]], errors="coerce")
        result["longitude"] = pd.to_numeric(result[lon_columns[0]], errors="coerce")
        return result

    coordinate_column = _find_coordinate_column(result.columns)
    if coordinate_column is None:
        raise ValueError(
            "Impossible de trouver les coordonnées. "
            "Aucune paire latitude/longitude ni colonne de coordonnées n'a été détectée."
        )

    pairs = result[coordinate_column].map(_parse_coordinate_pair)
    result[["latitude", "longitude"]] = pd.DataFrame(
        pairs.tolist(), index=result.index, columns=["latitude", "longitude"]
    )

    return result


def valid_coordinate_mask(data: pd.DataFrame) -> pd.Series:
    """Return a boolean mask for rows with valid geographic coordinates."""
    if not {"latitude", "longitude"}.issubset(data.columns):
        raise ValueError("Les colonnes 'latitude' et 'longitude' sont requises.")

    latitude = pd.to_numeric(data["latitude"], errors="coerce")
    longitude = pd.to_numeric(data["longitude"], errors="coerce")

    return latitude.between(-90, 90) & longitude.between(-180, 180)


def filter_valid_coordinates(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy containing only rows with valid latitude/longitude values."""
    mask = valid_coordinate_mask(data)
    return data.loc[mask].copy()
