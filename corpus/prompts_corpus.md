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

## P03 : Morceau 2, documents de POMPE-B-01

- Date : 2026-11-05
- Outil : Claude
- Objectif : rédiger les 8 documents de POMPE-B-01 en respectant strictement `pompe_b_01.yaml` (pompe multicellulaire à 4 étages, voyant bleu AUTO, 7 codes d'alarme dont E58, seuils propres à cette pompe, pièges PIEGE-01 et PIEGE-02).
- Consigne : après validation du morceau 1, générer le morceau 2 (manuel de 28 pages, fiche des codes d'alarme, fiche de sécurité, schémas, photo du panneau, historique, procédure de démarrage, procédure de remplacement de la garniture), avec les pages et figures prévues dans la vérité terrain.
- Résultat : 7 PDF et 1 image dans `documents/famille_1/` et `images/`.
- Contrôles automatiques réalisés après génération : nombre de pages conforme, figures et tableaux aux pages prévues, 7 codes d'alarme comparés cellule par cellule à la vérité terrain (manuel p.24 et fiche p.2), couples 12 et 85 N·m uniquement dans la procédure de garniture, absence de toute valeur propre à POMPE-A-01 (2,0 bar, 4,5 mm/s, 85 °C, 3,2 bar, 27 A, DN 100, couples de vidange), absence de marques réelles et d'adresses non fictives.
- Erreur de l'IA repérée à la relecture croisée : une phrase du manuel indiquait que les seuils différaient de ceux de POMPE-A-01 pour les codes E22, E33, E41, E42 et E57, en oubliant E15 (seuil de pression de refoulement de 0,5 bar contre 0,3 bar) ; la comparaison automatique des deux fichiers de vérité terrain a confirmé que les six codes communs ont des seuils différents, et la phrase a été corrigée.
- Limites connues : la photo du panneau est un rendu synthétique, les valeurs techniques sont inventées et n'ont pas de valeur réelle.
- Relecture humaine : À COMPLÉTER (relecteur, erreurs trouvées et corrigées).

## P04 : Morceau 3, documents de COMP-A-01

- Date : 2026-11-05
- Outil : Claude
- Objectif : rédiger les 8 documents de COMP-A-01 (compresseur à vis lubrifié) en respectant strictement `comp_a_01.yaml` (circuits d'air et d'huile, 5 codes d'alarme E18, E19, E41, E52, E63, pièges PIEGE-01 et PIEGE-02).
- Consigne : après validation du morceau 2, générer le morceau 3 (manuel de 26 pages, fiche des codes d'alarme, fiche de sécurité, schémas, photo du panneau, historique, procédure de démarrage, procédure de remplacement du filtre à air), avec les pages et figures prévues dans la vérité terrain.
- Résultat : 7 PDF dans `documents/famille_2/` et 1 image dans `images/`.
- Choix de conception : la photo du panneau montre le voyant rouge DEFAUT et le code E41 (pression d'huile basse), pour créer un cas ambigu avec le code E41 des pompes (température de palier, orange) ; la photo et le fichier index ont été classés en usage « ambigu » dans la vérité terrain.
- Contrôles automatiques réalisés après génération : nombre de pages conforme, figures et tableaux aux pages prévues, 5 codes d'alarme comparés cellule par cellule à la vérité terrain (manuel p.18 et fiche p.2), couple de 8 N·m uniquement dans la procédure de filtre à air, absence de toute valeur propre aux pompes ou à COMP-B-02 (codes E15, E22, E28, E29, E33, E35, E42, E57, E58, E71, M01, valeurs d'huile et de pression), absence de marques réelles et d'adresses non fictives.
- Erreur de l'IA repérée : le plan de pagination du manuel ne comptait que 25 pages au lieu des 26 inscrites dans la vérité terrain ; l'écart a été détecté par un comptage avant génération et corrigé en ajoutant une page de registre de maintenance et d'arrêt prolongé (le sommaire a été mis à jour).
- Limites connues : la photo du panneau est un rendu synthétique, les valeurs techniques sont inventées et n'ont pas de valeur réelle.
- Relecture humaine : À COMPLÉTER (relecteur, erreurs trouvées et corrigées).
