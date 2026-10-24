"""PostgreSQL/PostGIS helpers for the data-center pipeline.

SQLAlchemy and psycopg are optional project dependencies. They are imported only
when a database connection or SQL operation is requested, so local CSV-only
work can still use the rest of the package without a database server.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from datacenter_usa.cleaning import extract_coordinates, normalize_columns, valid_coordinate_mask
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine

DEFAULT_SOURCE_NAME = "pnnl_im3_atlas"
DEFAULT_SOURCE_URL = "https://energyfactbook.com/data-centers/data/pnnl_atlas_records.csv"

"""Database connection helpers for the data center pipeline."""

def get_engine() -> Engine:
    """Create a SQLAlchemy engine using DATABASE_URL.

    Returns:
        Engine: SQLAlchemy engine configured for PostgreSQL.

    Raises:
        RuntimeError: If DATABASE_URL is missing.
    """
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is missing. Check your .env configuration."
        )

    return create_engine(database_url, pool_pre_ping=True)




def get_database_url(database_url: str | None = None) -> str:
    """Get the DB URL from argument or the DATABASE_URL environment variable.

    If python-dotenv is installed, load a local .env file without overriding
    environment variables already set by the shell.
    """
    if database_url and database_url.strip():
        return database_url.strip()

    try:
        from dotenv import load_dotenv
    except ImportError:
        pass
    else:
        load_dotenv(override=False)

    value = os.getenv("DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError(
            "DATABASE_URL n'est pas configurée. Copiez .env.example vers .env "
            "et renseignez la connexion, ou définissez DATABASE_URL dans votre shell."
        )
    return value


def create_database_engine(database_url: str | None = None):
    """Create a SQLAlchemy engine using psycopg 3."""
    try:
        from sqlalchemy import create_engine
    except ImportError as exc:
        raise RuntimeError(
            "SQLAlchemy n'est pas installé. Installez les dépendances avec "
            '`python -m pip install -e ".[dev,db]".'
        ) from exc

    url = get_database_url(database_url)
    return create_engine(url, pool_pre_ping=True)


def initialize_database(engine, sql_path: str | Path) -> None:
    """Execute a simple SQL migration file inside a transaction.

    The migration is intentionally kept to simple statements separated by
    semicolons. For more complex migrations, use a migration tool such as Alembic.
    """
    path = Path(sql_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Fichier SQL introuvable : {path}")

    sql_text = path.read_text(encoding="utf-8")
    statements = [part.strip() for part in sql_text.split(";") if part.strip()]
    if not statements:
        raise ValueError(f"Le fichier SQL ne contient aucune instruction : {path}")

    with engine.begin() as connection:
        for statement in statements:
            connection.exec_driver_sql(statement)


def postgis_healthcheck(engine) -> dict[str, str]:
    """Return database name, PostgreSQL version and PostGIS version."""
    with engine.connect() as connection:
        row = connection.exec_driver_sql(
            "SELECT current_database(), version(), PostGIS_Full_Version()"
        ).one()
    return {
        "database": str(row[0]),
        "postgresql_version": str(row[1]),
        "postgis_version": str(row[2]),
    }


def _normalize_site_id(value: Any) -> str | None:
    if pd.isna(value):
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    text_value = str(value).strip()
    return text_value or None


def _to_db_value(value: Any) -> Any:
    """Convert Pandas/NumPy missing/scalar values to DBAPI-friendly values."""
    if pd.isna(value):
        return None
    if hasattr(value, "item") and callable(value.item):
        try:
            return value.item()
        except (ValueError, TypeError):
            pass
    return value


def prepare_data_centers_for_db(
    data: pd.DataFrame,
    *,
    source_name: str = DEFAULT_SOURCE_NAME,
    source_url: str = DEFAULT_SOURCE_URL,
    retrieved_at: datetime | None = None,
) -> pd.DataFrame:
    """Map the PNNL-style dataset to the database staging schema and validate it.

    This function performs no database connection, which makes the preparation
    step easy to unit test. Missing optional attributes remain NULL; IDs and
    valid geographic coordinates are required for a staging record.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data doit être un pandas.DataFrame")
    if not source_name.strip() or not source_url.strip():
        raise ValueError("source_name et source_url ne peuvent pas être vides")

    normalized = normalize_columns(data)
    required = {"id", "state", "state_abb", "county"}
    missing = sorted(required - set(normalized.columns))
    if missing:
        raise ValueError(f"Colonnes requises absentes pour PostGIS : {missing}")

    coordinates = extract_coordinates(normalized)
    valid = valid_coordinate_mask(coordinates)
    if not valid.all():
        raise ValueError(
            f"{int((~valid).sum())} ligne(s) ont des coordonnées absentes ou invalides. "
            "Nettoyez/filtrez les coordonnées avant le chargement."
        )

    ids = coordinates["id"].map(_normalize_site_id)
    if ids.isna().any():
        raise ValueError("La colonne id contient des identifiants vides ou manquants")
    if ids.duplicated().any():
        duplicates = ids[ids.duplicated(keep=False)].unique().tolist()
        raise ValueError(f"Identifiants de data centers dupliqués : {duplicates[:10]}")

    area = (
        pd.to_numeric(coordinates["sqft"], errors="coerce")
        if "sqft" in coordinates.columns
        else pd.Series(float("nan"), index=coordinates.index)
    )
    if (area.dropna() < 0).any():
        raise ValueError("La surface sqft ne peut pas être négative")

    timestamp = retrieved_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    def optional_column(column: str) -> pd.Series:
        if column in coordinates.columns:
            return coordinates[column]
        return pd.Series(None, index=coordinates.index, dtype="object")

    result = pd.DataFrame(
        {
            "site_id": ids,
            "source_layer": optional_column("layer"),
            "state_name": coordinates["state"],
            "state_abbr": coordinates["state_abb"].astype("string").str.upper(),
            "county_name": coordinates["county"],
            "operator": optional_column("operator"),
            "site_name": optional_column("name"),
            "area_sqft": area,
            "latitude": pd.to_numeric(coordinates["latitude"], errors="coerce"),
            "longitude": pd.to_numeric(coordinates["longitude"], errors="coerce"),
            "source_name": source_name,
            "source_url": source_url,
            "retrieved_at": timestamp,
        },
        index=coordinates.index,
    )
    return result.reset_index(drop=True)


