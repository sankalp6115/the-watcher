import os
import sys
import glob
from pathlib import Path
from tqdm import tqdm

# Ensure backend root is in sys.path so modules like pipeline and storage can be imported
sys.path.append(str(Path(__file__).resolve().parent.parent))

from pipeline.ingestion_pipeline import ingestion_to_db
from storage.sqlite_db import init_db, insert_image_record, search_text, get_existing_paths

def run_batch_ingestion(folder_path):
    init_db()
    
    existing_paths = get_existing_paths()

    image_files = []
    for ext in ('*.png', '*.jpg', '*.jpeg'):
        search_pattern = os.path.join(folder_path, "**", ext)
        image_files.extend(glob.glob(search_pattern, recursive=True))

    total_images = len(image_files)
    # Filter out already ingested images beforehand so the progress bar only tracks actual work
    images_to_process = [p for p in image_files if os.path.abspath(p) not in existing_paths]
    skipped_count = total_images - len(images_to_process)

    if skipped_count > 0:
        print(f"Total images found: {total_images} | Already in DB (skipped): {skipped_count} | To process: {len(images_to_process)}")

    success_count = 0
    failed_count = 0

    # Ensure stdout is unbuffered for immediate live updates
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    with tqdm(
        total=len(images_to_process),
        desc="Processing",
        file=sys.stdout,
        miniters=1,
        mininterval=0,
        dynamic_ncols=True
    ) as pbar:
        for img_path in images_to_process:
            file_name = os.path.basename(img_path)
            # Display current file in the progress bar
            display_name = file_name if len(file_name) <= 30 else file_name[:27] + "..."
            pbar.set_postfix_str(f"{display_name}")
            pbar.refresh()

            try:
                result_dict = ingestion_to_db(img_path)
                insert_image_record(result_dict)
                success_count += 1
            except Exception as e:
                failed_count += 1
                tqdm.write(f"\n[Error] Failed to process {file_name}: {e}")
            finally:
                pbar.update(1)

    print(f"\nFinished! Ingested: {success_count} | Skipped: {skipped_count} | Failed: {failed_count} | Total: {total_images}")

if __name__ == "__main__":
    SS_FOLDER = "/Users/sankalpomar/Pictures/Screenshots"
    run_batch_ingestion(SS_FOLDER)