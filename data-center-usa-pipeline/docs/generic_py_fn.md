# About clean code practice

## Generical function 

* Intérêt de la fn ?

    * fn permet :

```py
# Fichier local
from datacenter_usa.ingestion import load_csv

df = load_csv(
    "data/raw/pnnl_atlas_records.csv"
)
```


```py
# URL distante
df = load_csv(
    "https://example.com/data.csv"
)
```

## Architecture composé de plusieurs fns - principe SOLID

* en appliquant le principe SOLID de Responsabilité unique:

    - "Une classe, fonction, méthode, objet doit faire une seule chose, bien la faire, en porter sa responsabilité..." 

        * pr un code + robuste, + simple à comprendre ou à réparer, ainsi que:
            - plus facile à tester
            - plus facile à comprendre
            - plus facile à réutiliser
            - plus facile à modifier

* principe respecté par les logiciels, OS dont la puissance et la fiabilité 
ne sont plus à démontrer... (distrib. Linux, VIM ...) (Linux avait déjà qques utiisateurs légèrement porté sur la qualité, mais qd on voit que le CERN a céée un fork de Debian, là faut pas déconner, qd on sait qu'il existe des possibilité de création accidentelles de trous noirs, possibilité extremement faible, mais avec la chance qui nous entoure (Trump ayant bien été élus à 2 rerise), cette théorie me semble plus réaliste! d'anéaintire )... digression, digression... commit & bonne nuit
 
* ah oui, on a aussi les super appli windows fesant 25 choses différentes, chacune plus inutile que l'autre, ça vaut le coût d'acheter la licence (au fait, pr les gamers, jeter un coup d'oeil sur certaines distrib. du pyngoin, les jeux tournent très bien sous Linux, et pourtant Bill n'a jamais eu les poche aussi pleine, reste les féneants, les dépressifs à l'êtreme ne trouvant plus aucun sens à la vie, pour qui ne reste qu'une issue, ms le flingue se trouvant ds la cuisine, il reste bloqué devant son écran, les yeux remplies de larmes, pétrifié devant l'écran jouant cet air de musique, lui permettant de respirer, ET PAFF, c'est Bill dans le rôle de la faucheuse, qui lui balance la 50eme MAJ de la semaine, ordi qui rame, non, comment patienter 1 heure, aller, cuisine, on s'retrouvera en enfer... ):

quality_report(df)
duplicate_count(df)
missing_rate(series)
validate_required_columns(df, [...])

pratique notre architecture.
Cela rend :

3. Les tests

Crée :

tests/unit/test_quality.py

avec :

import pandas as pd
import pytest

from datacenter_usa.quality import (
    duplicate_count,
    missing_rate,
    quality_report,
    validate_required_columns,
)


def test_quality_report():
    df = pd.DataFrame(
        {
            "name": ["A", "B", None],
            "value": [10, 20, 30],
        }
    )

    result = quality_report(df)

    assert result.loc["name", "missing_n"] == 1
    assert result.loc["name", "missing_pct"] == pytest.approx(33.33)
    assert result.loc["value", "missing_n"] == 0
    assert result.loc["value", "unique_n"] == 3


def test_duplicate_count():
    df = pd.DataFrame(
        {
            "name": ["A", "A", "B"],
            "value": [10, 10, 20],
        }
    )

    assert duplicate_count(df) == 1


def test_duplicate_count_without_duplicates():
    df = pd.DataFrame(
        {
            "name": ["A", "B"],
            "value": [10, 20],
        }
    )

    assert duplicate_count(df) == 0


def test_missing_rate():
    series = pd.Series([10, None, 30, None])

    assert missing_rate(series) == 0.5


def test_missing_rate_empty_series():
    series = pd.Series([], dtype="float64")

    assert missing_rate(series) == 0.0


def test_validate_required_columns():
    df = pd.DataFrame(
        {
            "name": ["A"],
            "latitude": [40],
        }
    )

    validate_required_columns(
        df,
        ["name", "latitude"],
    )


def test_validate_required_columns_raises():
    df = pd.DataFrame(
        {
            "name": ["A"],
        }
    )

    with pytest.raises(ValueError, match="latitude"):
        validate_required_columns(
            df,
            ["name", "latitude"],
        )