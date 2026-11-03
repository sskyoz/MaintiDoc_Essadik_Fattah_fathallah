import pytest
from pydantic import ValidationError

from maintidoc.schemas import MaintiDocAnswer


def test_clarification_valide():
    r = MaintiDocAnswer(
        status="needs_clarification",
        answer="Le modèle de l'équipement doit être confirmé.",
        clarification_question="Pouvez-vous photographier la plaque signalétique ?",
        uncertainties=["La plaque signalétique est illisible."],
    )
    assert r.proposed_action is None
    assert r.citations == []


def test_statut_invalide_refuse():
    with pytest.raises(ValidationError):
        MaintiDocAnswer(status="inconnu", answer="x")