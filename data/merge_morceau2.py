"""Ajoute au corpus les lignes d'inventaire et l'entrée de prompt du morceau 2.

À lancer depuis la racine du projet : python data/merge_morceau2.py
Le script peut être relancé sans risque : il n'ajoute jamais deux fois la même ligne.
"""

import csv
from pathlib import Path

INV = Path("corpus/inventaire.csv")
NEW = Path("data/inventaire_morceau2.csv")
PROMPTS = Path("corpus/prompts_corpus.md")
P03 = Path("data/prompt_P03.md")


def terminer_par_saut_de_ligne(path):
    data = path.read_bytes()
    if data and not data.endswith(b"\n"):
        with path.open("ab") as f:
            f.write(b"\r\n")


def main():
    with INV.open(encoding="utf-8", newline="") as f:
        existants = {r[0].lstrip("\ufeff") for r in csv.reader(f) if r}
    with NEW.open(encoding="utf-8", newline="") as f:
        nouvelles = list(csv.reader(f))[1:]
    ajout = [r for r in nouvelles if r[0] not in existants]
    if ajout:
        terminer_par_saut_de_ligne(INV)
        with INV.open("a", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(ajout)
    print(f"Inventaire : {len(ajout)} ligne(s) ajoutée(s), {len(nouvelles) - len(ajout)} déjà présente(s).")

    texte = PROMPTS.read_text(encoding="utf-8")
    if "## P03" in texte:
        print("Prompts : P03 déjà présent.")
    else:
        terminer_par_saut_de_ligne(PROMPTS)
        with PROMPTS.open("a", encoding="utf-8", newline="") as f:
            f.write("\n" + P03.read_text(encoding="utf-8"))
        print("Prompts : P03 ajouté.")


if __name__ == "__main__":
    main()
