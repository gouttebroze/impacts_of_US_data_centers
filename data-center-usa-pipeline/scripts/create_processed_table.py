
"""Create the processed PostGIS table from staging data."""

from pathlib import Path

from sqlalchemy import text

from datacenter_usa.database import get_engine


def main() -> None:
    sql_path = (
        Path(__file__).resolve().parents[1]
        / "sql"
        / "02_create_processed_table.sql"
    )

    sql_script = sql_path.read_text(encoding="utf-8")
    engine = get_engine()

    try:
        with engine.begin() as connection:
            # Le script contient plusieurs instructions SQL.
            raw_connection = connection.connection.driver_connection
            with raw_connection.cursor() as cursor:
                cursor.execute(sql_script)

        print("Table processed.data_centers créée avec succès.")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
