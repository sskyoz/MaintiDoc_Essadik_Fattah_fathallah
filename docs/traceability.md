# Matrice de traçabilité : cahier des charges, étape, preuve

Statuts : à faire / en cours / fait

| # | Exigence du cahier | Étape | Preuve attendue | Statut |
|---|--------------------|-------|-----------------|--------|
| 1 | Modèle vision-langage à poids ouverts | 4 | Modèle local, révision figée | à faire |
| 2 | Corpus de 30 à 50 documents, 2 familles, synthétiques | 1 | data/raw, journal des prompts | à faire |
| 3 | Documents synthétiques ou autorisés, sans donnée personnelle | 1 | corpus_prompts_log.md, vérification des photos | à faire |
| 4 | Schémas, tableaux, scans et photos dans le corpus | 1 | Au moins 10 documents avec visuels | à faire |
| 5 | Métadonnées par élément (document, version, page, élément, équipement, groupes) | 2 | Table PostgreSQL, payload Qdrant | à faire |
| 6 | OCR local | 2 | Script d'OCR, PDF scannés indexés | à faire |
| 7 | Recherche texte et image, fusion RRF | 3 | Tests de recherche, ablation | à faire |
| 8 | Filtrage des accès avant récupération et à l'affichage | 3 | Tests d'accès entre groupes | à faire |
| 9 | Citations pointant vers des pages et figures réellement récupérées | 4 | Vérificateur de citations | à faire |
| 10 | Citation qui soutient l'affirmation associée | 4 | Prompt evidence_check, métrique | à faire |
| 11 | Prompts versionnés dans Git | 0 et 4 | prompts/ | en cours |
| 12 | Sorties validées par schéma Pydantic | 0 et 4 | schemas.py, tests | fait |
| 13 | Incertitude : clarification ou abstention, sans pourcentage inventé | 4 | Scénarios d'évaluation | à faire |
| 14 | Serveur MCP avec 3 outils | 5 | mcp_server/ | à faire |
| 15 | Autorisations vérifiées côté serveur MCP à chaque appel | 5 | Tests d'accès MCP | à faire |
| 16 | Approbation liée à l'utilisateur et au contenu exact | 5 | Test de modification après approbation | à faire |
| 17 | Idempotence de create_ticket | 5 | Test de double envoi | à faire |
| 18 | LangGraph : état, limites de boucle, interruption humaine | 6 | agent/ | à faire |
| 19 | Budgets : 3 appels MCP, 6 appels modèle, 60 s | 6 | Tests de dépassement | à faire |
| 20 | Limites taille image, contexte, tokens, quotas, plafond GPU | 6 | Configuration et tests | à faire |
| 21 | Destinations réseau et outils restreints | 0 et 6 | Ports liés à 127.0.0.1, liste d'autorisation | en cours |
| 22 | Secrets hors Git, prompts et journaux | 0 | .gitignore, gitleaks | fait |
| 23 | Minimisation, anonymisation, chiffrement, durée de conservation | 7 | Politique documentée | à faire |
| 24 | Journalisation sans contenu brut | 7 | Tests de journaux | à faire |
| 25 | Injection testée dans textes, OCR d'images et réponses MCP | 7 | 20 scénarios d'injection | à faire |
| 26 | Reranker multilingue fine-tuné (800 à 1500 exemples) | 8 | Dataset, modèle, MLflow | à faire |
| 27 | Séparation train/val/test par document ou famille | 8 | Script de split | à faire |
| 28 | Trois configurations comparées (sans, d'origine, adapté) | 8 | Tableau nDCG@5, MRR@10 | à faire |
| 29 | Jeu de test d'environ 150 scénarios | 9 | data/eval | à faire |
| 30 | Comparaison avec une version texte seul | 9 | Résultats d'ablation | à faire |
| 31 | Latence p50 et p95, mémoire et temps GPU | 9 | Rapport de benchmark | à faire |
| 32 | Analyse manuelle des cas difficiles | 9 | Fichier d'analyse | à faire |
| 33 | Dépendances, révisions de modèles et configurations figées | 0 | requirements.lock, digests Docker | en cours |
| 34 | Licences vérifiées | 0 | docs/LICENSES.md | en cours |
| 35 | Tests unitaires, d'intégration et de sécurité en CI | 0 et 10 | .github/workflows/ci.yml | en cours |
| 36 | Contrôle des secrets et des dépendances en CI | 0 et 10 | gitleaks, scan des dépendances | en cours |
| 37 | Versionnage des corpus, index, prompts et modèles | 10 | Hashes, MLflow | à faire |
| 38 | Chaque exécution liée aux versions modèle, prompt, reranker, index | 10 | Champs de traçabilité | à faire |
| 39 | Suivi MLflow | 0 et 10 | MLflow sur localhost:5000 | en cours |
| 40 | Surveillance : erreurs, latences, consommation, refus d'accès | 10 | Tableau de bord ou journaux | à faire |
| 41 | Retour à la version précédente | 10 | Procédure testée | à faire |
| 42 | Déploiement Docker Compose | 10 | docker-compose.yml complet | en cours |
| 43 | Fiche de limites | 11 | docs/limits.md | à faire |
| 44 | Démonstration en 7 étapes | 11 | Scénario de démo | à faire |