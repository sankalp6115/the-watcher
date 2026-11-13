import os
import sys
from pathlib import Path

# Ensure backend root is in sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from concurrent.futures import ThreadPoolExecutor
from pipeline.metadata_parser import get_file_metadata
from pipeline.ocr import ocr
from pipeline.preprocessing_pipeline import cleaning_pipeline
from embedding.embedding import embed_text, embed_image, embed_texts, embed_images


def run_text_pipeline(image_path):
    # OCR -> Cleaning -> Text Embedding (direct in-process)
    ocr_text = ocr(image_path)
    cleaned_text = cleaning_pipeline(ocr_text)
    text_embedding = embed_text(cleaned_text)
    text_embedding_bytes = text_embedding.tobytes()
    return cleaned_text, text_embedding_bytes


def run_image_pipeline(image_path):
    # Image Embedding (direct in-process)
    img_embedding = embed_image(image_path)
    img_embedding_bytes = img_embedding.tobytes()
    return img_embedding_bytes


def ingestion_to_db(image):
    metadata = get_file_metadata(image)
    cleaned_text, text_embedding_bytes = run_text_pipeline(image)
    img_embedding_bytes = run_image_pipeline(image)

    return {
        "metadata": metadata,
        "cleaned_text": cleaned_text,
        "text_embedding": text_embedding_bytes,
        "image_embedding": img_embedding_bytes
    }


def _process_single_cpu(img_path):
    try:
        metadata = get_file_metadata(img_path)
        ocr_text = ocr(img_path)
        cleaned_text = cleaning_pipeline(ocr_text)
        return {
            "path": img_path,
            "metadata": metadata,
            "cleaned_text": cleaned_text,
            "ok": True
        }
    except Exception as e:
        return {
            "path": img_path,
            "error": str(e),
            "ok": False
        }


def ingest_batch_to_db(image_paths: list[str], max_workers: int = 8) -> list[dict]:
    """
    Batched ingestion pipeline:
    1. Extracts metadata, OCR, and cleaned text concurrently across CPU cores.
    2. Runs batched text embeddings (1 forward pass on GPU/MPS).
    3. Runs batched image embeddings (1 forward pass on GPU/MPS).
    Returns list of record dicts ready for database insertion.
    """
    if not image_paths:
        return []

    # 1. Parallel CPU extraction
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        cpu_results = list(executor.map(_process_single_cpu, image_paths))

    valid_items = [r for r in cpu_results if r.get("ok")]
    if not valid_items:
        return []

    # 2. Batched text embeddings
    texts = [item["cleaned_text"] for item in valid_items]
    text_embeddings = embed_texts(texts, batch_size=len(texts))

    # 3. Batched image embeddings
    paths = [item["path"] for item in valid_items]
    img_embeddings = embed_images(paths, batch_size=len(paths))

    # 4. Construct records
    records = []
    for i, item in enumerate(valid_items):
        img_emb = img_embeddings[i]
        if img_emb is None:
            continue
        records.append({
            "metadata": item["metadata"],
            "cleaned_text": item["cleaned_text"],
            "text_embedding": text_embeddings[i].tobytes(),
            "image_embedding": img_emb.tobytes()
        })

    return records