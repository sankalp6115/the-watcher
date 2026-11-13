import os
import requests
import numpy as np
import uvicorn

def image_embedding(image_path):
    abs_path = os.path.abspath(image_path)
    try:
        response = requests.post(
            "http://localhost:8000/embed-image",
            json={"path": abs_path}
        )
        response.raise_for_status()
        embedding = np.array(response.json()["embedding"]).reshape(1, -1)
        return embedding
    except Exception as e:
        print(f"Error fetching image embedding for {image_path}: {e}")
        return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python image_embedding.py <image_path>")
        sys.exit(1)
        
    emb = image_embedding(sys.argv[1])
    if emb is not None:
        print(f"Embedding generated successfully. Shape: {emb.shape}")
        print(emb)