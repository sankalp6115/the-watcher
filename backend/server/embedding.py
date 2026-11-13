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

def embed_image(image_path: str) -> np.ndarray:
    with torch.no_grad():
        with Image.open(image_path) as im:
            img_tensor = clip_preprocess(im).unsqueeze(0).to(device)
            emb = clip_model.encode_image(img_tensor)
            emb = emb / emb.norm(dim=-1, keepdim=True)
            return emb.cpu().numpy().flatten().astype(np.float32)