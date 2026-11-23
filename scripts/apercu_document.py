"""Extraction + aperçu d'un document du corpus (notebook jusqu'à l'aperçu).

Usage :
  python scripts/apercu_document.py schema_pompe_a
  python scripts/apercu_document.py schema_pompe_a --clip
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from maintidoc.extraction import apercu_extraction, extraire_document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document_id", help="ex. schema_pompe_a")
    parser.add_argument(
        "--clip",
        action="store_true",
        help="Lance aussi le smoke test OpenCLIP du notebook",
    )
    args = parser.parse_args()

    if args.clip:
        from maintidoc.clip_smoke import encoder_exemple

        print("=== CLIP (smoke test notebook) ===")
        print(json.dumps(encoder_exemple(), ensure_ascii=False, indent=2))
        print()

    print("=== Extraction PDF ===")
    resultat = extraire_document(args.document_id)
    print(f"PDF : {resultat.pdf}")
    print(f"Sortie : {resultat.output_dir}")
    print(f"Pages : {resultat.nombre_pages}")
    print(f"Images : {resultat.nombre_images}")
    if resultat.pages_sans_texte:
        print("Pages sans texte :", resultat.pages_sans_texte)

    print("\n=== Aperçu du résultat ===")
    apercu = apercu_extraction(args.document_id)
    print("APERÇU DU TEXTE\n")
    print(apercu["texte_apercu"])
    print("\nAPERÇU DES IMAGES\n")
    for nom in apercu["images"]:
        print(Path(nom).name)
    for vignette in apercu["vignettes"]:
        print("vignette :", vignette)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
