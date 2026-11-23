"""Obsolète : redirige vers Qdrant (cible cahier des charges)."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

print(
    "Avertissement : indexer_chromadb.py est obsolète ; "
    "utilisez scripts/indexer_qdrant.py",
    file=sys.stderr,
)
runpy.run_path(
    str(Path(__file__).resolve().parent / "indexer_qdrant.py"),
    run_name="__main__",
)
