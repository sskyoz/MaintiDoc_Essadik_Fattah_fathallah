import json
from pathlib import Path

import pytest

pytest.importorskip("qdrant_client")

from maintidoc.qdrant_index import (
    compter,
    formater_resultats,
    indexer_document,
    ouvrir_client,
    rechercher,
)


def _ecrire_embeddings(dossier: Path) -> None:
    emb_dir = dossier / "embeddings"
    emb_dir.mkdir(parents=True)
    payload = {
        "document_id": "schema_pompe_a",
        "dimension": 3,
        "elements": [
            {
                "id": "schema_pompe_a:texte:1:0",
                "type": "texte",
                "document_id": "schema_pompe_a",
                "page": 1,
                "fragment": 0,
                "texte": "Alarme E41 temperature de palier",
                "source": str(dossier / "textes" / "page_001.txt"),
                "embedding": [1.0, 0.0, 0.0],
            },
            {
                "id": "schema_pompe_a:image:page_001_image_3.png",
                "type": "image",
                "document_id": "schema_pompe_a",
                "page": 1,
                "texte": "Image extraite",
                "source": str(dossier / "images" / "page_001_image_3.png"),
                "embedding": [0.0, 1.0, 0.0],
            },
        ],
    }
    (emb_dir / "embeddings.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )


def test_indexer_et_rechercher_texte(tmp_path, monkeypatch):
    dossier = tmp_path / "schema_pompe_a"
    _ecrire_embeddings(dossier)
    monkeypatch.setattr(
        "maintidoc.qdrant_index.charger_embeddings",
        lambda _doc: json.loads(
            (dossier / "embeddings" / "embeddings.json").read_text(encoding="utf-8")
        ),
    )
    monkeypatch.setattr(
        "maintidoc.qdrant_index.encoder_textes",
        lambda textes, **_kwargs: [[1.0, 0.0, 0.0] for _ in textes],
    )

    client = ouvrir_client(":memory:")
    assert indexer_document("schema_pompe_a", client=client) == 2
    assert compter(client) == 2

    resultats = rechercher(texte="E41", k=2, client=client)
    lignes = formater_resultats(resultats)
    assert lignes[0]["document_id"] == "schema_pompe_a"
    assert lignes[0]["type"] == "texte"
    assert lignes[0]["similarite"] >= lignes[-1]["similarite"]

    images = rechercher(texte="schema", type_resultat="image", k=1, client=client)
    assert formater_resultats(images)[0]["type"] == "image"
