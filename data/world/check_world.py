"""Contrôle la cohérence des fichiers YAML du monde MaintiDoc.

Usage : python check_world.py
Le script lit les YAML placés dans le même dossier que lui.
"""

import collections
import glob
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent

TYPES = {
    "manuel",
    "procedure",
    "fiche_securite",
    "schema",
    "codes_alarme",
    "photo",
    "historique",
}
FORMATS = {"pdf_texte", "pdf_scanne", "image"}
USAGES = {"normal", "contradictoire", "injection", "ambigu"}
GROUPES = {"techniciens_pompes", "techniciens_compresseurs", "responsables"}
EQ_RE = re.compile(r"^(POMPE|COMP)-[A-Z]-\d{2}$")
DOC_RE = re.compile(r"^[a-z0-9_]+$")


def load(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def register(docs, errors, doc, equipement, famille):
    did = doc["document_id"]
    if did in docs:
        errors.append(f"doublon {did}")
    if not DOC_RE.match(did):
        errors.append(f"id invalide {did}")
    for key, allowed in (("type", TYPES), ("format", FORMATS), ("usage_test", USAGES)):
        if doc[key] not in allowed:
            errors.append(f"{did}: {key}={doc[key]}")
    for groupe in doc["groupes"]:
        if groupe not in GROUPES:
            errors.append(f"{did}: groupe {groupe}")
    entry = dict(doc)
    entry["_eq"] = equipement
    entry["_fam"] = famille
    docs[did] = entry


def check_reference(docs, errors, ref):
    doc = docs.get(ref["document_id"])
    if doc is None:
        errors.append(f"référence vers {ref['document_id']} inconnue")
        return
    if ref["page"] > doc["nb_pages"]:
        errors.append(f"{ref['document_id']}: page {ref['page']} > {doc['nb_pages']}")
    if f"p.{ref['page']}" not in doc["elements_visuels"]:
        errors.append(f"{ref['document_id']}: p.{ref['page']} absente de elements_visuels")


def main():
    idx = load(HERE / "_index.yaml")
    files = sorted(glob.glob(str(HERE / "*_0?.yaml")))
    eqs = [load(f) for f in files]
    errors = []
    docs = {}

    for eq in eqs:
        if not EQ_RE.match(eq["equipment_id"]):
            errors.append(f"equipment_id {eq['equipment_id']}")
        for doc in eq["documents"]:
            register(docs, errors, doc, eq["equipment_id"], eq["famille"])
    for doc in idx["documents_communs"]:
        register(docs, errors, doc, doc["equipement_id"], doc["famille_equipement"])

    for eq in eqs:
        refs = [a["reference"] for a in eq["alarmes"]]
        refs.append(eq["panneau"]["reference_manuel"])
        for ref in refs:
            check_reference(docs, errors, ref)
        if eq["panneau"]["reference_photo"] not in docs:
            errors.append(f"photo {eq['panneau']['reference_photo']} inconnue")
        for proc in eq["procedures"]:
            for key, value in proc.items():
                if key.startswith("document_id") and value not in docs:
                    errors.append(f"procédure {proc['id']}: {value} inconnu")
        codes = [a["code"] for a in eq["alarmes"]]
        if len(codes) != len(set(codes)):
            errors.append(f"{eq['equipment_id']}: codes en double")

    for piege in idx["pieges"]:
        for did in piege["documents"]:
            if did not in docs:
                errors.append(f"{piege['id']}: {did} inconnu")

    n = len(docs)
    visuels = [k for k, d in docs.items() if d["elements_visuels"].strip().lower() != "aucun"]
    scans = [k for k, d in docs.items() if d["format"] == "pdf_scanne"]
    contr = [k for k, d in docs.items() if d["usage_test"] == "contradictoire"]
    inj = [k for k, d in docs.items() if d["usage_test"] == "injection"]
    anglais = [k for k, d in docs.items() if d["langue"] == "en"]
    types = collections.Counter(d["type"] for d in docs.values())
    familles = collections.Counter(d["_fam"] for d in docs.values())

    print("documents:", n, "| par famille:", dict(familles))
    print("types:", dict(types))
    print("avec éléments visuels:", len(visuels), "| scannés:", scans)
    print("contradictoires:", contr, "| injection:", inj, "| en anglais:", anglais)
    print("pages totales:", sum(d["nb_pages"] for d in docs.values()))
    exigences = (
        ("30 à 50 documents", 30 <= n <= 50),
        ("au moins 10 documents avec éléments visuels", len(visuels) >= 10),
        ("au moins 2 documents scannés", len(scans) >= 2),
        ("au moins 2 documents contradictoires", len(contr) >= 2),
        ("au moins 1 document piégé", len(inj) >= 1),
    )
    for libelle, ok in exigences:
        print(("OK  " if ok else "KO  ") + libelle)
    print("ERREURS:", errors if errors else "aucune")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
