import os
from pathlib import Path
import sys
import numpy as np
from sklearn.metrics import pairwise_distances
BACKEND_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(BACKEND_DIR))
from storage.sqlite_db import get_connection, get_img_embedding, get_text_embedding, update_cluster_ids
IMG_WEIGHT = 0.50
TEXT_WEIGHT = 0.50

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

import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_distances
from storage.sqlite_db import get_cluster_with_image

# Fetch the assigned cluster for each image from the database
cluster_data = get_cluster_with_image()
cluster_map = {row["id"]: row["cluster_id"] for row in cluster_data}

# Group image indices by their cluster
clusters = {}
for i, img_id in enumerate(image_ids):
    c_id = cluster_map.get(img_id, -1)
    if c_id != -1 and c_id is not None:
        if c_id not in clusters:
            clusters[c_id] = []
        clusters[c_id].append(i)

all_distances = []

for c_id, indices in clusters.items():
    if len(indices) == 0:
        continue
    
    # Get embeddings for this cluster
    c_img_embs = np.array([img_embeddings_list[i] for i in indices]).reshape(len(indices), -1)
    c_text_embs = np.array([text_embeddings_list[i] for i in indices]).reshape(len(indices), -1)
    
    # Calculate the mean centroid for this cluster
    centroid_img = np.mean(c_img_embs, axis=0).reshape(1, -1)
    centroid_text = np.mean(c_text_embs, axis=0).reshape(1, -1)
    
    # Compute cosine distance of each point to the centroid
    d_img = cosine_distances(c_img_embs, centroid_img).flatten()
    d_text = cosine_distances(c_text_embs, centroid_text).flatten()
    
    # Weighted combination
    d_combined = (IMG_WEIGHT * d_img) + (TEXT_WEIGHT * d_text)
    all_distances.extend(d_combined)

print(f"Computed distances for {len(all_distances)} clustered images.")

# Plot the distribution and KDE
plt.figure(figsize=(10, 6))

# Histogram (set density=True so it scales properly with the KDE curve)
plt.hist(all_distances, bins=100, density=True, color='skyblue', edgecolor='black', alpha=0.6, label='Histogram')

# KDE Curve
from scipy.stats import gaussian_kde
kde = gaussian_kde(all_distances)
x_vals = np.linspace(min(all_distances), max(all_distances), 500)
plt.plot(x_vals, kde(x_vals), color='darkblue', linewidth=2.5, label='KDE (Density)')

plt.title('Distribution and KDE of Distances to Cluster Centroids')
plt.xlabel('Weighted Cosine Distance')
plt.ylabel('Density')
plt.grid(axis='y', alpha=0.75)

# Add a vertical line for the mean distance
mean_dist = np.mean(all_distances)
plt.axvline(mean_dist, color='red', linestyle='dashed', linewidth=1.5, label=f'Mean: {mean_dist:.3f}')
plt.legend()

# Save the plot
output_file = 'distances_histogram.png'
plt.savefig(output_file, dpi=200, bbox_inches='tight')
print(f"Histogram and KDE saved as '{output_file}'!")