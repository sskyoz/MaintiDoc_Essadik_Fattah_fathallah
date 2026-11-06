# Prompts utilisés pour constituer le corpus

Outil : Claude (Anthropic), interface web claude.ai. Les prompts sont numérotés P01, P02... La colonne `outil_ia` de `inventaire.csv` renvoie à ces numéros.
Le texte exact des échanges est conservé dans l'historique de la conversation ; les consignes ci-dessous en reprennent l'essentiel.

## P01 : Choix des familles et définition du « monde » (vérité terrain)

- Date : 2026-11-03
- Outil : Claude
- Objectif : fixer, avant toute rédaction, les familles d'équipements, les équipements, les groupes d'accès, les pièges d'évaluation et le plan des documents.
- Consigne : Essadik demande à Claude de générer le corpus lui-même, en morceaux, après un choix commun des 2 familles ; familles retenues : pompes centrifuges et compresseurs ; validation du monde proposé (4 équipements, 3 groupes, environ 40 documents).
- Résultat : fichiers `_index.yaml`, `pompe_a_01.yaml`, `pompe_b_01.yaml`, `comp_a_01.yaml`, `comp_b_02.yaml` (dossier `data/world/`).
- Vérifications faites par l'équipe : recherche en ligne des noms de marque proposés.
- Erreur de l'IA repérée : les noms de fabricants fictifs proposés (Kelvor, Airvex) correspondent à une entité et à un produit réels ; remplacés par Pompall et Compramex.

## P02 : Morceau 1, documents de POMPE-A-01

- Date : 2026-11-04
- Outil : Claude
- Objectif : rédiger les 9 documents de POMPE-A-01 en respectant strictement `pompe_a_01.yaml` (identifiants, codes d'alarme, seuils, pages et figures de référence, pièges PIEGE-01 à PIEGE-04).
- Consigne : générer le morceau 1 (manuel de 24 pages, fiche des codes d'alarme, fiche de sécurité, schémas, photo du panneau, historique, procédure de démarrage, procédures de vidange v1 scannée et v2), avec les pages et figures prévues dans la vérité terrain.
- Résultat : 8 PDF et 1 image dans `documents/famille_1/` et `images/`.
- Contrôles automatiques réalisés après génération : nombre de pages conforme, figures et tableaux aux pages prévues, codes d'alarme, désignations, seuils, voyants et gravités comparés cellule par cellule à la vérité terrain (E41 à 85 °C dans le manuel, 80 °C dans la fiche, volontairement), couples 18 et 25 N·m aux bons endroits, absence de couche de texte dans la v1, OCR de la v1.
- Limites connues : la photo du panneau est un rendu synthétique, le scan de la v1 est simulé par traitement d'image, les valeurs techniques sont inventées et n'ont pas de valeur réelle.
- Relecture humaine : À COMPLÉTER (relecteur, erreurs trouvées et corrigées).
