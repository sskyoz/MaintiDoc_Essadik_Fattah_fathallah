"""Obsolète : l'index vectoriel MaintiDoc utilise Qdrant.

Conservé pour d'éventuels imports du notebook. Préférer
`maintidoc.qdrant_index`.
"""

from __future__ import annotations

import warnings

import maintidoc.qdrant_index as _qdrant

warnings.warn(
    "maintidoc.chroma_index est obsolète ; utilisez maintidoc.qdrant_index",
    DeprecationWarning,
    stacklevel=2,
)

COLLECTION = _qdrant.COLLECTION
TypeResultat = _qdrant.TypeResultat
compter = _qdrant.compter
documents_vectorises = _qdrant.documents_vectorises
dossier_chroma = _qdrant.dossier_qdrant
formater_resultats = _qdrant.formater_resultats
indexer_corpus = _qdrant.indexer_corpus
indexer_document = _qdrant.indexer_document
lister_passages = _qdrant.lister_passages
ouvrir_collection = _qdrant.ouvrir_client
rechercher = _qdrant.rechercher
