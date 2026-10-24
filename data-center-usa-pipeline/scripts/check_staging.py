
"""Run data quality checks on the raw staging table."""

from sqlalchemy import text

from datacenter_usa.database import get_engine


def main() -> None:
    engine = get_engine()

    summary_query = text(
        r"""
        WITH parsed AS (
            SELECT
                NULLIF(BTRIM(id), '') AS clean_id,
                CASE
                    WHEN BTRIM(lat) ~
                        '^[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)$'
                    THEN BTRIM(lat)::numeric
                END AS latitude,
                CASE
                    WHEN BTRIM(lon) ~
                        '^[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)$'
                    THEN BTRIM(lon)::numeric
                END AS longitude
            FROM staging.pnnl_atlas_records
        ),
        duplicate_ids AS (
            SELECT clean_id
            FROM parsed
            WHERE clean_id IS NOT NULL
            GROUP BY clean_id
            HAVING COUNT(*) > 1
        )
        SELECT
            COUNT(*) AS total_rows,
            COUNT(*) FILTER (
                WHERE clean_id IS NULL
            ) AS missing_ids,
            (SELECT COUNT(*) FROM duplicate_ids)
                AS duplicated_id_values,
            COUNT(*) FILTER (
                WHERE latitude IS NULL
                   OR longitude IS NULL
                   OR latitude NOT BETWEEN -90 AND 90
                   OR longitude NOT BETWEEN -180 AND 180
            ) AS invalid_coordinates
        FROM parsed;
        """
    )

    missing_query = text(
        """
        SELECT
            COUNT(*) FILTER (
                WHERE NULLIF(BTRIM(state), '') IS NULL
            ) AS missing_state,
            COUNT(*) FILTER (
                WHERE NULLIF(BTRIM(county), '') IS NULL
            ) AS missing_county,
            COUNT(*) FILTER (
                WHERE NULLIF(BTRIM(operator), '') IS NULL
            ) AS missing_operator,
            COUNT(*) FILTER (
                WHERE NULLIF(BTRIM(name), '') IS NULL
            ) AS missing_name,
            COUNT(*) FILTER (
                WHERE NULLIF(BTRIM(sqft), '') IS NULL
            ) AS missing_sqft
        FROM staging.pnnl_atlas_records;
        """
    )


    sqft_query = text(
        r"""
        WITH values_checked AS (
            SELECT
                BTRIM(sqft) AS raw_sqft,
                CASE
                    WHEN BTRIM(sqft) ~
                        '^[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)$'
                    THEN BTRIM(sqft)::numeric
                END AS numeric_sqft
            FROM staging.pnnl_atlas_records
        )
        SELECT
            COUNT(*) FILTER (
                WHERE numeric_sqft IS NULL
            ) AS invalid_sqft,
            COUNT(*) FILTER (
                WHERE numeric_sqft < 0
            ) AS negative_sqft,
            COUNT(*) FILTER (
                WHERE numeric_sqft = 0
            ) AS zero_sqft
        FROM values_checked;
        """
    )


    try:
        with engine.connect() as connection:
            summary = connection.execute(summary_query).mappings().one()
            missing = connection.execute(missing_query).mappings().one()
            sqft = connection.execute(sqft_query).mappings().one()

        print("=== STAGING DATA QUALITY REPORT ===")
        for key, value in summary.items():
            print(f"{key}: {value}")

        print("\n=== MISSING VALUES ===")
        for key, value in missing.items():
            print(f"{key}: {value}")

        print("\n=== SURFACE QUALITY CHECKS ===")
        for key, value in sqft.items():
            print(f"{key}: {value}")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
