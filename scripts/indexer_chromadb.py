"""Indexe les embeddings.json locaux dans ChromaDB.

Usage :
  python scripts/indexer_chromadb.py schema_pompe_a
  python scripts/indexer_chromadb.py --tout
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from maintidoc.chroma_index import (
    dossier_chroma,
    indexer_corpus,
    indexer_document,
    ouvrir_collection,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document_id", nargs="?", help="ex. schema_pompe_a")
    parser.add_argument("--tout", action="store_true", help="Tous les docs vectorisés")
    args = parser.parse_args()
    if not args.tout and not args.document_id:
        parser.error("Indiquez un document_id ou --tout")

    col = ouvrir_collection()
    print(f"ChromaDB : {dossier_chroma()}")
    if args.tout:
        stats = indexer_corpus(collection=col)
        for doc_id, n in stats.items():
            print(f"  {doc_id}: {n} éléments")
        print(f"Total collection : {col.count()}")
        return 0

    n = indexer_document(args.document_id, collection=col)
    print(f"{args.document_id}: {n} éléments indexés")
    print(f"Total collection : {col.count()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
