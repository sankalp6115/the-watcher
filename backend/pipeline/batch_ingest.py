import os
import sys
import glob

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.ingestion_pipeline import ingestion_to_db
from storage.sqlite_db import init_db, insert_image_record, search_text, get_existing_paths

def run_batch_ingestion(folder_path):
    print("Initializing Database...")
    init_db()
    
    existing_paths = get_existing_paths()
    if existing_paths:
        print(f"Found {len(existing_paths)} images already in the database. Will skip processing these.")

    image_files = []
    for ext in ('*.png', '*.jpg', '*.jpeg'):
        search_pattern = os.path.join(folder_path, "**", ext)
        image_files.extend(glob.glob(search_pattern, recursive=True))
    
    print(f"Found {len(image_files)} total images in {folder_path}")

    success_count = 0
    skipped_count = 0
    for idx, img_path in enumerate(image_files):
        print(f"\n[{idx+1}/{len(image_files)}] Processing {os.path.basename(img_path)}...")
        
        abs_path = os.path.abspath(img_path)
        if abs_path in existing_paths:
            print("Skipped: Already exists in DB")
            skipped_count += 1
            continue

        try:
            result_dict = ingestion_to_db(img_path)
        
            insert_image_record(result_dict)
            print(f"Saved to DB")
            success_count += 1
        except Exception as e:
            print(f"Failed to process {img_path}: {e}")

    print(f"\nFinished! Ingested: {success_count} | Skipped: {skipped_count} | Total: {len(image_files)}")

if __name__ == "__main__":
    SS_FOLDER = "/Users/sankalpomar/Pictures/Screenshots"
    run_batch_ingestion(SS_FOLDER)