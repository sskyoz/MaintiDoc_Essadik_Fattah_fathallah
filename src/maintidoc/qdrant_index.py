"""Indexation et recherche Qdrant à partir des embeddings CLIP locaux.

Par défaut : stockage embarqué sous data/qdrant (sans Docker).
Serveur Docker Compose : MAINTIDOC_QDRANT_URL=http://127.0.0.1:6333
Tests : QdrantClient(\":memory:\") passé en argument client=.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any, Literal

from maintidoc.agent import racine_depot
from maintidoc.vectorisation import charger_embeddings, encoder_image, encoder_textes

COLLECTION = "maintidoc_clip_vit_b32"
TypeResultat = Literal["texte", "image"] | None


def dossier_qdrant() -> Path:
    env = os.environ.get("MAINTIDOC_QDRANT_DIR")
    if env:
        return Path(env)
    return racine_depot() / "data" / "qdrant"


def url_qdrant() -> str | None:
    return os.environ.get("MAINTIDOC_QDRANT_URL")


def ouvrir_client(chemin: Path | str | None = None):
    """Ouvre un client Qdrant (URL, chemin embarqué, ou :memory:)."""
    from qdrant_client import QdrantClient

    if chemin == ":memory:":
        return QdrantClient(":memory:")
    if chemin is None:
        url = url_qdrant()
        if url:
            return QdrantClient(url=url)
        racine = dossier_qdrant()
        racine.mkdir(parents=True, exist_ok=True)
        return QdrantClient(path=str(racine))
    if isinstance(chemin, str) and chemin.startswith("http"):
        return QdrantClient(url=chemin)
    racine = Path(chemin)
    racine.mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=str(racine))


def _point_id(element_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, element_id))


def _payload(element: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "element_id": str(element["id"]),
        "texte": str(element.get("texte", "")),
        "type": element["type"],
        "document_id": element["document_id"],
        "page": int(element["page"]),
        "source": str(element["source"]),
    }
    if "fragment" in element and element["fragment"] is not None:
        payload["fragment"] = int(element["fragment"])
    return payload


def assurer_collection(client, dimension: int, *, collection: str = COLLECTION) -> None:
    """Crée la collection CLIP si besoin (distance cosinus)."""
    from qdrant_client.models import Distance, VectorParams

    existantes = {c.name for c in client.get_collections().collections}
    if collection in existantes:
        info = client.get_collection(collection)
        taille = info.config.params.vectors.size
        if taille != dimension:
            raise ValueError(
                f"Collection {collection} en dim {taille}, embeddings en dim {dimension}."
            )
        return
    client.create_collection(
        collection_name=collection,
        vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
    )


def compter(client, *, collection: str = COLLECTION) -> int:
    existantes = {c.name for c in client.get_collections().collections}
    if collection not in existantes:
        return 0
    return int(client.count(collection_name=collection).count)


def indexer_document(
    document_id: str,
    *,
    client=None,
    collection: str = COLLECTION,
) -> int:
    """Charge embeddings.json et upsert dans Qdrant (remplace l'ancien index du doc)."""
    from qdrant_client.models import (
        FieldCondition,
        Filter,
        FilterSelector,
        MatchValue,
        PointStruct,
    )

    data = charger_embeddings(document_id)
    elements = data["elements"]
    if not elements:
        return 0

    cli = client or ouvrir_client()
    dimension = len(elements[0]["embedding"])
    assurer_collection(cli, dimension, collection=collection)

    if compter(cli, collection=collection) > 0:
        cli.delete(
            collection_name=collection,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id),
                        )
                    ]
                )
            ),
        )

    points = [
        PointStruct(
            id=_point_id(str(e["id"])),
            vector=list(e["embedding"]),
            payload=_payload(e),
        )
        for e in elements
    ]
    taille_lot = 64
    for debut in range(0, len(points), taille_lot):
        cli.upsert(collection_name=collection, points=points[debut : debut + taille_lot])
    return len(points)


