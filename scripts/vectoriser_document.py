"""Vectorisation CLIP d'un document extrait (sans ChromaDB).

Usage :
  python scripts/vectoriser_document.py schema_pompe_a
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from maintidoc.vectorisation import apercu_vectorisation, vectoriser_document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document_id", help="ex. schema_pompe_a")
    parser.add_argument(
        "--sans-extraction",
        action="store_true",
        help="Ne pas ré-extraire le PDF (utilise data/processed existant)",
    )
    args = parser.parse_args()

    print("=== Vectorisation CLIP (sans ChromaDB) ===")
    resultat = vectoriser_document(
        args.document_id, extraire=not args.sans_extraction
    )
    print(f"Fichier : {resultat.fichier}")
    print(f"Fragments texte : {resultat.nombre_fragments_texte}")
    print(f"Images : {resultat.nombre_images}")
    print(f"Dimension : {resultat.dimension}")

    print("\n=== Aperçu des embeddings (texte + image) ===")
    for ligne in apercu_vectorisation(args.document_id, n=4):
        print(json.dumps(ligne, ensure_ascii=False))
    print(
        "\nNote : un nouvel appel réécrit embeddings.json (pas de doublon)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
