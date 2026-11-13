from pathlib import Path
import sys
import numpy as np
import umap
BACKEND_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(BACKEND_DIR))
from storage.sqlite_db import get_connection, get_img_embedding
result = get_img_embedding()
embeddings = []
for row in result:
    blob_data = row[1]
    if blob_data:
        embedding_array = np.frombuffer(blob_data,dtype=np.float32)
        embeddings.append(embedding_array)
print(len(embeddings))


reducer = umap.UMAP(n_components=2,random_state=42)
points = reducer.fit_transform(embeddings)
print(points)