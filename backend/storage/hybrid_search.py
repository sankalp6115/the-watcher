import requests
import numpy as np
from sqlite_db import get_connection, get_text_embedding, search_text

def calculate_cosine_similarity(a, b):
    dot_product = np.dot(a, b)
    normA = np.linalg.norm(a)
    normB = np.linalg.norm(b)
    if normA == 0 or normB == 0:
        return 0.0
    return dot_product / (normA * normB)

def reciprocal_rank_fusion(fts_results, vector_results, k=60):
    """
    Combines two lists of ranked results using Reciprocal Rank Fusion (RRF).
    RRF Score = 1 / (k + rank)
    """
    rrf_scores = {}

    # Rank FTS results (BM25)
    for rank, item in enumerate(fts_results):
        img_id = item["id"]
        if img_id not in rrf_scores:
            rrf_scores[img_id] = 0.0
        rrf_scores[img_id] += 1.0 / (k + rank + 1)

    # Rank Vector results (Cosine Similarity)
    for rank, item in enumerate(vector_results):
        img_id = item["id"]
        if img_id not in rrf_scores:
            rrf_scores[img_id] = 0.0
        rrf_scores[img_id] += 1.0 / (k + rank + 1)

    # Sort the combined scores
    sorted_rrf = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_rrf

if __name__ == "__main__":
    print("Enter your hybrid search query:")
    query = input()
    
    LIMIT = 20

    print("\n--- Running FTS Search ---")
    fts_results = search_text(query, limit=LIMIT)
    print("\n--- Running Vector Search ---")
    embeddings = {}
    db_embeddings = get_text_embedding()
    for blob in db_embeddings:
        embeddings[blob[0]] = np.frombuffer(blob[1], dtype=np.float32)
    query_response = requests.post(
        "http://localhost:8000/embed-text",
        json={"text": query}
    )
    query_embedding = query_response.json()['embedding']

    cosine_similarities = []
    for image_id, db_embedding in embeddings.items():
        sim = calculate_cosine_similarity(query_embedding, db_embedding)
        cosine_similarities.append({"id": image_id, "score": sim})

    # Sort vector results
    vector_results = sorted(cosine_similarities, key=lambda x: x["score"], reverse=True)[:LIMIT]

    print("\n--- Combining with Reciprocal Rank Fusion (RRF) ---")
    final_ranked_ids = reciprocal_rank_fusion(fts_results, vector_results)
    top_5 = final_ranked_ids[:5]
    final_output = []
    for img_id, rrf_score in top_5:
        response = requests.get(f"http://localhost:1000/image/search_id/{img_id}")
        image_data = response.json()[0]
        image_data['rrf_score'] = rrf_score
        final_output.append(image_data)
    import json
    print(json.dumps(final_output, indent=4))