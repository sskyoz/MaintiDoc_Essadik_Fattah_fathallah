"""Extraction texte/images d'un PDF du corpus (étape notebook jusqu'à l'aperçu)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from maintidoc.agent import fiche_inventaire, racine_depot


@dataclass
class ResultatExtraction:
    document_id: str
    pdf: Path
    output_dir: Path
    text_dir: Path
    image_dir: Path
    nombre_pages: int
    nombre_images: int
    pages_sans_texte: list[int]


def dossier_sortie(document_id: str) -> Path:
    return racine_depot() / "data" / "processed" / document_id


def chemin_pdf(document_id: str) -> Path:
    fiche = fiche_inventaire(document_id)
    if fiche["format"] == "image":
        raise ValueError(f"{document_id} est une image, pas un PDF.")
    chemin = racine_depot() / "corpus" / fiche["fichier"]
    if not chemin.is_file():
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")
    return chemin


def extraire_document(document_id: str) -> ResultatExtraction:
    """Reprend l'étape d'extraction du notebook du cours, sur un document inventorié."""
    import pymupdf

    pdf = chemin_pdf(document_id)
    output_dir = dossier_sortie(document_id)
    text_dir = output_dir / "textes"
    image_dir = output_dir / "images"
    text_dir.mkdir(parents=True, exist_ok=True)
    image_dir.mkdir(parents=True, exist_ok=True)

    textes: list[str] = []
    nombre_images = 0
    pages_sans_texte: list[int] = []

    with pymupdf.open(pdf) as document:
        nombre_pages = len(document)
        for numero_page, page in enumerate(document, start=1):
            texte = page.get_text("text", sort=True)
            (text_dir / f"page_{numero_page:03d}.txt").write_text(texte, encoding="utf-8")
            textes.append(f"===== PAGE {numero_page} =====\n\n{texte}")
            if not texte.strip():
                pages_sans_texte.append(numero_page)

            images_vues: set[int] = set()
            for image_info in page.get_images(full=True):
                xref = image_info[0]
                if xref in images_vues:
                    continue
                images_vues.add(xref)
                try:
                    image = document.extract_image(xref)
                    if not image:
                        continue
                    extension = image["ext"]
                    fichier = image_dir / f"page_{numero_page:03d}_image_{xref}.{extension}"
                    fichier.write_bytes(image["image"])
                    nombre_images += 1
                except Exception as erreur:  # noqa: BLE001 — même tolérance que le notebook
                    print(
                        f"Erreur d'extraction : page {numero_page}, "
                        f"image {xref} : {erreur}"
                    )

    (output_dir / "texte_complet.txt").write_text("\n\n".join(textes), encoding="utf-8")
    return ResultatExtraction(
        document_id=document_id,
        pdf=pdf,
        output_dir=output_dir,
        text_dir=text_dir,
        image_dir=image_dir,
        nombre_pages=nombre_pages,
        nombre_images=nombre_images,
        pages_sans_texte=pages_sans_texte,
    )


def apercu_extraction(
    document_id: str,
    *,
    max_chars: int = 2000,
    max_images: int = 5,
) -> dict[str, object]:
    """Aperçu texte + liste d'images, comme la cellule « Afficher un aperçu des résultats »."""
    output_dir = dossier_sortie(document_id)
    image_dir = output_dir / "images"
    texte_complet = (output_dir / "texte_complet.txt").read_text(encoding="utf-8")
    images = sorted(p for p in image_dir.iterdir() if p.is_file())[:max_images]
    vignettes_dir = output_dir / "vignettes"
    vignettes_dir.mkdir(parents=True, exist_ok=True)
    vignettes: list[Path] = []
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Installez pillow pour l'aperçu des images.") from exc
    for fichier in images:
        with Image.open(fichier) as image:
            apercu = image.copy()
            apercu.thumbnail((600, 600))
            cible = vignettes_dir / f"apercu_{fichier.stem}.png"
            apercu.save(cible)
            vignettes.append(cible)
    return {
        "document_id": document_id,
        "texte_apercu": texte_complet[:max_chars],
        "images": [str(p) for p in images],
        "vignettes": [str(p) for p in vignettes],
        "output_dir": str(output_dir),
    }
