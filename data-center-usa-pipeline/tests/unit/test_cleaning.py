import pandas as pd
import pytest

from datacenter_usa.cleaning import (
    extract_coordinates,
    filter_valid_coordinates,
    normalize_columns,
    valid_coordinate_mask,
)


@pytest.mark.parametrize(
    "original, expected",
    [
        ("État", "etat"),
        ("São Paulo", "sao_paulo"),
        ("Crème brûlée", "creme_brulee"),
        ("Latitude (°)", "latitude"),
        ("County, State", "county_state"),
        (" Data Center Name ", "data_center_name"),
        ("E\u0301tat", "etat"),
        ("Straße", "strasse"),
        ("Data—Center", "data_center"),
    ],
)
def test_normalize_column_names(original, expected):
    df = pd.DataFrame([[1]], columns=[original])
    result = normalize_columns(df)
    assert result.columns.tolist() == [expected]


def test_normalize_columns_does_not_modify_original():
    df = pd.DataFrame([[1]], columns=[" State "])
    result = normalize_columns(df)
    assert df.columns.tolist() == [" State "]
    assert result.columns.tolist() == ["state"]


def test_normalize_columns_detects_accent_collision():
    df = pd.DataFrame([[1, 2]], columns=["État", "Etat"])
    with pytest.raises(ValueError, match="dupliqués"):
        normalize_columns(df)


def test_normalize_columns_rejects_empty_names():
    df = pd.DataFrame([[1]], columns=["!!!"])
    with pytest.raises(ValueError, match="vide"):
        normalize_columns(df)


def test_normalize_columns_requires_dataframe():
    with pytest.raises(TypeError, match="DataFrame"):
        normalize_columns(["State"])


def test_extract_coordinates_from_lat_lon_columns():
    df = pd.DataFrame({"name": ["A", "B"], "lat": [40.5, 34.1], "lon": ["-74.5", "-118.2"]})
    result = extract_coordinates(df)
    assert result["latitude"].tolist() == [40.5, 34.1]
    assert result["longitude"].tolist() == [-74.5, -118.2]
    assert "latitude" not in df.columns


def test_extract_coordinates_from_combined_coordinates():
    df = pd.DataFrame({"coordinates": ["40.54426, -74.49652", "35.04994, -106.54282"]})
    result = extract_coordinates(df)
    assert result.loc[0, "latitude"] == pytest.approx(40.54426)
    assert result.loc[0, "longitude"] == pytest.approx(-74.49652)
    assert result.loc[1, "latitude"] == pytest.approx(35.04994)
    assert result.loc[1, "longitude"] == pytest.approx(-106.54282)


def test_extract_coordinates_returns_nan_for_unparseable_values():
    result = extract_coordinates(pd.DataFrame({"coordinates": ["not a coordinate", None]}))
    assert result["latitude"].isna().all()
    assert result["longitude"].isna().all()


def test_extract_coordinates_raises_when_coordinates_are_missing():
    with pytest.raises(ValueError, match="coordonnées"):
        extract_coordinates(pd.DataFrame({"name": ["A"]}))


def test_extract_coordinates_requires_dataframe():
    with pytest.raises(TypeError, match="DataFrame"):
        extract_coordinates([40.5, -74.5])


def test_valid_coordinate_mask_rejects_out_of_range_values():
    df = pd.DataFrame({"latitude": [40, 91, 35, None], "longitude": [-74, -74, 181, -118]})
    assert valid_coordinate_mask(df).tolist() == [True, False, False, False]


def test_valid_coordinate_mask_requires_both_columns():
    with pytest.raises(ValueError, match="requises"):
        valid_coordinate_mask(pd.DataFrame({"latitude": [40]}))


def test_filter_valid_coordinates_keeps_only_valid_rows():
    df = pd.DataFrame({"name": ["valid", "bad_lat", "bad_lon"], "latitude": [40, 91, 35], "longitude": [-74, -74, 181]})
    result = filter_valid_coordinates(df)
    assert result["name"].tolist() == ["valid"]
    assert len(df) == 3
