import numpy as np
import open_clip
from PIL import Image
from sentence_transformers import SentenceTransformer
import torch

device = "mps" if torch.backends.mps.is_available() else "cpu"
if torch.cuda.is_available():
    device = "cuda"

text_model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
clip_model, _, clip_preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32", pretrained="laion2b_s34b_b79k"
)
clip_model = clip_model.to(device)
clip_model.eval()

def embed_text(text: str) -> np.ndarray:
    emb = text_model.encode(text, convert_to_numpy=True)
    return emb.astype(np.float32)

def embed_texts(texts: list[str], batch_size: int = 32) -> np.ndarray:
    if not texts:
        return np.empty((0, 384), dtype=np.float32)
    embs = text_model.encode(texts, batch_size=batch_size, convert_to_numpy=True, show_progress_bar=False)
    return embs.astype(np.float32)

def embed_image(image_path: str) -> np.ndarray:
    with torch.no_grad():
        with Image.open(image_path) as im:
            img_tensor = clip_preprocess(im.convert("RGB")).unsqueeze(0).to(device)
            emb = clip_model.encode_image(img_tensor)
            emb = emb / emb.norm(dim=-1, keepdim=True)
            return emb.cpu().numpy().flatten().astype(np.float32)

def embed_images(image_paths: list[str], batch_size: int = 32) -> list[np.ndarray | None]:
    if not image_paths:
        return []

    results: list[np.ndarray | None] = [None] * len(image_paths)

    for i in range(0, len(image_paths), batch_size):
        chunk_paths = image_paths[i:i + batch_size]
        valid_indices = []
        tensors = []

        for idx_in_chunk, path in enumerate(chunk_paths):
            try:
                with Image.open(path) as im:
                    tensors.append(clip_preprocess(im.convert("RGB")))
                    valid_indices.append(i + idx_in_chunk)
            except Exception as e:
                continue

        if tensors:
            with torch.no_grad():
                batch_tensor = torch.stack(tensors).to(device)
                embs = clip_model.encode_image(batch_tensor)
                embs = embs / embs.norm(dim=-1, keepdim=True)
                embs_np = embs.cpu().numpy().astype(np.float32)
                for out_idx, orig_idx in enumerate(valid_indices):
                    results[orig_idx] = embs_np[out_idx]

    return results