import requests
from PIL import Image
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from metadata_parser import get_file_metadata
from ocr import ocr
from preprocessing_pipeline import cleaning_pipeline


def run_text_pipeline(image_path):
    # OCR -> Cleaning -> Text Embedding
    # print("OCR Started")
    ocr_text = ocr(image_path)

    # print("Cleaning started")
    cleaned_text = cleaning_pipeline(ocr_text)

    # print("Text to Embedding started")
    response_text = requests.post("http://localhost:8000/embed-text", json={"text": cleaned_text})
    response_text.raise_for_status()
    text_embedding = np.array(response_text.json()["embedding"]).reshape(1, -1)
    text_embedding_bytes = text_embedding.astype("float32").tobytes()
    return cleaned_text, text_embedding_bytes

def run_image_pipeline(image_path):
    # Image Embedding
    # print("Image to Embedding started")
    response_img = requests.post("http://localhost:8000/embed-image", json={"path": image_path})
    response_img.raise_for_status()
    img_embedding = np.array(response_img.json()["embedding"]).reshape(1, -1)
    img_embedding_bytes = img_embedding.astype("float32").tobytes()
    
    return img_embedding_bytes

def ingestion_to_db(image):
    # print("Extracting metadata")
    metadata = get_file_metadata(image)
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_text = executor.submit(run_text_pipeline, image)
        future_img = executor.submit(run_image_pipeline, image)
        cleaned_text, text_embedding_bytes = future_text.result()
        img_embedding_bytes = future_img.result()

    return {
        "metadata": metadata,
        "cleaned_text": cleaned_text,
        "text_embedding": text_embedding_bytes,
        "image_embedding": img_embedding_bytes
    }