_UPSERT_SQL = """
INSERT INTO staging.data_centers (
    site_id, source_layer, state_name, state_abbr, county_name,
    operator, site_name, area_sqft, latitude, longitude,
    source_name, source_url, retrieved_at, geom
)
VALUES (
    :site_id, :source_layer, :state_name, :state_abbr, :county_name,
    :operator, :site_name, :area_sqft, :latitude, :longitude,
    :source_name, :source_url, :retrieved_at,
    ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)
)
ON CONFLICT (site_id) DO UPDATE SET
    source_layer = EXCLUDED.source_layer,
    state_name = EXCLUDED.state_name,
    state_abbr = EXCLUDED.state_abbr,
    county_name = EXCLUDED.county_name,
    operator = EXCLUDED.operator,
    site_name = EXCLUDED.site_name,
    area_sqft = EXCLUDED.area_sqft,
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    source_name = EXCLUDED.source_name,
    source_url = EXCLUDED.source_url,
    retrieved_at = EXCLUDED.retrieved_at,
    geom = EXCLUDED.geom
"""


def write_data_centers(
    data: pd.DataFrame,
    engine,
    *,
    source_name: str = DEFAULT_SOURCE_NAME,
    source_url: str = DEFAULT_SOURCE_URL,
    retrieved_at: datetime | None = None,
) -> int:
    """Insert/update data-center records in ``staging.data_centers``.

    The target table must exist (run the SQL migration first). Returns the number
    of records submitted. Existing ``site_id`` values are updated idempotently.
    """
    from sqlalchemy import text

    records_df = prepare_data_centers_for_db(
        data,
        source_name=source_name,
        source_url=source_url,
        retrieved_at=retrieved_at,
    )
    records = [
        {key: _to_db_value(value) for key, value in row.items()}
        for row in records_df.to_dict(orient="records")
    ]
    if not records:
        return 0

    with engine.begin() as connection:
        connection.execute(text(_UPSERT_SQL), records)
    return len(records)


def count_data_centers(engine, *, site_id: str | None = None) -> int:
    """Count records in the staging table, optionally filtering by site ID."""
    from sqlalchemy import text

    if site_id is None:
        query = text("SELECT COUNT(*) FROM staging.data_centers")
        params: dict[str, Any] = {}
    else:
        query = text("SELECT COUNT(*) FROM staging.data_centers WHERE site_id = :site_id")
        params = {"site_id": site_id}

    with engine.connect() as connection:
        return int(connection.execute(query, params).scalar_one())


def read_data_centers(engine, *, site_id: str | None = None) -> pd.DataFrame:
    """Read staging records into a DataFrame with WKT geometry for inspection."""
    from sqlalchemy import text

    query = """
    SELECT site_id, source_layer, state_name, state_abbr, county_name,
           operator, site_name, area_sqft, latitude, longitude,
           source_name, source_url, retrieved_at, ST_AsText(geom) AS geometry_wkt
    FROM staging.data_centers
    """
    params: dict[str, Any] = {}
    if site_id is not None:
        query += " WHERE site_id = :site_id"
        params["site_id"] = site_id
    query += " ORDER BY site_id"

    return pd.read_sql_query(text(query), engine, params=params)
