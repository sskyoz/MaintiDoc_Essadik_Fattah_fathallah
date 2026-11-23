import json
from pathlib import Path

from maintidoc.vectorisation import (
    decouper_texte,
    numero_page,
    vectoriser_document,
)


class _BpeFactice:
    def encode(self, texte: str) -> list[str]:
        return texte.split()

    def decode(self, tokens: list[str]) -> str:
        return " ".join(tokens)


def test_numero_page():
    assert numero_page("page_012.txt") == 12
    assert numero_page(Path("page_003_image_7.png")) == 3
    assert numero_page("sans_page.png") == -1


def test_decouper_texte_avec_chevauchement():
    texte = " ".join(f"mot{i}" for i in range(25))
    fragments = list(decouper_texte(texte, taille=10, chevauchement=2, bpe=_BpeFactice()))
    assert len(fragments) >= 2
    assert all(fragments)


def test_vectoriser_document_sans_clip(monkeypatch, tmp_path):
    out = tmp_path / "schema_pompe_a"
    text_dir = out / "textes"
    image_dir = out / "images"
    text_dir.mkdir(parents=True)
    image_dir.mkdir(parents=True)
    (text_dir / "page_001.txt").write_text("Alarme E41 temperature palier", encoding="utf-8")
    (image_dir / "page_001_image_1.png").write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
        b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05"
        b"\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    monkeypatch.setattr(
        "maintidoc.vectorisation.dossier_sortie", lambda _doc: out
    )
    monkeypatch.setattr(
        "maintidoc.vectorisation.extraire_document",
        lambda _doc: None,
    )
    monkeypatch.setattr(
        "maintidoc.vectorisation.charger_clip",
        lambda: ("model", "preprocess", "tokenizer", "cpu"),
    )
    monkeypatch.setattr(
        "maintidoc.vectorisation.decouper_texte",
        lambda texte, taille=60, chevauchement=10, bpe=None: [texte.strip()],
    )
    monkeypatch.setattr(
        "maintidoc.vectorisation.encoder_textes",
        lambda textes, **_kwargs: [[0.1, 0.2, 0.3] for _ in textes],
    )
    monkeypatch.setattr(
        "maintidoc.vectorisation.encoder_image",
        lambda _chemin, **_kwargs: [0.4, 0.5, 0.6],
    )

    resultat = vectoriser_document("schema_pompe_a", extraire=True)
    assert resultat.nombre_fragments_texte == 1
    assert resultat.nombre_images == 1
    assert resultat.dimension == 3
    data = json.loads(resultat.fichier.read_text(encoding="utf-8"))
    assert data["nombre_elements"] == 2
    assert data["elements"][0]["type"] == "texte"
    assert data["elements"][1]["type"] == "image"
