"""Load the PNNL CSV snapshot into PostgreSQL/PostGIS staging."""

from __future__ import annotations

import argparse
from pathlib import Path

from datacenter_usa.database import (
    create_database_engine,
    count_data_centers,
    write_data_centers,
)
from datacenter_usa.pipeline import prepare_dataset

DEFAULT_SOURCE_URL = "https://energyfactbook.com/data-centers/data/pnnl_atlas_records.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="Chemin du snapshot CSV PNNL")
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL)
    parser.add_argument("--source-name", default="pnnl_im3_atlas")
    args = parser.parse_args()

    if not args.csv_path.exists() or not args.csv_path.is_file():
        parser.error(f"CSV introuvable : {args.csv_path}")

    pipeline_result = prepare_dataset(args.csv_path, coordinate_policy="drop")
    engine = create_database_engine()
    try:
        count_submitted = write_data_centers(
            pipeline_result.data,
            engine,
            source_name=args.source_name,
            source_url=args.source_url,
        )
        total_in_staging = count_data_centers(engine)
        print(f"Lignes du CSV : {pipeline_result.summary['rows_loaded']}")
        print(f"Lignes soumises à PostGIS : {count_submitted}")
        print(f"Records actuellement en staging : {total_in_staging}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
