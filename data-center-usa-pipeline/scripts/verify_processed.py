
"""Verify the processed data center table."""

from sqlalchemy import text

from datacenter_usa.database import get_engine


def main() -> None:
    engine = get_engine()

    query = text("""
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT id) AS unique_ids,
            COUNT(*) FILTER (
                WHERE geom IS NULL
            ) AS missing_geometries,
            COUNT(*) FILTER (
                WHERE NOT ST_IsValid(geom)
            ) AS invalid_geometries,
            COUNT(*) FILTER (
                WHERE ST_SRID(geom) <> 4326
            ) AS wrong_srid
        FROM processed.data_centers;
    """)

    try:
        with engine.connect() as connection:
            result = connection.execute(query).mappings().one()

        print("=== PROCESSED DATA QUALITY ===")
        for key, value in result.items():
            print(f"{key}: {value}")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
