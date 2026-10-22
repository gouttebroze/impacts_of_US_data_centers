import pandas as pd
import pytest

from datacenter_usa.pipeline import prepare_dataset


@pytest.fixture
def pnnl_like_csv(tmp_path):
    path = tmp_path / "pnnl.csv"
    pd.DataFrame(
        {
            "ID": [1, 2, 3],
            "Layer": ["building", "building", "building"],
            "State": ["Virginia", "Texas", "Ohio"],
            "State Abb": ["VA", "TX", "OH"],
            "County": ["A", "B", "C"],
            "Operator": [None, "Operator B", "Operator C"],
            "Name": ["Site A", "Site B", "Site C"],
            "Sqft": [1200, 900, 800],
            "Lat": [39.0, 32.0, 100.0],
            "Lon": [-77.0, -96.0, -82.0],
        }
    ).to_csv(path, index=False)
    return path


def test_prepare_dataset_normalizes_validates_and_drops_bad_coordinates(pnnl_like_csv):
    result = prepare_dataset(pnnl_like_csv)
    assert len(result.data) == 2
    assert result.data.columns.tolist() == [
        "id", "layer", "state", "state_abb", "county", "operator", "name",
        "sqft", "lat", "lon", "latitude", "longitude",
    ]
    assert result.summary["rows_loaded"] == 3
    assert result.summary["valid_coordinate_rows"] == 2
    assert result.summary["invalid_coordinate_rows"] == 1
    assert result.summary["rows_returned"] == 2
    # Quality report is computed before invalid coordinate rows are filtered.
    assert result.quality_report.loc["state", "unique_n"] == 3


def test_prepare_dataset_can_keep_invalid_coordinate_rows(pnnl_like_csv):
    result = prepare_dataset(pnnl_like_csv, coordinate_policy="keep")
    assert len(result.data) == 3
    assert result.summary["invalid_coordinate_rows"] == 1


def test_prepare_dataset_missing_required_column_raises(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"ID": [1], "State": ["Ohio"]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="absentes"):
        prepare_dataset(path)


def test_prepare_dataset_invalid_policy_raises(pnnl_like_csv):
    with pytest.raises(ValueError, match="coordinate_policy"):
        prepare_dataset(pnnl_like_csv, coordinate_policy="ignore")
