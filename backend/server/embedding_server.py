import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import torch
import open_clip
import numpy as np
from PIL import Image   
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import uvicorn

app = FastAPI(title="Watcher Embedding Server")

device = "mps" if torch.backends.mps.is_available() else "cpu"
if torch.cuda.is_available():
    device = "cuda"

print(f"Loading models on device: {device}...")

text_model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

clip_model, _, clip_preprocess = open_clip.create_model_and_transforms(
    'ViT-B-32', pretrained='laion2b_s34b_b79k'
)
clip_model = clip_model.to(device)
clip_model.eval()

print("Models loaded successfully!")

class TextRequest(BaseModel):
    text: str

class ImageRequest(BaseModel):
    path: str

@app.post("/embed-text")
def embed_text(req: TextRequest):
    try:
        embedding = text_model.encode(req.text).tolist()
        return {"embedding": embedding}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text embedding failed: {str(e)}")

@app.post("/embed-image")
def embed_image(req: ImageRequest):
    if not os.path.exists(req.path):
        raise HTTPException(status_code=400, detail=f"Image file not found: {req.path}")
    try:
        with torch.no_grad():
            with Image.open(req.path) as im:
                img_tensor = clip_preprocess(im).unsqueeze(0).to(device)
                embedding = clip_model.encode_image(img_tensor)
                embedding = embedding / embedding.norm(dim=-1, keepdim=True)
                embedding = embedding.cpu().numpy().flatten().tolist()
        return {"embedding": embedding}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image embedding failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("embedding_server:app", host="0.0.0.0", port=8000)