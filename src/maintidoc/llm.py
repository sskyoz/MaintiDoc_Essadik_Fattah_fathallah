"""Rédaction locale via Ollama, à partir d'un extrait déjà récupéré."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml

from maintidoc.schemas import MaintiDocAnswer

PROMPT_ANSWER = Path(__file__).resolve().parents[2] / "prompts" / "answer_v1.yaml"
JSON_BLOC = re.compile(r"\{.*\}", re.DOTALL)


def charger_prompt_answer() -> dict[str, Any]:
    return yaml.safe_load(PROMPT_ANSWER.read_text(encoding="utf-8"))


def construire_prompt(
    *,
    question: str,
    document_id: str,
    page: int,
    element_id: str,
    extrait: str,
) -> str:
    spec = charger_prompt_answer()
    return spec["prompt"].format(
        question=question,
        document_id=document_id,
        page=page,
        element_id=element_id,
        extrait=extrait,
    )


def _base_ollama() -> str:
    return os.environ.get("MAINTIDOC_OLLAMA_BASE", "http://127.0.0.1:11434").rstrip("/")


def _modele_ollama() -> str:
    return os.environ.get("MAINTIDOC_OLLAMA_MODEL", "qwen2.5:3b")


def appeler_ollama(prompt: str) -> str:
    payload = {
        "model": _modele_ollama(),
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1},
    }
    requete = urllib.request.Request(
        f"{_base_ollama()}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(requete, timeout=180) as reponse:
            corps = json.load(reponse)
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Ollama inaccessible. Lancez `ollama serve` et tirez le modèle "
            f"`ollama pull {_modele_ollama()}`."
        ) from exc
    texte = corps.get("response", "")
    if not isinstance(texte, str) or not texte.strip():
        raise RuntimeError("Ollama a renvoyé une réponse vide.")
    return texte


def _parser_json(texte: str) -> dict[str, Any]:
    try:
        donnees = json.loads(texte)
    except json.JSONDecodeError:
        match = JSON_BLOC.search(texte)
        if not match:
            raise
        donnees = json.loads(match.group(0))
    if not isinstance(donnees, dict):
        raise TypeError("La sortie du modèle n'est pas un objet JSON.")
    return donnees


def rediger_reponse(
    *,
    question: str,
    document_id: str,
    page: int,
    element_id: str,
    extrait: str,
) -> MaintiDocAnswer:
    """Demande au modèle local une réponse structurée ; sans citations inventées."""
    prompt = construire_prompt(
        question=question,
        document_id=document_id,
        page=page,
        element_id=element_id,
        extrait=extrait,
    )
    brut = appeler_ollama(prompt)
    donnees = _parser_json(brut)
    donnees["citations"] = []
    donnees["proposed_action"] = None
    return MaintiDocAnswer.model_validate(donnees)
