
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
