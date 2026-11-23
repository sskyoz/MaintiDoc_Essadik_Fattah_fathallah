import pytest

from maintidoc.agent import (
    fiche_inventaire,
    lire_pages,
    racine_depot,
    travailler_sur_document,
)
from maintidoc.schemas import MaintiDocAnswer


def _redacteur_fixe(**kwargs) -> MaintiDocAnswer:
    return MaintiDocAnswer(
        status="answered",
        answer=(
            "Le code E41 signifie une température de palier élevée ; "
            "le seuil de déclenchement est 80 °C."
        ),
        uncertainties=[],
    )


def test_e41_cite_la_page_du_tableau():
    reponse = travailler_sur_document(
        "codes_alarme_pompe_a",
        "Que signifie le code E41 ?",
        rediger=_redacteur_fixe,
    )
    assert reponse.status == "answered"
    assert len(reponse.citations) == 1
    citation = reponse.citations[0]
    assert citation.document_id == "codes_alarme_pompe_a"
    assert citation.page == 2
    assert citation.element_id == "tableau_2_1"
    assert "palier" in reponse.answer.lower()
    assert "80" in reponse.answer
    assert "E41 Température de palier élevée" not in reponse.answer

    fiche = fiche_inventaire("codes_alarme_pompe_a")
    pages = dict(lire_pages(racine_depot() / "corpus" / fiche["fichier"]))
    assert "e41" in pages[citation.page].lower()
    assert "80" in pages[citation.page]


def test_redacteur_recoit_lextrait_de_la_page():
    recu = {}

    def espion(**kwargs):
        recu.update(kwargs)
        return MaintiDocAnswer(status="answered", answer="ok")

    reponse = travailler_sur_document(
        "codes_alarme_pompe_a",
        "Que signifie le code E41 ?",
        rediger=espion,
    )
    assert reponse.status == "answered"
    assert recu["page"] == 2
    assert recu["document_id"] == "codes_alarme_pompe_a"
    assert "E41" in recu["extrait"]
    assert "80" in recu["extrait"]


def test_question_sans_rapport_sabstient():
    def interdit(**_kwargs):
        raise AssertionError("le modèle ne doit pas être appelé sans extrait")

    reponse = travailler_sur_document(
        "codes_alarme_pompe_a",
        "Quel est le couple de serrage du bouchon ?",
        rediger=interdit,
    )
    assert reponse.status == "abstained"
    assert reponse.citations == []


def test_autre_groupe_ne_lit_pas_le_document():
    def interdit(**_kwargs):
        raise AssertionError("le modèle ne doit pas être appelé si l'accès est refusé")

    reponse = travailler_sur_document(
        "codes_alarme_pompe_a",
        "Que signifie le code E41 ?",
        groupe="techniciens_compresseurs",
        rediger=interdit,
    )
    assert reponse.status == "abstained"
    assert reponse.citations == []
    assert "palier" not in reponse.answer.lower()
    assert "80" not in reponse.answer


def test_responsable_lit_le_document():
    reponse = travailler_sur_document(
        "codes_alarme_pompe_a",
        "Que signifie le code E41 ?",
        groupe="responsables",
        rediger=_redacteur_fixe,
    )
    assert reponse.status == "answered"
    assert reponse.citations[0].page == 2


def test_scan_sans_texte_sabstient():
    def interdit(**_kwargs):
        raise AssertionError("le modèle ne doit pas être appelé sans texte")

    reponse = travailler_sur_document(
        "proc_vidange_pompe_a_v1",
        "Quel est le couple de serrage ?",
        rediger=interdit,
    )
    assert reponse.status == "abstained"
    assert reponse.citations == []
    assert "18" not in reponse.answer
    assert "25" not in reponse.answer


def test_image_sans_texte_sabstient():
    def interdit(**_kwargs):
        raise AssertionError("le modèle ne doit pas être appelé pour une image")

    reponse = travailler_sur_document(
        "photo_panneau_pompe_a",
        "Que signifie le voyant orange ?",
        rediger=interdit,
    )
    assert reponse.status == "abstained"
    assert reponse.citations == []


def test_question_vide_demande_une_precision():
    reponse = travailler_sur_document(
        "codes_alarme_pompe_a", "  ", rediger=_redacteur_fixe
    )
    assert reponse.status == "needs_clarification"
    assert reponse.clarification_question


def test_document_inconnu():
    with pytest.raises(LookupError):
        travailler_sur_document("document_inexistant", "E41", rediger=_redacteur_fixe)
