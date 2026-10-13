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
        ("E\u0301tat", "etat"),  # Accent décomposé en Unicode
        ("Straße", "strasse"),
        ("Data—Center", "data_center"),
    ],
)
def test_normalize_column_names(original, expected):
    df = pd.DataFrame([[1]], columns=[original])

    result = normalize_columns(df)

    assert result.columns.tolist() == [expected]

# Vérifier le cas des doublons
# tester que la translittération ne crée pas silencieusement deux colonnes identiques
def test_normalize_columns_detects_accent_collision():
    df = pd.DataFrame(
        [[1, 2]],
        columns=["État", "Etat"],
    )

    with pytest.raises(ValueError, match="dupliqués"):
        normalize_columns(df)

def test_normalize_columns():
    df = pd.DataFrame(
        [[1, 2, 3]],
        columns=[
            " Data Center Name ",
            "State",
            "Latitude (°)",
        ],
    )

    result = normalize_columns(df)

    assert result.columns.tolist() == [
        "data_center_name",
        "state",
        "latitude",
    ]


def test_normalize_columns_does_not_modify_original():
    df = pd.DataFrame([[1]], columns=[" State "])

    result = normalize_columns(df)

    assert df.columns.tolist() == [" State "]
    assert result.columns.tolist() == ["state"]


def test_normalize_columns_rejects_duplicates():
    df = pd.DataFrame(
        [[1, 2]],
        columns=["State", " state "],
    )

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
