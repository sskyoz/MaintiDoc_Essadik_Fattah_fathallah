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
| 8 | 2026-11-23 | Rédaction locale | VLM Qwen prévu pour questions + image | Pour la rédaction texte sur un document : Ollama `qwen2.5:3b` ; citations imposées par le code | GPU / VLM multimodal encore à trancher ; Ollama déjà présent sur la machine | prompts/answer_v1.yaml, src/maintidoc/llm.py |
| 9 | 2026-11-23 | Notebook cours | RAG multimodal agentique complet | Intégré jusqu'à « aperçu des résultats » seulement (CLIP smoke + extraction + aperçu) ; pas ChromaDB / agent | Demande enseignant : s'arrêter à l'aperçu | notebooks/01_extraction_apercu.ipynb, src/maintidoc/extraction.py |
| 10 | 2026-11-23 | Vectorisation | Index CLIP dans ChromaDB | Découpage + embeddings CLIP sauvegardés en JSON local ; ChromaDB reporté | Demande : vectoriser sans ChromaDB d'abord | src/maintidoc/vectorisation.py |
| 11 | 2026-11-23 | Arborescence corpus | dossiers famille_1/famille_2 | `corpus/raw/<équipement>/<type>/<document_id>/<version>/` (+ `_shared`) | Feedback enseignant : arbo pédagogique ≠ GED pro ; préparer ChromaDB | corpus/README.md, scripts/migrer_arbo_corpus.py |
| 12 | 2026-11-23 | Index vectoriel cours | ChromaDB (notebook) | ChromaDB local `data/chroma`, collection CLIP ViT-B-32 ; Qdrant reste la cible cahier | Suivre le notebook du cours avant Qdrant | src/maintidoc/chroma_index.py |
| 13 | 2026-11-23 | Génération RAG | OpenAI GPT du notebook | Ollama local `qwen2.5:3b` + prompt `answer_rag_v1` ; citations imposées par le code | Pas de clé API ; modèle local déjà en place | src/maintidoc/rag.py |
| 14 | 2026-11-23 | Découpage CLIP | `bpe.decode` du notebook | Fragments stockés en texte original (comptage BPE mot à mot) + rerank lexical des codes | `decode` cassait `E41` → `e 4 1` et nuisait au RAG | src/maintidoc/vectorisation.py, src/maintidoc/rag.py |
| 15 | 2026-11-23 | Index vectoriel | ChromaDB du notebook | Qdrant (embarqué `data/qdrant` ou Docker `:6333`) ; Chroma scripts en redirect | Alignement cahier ; Qdrant déjà dans docker-compose | src/maintidoc/qdrant_index.py |