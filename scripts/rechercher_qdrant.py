"""Recherche multimodale dans Qdrant (texte ou image).

Usage :
  python scripts/rechercher_qdrant.py "température de palier E41"
  python scripts/rechercher_qdrant.py --image corpus/raw/.../photo.jpg --type image
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from maintidoc.qdrant_index import formater_resultats, rechercher


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("texte", nargs="?", help="Question / requête texte")
    parser.add_argument("--image", help="Chemin d'une image requête")
    parser.add_argument("--type", choices=["texte", "image"], dest="type_resultat")
    parser.add_argument("-k", type=int, default=5)
    args = parser.parse_args()
    if not args.texte and not args.image:
        parser.error("Fournissez un texte ou --image")

    resultats = rechercher(
        texte=args.texte,
        image=args.image,
        type_resultat=args.type_resultat,
        k=args.k,
    )
    for ligne in formater_resultats(resultats):
        print(json.dumps(ligne, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
