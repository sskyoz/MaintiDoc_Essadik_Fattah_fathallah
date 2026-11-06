## P06 : Morceau 5, documents communs

- Date : 2026-11-05
- Outil : Claude
- Objectif : rédiger les 5 documents communs qui complètent le corpus : deux fiches de sécurité générales (dont un scan simulé), deux datasheets en anglais et une note de service piégée réservée aux responsables.
- Consigne : après validation du morceau 4, générer le morceau 5 en respectant la vérité terrain (`_index.yaml`, `pompe_a_01.yaml`, `comp_a_01.yaml`) ; les datasheets doivent reprendre exactement les valeurs des manuels, la note de service doit contenir une instruction malveillante fictive en page 2 (PIEGE-05) et le scan doit être une image sans couche de texte.
- Résultat : 5 PDF, 2 dans `documents/famille_1/` et 3 dans `documents/famille_2/`.
- Contrôles automatiques réalisés après génération : nombre de pages conforme, éléments aux pages prévues (tableaux EPI, figures, tables), valeurs des datasheets comparées à la vérité terrain, datasheets entièrement en anglais, scan sans couche de texte puis OCR (mots clés retrouvés), instruction malveillante présente uniquement en page 2 de la note et nulle part ailleurs, URL fictive (exemple.org), absence de référence à un modèle précis dans les documents génériques, nouvelle recherche de mots coupés dans les tableaux de tout le corpus (aucun).
- Erreur de l'IA repérée : aucune erreur de contenu détectée par les contrôles automatiques sur ce morceau (la relecture humaine peut en trouver d'autres).
- Limites connues : le scan est simulé par traitement d'image, les datasheets et fiches sont fictives, les valeurs techniques sont inventées.
- Relecture humaine : À COMPLÉTER (relecteur, erreurs trouvées et corrigées).
