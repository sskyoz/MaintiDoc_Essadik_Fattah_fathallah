# Corpus MaintiDoc — arborescence

Organisation proche d’une GED légère (équipement → type → document → version),
tout en gardant un `document_id` stable pour les citations et Qdrant.

```text
corpus/
  inventaire.csv              # registre (métadonnées + chemin)
  prompts_corpus.md
  raw/
    POMPE-A-01/
      manuel/
        manuel_pompe_a/
          v2.0_2025-01/
            manuel_pompe_a.pdf
      procedure/
        proc_vidange_pompe_a_v1/
          v1_2023-06/
            ...
        proc_vidange_pompe_a_v2/
          v2_2025-03/
            ...
      photo/
        photo_panneau_pompe_a/
          2026-11/
            photo_panneau_pompe_a.jpg
    POMPE-B-01/
    COMP-A-01/
    COMP-B-02/
    _shared/
      pompes/                 # docs multi-équipements
      compresseurs/
```

## Règles

- Fichier brut : toujours nommé `<document_id>.<ext>` (exigence inventaire / citations).
- Un document multi-équipements va dans `raw/_shared/<famille>/...`.
- Les dérivés (texte extrait, images, embeddings) restent dans `data/processed/<document_id>/`
  jusqu’à l’indexation Qdrant.
- Ne pas renommer un `document_id` sans mettre à jour inventaire, embeddings et tests.
