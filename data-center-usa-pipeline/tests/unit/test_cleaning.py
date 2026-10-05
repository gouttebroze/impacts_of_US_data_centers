import pandas as pd
import pytest

from src.datacenter_usa.cleaning import (
    extract_coordinates,
    filter_valid_coordinates,
    valid_coordinate_mask,
)


def test_extract_coordinates_from_lat_lon_columns():
    df = pd.DataFrame(
        {
            "name": ["A", "B"],
            "lat": [40.5, 34.1],
            "lon": ["-74.5", "-118.2"],
        }
    )

    result = extract_coordinates(df)

    assert result["latitude"].tolist() == [40.5, 34.1]
    assert result["longitude"].tolist() == [-74.5, -118.2]
    assert "latitude" not in df.columns
    assert "longitude" not in df.columns


def test_extract_coordinates_from_combined_coordinates():
    df = pd.DataFrame(
        {
            "coordinates": ["40.54426, -74.49652", "35.04994, -106.54282"]
        }
    )

    result = extract_coordinates(df)

    assert result.loc[0, "latitude"] == pytest.approx(40.54426)
    assert result.loc[0, "longitude"] == pytest.approx(-74.49652)
    assert result.loc[1, "latitude"] == pytest.approx(35.04994)
    assert result.loc[1, "longitude"] == pytest.approx(-106.54282)


def test_extract_coordinates_sets_nan_for_unparseable_values():
    df = pd.DataFrame({"coordinates": ["not a coordinate", None]})

    result = extract_coordinates(df)

    assert result["latitude"].isna().all()
    assert result["longitude"].isna().all()


def test_extract_coordinates_raises_when_coordinates_are_missing():
    df = pd.DataFrame({"name": ["A"]})

    with pytest.raises(ValueError, match="coordonnées"):
        extract_coordinates(df)


def test_extract_coordinates_requires_dataframe():
    with pytest.raises(TypeError, match="DataFrame"):
        extract_coordinates([40.5, -74.5])


def test_valid_coordinate_mask_rejects_out_of_range_values():
    df = pd.DataFrame(
        {
            "latitude": [40, 91, 35, None],
            "longitude": [-74, -74, 181, -118],
        }
    )

    result = valid_coordinate_mask(df)

    assert result.tolist() == [True, False, False, False]


def test_filter_valid_coordinates_keeps_only_valid_rows():
    df = pd.DataFrame(
        {
            "name": ["valid", "invalid_lat", "invalid_lon"],
            "latitude": [40, 91, 35],
            "longitude": [-74, -74, 181],
        }
    )

    result = filter_valid_coordinates(df)

    assert result["name"].tolist() == ["valid"]