def documents_vectorises() -> list[str]:
    processed = racine_depot() / "data" / "processed"
    if not processed.is_dir():
        return []
    ids = []
    for dossier in sorted(processed.iterdir()):
        if (dossier / "embeddings" / "embeddings.json").is_file():
            ids.append(dossier.name)
    return ids


def indexer_corpus(*, client=None, collection: str = COLLECTION) -> dict[str, int]:
    cli = client or ouvrir_client()
    return {
        doc_id: indexer_document(doc_id, client=cli, collection=collection)
        for doc_id in documents_vectorises()
    }


def rechercher(
    *,
    texte: str | None = None,
    image: str | Path | None = None,
    type_resultat: TypeResultat = None,
    k: int = 5,
    client=None,
    collection: str = COLLECTION,
) -> dict[str, Any]:
    """Recherche multimodale : fournir soit un texte, soit une image."""
    from qdrant_client.models import FieldCondition, Filter, MatchValue

    if (texte is None) == (image is None):
        raise ValueError("Fournissez soit un texte, soit une image.")
    if type_resultat not in (None, "texte", "image"):
        raise ValueError("type_resultat doit être 'texte', 'image' ou None.")
    if k < 1:
        raise ValueError("k doit être supérieur ou égal à 1.")

    cli = client or ouvrir_client()
    total = compter(cli, collection=collection)
    if total == 0:
        raise ValueError("La collection est vide. Indexez d'abord un document.")

    vecteur = (
        encoder_textes([texte])[0]
        if texte is not None
        else encoder_image(image)
    )
    filtre = None
    if type_resultat is not None:
        filtre = Filter(
            must=[FieldCondition(key="type", match=MatchValue(value=type_resultat))]
        )

    hits = cli.query_points(
        collection_name=collection,
        query=vecteur,
        query_filter=filtre,
        limit=min(k, total),
        with_payload=True,
    ).points

    documents: list[str] = []
    metadatas: list[dict[str, Any]] = []
    distances: list[float] = []
    for hit in hits:
        payload = dict(hit.payload or {})
        documents.append(str(payload.pop("texte", "")))
        payload.pop("element_id", None)
        metadatas.append(payload)
        # Qdrant COSINE : score = similarité → distance type Chroma = 1 - score
        distances.append(1.0 - float(hit.score))

    return {
        "documents": [documents],
        "metadatas": [metadatas],
        "distances": [distances],
    }


def formater_resultats(resultats: dict[str, Any]) -> list[dict[str, Any]]:
    """Convertit la sortie recherche en liste simple (similarité = 1 - distance)."""
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


def lister_passages(
    *,
    type_resultat: TypeResultat = "texte",
    client=None,
    collection: str = COLLECTION,
) -> list[dict[str, Any]]:
    """Parcourt les payloads indexés (complément lexical pour les codes d'alarme)."""
    from qdrant_client.models import FieldCondition, Filter, MatchValue

    cli = client or ouvrir_client()
    if compter(cli, collection=collection) == 0:
        return []

    filtre = None
    if type_resultat is not None:
        filtre = Filter(
            must=[FieldCondition(key="type", match=MatchValue(value=type_resultat))]
        )

    lignes: list[dict[str, Any]] = []
    offset = None
    while True:
        points, offset = cli.scroll(
            collection_name=collection,
            scroll_filter=filtre,
            limit=128,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        for point in points:
            payload = dict(point.payload or {})
            ligne = {
                "rang": 0,
                "type": payload.get("type"),
                "document_id": payload.get("document_id"),
                "page": payload.get("page"),
                "source": payload.get("source"),
                "distance": 1.0,
                "similarite": 0.0,
                "texte": payload.get("texte", ""),
            }
            if "fragment" in payload:
                ligne["fragment"] = payload["fragment"]
            lignes.append(ligne)
        if offset is None:
            break
    return lignes
