"""Run schema and data-quality checks against the repository's PNNL CSV.

Expected placement: data-center-usa-pipeline/scripts/validate_source_dataset.py
Run from the data-center-usa-pipeline directory with the project venv active:
    python scripts/validate_source_dataset.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from datacenter_usa.cleaning import (
    extract_coordinates,
    normalize_columns,
    valid_coordinate_mask,
)
from datacenter_usa.ingestion import load_csv


def locate_source_csv() -> Path:
    """Locate the project CSV without depending on the current working directory."""
    # This script is expected in <repo>/data-center-usa-pipeline/scripts/.
    repo_root = Path(__file__).resolve().parents[2]
    pipeline_root = Path(__file__).resolve().parents[1]

    candidates = [
        repo_root / "pnnl_atlas_records.csv",
        repo_root / "data" / "raw" / "pnnl_atlas_records.csv",
        pipeline_root / "data" / "raw" / "pnnl_atlas_records.csv",
    ]
    for path in candidates:
        if path.is_file():
            return path

    expected = "\n".join(f"- {path}" for path in candidates)
    raise FileNotFoundError(
        "Impossible de trouver pnnl_atlas_records.csv. Emplacements testés :\n"
        f"{expected}"
    )


def main() -> None:
    source_path = locate_source_csv()
    print(f"Source : {source_path}")

    df_raw = load_csv(source_path)
    df = normalize_columns(df_raw)

    required_columns = {
        "id", "layer", "state", "state_abb", "county",
        "operator", "name", "sqft", "lat", "lon",
    }
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        raise ValueError(f"Colonnes attendues absentes : {missing_columns}")

    df = extract_coordinates(df)
    coord_mask = valid_coordinate_mask(df)

    print("\n--- Schéma ---")
    print(f"Lignes : {len(df):,}")
    print(f"Colonnes source : {len(df_raw.columns)}")
    print(f"Noms normalisés : {df.columns.tolist()}")
    print(f"Doublons de lignes exactes : {int(df.duplicated().sum())}")
    print(f"Doublons de id : {int(df['id'].duplicated().sum())}")
    print(f"États distincts : {df['state'].nunique(dropna=True)}")
    print(f"Abréviations d'État distinctes : {df['state_abb'].nunique(dropna=True)}")
    print(f"Coordonnées valides (bornes numériques) : {int(coord_mask.sum()):,}")
    print(f"Coordonnées invalides : {int((~coord_mask).sum()):,}")

    report = pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "missing_n": df.isna().sum(),
        "missing_pct": (df.isna().mean() * 100).round(2),
        "unique_n": df.nunique(dropna=True),
    }).sort_values("missing_pct", ascending=False)

    print("\n--- Rapport de qualité par colonne ---")
    print(report.to_string())

    output_dir = Path(__file__).resolve().parents[1] / "outputs" / "tables"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "data_quality_report.csv"
    report.to_csv(output_path, index_label="column", encoding="utf-8")
    print(f"\nRapport exporté : {output_path}")


if __name__ == "__main__":
    main()
