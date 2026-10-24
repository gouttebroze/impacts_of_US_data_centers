"""Initialize the local PostgreSQL/PostGIS schemas and verify connectivity."""

from pathlib import Path

from datacenter_usa.database import (
    create_database_engine,
    initialize_database,
    postgis_healthcheck,
)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    migration = project_root / "sql" / "staging" / "001_create_data_centers.sql"

    engine = create_database_engine()
    try:
        initialize_database(engine, migration)
        info = postgis_healthcheck(engine)
        print(f"Database : {info['database']}")
        print(f"PostgreSQL : {info['postgresql_version'].splitlines()[0]}")
        print(f"PostGIS : {info['postgis_version'].split(';')[0]}")
        print("Schéma staging et table data_centers disponibles.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
