"""Reusable data-ingestion helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def load_csv(
    source: str | Path,
    *,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> pd.DataFrame:
    """Read a CSV from a local path or HTTP(S) URL using pandas."""
    source_text = str(source).strip()
    if not source_text:
        raise ValueError("La source CSV ne peut pas être vide.")

    if source_text.startswith(("http://", "https://")):
        # Let pandas surface network and parsing errors to the caller.
        return pd.read_csv(source_text, encoding=encoding, **kwargs)

    path = Path(source_text)
    if not path.exists():
        raise FileNotFoundError(f"Fichier CSV introuvable : {path}")
    if not path.is_file():
        raise ValueError(f"La source n'est pas un fichier : {path}")

    try:
        return pd.read_csv(path, encoding=encoding, **kwargs)
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"Le fichier CSV est vide : {path}") from exc
