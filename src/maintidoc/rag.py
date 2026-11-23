"""RAG MaintiDoc : Qdrant → contexte → Ollama → MaintiDocAnswer."""

from __future__ import annotations

import csv
import json
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from maintidoc.agent import _termes, plier, racine_depot
from maintidoc.qdrant_index import (
    formater_resultats,
    lister_passages,
    ouvrir_client,
    rechercher,
)
from maintidoc.schemas import Citation, MaintiDocAnswer

RedacteurRag = Callable[..., MaintiDocAnswer]
CODE_ALARME = re.compile(r"\be\s*(\d)\s*(\d)\b", re.IGNORECASE)


def _inventaire_groupes() -> dict[str, set[str]]:
    chemin = racine_depot() / "corpus" / "inventaire.csv"
    mapping: dict[str, set[str]] = {}
    with chemin.open(encoding="utf-8-sig", newline="") as fichier:
        for ligne in csv.DictReader(fichier):
            mapping[ligne["document_id"]] = {
                g.strip() for g in ligne["groupe_acces"].split(";") if g.strip()
            }
    return mapping


def filtrer_par_groupe(
    lignes: list[dict[str, Any]], groupe: str | None
) -> list[dict[str, Any]]:
    if groupe is None:
        return lignes
    acces = _inventaire_groupes()
    return [
        ligne
        for ligne in lignes
        if groupe in acces.get(str(ligne.get("document_id")), set())
    ]


def _citations_depuis_sources(sources: list[dict[str, Any]]) -> list[Citation]:
    vues: set[tuple[str, int]] = set()
    citations: list[Citation] = []
    for source in sources:
        doc = str(source["document_id"])
        page = int(source["page"])
        cle = (doc, page)
        if cle in vues:
            continue
        vues.add(cle)
        fragment = source.get("fragment")
        element_id = (
            f"fragment_{fragment}" if fragment is not None else f"passage_p{page}"
        )
        citations.append(
            Citation(document_id=doc, page=page, element_id=element_id)
        )
    return citations


def _texte_indexable(texte: str) -> str:
    """Normalise le texte indexé (y compris anciens fragments BPE « e 4 1 »)."""
    normalise = CODE_ALARME.sub(lambda m: f"e{m.group(1)}{m.group(2)}", plier(texte))
    return re.sub(r"\s+", " ", normalise)


def _codes_question(question: str) -> list[str]:
    return [t for t in _termes(question) if re.fullmatch(r"e\d+", t)]


def _score_lexical(question: str, ligne: dict[str, Any]) -> int:
    termes = _termes(question)
    texte = _texte_indexable(str(ligne.get("texte") or ""))
    doc_id = str(ligne.get("document_id") or "")
    lexical = 0
    for terme in termes:
        if terme not in texte:
            continue
        lexical += 5 if re.fullmatch(r"e\d+", terme) else 1
    if lexical and _codes_question(question):
        if "codes_alarme" in doc_id:
            lexical += 3
        if any(
            indice in texte
            for indice in (
                "temperature",
                "pression",
                "vibration",
                "alerte",
                "arret",
                "seuil",
                "palier",
            )
        ):
            lexical += 2
    return lexical


def rerank_lexical(question: str, lignes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remonte les passages qui contiennent vraiment les termes de la question."""
    if not _termes(question) or not lignes:
        return lignes
    return sorted(
        lignes,
        key=lambda ligne: (
            _score_lexical(question, ligne),
            float(ligne.get("similarite") or 0.0),
        ),
        reverse=True,
    )


def completer_par_mots_cles(
    question: str,
    lignes: list[dict[str, Any]],
    *,
    client=None,
) -> list[dict[str, Any]]:
    """Complète la recherche vectorielle par un balayage lexical (codes E41, etc.)."""
    codes = _codes_question(question)
    if not codes:
        return lignes

    cli = client or ouvrir_client()
    deja = {
        (
            str(l.get("document_id")),
            int(l.get("page") or -1),
            l.get("fragment"),
            str(l.get("texte") or ""),
        )
        for l in lignes
    }
    extras: list[dict[str, Any]] = []
    for ligne in lister_passages(type_resultat="texte", client=cli):
        texte = str(ligne.get("texte") or "")
        indexable = _texte_indexable(texte)
        if not any(code in indexable for code in codes):
            continue
        cle = (
            str(ligne.get("document_id")),
            int(ligne.get("page") or -1),
            ligne.get("fragment"),
            texte,
        )
        if cle in deja:
            continue
        deja.add(cle)
        extras.append(ligne)
    return lignes + extras


def filtrer_sources_code(
    question: str, lignes: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Pour une question sur un code, ne garde que les passages qui le mentionnent."""
    codes = _codes_question(question)
    if not codes:
        return lignes
    retenues = [
        ligne
        for ligne in lignes
        if any(code in _texte_indexable(str(ligne.get("texte") or "")) for code in codes)
    ]
    return retenues


def rag(
    question: str,
    *,
    groupe: str | None = None,
    k: int = 5,
    type_resultat: str | None = "texte",
    image_requete: str | Path | None = None,
    rediger: RedacteurRag | None = None,
    client=None,
) -> MaintiDocAnswer:
    """Recherche Qdrant puis rédaction locale sourcée."""
    if not question.strip() and image_requete is None:
        return MaintiDocAnswer(
            status="needs_clarification",
            answer="La question est vide.",
            clarification_question="Quelle information cherchez-vous ?",
        )

    n_recherche = max(k * 8, 24) if groupe is not None else max(k * 4, 12)
    try:
        bruts = rechercher(
            texte=question if question.strip() else None,
            image=image_requete,
            type_resultat=type_resultat,  # type: ignore[arg-type]
            k=max(n_recherche, k),
            client=client,
        )
    except ValueError as exc:
        return MaintiDocAnswer(
            status="abstained",
            answer=str(exc),
            uncertainties=["Index indisponible ou vide."],
        )

    candidates = filtrer_par_groupe(formater_resultats(bruts), groupe)
    candidates = completer_par_mots_cles(question, candidates, client=client)
    candidates = filtrer_par_groupe(candidates, groupe)
    candidates = filtrer_sources_code(question, candidates)
    lignes = rerank_lexical(question, candidates)[:k]
    if not lignes:
        return MaintiDocAnswer(
            status="abstained",
            answer="Aucune source accessible ne répond à la question.",
            uncertainties=[
                "Aucun résultat après recherche"
                + (" et filtrage d'accès." if groupe else ".")
            ],
        )

    sources = [ligne for ligne in lignes if ligne.get("type") == "texte"] or lignes
    if rediger is None:
        from maintidoc.llm import rediger_reponse_rag

        rediger = rediger_reponse_rag
    brouillon = rediger(question=question or "(requête image)", sources=sources)
    citations = (
        _citations_depuis_sources(sources) if brouillon.status == "answered" else []
    )
    return MaintiDocAnswer(
        status=brouillon.status,
        answer=brouillon.answer,
        citations=citations,
        uncertainties=brouillon.uncertainties,
        clarification_question=brouillon.clarification_question,
        proposed_action=None,
    )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(
            'Usage : python -m maintidoc.rag "<question>" [--groupe NOM]',
            file=sys.stderr,
        )
        return 2
    question = args[0]
    groupe = None
    if len(args) >= 3 and args[1] == "--groupe":
        groupe = args[2]
    reponse = rag(question, groupe=groupe)
    print(json.dumps(reponse.model_dump(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
