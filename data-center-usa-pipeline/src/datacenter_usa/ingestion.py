"""Generic data ingestion utilities."""

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
    """
    -----------
  -- Parameters --
    -----------
    source:
        Local file path or HTTP(S) URL.
    encoding:
        File encoding. Defaults to UTF-8.
    
    **kwargs: (see .py doc to get more informations on **kwargs with parameters details)
        Additional arguments passed to pandas.read_csv().

    Returns
    -------
    pandas.DataFrame
        Loaded dataset.

    Raises
    ------
    FileNotFoundError
        If a local file does not exist.
    ValueError
        If the source is empty.
    """
    source = str(source).strip()

    if not source:
        raise ValueError("La source CSV ne peut pas être vide.")

    if source.startswith(("http://", "https://")):
        return pd.read_csv(
            source,
            encoding=encoding,
            **kwargs,
        )

    path = Path(source)

    if not path.exists():
        raise FileNotFoundError(
            f"Fichier CSV introuvable : {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"La source n'est pas un fichier : {path}"
        )

    return pd.read_csv(
        path,
        encoding=encoding,
        **kwargs,
    )