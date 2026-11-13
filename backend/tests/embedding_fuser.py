# Image emb is 512dimension
# Text emb is 384dimension
import numpy as np

def fused_embedding(image_emb, text_emb, image_wt=0.5, text_wt=0.5):
    # Convert inputs to numpy arrays
    image_emb = np.asarray(image_emb)
    text_emb = np.asarray(text_emb)

    # Calculate norms, avoiding division by zero
    img_norm = np.linalg.norm(image_emb)
    txt_norm = np.linalg.norm(text_emb)
    
    image_emb = image_emb / (img_norm if img_norm > 0 else 1.0)
    text_emb = text_emb / (txt_norm if txt_norm > 0 else 1.0)

    # Flatten to 1D for clean concatenation
    fused = np.concatenate([image_wt * image_emb.ravel(), text_wt * text_emb.ravel()])

    # Normalize fused vector
    fused_norm = np.linalg.norm(fused)
    fused = fused / (fused_norm if fused_norm > 0 else 1.0)

    return fused.reshape(1, -1)