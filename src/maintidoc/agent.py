"""Travail sur un document du corpus.

Travailler sur un document veut dire : ouvrir un document inventorié, lire
ses pages, et rendre une réponse validée par MaintiDocAnswer. La citation
désigne une page réellement lue. Le texte de la réponse est un extrait de
cette page. S'il n'y a rien à citer, la réponse s'abstient.
"""

import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

from maintidoc.schemas import Citation, MaintiDocAnswer

JETON = re.compile(r"[^\W_]+", re.UNICODE)
MOTS_VIDES = {
    "a", "au", "aux", "avec", "car", "ce", "ces", "cet", "cette", "comme",
    "comment", "dans", "de", "des", "donc", "du", "elle", "en", "est", "et",
    "il", "je", "la", "le", "les", "leur", "mais", "me", "moins", "ne",
    "nous", "on", "ou", "par", "pas", "plus", "pour", "qu", "que", "quel",
    "quelle", "quels", "quelles", "qui",
    "sa", "se", "si", "son", "sont", "sur", "tu", "un", "une", "votre",
    "vous", "y",
}


def racine_depot() -> Path:
    return Path(__file__).resolve().parents[2]


def plier(texte: str) -> str:
    forme = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in forme if unicodedata.category(c) != "Mn")


def fiche_inventaire(document_id: str) -> dict[str, str]:
    chemin = racine_depot() / "corpus" / "inventaire.csv"
    with chemin.open(encoding="utf-8-sig", newline="") as fichier:
        for ligne in csv.DictReader(fichier):
            if ligne["document_id"] == document_id:
                return ligne
    raise LookupError(f"Document inconnu : {document_id}")


def lire_pages(chemin: Path) -> list[tuple[int, str]]:
    """Pages numérotées à partir de 1, dans l'ordre du fichier."""
    try:
        import pymupdf
    except ImportError:
        pymupdf = None
    if pymupdf is not None:
        with pymupdf.open(chemin) as pdf:
            return [(i, page.get_text()) for i, page in enumerate(pdf, 1)]
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("Installez pymupdf ou pypdf pour lire un document.") from exc
    lecteur = PdfReader(chemin)
    return [(i, page.extract_text() or "") for i, page in enumerate(lecteur.pages, 1)]


def _termes(question: str) -> list[str]:
    vus: list[str] = []
    for jeton in JETON.findall(question):
        terme = plier(jeton)
        if len(terme) < 2 or terme in MOTS_VIDES or terme in vus:
            continue
        vus.append(terme)
    return vus


def _jetons(texte: str) -> set[str]:
    return {plier(j) for j in JETON.findall(texte)}


def _score(jetons: set[str], termes: list[str]) -> int:
    score = 0
    for terme in termes:
        if terme not in jetons:
            continue
        score += 3 if re.fullmatch(r"e\d+", terme) else 1
    return score


def _prioritaire(termes: list[str], jetons: set[str]) -> str:
    presents = [t for t in termes if t in jetons]
    return min(presents, key=lambda t: (0 if re.fullmatch(r"e\d+", t) else 1, -len(t)))


def _couvre(jetons: set[str], termes: list[str]) -> bool:
    """Un seul mot commun ne suffit pas quand la question en contient plusieurs."""
    trouves = [t for t in termes if t in jetons]
    if not trouves:
        return False
    if any(re.fullmatch(r"e\d+", t) for t in trouves):
        return True
    if len(termes) == 1:
        return True
    return len(trouves) >= 2 and len(trouves) * 2 >= len(termes)


def _extrait(texte: str, terme: str) -> str:
    spans = list(JETON.finditer(texte))
    for index, correspondance in enumerate(spans):
        if plier(correspondance.group(0)) != terme:
            continue
        limite = min(len(texte), correspondance.end() + 320)
        fin = correspondance.end()
        for autre in spans[index + 1 :]:
            if autre.end() <= limite:
                fin = autre.end()
            else:
                break
        if re.fullmatch(r"e\d+", terme):
            for autre in spans[index + 1 :]:
                if autre.start() >= fin:
                    break
                if re.fullmatch(r"e\d+", plier(autre.group(0))):
                    fin = autre.start()
                    break
        return " ".join(texte[correspondance.start() : fin].split())
    return " ".join(texte.split())[:400]


def _element(texte: str, page: int) -> str:
    tableau = re.search(r"\btableau\s+(\d+)\.(\d+)", texte, flags=re.IGNORECASE)
    if tableau:
        return f"tableau_{tableau.group(1)}_{tableau.group(2)}"
    figure = re.search(r"\bfig(?:ure)?\.?\s+(\d+)\.(\d+)", texte, flags=re.IGNORECASE)
    if figure:
        return f"figure_{figure.group(1)}_{figure.group(2)}"
    return f"passage_p{page}"


def _abstention(answer: str, incertitude: str) -> MaintiDocAnswer:
    return MaintiDocAnswer(status="abstained", answer=answer, uncertainties=[incertitude])


def travailler_sur_document(
    document_id: str, question: str, groupe: str | None = None
) -> MaintiDocAnswer:
    """Répond à une question à partir d'un seul document du corpus."""
    fiche = fiche_inventaire(document_id)
    groupes = {g.strip() for g in fiche["groupe_acces"].split(";") if g.strip()}
    if groupe is not None and groupe not in groupes:
        return _abstention(
            "Ce document n'est pas accessible pour ce groupe.",
            "Accès refusé avant lecture du document.",
        )
    if not question.strip():
        return MaintiDocAnswer(
            status="needs_clarification",
            answer="La question est vide.",
            clarification_question="Quelle information cherchez-vous dans ce document ?",
        )
    if fiche["format"] == "image":
        return _abstention(
            "Ce document est une image : aucun texte n'en a été extrait.",
            "L'analyse visuelle n'est pas faite sur ce document.",
        )

    chemin = racine_depot() / "corpus" / fiche["fichier"]
    pages = [(n, t) for n, t in lire_pages(chemin) if t.strip()]
    if not pages:
        return _abstention(
            "Ce document n'a pas de texte extractible.",
            "Aucune page ne contient de texte à citer.",
        )

    termes = _termes(question)
    candidats = []
    for numero, texte in pages:
        jetons = _jetons(texte)
        score = _score(jetons, termes)
        if not _couvre(jetons, termes):
            continue
        terme = _prioritaire(termes, jetons)
        occurrences = sum(1 for j in JETON.findall(texte) if plier(j) == terme)
        candidats.append((score, occurrences, numero, texte, terme))
    if not candidats:
        return _abstention(
            "Aucun passage de ce document ne répond à la question.",
            "Les pages lues ne contiennent pas les termes de la question.",
        )

    _score_page, _occ, numero, texte, terme = max(candidats, key=lambda c: (c[0], c[1], -c[2]))
    extrait = _extrait(texte, terme)
    return MaintiDocAnswer(
        status="answered",
        answer=extrait,
        citations=[
            Citation(
                document_id=document_id,
                page=numero,
                element_id=_element(texte, numero),
            )
        ],
    )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print(
            'Usage : python -m maintidoc.agent <document_id> "<question>"',
            file=sys.stderr,
        )
        return 2
    try:
        reponse = travailler_sur_document(args[0], args[1])
    except LookupError as exc:
        print(exc, file=sys.stderr)
        return 2
    print(json.dumps(reponse.model_dump(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
