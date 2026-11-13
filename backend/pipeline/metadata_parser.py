import os
import hashlib
from datetime import datetime

def generate_file_hash(file_path):
    """
    Generates a unique and consistent SHA-256 hash based on the file contents.
    Reads in chunks to handle files of any size efficiently.
    """
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"Error generating hash for {file_path}: {e}")
        return ""

def get_file_metadata(file_path):
    stat = os.stat(file_path)

    return {
        "id": generate_file_hash(file_path),
        "name": os.path.basename(file_path),
        "extension": os.path.splitext(file_path)[1],
        "size_bytes": stat.st_size,
        "modified_time": datetime.fromtimestamp(stat.st_mtime),
        "path": os.path.abspath(file_path)
    }