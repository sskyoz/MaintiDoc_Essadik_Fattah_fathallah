from maintidoc.rag import (
    filtrer_par_groupe,
    filtrer_sources_code,
    rag,
    rerank_lexical,
)
from maintidoc.schemas import MaintiDocAnswer


def test_rerank_lexical_priorise_le_code():
    lignes = [
        {
            "document_id": "schema_pompe_a",
            "texte": "capteur e41 température",
            "similarite": 0.9,
        },
        {
            "document_id": "codes_alarme_pompe_a",
            "texte": "e 4 1 température de palier élevée 80 C alerte",
            "similarite": 0.4,
        },
    ]
    ordonnees = rerank_lexical("Que signifie E41 ?", lignes)
    assert ordonnees[0]["document_id"] == "codes_alarme_pompe_a"


def test_filtrer_sources_code():
    lignes = [
        {"document_id": "a", "texte": "pression nominale"},
        {"document_id": "b", "texte": "E41 Température de palier"},
    ]
    assert filtrer_sources_code("Que signifie E41 ?", lignes) == [lignes[1]]


def test_filtrer_par_groupe(monkeypatch):
    monkeypatch.setattr(
        "maintidoc.rag._inventaire_groupes",
        lambda: {
            "schema_pompe_a": {"techniciens_pompes", "responsables"},
            "note_service_compresseurs": {"responsables"},
        },
    )
    lignes = [
        {"document_id": "schema_pompe_a", "texte": "ok"},
        {"document_id": "note_service_compresseurs", "texte": "secret"},
    ]
    filtrées = filtrer_par_groupe(lignes, "techniciens_pompes")
    assert len(filtrées) == 1
    assert filtrées[0]["document_id"] == "schema_pompe_a"


def test_rag_chroma_vers_reponse(monkeypatch):
    monkeypatch.setattr(
        "maintidoc.rag.rechercher",
        lambda **_kwargs: {
            "documents": [["E41 temperature de palier 80 C"]],
            "metadatas": [
                [
                    {
                        "type": "texte",
                        "document_id": "codes_alarme_pompe_a",
                        "page": 2,
                        "source": "x",
                        "fragment": 1,
                    }
                ]
            ],
            "distances": [[0.2]],
        },
    )
    monkeypatch.setattr(
        "maintidoc.rag.completer_par_mots_cles",
        lambda question, lignes, collection=None: lignes,
    )

    def fake_rediger(**kwargs):
        assert kwargs["sources"][0]["document_id"] == "codes_alarme_pompe_a"
        return MaintiDocAnswer(
            status="answered",
            answer="E41 concerne la température de palier (80 °C).",
        )

    reponse = rag("Que signifie E41 ?", rediger=fake_rediger, k=1)
    assert reponse.status == "answered"
    assert "80" in reponse.answer
    assert reponse.citations[0].document_id == "codes_alarme_pompe_a"
    assert reponse.citations[0].page == 2


def test_rag_groupe_sans_acces(monkeypatch):
    monkeypatch.setattr(
        "maintidoc.rag.rechercher",
        lambda **_kwargs: {
            "documents": [["secret"]],
            "metadatas": [
                [
                    {
                        "type": "texte",
                        "document_id": "note_service_compresseurs",
                        "page": 1,
                        "source": "x",
                    }
                ]
            ],
            "distances": [[0.1]],
        },
    )
    monkeypatch.setattr(
        "maintidoc.rag._inventaire_groupes",
        lambda: {"note_service_compresseurs": {"responsables"}},
    )
    monkeypatch.setattr(
        "maintidoc.rag.completer_par_mots_cles",
        lambda question, lignes, collection=None: lignes,
    )

    def interdit(**_kwargs):
        raise AssertionError("ne doit pas rédiger sans source accessible")

    reponse = rag(
        "que dit la note ?",
        groupe="techniciens_pompes",
        rediger=interdit,
    )
    assert reponse.status == "abstained"
    assert reponse.citations == []
