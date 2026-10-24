import pandas as pd
import pytest

from datacenter_usa.database import prepare_data_centers_for_db


def sample_data():
    return pd.DataFrame(
        {
            "id": ["site-1", "site-2"],
            "layer": ["existing", "existing"],
            "state": ["Virginia", "Texas"],
            "state_abb": ["va", "tx"],
            "county": ["Loudoun", "Dallas"],
            "operator": ["Example A", None],
            "name": ["Facility A", "Facility B"],
            "sqft": [1000, None],
            "lat": [39.0, 32.8],
            "lon": [-77.0, -96.8],
        }
    )


def test_prepare_data_centers_for_db_maps_columns_and_metadata():
    result = prepare_data_centers_for_db(sample_data(), source_url="https://example.test/data.csv")

    assert result["site_id"].tolist() == ["site-1", "site-2"]
    assert result["state_abbr"].tolist() == ["VA", "TX"]
    assert result.loc[0, "latitude"] == pytest.approx(39.0)
    assert result.loc[0, "longitude"] == pytest.approx(-77.0)
    assert result.loc[0, "source_url"] == "https://example.test/data.csv"
    assert pd.isna(result.loc[1, "operator"])


def test_prepare_data_centers_rejects_duplicate_ids():
    df = sample_data()
    df.loc[1, "id"] = "site-1"
    with pytest.raises(ValueError, match="dupliqués"):
        prepare_data_centers_for_db(df)


def test_prepare_data_centers_rejects_invalid_coordinates():
    df = sample_data()
    df.loc[1, "lat"] = 91
    with pytest.raises(ValueError, match="coordonnées"):
        prepare_data_centers_for_db(df)


def test_prepare_data_centers_rejects_missing_required_columns():
    df = sample_data().drop(columns=["state_abb"])
    with pytest.raises(ValueError, match="state_abb"):
        prepare_data_centers_for_db(df)


def test_prepare_data_centers_rejects_negative_area():
    df = sample_data()
    df.loc[0, "sqft"] = -5
    with pytest.raises(ValueError, match="négative"):
        prepare_data_centers_for_db(df)
