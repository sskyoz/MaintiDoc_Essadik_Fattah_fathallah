from maintidoc.llm import (
    _normaliser_sortie_modele,
    charger_prompt_answer,
    charger_prompt_answer_rag,
    construire_prompt,
    construire_prompt_rag,
)


def test_prompt_answer_versionne():
    spec = charger_prompt_answer()
    assert spec["id"] == "answer_v1"
    texte = construire_prompt(
        question="Que signifie le code E41 ?",
        document_id="codes_alarme_pompe_a",
        page=2,
        element_id="tableau_2_1",
        extrait="E41 Température de palier élevée 80 °C",
    )
    assert "codes_alarme_pompe_a" in texte
    assert "tableau_2_1" in texte
    assert "80 °C" in texte
    assert "Que signifie le code E41 ?" in texte


def test_prompt_answer_rag_versionne():
    spec = charger_prompt_answer_rag()
    assert spec["id"] == "answer_rag_v1"
    texte = construire_prompt_rag(
        question="Que signifie E41 ?",
        sources=[
            {
                "document_id": "schema_pompe_a",
                "page": 2,
                "type": "texte",
                "texte": "E41 température de palier",
            }
        ],
    )
    assert "[S1]" in texte
    assert "schema_pompe_a" in texte
    assert "E41" in texte


def test_normaliser_sortie_modele_answer_null():
    donnees = _normaliser_sortie_modele(
        {
            "status": "answered",
            "answer": None,
            "uncertainties": None,
            "clarification_question": None,
        }
    )
    assert donnees["answer"] == "Réponse modèle incomplète."
    assert donnees["status"] == "abstained"
    assert donnees["citations"] == []
    assert donnees["proposed_action"] is None
