# code   

## Tests

## tests unitaires & les tests d’intégration PostgreSQL/PostGIS

* **Isolation**: **Les tests unitaires vérifient une fonction devant être isolé du reste du code, son fonctionnement ne doit pas être affecté par les changements d'autres parties du code, d'où la nécessité de vérifié son comportement s'il recoie des imports de modules**. 

* Les **tests d’intégration** vérifient que notre code fonctionne avec la vraie base de données, ses tables, ses types et ses fonctions spatiales.

* Nous allons tester quatre éléments :

    - la connexion à ``PostgreSQL`` et la disponibilité de ``PostGIS`` ;
    - le nombre de lignes et l'unicité des identifiants ;
    - la validité des géométries et leur système de coordonnées ;
    - la cohérence des coordonnées géographiques avec les colonnes **lat** et **lon**.

* Comme une géométrie peut être techniquement valide tout en ayant été construite en inversant latitude et longitude, le test d'intégration suivant et nommé `./tests/integration/test_postgis_integration.py` doit détecter si cette erreur existe.

```py
"""Integration tests for the PostgreSQL/PostGIS data pipeline.

These tests read from the configured database.
They do not create, update, or delete production data.
"""

import pytest
from sqlalchemy import text

from datacenter_usa.database import get_engine


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def engine():
    """Connect to the configured PostgreSQL database."""
    db_engine = get_engine()

    try:
        with db_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        yield db_engine
    finally:
        db_engine.dispose()


def test_postgis_extension_is_available(engine):
    """PostGIS must be installed in the connected database."""
    query = text("""
        SELECT EXISTS (
            SELECT 1
            FROM pg_extension
            WHERE extname = 'postgis'
        )
    """)

    with engine.connect() as connection:
        result = connection.execute(query).scalar_one()

    assert result is True


def test_processed_table_contains_expected_rows(engine):
    """The processed table should contain all source records."""
    query = text("""
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT id) AS unique_ids
        FROM processed.data_centers
    """)

    with engine.connect() as connection:
        result = connection.execute(query).mappings().one()

    assert result["total_rows"] == 1237
    assert result["unique_ids"] == result["total_rows"]


def test_geometries_are_valid_and_use_wgs84(engine):
    """Every geometry must be a valid Point in EPSG:4326."""
    query = text("""
        SELECT
            COUNT(*) FILTER (
                WHERE geom IS NULL
            ) AS missing_geometries,
            COUNT(*) FILTER (
                WHERE NOT ST_IsValid(geom)
            ) AS invalid_geometries,
            COUNT(*) FILTER (
                WHERE ST_SRID(geom) <> 4326
            ) AS wrong_srid,
            COUNT(*) FILTER (
                WHERE GeometryType(geom) <> 'POINT'
            ) AS wrong_geometry_type
        FROM processed.data_centers
    """)

    with engine.connect() as connection:
        result = connection.execute(query).mappings().one()

    assert result["missing_geometries"] == 0
    assert result["invalid_geometries"] == 0
    assert result["wrong_srid"] == 0
    assert result["wrong_geometry_type"] == 0


def test_geometry_matches_longitude_and_latitude(engine):
    """Geometry X must equal longitude and Y must equal latitude."""
    query = text("""
        SELECT COUNT(*)
        FROM processed.data_centers
        WHERE
            ABS(ST_X(geom) - lon) > 0.0000001
            OR ABS(ST_Y(geom) - lat) > 0.0000001
    """)

    with engine.connect() as connection:
        mismatches = connection.execute(query).scalar_one()

    assert mismatches == 0
```
* On doit déclarer le marqueur ``pytest`` dans ``pyproject.toml``:

* ```toml```

## Genericité

* Intérêt de la fn ?

    * fn permet :

```py
# Fichier local
from datacenter_usa.ingestion import load_csv

df = load_csv(
    "data/raw/pnnl_atlas_records.csv"
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