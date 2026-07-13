import requests
import numpy as np

from sqlite_db import get_connection, get_text_embedding

def calculate_cosine_similarity(a,b):
    dot_product = np.dot(a,b)
    normA = np.linalg.norm(a)
    normB = np.linalg.norm(b)

    if normA == 0 or normB == 0:
        return 0.0
    return dot_product / (normA * normB)

embeddings = {}
result = get_text_embedding()
for blob in result:
    image_id = blob[0]
    embedding = np.frombuffer(blob[1], dtype=np.float32)
    embeddings[image_id] = embedding

# print(embeddings[0])
print("Enter your query")
query = input()

query_response = requests.post(
    "http://localhost:8000/embed-text",
    json={"text": query}
)

query_embedding = query_response.json()
# print(query_embedding['embedding'])

cosine_similarities = []
for image_id, db_embedding in embeddings.items():
    similarity = calculate_cosine_similarity(query_embedding['embedding'], db_embedding)
    cosine_similarities.append((similarity, image_id))

cosine_similarities.sort(key=lambda x: x[0], reverse=True)
for i in range(min(10, len(cosine_similarities))):
    score, img_id = cosine_similarities[i]
    print(f"Score: {score:.4f} | Image ID: {img_id}")