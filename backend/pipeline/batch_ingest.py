import os
import sys
import glob
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parent.parent / "settings" / ".env"
load_dotenv(dotenv_path=ENV_FILE)

sys.path.append(str(Path(__file__).resolve().parent.parent))

from pipeline.ingestion_pipeline import ingest_batch_to_db
from storage.sqlite_db import init_db, insert_image_records, get_existing_paths

def run_batch_ingestion(folder_path, batch_size=32, max_workers=8):
    init_db()
    
    existing_paths = get_existing_paths()

    image_files = []
    for ext in ('*.png', '*.jpg', '*.jpeg'):
        search_pattern = os.path.join(folder_path, "**", ext)
        image_files.extend(glob.glob(search_pattern, recursive=True))

    total_images = len(image_files)
    images_to_process = [p for p in image_files if os.path.abspath(p) not in existing_paths]
    skipped_count = total_images - len(images_to_process)

    if skipped_count > 0:
        print(f"Total images found: {total_images} | Already in DB (skipped): {skipped_count} | To process: {len(images_to_process)}")

    if not images_to_process:
        print("All images are already ingested into the database!")
        return

    success_count = 0
    failed_count = 0

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    total_batches = (len(images_to_process) + batch_size - 1) // batch_size

    with tqdm(
        total=len(images_to_process),
        desc="Batch Ingesting",
        file=sys.stdout,
        miniters=1,
        mininterval=0,
        dynamic_ncols=True
    ) as pbar:
        for i in range(0, len(images_to_process), batch_size):
            batch_paths = images_to_process[i:i + batch_size]
            batch_num = (i // batch_size) + 1

            pbar.set_postfix_str(f"Batch {batch_num}/{total_batches} ({len(batch_paths)} items)")
            pbar.refresh()

            try:
                records = ingest_batch_to_db(batch_paths, max_workers=max_workers)
                if records:
                    inserted = insert_image_records(records)
                    success_count += inserted
                    batch_failed = len(batch_paths) - inserted
                    failed_count += batch_failed
                else:
                    failed_count += len(batch_paths)
            except Exception as e:
                failed_count += len(batch_paths)
                tqdm.write(f"\n[Error] Failed processing batch {batch_num}: {e}")
            finally:
                pbar.update(len(batch_paths))

    print(f"\nFinished! Ingested: {success_count} | Skipped: {skipped_count} | Failed: {failed_count} | Total: {total_images}")

if __name__ == "__main__":
    IMG_DIR = os.getenv("IMG_DIR")
    if not IMG_DIR:
        print(f"Error: IMG_DIR not set in {ENV_FILE}")
        sys.exit(1)
    run_batch_ingestion(IMG_DIR)