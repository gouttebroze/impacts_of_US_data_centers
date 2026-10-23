"""Run the local data-center ingestion and quality pipeline.

Run from ``data-center-usa-pipeline``:
    python scripts/validate_local_pipeline.py
"""
from __future__ import annotations

import json
from pathlib import Path

from datacenter_usa.pipeline import prepare_dataset


def locate_source_csv() -> Path:
    """Find the project CSV without relying on the current working directory."""
    pipeline_root = Path(__file__).resolve().parents[1]
    repository_root = pipeline_root.parent
    candidates = (
        repository_root / "pnnl_atlas_records.csv",
        repository_root / "data" / "raw" / "pnnl_atlas_records.csv",
        pipeline_root / "data" / "raw" / "pnnl_atlas_records.csv",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    paths = "\n".join(f"- {candidate}" for candidate in candidates)
    raise FileNotFoundError(
        "Impossible de localiser pnnl_atlas_records.csv. Chemins testés :\n" + paths
    )


def main() -> None:
    source = locate_source_csv()
    result = prepare_dataset(source, coordinate_policy="drop")

    print("--- Résumé du pipeline ---")
    print(json.dumps(result.summary, indent=2, ensure_ascii=False))
    print("\n--- Qualité par colonne (avant filtrage géographique) ---")
    print(result.quality_report.to_string())

    output_dir = Path(__file__).resolve().parents[1] / "outputs" / "tables"
    output_dir.mkdir(parents=True, exist_ok=True)
    result.quality_report.to_csv(
        output_dir / "data_quality_report.csv",
        index_label="column",
        encoding="utf-8",
    )
    result.data.to_csv(
        output_dir / "data_centers_prepared.csv",
        index=False,
        encoding="utf-8",
    )
    (output_dir / "pipeline_summary.json").write_text(
        json.dumps(result.summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nRésultats exportés dans : {output_dir}")


if __name__ == "__main__":
    main()
