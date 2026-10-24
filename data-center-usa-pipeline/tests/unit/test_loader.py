
import pandas as pd
import pytest

from datacenter_usa.loader import load_csv_to_staging


def test_load_csv_to_staging_returns_row_count(
    tmp_path, monkeypatch
):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        "id,name\n1,Alpha\n2,Beta\n",
        encoding="utf-8",
    )

    dataframe = pd.DataFrame(
        {"id": ["1", "2"], "name": ["Alpha", "Beta"]}
    )

    monkeypatch.setattr(
        pd,
        "read_csv",
        lambda *args, **kwargs: dataframe,
    )

    calls = {}

    def fake_to_sql(self, **kwargs):
        calls.update(kwargs)

    monkeypatch.setattr(pd.DataFrame, "to_sql", fake_to_sql)

    result = load_csv_to_staging(csv_file, engine=object())

    assert result == 2
    assert calls["name"] == "pnnl_atlas_records"
    assert calls["schema"] == "staging"
    assert calls["if_exists"] == "fail"
    assert calls["index"] is False


def test_load_csv_to_staging_rejects_missing_file():
    with pytest.raises(FileNotFoundError):
        load_csv_to_staging(
            "missing.csv",
            engine=object(),
        )


def test_load_csv_to_staging_rejects_invalid_table_name(
    tmp_path,
):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        "id\n1\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid table name"):
        load_csv_to_staging(
            csv_file,
            engine=object(),
            table_name="invalid; DROP TABLE",
        )
