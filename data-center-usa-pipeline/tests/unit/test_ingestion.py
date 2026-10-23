import pandas as pd
import pytest

from datacenter_usa.ingestion import load_csv


def test_load_csv_from_local_file(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("name,value\nA,10\nB,20\n", encoding="utf-8")
    result = load_csv(path)
    assert result.shape == (2, 2)
    assert result["name"].tolist() == ["A", "B"]
    assert result["value"].tolist() == [10, 20]


def test_load_csv_supports_separator_keyword(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("name;value\nA;10\n", encoding="utf-8")
    result = load_csv(path, sep=";")
    assert result.columns.tolist() == ["name", "value"]


def test_load_csv_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_csv(tmp_path / "missing.csv")


def test_load_csv_empty_source_raises():
    with pytest.raises(ValueError, match="vide"):
        load_csv("  ")


def test_load_csv_directory_raises(tmp_path):
    with pytest.raises(ValueError, match="pas un fichier"):
        load_csv(tmp_path)


def test_load_csv_empty_file_raises(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="vide"):
        load_csv(path)
