"""Indexation et recherche ChromaDB à partir des embeddings CLIP locaux."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

from maintidoc.agent import racine_depot
from maintidoc.vectorisation import charger_embeddings, encoder_image, encoder_textes

COLLECTION = "maintidoc_clip_vit_b32"
TypeResultat = Literal["texte", "image"] | None


def dossier_chroma() -> Path:
    env = os.environ.get("MAINTIDOC_CHROMA_DIR")
    if env:
        return Path(env)
    return racine_depot() / "data" / "chroma"


def ouvrir_collection(chemin: Path | None = None):
    """Ouvre (ou crée) la collection CLIP persistante."""
    import chromadb

    racine = chemin or dossier_chroma()
    racine.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(racine))
    return client.get_or_create_collection(
        name=COLLECTION,
        embedding_function=None,
        metadata={"hnsw:space": "cosine"},
    )


def _meta(element: dict[str, Any]) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "type": element["type"],
        "document_id": element["document_id"],
        "page": int(element["page"]),
        "source": str(element["source"]),
    }
    if "fragment" in element and element["fragment"] is not None:
        meta["fragment"] = int(element["fragment"])
    return meta


def indexer_document(document_id: str, *, collection=None) -> int:
    """Charge embeddings.json et upsert dans ChromaDB (remplace l'ancien index du doc)."""
    data = charger_embeddings(document_id)
    elements = data["elements"]
    if not elements:
        return 0

    col = collection or ouvrir_collection()
    col.delete(where={"document_id": document_id})

    ids = [str(e["id"]) for e in elements]
    documents = [str(e.get("texte", "")) for e in elements]
    metadatas = [_meta(e) for e in elements]
    embeddings = [e["embedding"] for e in elements]

    taille_lot = 64
    for debut in range(0, len(ids), taille_lot):
        fin = debut + taille_lot
        col.upsert(
            ids=ids[debut:fin],
            documents=documents[debut:fin],
            metadatas=metadatas[debut:fin],
            embeddings=embeddings[debut:fin],
        )
    return len(ids)


def documents_vectorises() -> list[str]:
    processed = racine_depot() / "data" / "processed"
    if not processed.is_dir():
        return []
    ids = []
    for dossier in sorted(processed.iterdir()):
        if (dossier / "embeddings" / "embeddings.json").is_file():
            ids.append(dossier.name)
    return ids


def indexer_corpus(*, collection=None) -> dict[str, int]:
    col = collection or ouvrir_collection()
    return {doc_id: indexer_document(doc_id, collection=col) for doc_id in documents_vectorises()}


def rechercher(
    *,
    texte: str | None = None,
    image: str | Path | None = None,
    type_resultat: TypeResultat = None,
    k: int = 5,
    collection=None,
) -> dict[str, Any]:
    """Recherche multimodale : fournir soit un texte, soit une image."""
    if (texte is None) == (image is None):
        raise ValueError("Fournissez soit un texte, soit une image.")
    if type_resultat not in (None, "texte", "image"):
        raise ValueError("type_resultat doit être 'texte', 'image' ou None.")
    if k < 1:
        raise ValueError("k doit être supérieur ou égal à 1.")

    col = collection or ouvrir_collection()
    total = col.count()
    if total == 0:
        raise ValueError("La collection est vide. Indexez d'abord un document.")

    vecteur = (
        encoder_textes([texte])[0]
        if texte is not None
        else encoder_image(image)
    )
    options: dict[str, Any] = {}
    if type_resultat is not None:
        options["where"] = {"type": type_resultat}

    return col.query(
        query_embeddings=[vecteur],
        n_results=min(k, total),
        include=["documents", "metadatas", "distances"],
        **options,
    )


def formater_resultats(resultats: dict[str, Any]) -> list[dict[str, Any]]:
    """Convertit la sortie Chroma en liste simple (similarité = 1 - distance cosinus)."""
    docs = resultats["documents"][0]
    metas = resultats["metadatas"][0]
    dists = resultats["distances"][0]
    lignes = []
    for rang, (document, meta, distance) in enumerate(
        zip(docs, metas, dists, strict=True), start=1
    ):
        ligne = {
            "rang": rang,
            "type": meta.get("type"),
            "document_id": meta.get("document_id"),
            "page": meta.get("page"),
            "source": meta.get("source"),
            "distance": distance,
            "similarite": 1.0 - float(distance),
            "texte": document,
        }
        if "fragment" in meta:
            ligne["fragment"] = meta["fragment"]
        lignes.append(ligne)
    return lignes
