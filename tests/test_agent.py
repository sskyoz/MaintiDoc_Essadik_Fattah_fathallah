import pytest

from maintidoc.agent import (
    fiche_inventaire,
    lire_pages,
    racine_depot,
    travailler_sur_document,
)


def test_e41_cite_la_page_du_tableau():
    reponse = travailler_sur_document(
        "codes_alarme_pompe_a", "Que signifie le code E41 ?"
    )
    assert reponse.status == "answered"
    assert len(reponse.citations) == 1
    citation = reponse.citations[0]
    assert citation.document_id == "codes_alarme_pompe_a"
    assert citation.page == 2
    assert citation.element_id == "tableau_2_1"
    assert "palier" in reponse.answer.lower()
    assert "80" in reponse.answer

    fiche = fiche_inventaire("codes_alarme_pompe_a")
    pages = dict(lire_pages(racine_depot() / "corpus" / fiche["fichier"]))
    assert " ".join(reponse.answer.split()) in " ".join(pages[citation.page].split())
    assert "e41" in pages[citation.page].lower()


def test_question_sans_rapport_sabstient():
    reponse = travailler_sur_document(
        "codes_alarme_pompe_a", "Quel est le couple de serrage du bouchon ?"
    )
    assert reponse.status == "abstained"
    assert reponse.citations == []


def test_autre_groupe_ne_lit_pas_le_document():
    reponse = travailler_sur_document(
        "codes_alarme_pompe_a",
        "Que signifie le code E41 ?",
        groupe="techniciens_compresseurs",
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
    )
    assert reponse.status == "answered"
    assert reponse.citations[0].page == 2


def test_scan_sans_texte_sabstient():
    reponse = travailler_sur_document(
        "proc_vidange_pompe_a_v1", "Quel est le couple de serrage ?"
    )
    assert reponse.status == "abstained"
    assert reponse.citations == []
    assert "18" not in reponse.answer
    assert "25" not in reponse.answer


def test_image_sans_texte_sabstient():
    reponse = travailler_sur_document(
        "photo_panneau_pompe_a", "Que signifie le voyant orange ?"
    )
    assert reponse.status == "abstained"
    assert reponse.citations == []


def test_question_vide_demande_une_precision():
    reponse = travailler_sur_document("codes_alarme_pompe_a", "  ")
    assert reponse.status == "needs_clarification"
    assert reponse.clarification_question


def test_document_inconnu():
    with pytest.raises(LookupError):
        travailler_sur_document("document_inexistant", "E41")
