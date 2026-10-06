import pandas as pd
import pytest

from datacenter_usa.ingestion import load_csv

def test_load_csv_from_local_file(tmp_path):
    """
    tmp_path est une fixture native de pytest.
    Elle permet de créer un fichier temporaire 
    uniquement pour le test.
    On ne touche donc pas à tes vraies données.
    """
    csv_file = tmp_path / "data.csv"

    csv_file.write_text(
        "name,value\nA,10\nB,20\n",
        encoding="utf-8",
    )

    result = load_csv(csv_file)

    assert isinstance(result, pd.DataFrame)
    assert result.shape == (2, 2)
    assert result["name"].tolist() == ["A", "B"]
    assert result["value"].tolist() == [10, 20]

def test_load_csv_missing_file():
    with pytest.raises(FileNotFoundError):
        load_csv("does_not_exist.csv")


def test_load_csv_empty_source():
    with pytest.raises(ValueError, match="vide"):
        load_csv("")

def test_load_csv_directory(tmp_path):
    with pytest.raises(ValueError, match="pas un fichier"):
        load_csv(tmp_path)


def test_load_csv_with_kwargs(tmp_path):
    csv_file = tmp_path / "data.csv"

    csv_file.write_text(
        "name;value\nA;10\nB;20\n",
        encoding="utf-8",
    )

    result = load_csv(
        csv_file,
        sep=";",
    )

    assert result["value"].tolist() == [10, 20]     