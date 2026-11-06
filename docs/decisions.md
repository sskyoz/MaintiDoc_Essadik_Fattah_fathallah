# Journal des décisions et écarts

Chaque écart par rapport au cahier des charges est noté ici avec sa justification.

| # | Date | Sujet | Cahier des charges | Décision | Justification | Preuve |
|---|------|-------|--------------------|----------|---------------|--------|
| 1 | 2026-11-03 | GPU | Cible plausible : GPU 24 Go, « à valider par benchmark » | GPU réel : RTX 5060, 8 Go. VLM à trancher : Qwen2.5-VL-7B en 4 bits ou Qwen2.5-VL-3B | Le cahier prévoit la validation par benchmark | À venir : benchmark VRAM (scripts/bench_gpu.py) |
| 2 | 2026-11-03 | Stockage de fichiers | MinIO (choix possible) | RustFS (API S3 compatible) | MinIO n'est plus publié sous forme d'images Docker et son dépôt est archivé ; RustFS garde l'API S3 et les mêmes ports | docker-compose.yml |
| 3 | 2026-11-03 | Planning | 6 semaines, indicatif, corpus déjà préparé | 4 semaines, corpus construit dans le projet | Le cahier indique que le planning est à adapter | Plan de travail |
| 4 | 2026-11-03 | Versions | Versions exactes figées dans le dépôt | Images Docker figées par digest | Reproductibilité | docker-compose.yml |
| 5 | 2026-11-03 | Port PostgreSQL | Non précisé | Port hôte 5433 | Le port 5432 est refusé par Windows sur cette machine | docker-compose.yml |
| 6 | 2026-11-03 | Licence du VLM | Licences à vérifier | Qwen2.5-VL-3B écarté en priorité (licence recherche) ; candidats : Qwen2.5-VL-7B en 4 bits et Qwen3-VL-4B | Licence permissive et VRAM de 8 Go | Fiches Hugging Face, benchmark |
| 7 | 2026-11-03 | Noms de fabricants | Documents sans ambiguïté légale | Pompall et Compramex, après remplacement de Kelvor et Airvex (existants, repérés par Essadik lors de la vérification) | Éviter toute confusion avec des marques réelles | Recherche en ligne |