"""Smoke test CLIP du notebook du cours (avant ChromaDB)."""

from __future__ import annotations

from pathlib import Path

from maintidoc.agent import racine_depot

MODEL_NAME = "ViT-B-32"
PRETRAINED = "laion2b_s34b_b79k"


def charger_clip():
    """Charge OpenCLIP comme dans le notebook du professeur."""
    import open_clip
    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _, preprocess = open_clip.create_model_and_transforms(
        MODEL_NAME, pretrained=PRETRAINED
    )
    model = model.to(device).eval()
    tokenizer = open_clip.get_tokenizer(MODEL_NAME)
    return model, preprocess, tokenizer, device


def encoder_exemple(
    texte: str = "Panneau de commande d'une pompe",
    image: Path | None = None,
) -> dict[str, object]:
    """Encode un texte et une image du corpus ; affiche les dimensions (512)."""
    import torch
    from PIL import Image

    if image is None:
        image = racine_depot() / "corpus" / "images" / "photo_panneau_pompe_a.jpg"
    if not image.is_file():
        raise FileNotFoundError(f"Image introuvable : {image}")

    model, preprocess, tokenizer, device = charger_clip()
    tokens = tokenizer([texte]).to(device)
    with Image.open(image) as img:
        tenseur = preprocess(img.convert("RGB")).unsqueeze(0).to(device)

    with torch.inference_mode():
        vecteur_texte = model.encode_text(tokens)
        vecteur_image = model.encode_image(tenseur)
        vecteur_texte = vecteur_texte / vecteur_texte.norm(dim=-1, keepdim=True)
        vecteur_image = vecteur_image / vecteur_image.norm(dim=-1, keepdim=True)

    vt = vecteur_texte[0].cpu().tolist()
    vi = vecteur_image[0].cpu().tolist()
    return {
        "device": device,
        "image": str(image),
        "dimension_texte": len(vt),
        "dimension_image": len(vi),
        "texte_5": vt[:5],
        "image_5": vi[:5],
    }
