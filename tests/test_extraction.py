from pathlib import Path

from maintidoc.extraction import apercu_extraction, dossier_sortie, extraire_document


def test_extraire_et_apercu_schema_pompe_a():
    resultat = extraire_document("schema_pompe_a")
    assert resultat.nombre_pages == 2
    assert resultat.nombre_images >= 1
    assert (resultat.output_dir / "texte_complet.txt").is_file()
    assert any(resultat.image_dir.iterdir())

    apercu = apercu_extraction("schema_pompe_a", max_chars=500, max_images=2)
    assert apercu["document_id"] == "schema_pompe_a"
    assert len(str(apercu["texte_apercu"])) > 0
    assert apercu["images"]
    assert apercu["vignettes"]
    for chemin in apercu["vignettes"]:
        assert Path(chemin).is_file()
    assert dossier_sortie("schema_pompe_a") == resultat.output_dir
