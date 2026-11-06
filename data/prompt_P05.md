## P05 : Morceau 4, documents de COMP-B-02, et correction des historiques

- Date : 2026-11-05
- Outil : Claude
- Objectif : rédiger les 8 documents de COMP-B-02 (compresseur à piston bi-étagé) en respectant strictement `comp_b_02.yaml` (voyant orange à trois sens M01, E28 et E71, code E41 propre aux compresseurs, pièges PIEGE-01 et PIEGE-02).
- Consigne : après validation du morceau 3, générer le morceau 4 (manuel de 22 pages, fiche des codes, fiche de sécurité, schémas, photo du panneau, historique, procédure de démarrage, procédure de purge et de vidange), avec les pages et figures prévues dans la vérité terrain.
- Résultat : 7 PDF dans `documents/famille_2/` et 1 image dans `images/`.
- Contrôles automatiques réalisés après génération : nombre de pages conforme, figures et tableaux aux pages prévues, 6 codes (E et M) comparés cellule par cellule à la vérité terrain (manuel p.16 et fiche p.2), couple de 30 N·m uniquement dans la procédure de purge et l'historique, absence de toute valeur propre aux pompes ou à COMP-A-01 (huile, pressions, couples, codes), absence de marques réelles et d'adresses non fictives.
- Erreurs de l'IA repérées : (1) dans les tableaux de codes, le mot « Information » était coupé en deux lignes (« Informatio » puis « n ») parce que la colonne Gravité était trop étroite, détecté par la comparaison cellule par cellule ; (2) une recherche de mots coupés sur tout le corpus puis un contrôle visuel ont montré que les tableaux des 4 historiques (morceaux 1 à 4) coupaient des mots et des identifiants (« Statu/t », « Ouver/t », « TCK-2025-01/20 », « 2025-04-0/8 », « Cod/e ») ; les colonnes ont été élargies et les 4 historiques régénérés (pagination inchangée).
- Limites connues : la photo du panneau est un rendu synthétique avec un léger reflet, le code M01 reste lisible ; les valeurs techniques sont inventées et n'ont pas de valeur réelle.
- Relecture humaine : À COMPLÉTER (relecteur, erreurs trouvées et corrigées).
