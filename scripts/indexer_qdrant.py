"""Indexe les embeddings.json locaux dans Qdrant.

Usage :
  python scripts/indexer_qdrant.py schema_pompe_a
  python scripts/indexer_qdrant.py --tout

Par défaut : Qdrant embarqué sous data/qdrant.
Serveur Docker : MAINTIDOC_QDRANT_URL=http://127.0.0.1:6333
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from maintidoc.qdrant_index import (
    compter,
    dossier_qdrant,
    indexer_corpus,
    indexer_document,
    ouvrir_client,
    url_qdrant,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document_id", nargs="?", help="ex. schema_pompe_a")
    parser.add_argument("--tout", action="store_true", help="Tous les docs vectorisés")
    args = parser.parse_args()
    if not args.tout and not args.document_id:
        parser.error("Indiquez un document_id ou --tout")

    client = ouvrir_client()
    cible = url_qdrant() or str(dossier_qdrant())
    print(f"Qdrant : {cible}")
    if args.tout:
        stats = indexer_corpus(client=client)
        for doc_id, n in stats.items():
            print(f"  {doc_id}: {n} éléments")
        print(f"Total collection : {compter(client)}")
        return 0

    n = indexer_document(args.document_id, client=client)
    print(f"{args.document_id}: {n} éléments indexés")
    print(f"Total collection : {compter(client)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
