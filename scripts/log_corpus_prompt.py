"""Construit un prompt de corpus, le sauvegarde et l'ajoute au journal."""

import argparse
import datetime
from pathlib import Path

import yaml

LOG = Path("docs/corpus_prompts_log.md")
SENT = Path("prompts/corpus/sent")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("prompt_file")
    p.add_argument("yaml_file")
    p.add_argument("doc_name")
    p.add_argument("--llm", required=True, help="nom et version exacts du LLM")
    p.add_argument("--temp", type=float, default=0.3)
    p.add_argument("--structure", default="Introduction, voyants, alarmes, procédures")
    p.add_argument("--pages", type=int, default=10)
    p.add_argument("--dry-run", action="store_true", help="affiche sans enregistrer")
    a = p.parse_args()

    spec = yaml.safe_load(Path(a.prompt_file).read_text(encoding="utf-8"))
    world = Path(a.yaml_file).read_text(encoding="utf-8")
    final = spec["prompt"].format(
        yaml_equipement=world, structure=a.structure, nb_pages=a.pages
    )

    if a.dry_run:
        print(final)
        return

    SENT.mkdir(parents=True, exist_ok=True)
    n = len(list(SENT.glob("*_prompt.txt"))) + 1
    (SENT / f"{n:03d}_prompt.txt").write_text(final, encoding="utf-8")

    row = (
        f"| {n:03d} | {datetime.date.today()} | {a.doc_name} | {spec['id']} | "
        f"{Path(a.yaml_file).name} | {a.llm} | {a.temp} | | à relire |\n"
    )
    with LOG.open("a", encoding="utf-8") as f:
        f.write(row)
    print(final)
    print(f"\nEnregistré : prompts/corpus/sent/{n:03d}_prompt.txt")
    print(f"Sauvegarde la sortie du LLM dans data/raw_llm/{n:03d}.md")


if __name__ == "__main__":
    main()