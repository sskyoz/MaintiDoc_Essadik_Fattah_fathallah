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
