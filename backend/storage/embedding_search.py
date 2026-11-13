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
names = []

for i in range(min(5, len(cosine_similarities))):
    score, img_id = cosine_similarities[i]
    
    response = requests.get(f"http://localhost:1000/image/search_id/{img_id}")
    # image_data = response.json()[0]['name']
    image_data = {
        "name": response.json()[0]['name'],
        "similarity_score": score,
        "cluster_id": response.json()[0]['cluster_id'],
    }
    # image_data['similarity_score'] = score
    names.append(image_data)

import json
print(json.dumps(names, indent=4))