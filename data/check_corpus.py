"""Contrôle final du corpus avant dépôt : inventaire, fichiers et exigences du livrable 1.

À lancer depuis la racine du projet : python data/check_corpus.py
Utilise PyMuPDF (pip install pymupdf) ou, à défaut, pypdf (pip install pypdf).
"""

import csv
import re
import sys
from pathlib import Path

try:
    import fitz
except ImportError:  # repli sur pypdf si PyMuPDF n'est pas installé
    fitz = None
    from pypdf import PdfReader

CORPUS = Path("corpus")
COLS = [
    "document_id", "fichier", "titre", "famille_equipement", "equipement_id", "type_document", "version", "nb_pages",
    "langue", "format", "elements_visuels", "provenance", "licence", "genere_par_ia", "outil_ia", "verifie_par",
    "corrections", "groupe_acces", "usage_test", "remarques",
]
TYPES = {"manuel", "procedure", "fiche_securite", "schema", "codes_alarme", "photo", "historique"}
FORMATS = {"pdf_texte", "pdf_scanne", "image"}
USAGES = {"normal", "contradictoire", "injection", "ambigu"}
GROUPES = {"techniciens_pompes", "techniciens_compresseurs", "responsables"}
FAMILLES = {"pompes", "compresseurs"}

erreurs = []
avertissements = []


def lire_pdf(chemin):
    """Retourne (nombre de pages, le PDF contient-il du texte extractible)."""
    if fitz is not None:
        with fitz.open(chemin) as pdf:
            return len(pdf), any(page.get_text().strip() for page in pdf)
    reader = PdfReader(chemin)
    return len(reader.pages), any((page.extract_text() or "").strip() for page in reader.pages)


def ko(msg):
    erreurs.append(msg)


def warn(msg):
    avertissements.append(msg)


def main():
    with (CORPUS / "inventaire.csv").open(encoding="utf-8-sig", newline="") as f:
        lignes = list(csv.reader(f))
    if lignes[0] != COLS:
        ko("En-tête de l'inventaire différent des 20 colonnes du sujet")
    rows = [dict(zip(COLS, r)) for r in lignes[1:] if r]
    for i, r in enumerate(lignes[1:], 2):
        if len(r) != 20:
            ko(f"ligne {i}: {len(r)} colonnes au lieu de 20")

    ids = [r["document_id"] for r in rows]
    if len(ids) != len(set(ids)):
        ko("identifiants en double dans l'inventaire")

    listes = {r["fichier"] for r in rows}
    presents = {
        p.relative_to(CORPUS).as_posix()
        for p in CORPUS.rglob("*")
        if p.is_file() and p.name not in ("inventaire.csv", "prompts_corpus.md")
    }
    for manquant in sorted(listes - presents):
        ko(f"fichier listé mais absent : {manquant}")
    for orphelin in sorted(presents - listes):
        ko(f"fichier présent mais absent de l'inventaire : {orphelin}")

    for r in rows:
        did = r["document_id"]
        if not re.fullmatch(r"[a-z0-9_]+", did):
            ko(f"{did}: identifiant invalide (minuscules, chiffres et _)")
        if Path(r["fichier"]).stem != did:
            ko(f"{did}: le nom du fichier doit être <document_id>.<extension>")
        for col, ok in (("type_document", TYPES), ("format", FORMATS), ("usage_test", USAGES), ("famille_equipement", FAMILLES)):
            if r[col] not in ok:
                ko(f"{did}: {col} « {r[col]} » invalide")
        if r["langue"] not in ("fr", "en"):
            ko(f"{did}: langue « {r['langue']} » invalide")
        if r["genere_par_ia"] not in ("oui", "non"):
            ko(f"{did}: genere_par_ia doit être oui ou non")
        for g in [x.strip() for x in r["groupe_acces"].split(";")]:
            if g not in GROUPES:
                ko(f"{did}: groupe d'accès « {g} » inconnu")
        for e in [x.strip() for x in r["equipement_id"].split(";")]:
            if not re.fullmatch(r"(POMPE|COMP)-[A-Z]-\d{2}", e):
                ko(f"{did}: equipement_id « {e} » hors format")
        if r["langue"] == "en" and "anglais" not in r["remarques"].lower():
            warn(f"{did}: document en anglais non signalé dans les remarques")
        if r["verifie_par"] in ("", "A_RELIRE"):
            warn(f"{did}: verifie_par à compléter")
        if r["corrections"] in ("", "A_COMPLETER"):
            warn(f"{did}: corrections à compléter")

        chemin = CORPUS / r["fichier"]
        if not chemin.exists():
            continue
        if r["format"] == "image":
            if r["nb_pages"] != "1":
                ko(f"{did}: une image doit avoir nb_pages = 1")
            continue
        nb, a_du_texte = lire_pdf(chemin)
        if str(nb) != r["nb_pages"]:
            ko(f"{did}: nb_pages = {r['nb_pages']} dans l'inventaire, {nb} dans le fichier")
        if r["format"] == "pdf_scanne" and a_du_texte:
            ko(f"{did}: marqué pdf_scanne mais contient une couche de texte")
        if r["format"] == "pdf_texte" and not a_du_texte:
            ko(f"{did}: marqué pdf_texte mais sans texte extractible")

    visuels = [r for r in rows if r["elements_visuels"].strip().lower() not in ("", "aucun")]
    scans = [r for r in rows if r["format"] == "pdf_scanne"]
    contradictoires = [r for r in rows if r["usage_test"] == "contradictoire"]
    pieges = [r for r in rows if r["usage_test"] == "injection"]
    familles = {r["famille_equipement"] for r in rows}
    exigences = [
        ("30 à 50 documents", 30 <= len(rows) <= 50, len(rows)),
        ("2 familles d'équipements", len(familles) == 2, sorted(familles)),
        ("au moins 10 documents avec éléments visuels", len(visuels) >= 10, len(visuels)),
        ("au moins 2 documents scannés", len(scans) >= 2, len(scans)),
        ("au moins 2 documents contradictoires", len(contradictoires) >= 2, len(contradictoires)),
        ("au moins 1 document piégé (injection)", len(pieges) >= 1, len(pieges)),
        ("fichier prompts_corpus.md présent", (CORPUS / "prompts_corpus.md").exists(), ""),
    ]
    print("EXIGENCES DU LIVRABLE 1")
    for libelle, ok, valeur in exigences:
        print(f"  {'OK ' if ok else 'KO '} {libelle} ({valeur})")
        if not ok:
            ko(f"exigence non remplie : {libelle}")

    print(f"\nERREURS : {len(erreurs)}")
    for e in erreurs:
        print("  KO ", e)
    print(f"AVERTISSEMENTS (à traiter avant le dépôt) : {len(avertissements)}")
    for w in avertissements[:12]:
        print("  !  ", w)
    if len(avertissements) > 12:
        print(f"  ... et {len(avertissements) - 12} autres")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
