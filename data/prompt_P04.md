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
