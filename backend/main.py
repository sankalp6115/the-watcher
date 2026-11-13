import sqlite3

import subprocess
import os
import uvicorn
import json
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path

from pipeline.ingestion_pipeline import ingestion_to_db
from storage.sqlite_db import get_connection, search_text, insert_image_record, get_cluster_with_image, search_text_with_id
from models.models import IngestRequest

ENV_FILE = Path(__file__).resolve().parent / "settings" / ".env"
load_dotenv(ENV_FILE)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

IMG_DIR = os.getenv("IMG_DIR")
VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.avif')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "watcher.db")
get_connection()

@app.get("/")
def health():
    return {"message": "Hi from fastapi"}

@app.get("/images")
def images():
    all_images = []
    for filename in os.listdir(IMG_DIR):
        if filename.lower().endswith(VALID_EXTENSIONS):
            all_images.append(filename)
    return all_images

@app.get("/image/{filename}")
def image(filename: str):
    file_path = os.path.join(IMG_DIR, filename)
    return FileResponse(file_path)

# Takes string query and uses text search with fts5
@app.get("/image/search/{query}")
def search_images(query: str):
    results = search_text(query, 20)
    return results

# Takes id of image and returns image
@app.get("/image/search_id/{img_id}")
def search_similar_images(img_id: str):
    return search_text_with_id(img_id)

@app.post("/ingest")
def ingest_image(req: IngestRequest):
    file_path = req.path

    if not os.path.exists(file_path):
        return {"error": f"Image not found at {file_path}"}
    try:
        result_dict = ingestion_to_db(file_path)
        insert_image_record(result_dict)
        return {"message": "Success", "filepath": file_path}
    except Exception as e:
        return {"error": str(e)}

@app.get("/get-clusters")
def images_with_clusters():
    result = get_cluster_with_image()
    return result

if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0",port=1000)