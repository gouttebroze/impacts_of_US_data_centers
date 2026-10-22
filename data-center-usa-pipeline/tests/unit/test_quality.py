import pandas as pd
import pytest

from datacenter_usa.quality import (
    duplicate_count,
    duplicate_key_count,
    missing_rate,
    quality_report,
    validate_required_columns,
)


def test_quality_report_calculates_missing_and_unique_values():
    df = pd.DataFrame({"name": ["A", "B", None], "value": [10, 20, 30]})
    report = quality_report(df)
    assert report.loc["name", "missing_n"] == 1
    assert report.loc["name", "missing_pct"] == pytest.approx(33.33)
    assert report.loc["value", "missing_n"] == 0
    assert report.loc["value", "unique_n"] == 3


def test_duplicate_count():
    df = pd.DataFrame({"name": ["A", "A", "B"], "value": [10, 10, 20]})
    assert duplicate_count(df) == 1


def test_missing_rate():
    assert missing_rate(pd.Series([10, None, 30, None])) == 0.5


def test_missing_rate_empty_series():
    assert missing_rate(pd.Series([], dtype="float64")) == 0.0


def test_validate_required_columns_passes():
    validate_required_columns(pd.DataFrame(columns=["id", "state"]), ["id", "state"])


def test_validate_required_columns_raises_with_missing_columns():
    with pytest.raises(ValueError, match="state"):
        validate_required_columns(pd.DataFrame(columns=["id"]), ["id", "state"])


def test_duplicate_key_count_ignores_missing_keys():
    df = pd.DataFrame({"id": [1, 1, None, None, 2]})
    assert duplicate_key_count(df, "id") == 1


def test_duplicate_key_count_missing_column_raises():
    with pytest.raises(ValueError, match="absente"):
        duplicate_key_count(pd.DataFrame({"other": [1]}), "id")
