from maintidoc.llm import charger_prompt_answer, construire_prompt


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
