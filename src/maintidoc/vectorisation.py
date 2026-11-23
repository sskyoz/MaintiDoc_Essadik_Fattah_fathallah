"""Découpage et vectorisation CLIP (notebook cours), sans ChromaDB.

Les embeddings sont enregistrés en JSON sous data/processed/<document_id>/embeddings/
pour pouvoir les charger plus tard dans une base vectorielle.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

from maintidoc.clip_smoke import MODEL_NAME, PRETRAINED, charger_clip
from maintidoc.extraction import dossier_sortie, extraire_document

EXTENSIONS_IMAGE = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff", ".jp2"}


def numero_page(chemin: Path | str) -> int:
    correspondance = re.search(r"page_(\d+)", Path(chemin).stem)
    return int(correspondance.group(1)) if correspondance else -1


def decouper_texte(
    texte: str,
    taille: int = 60,
    chevauchement: int = 10,
    bpe=None,
) -> Iterator[str]:
    """Découper le texte en fragments courts adaptés à CLIP (tokens BPE)."""
    if not 0 <= chevauchement < taille:
        raise ValueError("Le chevauchement doit être inférieur à la taille.")
    if bpe is None:
        from open_clip.tokenizer import SimpleTokenizer

        bpe = SimpleTokenizer()
    tokens = bpe.encode(texte)
    for debut in range(0, len(tokens), taille - chevauchement):
        fragment = bpe.decode(tokens[debut : debut + taille]).strip()
        if fragment:
            yield fragment
        if debut + taille >= len(tokens):
            break


def encoder_textes(
    textes: list[str],
    *,
    model=None,
    tokenizer=None,
    device: str | None = None,
) -> list[list[float]]:
    import torch

    if model is None or tokenizer is None or device is None:
        model, _preprocess, tokenizer, device = charger_clip()
    with torch.inference_mode():
        tokens = tokenizer(textes).to(device)
        vecteurs = model.encode_text(tokens).float()
        vecteurs = vecteurs / vecteurs.norm(dim=-1, keepdim=True).clamp_min(1e-12)
    return vecteurs.cpu().tolist()


def encoder_image(
    chemin: Path | str,
    *,
    model=None,
    preprocess=None,
    device: str | None = None,
) -> list[float]:
    import torch
    from PIL import Image

    if model is None or preprocess is None or device is None:
        model, preprocess, _tokenizer, device = charger_clip()
    with Image.open(chemin) as image:
        tenseur = preprocess(image.convert("RGB")).unsqueeze(0).to(device)
    with torch.inference_mode():
        vecteur = model.encode_image(tenseur).float()
        vecteur = vecteur / vecteur.norm(dim=-1, keepdim=True).clamp_min(1e-12)
    return vecteur.cpu().tolist()[0]


@dataclass
class ResultatVectorisation:
    document_id: str
    fichier: Path
    nombre_fragments_texte: int
    nombre_images: int
    dimension: int


def vectoriser_document(
    document_id: str,
    *,
    extraire: bool = True,
    taille: int = 60,
    chevauchement: int = 10,
    taille_lot: int = 32,
) -> ResultatVectorisation:
    """Découpe, encode, et écrit embeddings.json (pas de ChromaDB)."""
    if extraire:
        extraire_document(document_id)

    output_dir = dossier_sortie(document_id)
    text_dir = output_dir / "textes"
    image_dir = output_dir / "images"
    if not text_dir.is_dir():
        raise FileNotFoundError(
            f"Pas de textes extraits pour {document_id}. Lancez d'abord l'extraction."
        )

    model, preprocess, tokenizer, device = charger_clip()
    elements: list[dict[str, object]] = []

    fragments: list[tuple[int, int, str, Path]] = []
    for fichier in sorted(text_dir.glob("page_*.txt")):
        page = numero_page(fichier)
        texte = fichier.read_text(encoding="utf-8")
        for index, fragment in enumerate(
            decouper_texte(texte, taille=taille, chevauchement=chevauchement)
        ):
            fragments.append((page, index, fragment, fichier))

    for debut in range(0, len(fragments), taille_lot):
        lot = fragments[debut : debut + taille_lot]
        vecteurs = encoder_textes(
            [f[2] for f in lot],
            model=model,
            tokenizer=tokenizer,
            device=device,
        )
        for (page, index, fragment, fichier), vecteur in zip(lot, vecteurs, strict=True):
            elements.append(
                {
                    "id": f"{document_id}:texte:{page}:{index}",
                    "type": "texte",
                    "document_id": document_id,
                    "page": page,
                    "fragment": index,
                    "texte": fragment,
                    "source": str(fichier.resolve()),
                    "embedding": vecteur,
                }
            )

    nombre_images = 0
    if image_dir.is_dir():
        for fichier in sorted(image_dir.iterdir()):
            if not fichier.is_file() or fichier.suffix.lower() not in EXTENSIONS_IMAGE:
                continue
            try:
                vecteur = encoder_image(
                    fichier, model=model, preprocess=preprocess, device=device
                )
            except Exception as erreur:  # noqa: BLE001 — même tolérance que le notebook
                print(f"Image ignorée : {fichier.name} — {erreur}")
                continue
            elements.append(
                {
                    "id": f"{document_id}:image:{fichier.name}",
                    "type": "image",
                    "document_id": document_id,
                    "page": numero_page(fichier),
                    "texte": f"Image extraite du PDF : {fichier.name}",
                    "source": str(fichier.resolve()),
                    "embedding": vecteur,
                }
            )
            nombre_images += 1

    emb_dir = output_dir / "embeddings"
    emb_dir.mkdir(parents=True, exist_ok=True)
    fichier = emb_dir / "embeddings.json"
    payload = {
        "document_id": document_id,
        "modele": MODEL_NAME,
        "pretrained": PRETRAINED,
        "device": device,
        "dimension": len(elements[0]["embedding"]) if elements else 0,
        "nombre_elements": len(elements),
        "elements": elements,
    }
    fichier.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return ResultatVectorisation(
        document_id=document_id,
        fichier=fichier,
        nombre_fragments_texte=sum(1 for e in elements if e["type"] == "texte"),
        nombre_images=nombre_images,
        dimension=payload["dimension"],
    )


def charger_embeddings(document_id: str) -> dict[str, object]:
    fichier = dossier_sortie(document_id) / "embeddings" / "embeddings.json"
    if not fichier.is_file():
        raise FileNotFoundError(f"Embeddings introuvables : {fichier}")
    return json.loads(fichier.read_text(encoding="utf-8"))


def apercu_vectorisation(document_id: str, n: int = 3) -> Iterable[dict[str, object]]:
    data = charger_embeddings(document_id)
    for element in data["elements"][:n]:
        emb = element["embedding"]
        yield {
            "id": element["id"],
            "type": element["type"],
            "page": element["page"],
            "texte": str(element.get("texte", ""))[:120],
            "dimension": len(emb),
            "embedding_5": emb[:5],
        }
