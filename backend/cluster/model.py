import os
from pathlib import Path
import sys
import numpy as np
from sklearn.cluster import HDBSCAN
from sklearn.metrics import pairwise_distances

BACKEND_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(BACKEND_DIR))

from storage.sqlite_db import get_connection, get_img_embedding, get_text_embedding, update_cluster_ids
from settings.settings import settings

IMG_WEIGHT = settings.image_embedding_weight
TEXT_WEIGHT = settings.text_embedding_weight
DISTANCE_THRESHOLD = settings.clustering_distance_threshold

img_result = get_img_embedding()
text_result = get_text_embedding()
text_dict = {row[0]: row[1] for row in text_result}

image_ids = []
img_embeddings_list = []
text_embeddings_list = []

for row in img_result:
    img_id = row[0]
    img_blob = row[1]
    text_blob = text_dict.get(img_id)
    
    if img_blob and text_blob:
        img_arr = np.frombuffer(img_blob, dtype=np.float32)
        text_arr = np.frombuffer(text_blob, dtype=np.float32)
        
        image_ids.append(img_id)
        img_embeddings_list.append(img_arr)
        text_embeddings_list.append(text_arr)

print(f"Total valid image-text pairs: {len(image_ids)}")

METRIC = settings.clustering_distance_metric
dist_img = pairwise_distances(img_embeddings_list, metric=METRIC)
dist_text = pairwise_distances(text_embeddings_list, metric=METRIC)

distance_matrix = (IMG_WEIGHT * dist_img) + (TEXT_WEIGHT * dist_text)

model = HDBSCAN(min_samples=2, min_cluster_size=4, metric='precomputed', cluster_selection_method='eom', cluster_selection_epsilon=0.25)

labels = model.fit_predict(distance_matrix)

# 2nd pipeline
unique_labels = set(labels)
if -1 in unique_labels:
    unique_labels.remove(-1)

if unique_labels:
    cluster_ids_list = list(unique_labels)
    centroids_img = []
    centroids_text = []
    
    # Calculate centroids
    for c in cluster_ids_list:
        indices = [i for i, lbl in enumerate(labels) if lbl == c]
        centroids_img.append(np.mean([img_embeddings_list[i] for i in indices], axis=0))
        centroids_text.append(np.mean([text_embeddings_list[i] for i in indices], axis=0))
        
    centroids_img = np.array(centroids_img).reshape(len(cluster_ids_list), -1)
    centroids_text = np.array(centroids_text).reshape(len(cluster_ids_list), -1)
    
    noise_indices = [i for i, lbl in enumerate(labels) if lbl == -1]
    if noise_indices:
        noise_img = np.array([img_embeddings_list[i] for i in noise_indices]).reshape(len(noise_indices), -1)
        noise_text = np.array([text_embeddings_list[i] for i in noise_indices]).reshape(len(noise_indices), -1)
        
        d_img = pairwise_distances(noise_img, centroids_img, metric='cosine')
        d_text = pairwise_distances(noise_text, centroids_text, metric='cosine')
        
        d_combined = (IMG_WEIGHT * d_img) + (TEXT_WEIGHT * d_text)
        
        best_centroid_indices = np.argmin(d_combined, axis=1)
        min_distances = np.min(d_combined, axis=1)
        
        # Reassign labels only if they are closer than the threshold
        reassigned_count = 0
        for idx, best_idx, min_dist in zip(noise_indices, best_centroid_indices, min_distances):
            if min_dist <= DISTANCE_THRESHOLD:
                labels[idx] = cluster_ids_list[best_idx]
                reassigned_count += 1
                
        print(f"Reassigned {reassigned_count} noise images out of {len(noise_indices)}.")

print(labels)

import pandas as pd
df_clusters = pd.DataFrame({
    'Image_ID': image_ids,
    'Cluster_Label': labels
})
print("\n--- Image to Cluster Mapping ---")
print(df_clusters.head(10))
grouped = df_clusters.groupby('Cluster_Label')['Image_ID'].apply(list).to_dict()

print("\n--- Cluster Summaries ---")
cluster_mapping = []

for cluster_id, images in grouped.items():
    if cluster_id == -1:
        print(f"Cluster -1 (Outliers/Noise): {len(images)} images")
    else:
        print(f"\nCluster {cluster_id}: {len(images)} images")
        print("Sample Images:", images[:5])

    for img_id in images:
        cluster_mapping.append((int(cluster_id), img_id))

print("\n--- Updating Database ---")
update_cluster_ids(cluster_mapping)
print(f"Successfully updated {len(cluster_mapping)} images with their cluster IDs in the database!")

