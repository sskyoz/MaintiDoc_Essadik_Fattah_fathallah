"""Migre corpus/documents|images → corpus/raw/<équipement|shared>/...

Nouvelle forme :
  raw/<EQUIPEMENT>/<type>/<document_id>/<version>/<document_id>.<ext>
  raw/_shared/<famille>/<type>/<document_id>/<version>/<document_id>.<ext>

Met à jour inventaire.csv. Les chemins passent par l'inventaire : agent / extraction
continuent de fonctionner.
"""

from __future__ import annotations

import csv
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
INV = CORPUS / "inventaire.csv"
COLS = [
    "document_id", "fichier", "titre", "famille_equipement", "equipement_id",
    "type_document", "version", "nb_pages", "langue", "format", "elements_visuels",
    "provenance", "licence", "genere_par_ia", "outil_ia", "verifie_par",
    "corrections", "groupe_acces", "usage_test", "remarques",
]


def version_slug(version: str) -> str:
    texte = version.strip()
    texte = texte.replace("(", " ").replace(")", " ")
    texte = re.sub(r"[^\w.\-]+", "_", texte, flags=re.UNICODE)
    texte = re.sub(r"_+", "_", texte).strip("_")
    return texte or "sans_version"


def nouvel_emplacement(row: dict[str, str]) -> Path:
    ids = [x.strip() for x in row["equipement_id"].split(";") if x.strip()]
    if len(ids) == 1:
        racine_eq = Path("raw") / ids[0]
    else:
        racine_eq = Path("raw") / "_shared" / row["famille_equipement"]
    ancien = Path(row["fichier"])
    return (
        racine_eq
        / row["type_document"]
        / row["document_id"]
        / version_slug(row["version"])
        / f"{row['document_id']}{ancien.suffix.lower()}"
    )


def main() -> int:
    with INV.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit("inventaire vide")

    deplacements: list[tuple[Path, Path, dict[str, str]]] = []
    for row in rows:
        source = CORPUS / row["fichier"]
        if not source.is_file():
            raise FileNotFoundError(f"Absent : {source}")
        cible_rel = nouvel_emplacement(row)
        cible = CORPUS / cible_rel
        deplacements.append((source, cible, row))

    for source, cible, row in deplacements:
        cible.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != cible.resolve():
            if cible.exists():
                raise FileExistsError(f"Cible déjà présente : {cible}")
            shutil.move(str(source), str(cible))
        row["fichier"] = cible.relative_to(CORPUS).as_posix()
        print(f"OK  {row['document_id']} → {row['fichier']}")

    with INV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    # Nettoyage des anciens dossiers vides
    for dossier in (CORPUS / "documents", CORPUS / "images"):
        if dossier.is_dir():
            for sous in sorted(dossier.rglob("*"), reverse=True):
                if sous.is_dir():
                    try:
                        sous.rmdir()
                    except OSError:
                        pass
            try:
                dossier.rmdir()
            except OSError:
                print(f"Conservé (non vide) : {dossier}")

    print(f"\nInventaire mis à jour : {INV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
