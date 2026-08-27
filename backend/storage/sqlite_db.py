import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "watcher.db")
image_embedding_model = "openclip-vit-b-32-laion2b_s34b_b79k"
text_embedding_model = "sentence-transformers/all-MiniLM-L6-v2"

def get_connection():
    """Returns a SQLite connection."""
    return sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

def init_db():
    """Initializes the database schema including the main table and FTS5 virtual table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS images (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        extension TEXT,
        size_bytes INTEGER,
        modified_time TIMESTAMP,
        path TEXT NOT NULL UNIQUE,
        
        cleaned_text TEXT,
        
        text_embedding BLOB,
        image_embedding BLOB,
        
        cluster_id INTEGER,

        text_embedding_model TEXT,
        image_embedding_model TEXT
    )
    """)


    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS images_fts USING fts5(
        id UNINDEXED,
        cleaned_text
    )
    """)
    
    
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS images_ai AFTER INSERT ON images
    BEGIN
        INSERT INTO images_fts(id, cleaned_text) VALUES (new.id, new.cleaned_text);
    END;
    """)
    
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS images_ad AFTER DELETE ON images
    BEGIN
        DELETE FROM images_fts WHERE id = old.id;
    END;
    """)
    
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS images_au AFTER UPDATE ON images
    BEGIN
        DELETE FROM images_fts WHERE id = old.id;
        INSERT INTO images_fts(id, cleaned_text) VALUES (new.id, new.cleaned_text);
    END;
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully at:", DB_PATH)

def get_existing_paths():
    """Returns a set of all absolute image paths currently stored in the DB."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM images")
    paths = {row[0] for row in cursor.fetchall()}
    conn.close()
    return paths

def insert_image_record(record_dict):
    """
    Inserts a single image record into the database.
    record_dict should contain the metadata and cleaned_text from the ingestion pipeline.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        meta = record_dict["metadata"]
        cleaned_text = record_dict.get("cleaned_text", "")
        
        text_embedding_bytes = record_dict.get("text_embedding")
        image_embedding_bytes = record_dict.get("image_embedding")
        cluster_id = record_dict.get("cluster_id")
        
        cursor.execute("""
        INSERT OR REPLACE INTO images (id, name, extension, size_bytes, modified_time, path, cleaned_text, text_embedding, image_embedding, cluster_id, text_embedding_model, image_embedding_model)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            meta["id"],
            meta["name"],
            meta["extension"],
            meta["size_bytes"],
            meta["modified_time"],
            meta["path"],
            cleaned_text,
            text_embedding_bytes,
            image_embedding_bytes,
            cluster_id,
            text_embedding_model,
            image_embedding_model
        ))
        
        conn.commit()
    except Exception as e:
        print(f"Error inserting record for {meta.get('path')}: {e}")
    finally:
        conn.close()

def search_text(keyword, limit=10):
    """
    Performs a fast full-text search using the FTS5 table.
    Returns a list of matching records with their details from the main table.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT i.id, i.name, i.path, i.cleaned_text, i.cluster_id, bm25(images_fts) as score
    FROM images_fts f
    JOIN images i ON f.id = i.id
    WHERE images_fts MATCH ?
    ORDER BY score
    LIMIT ?
    """
    
    cursor.execute(query, (keyword, limit))
    results = cursor.fetchall()
    conn.close()
    formatted_results = []
    for row in results:
        formatted_results.append({
            "id": row[0],
            "name": row[1],
            "path": row[2],
            "cleaned_text": row[3],
            "cluster_id": row[4]
        })
    return formatted_results

def search_text_with_id(img_id):
    """Pass id and get image"""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT id, name, path, cleaned_text, cluster_id FROM images WHERE id=?"
    cursor.execute(query, (img_id,))
    result = cursor.fetchall()
    conn.close()

    formatted_result = []
    for row in result:
        formatted_result.append({
            "id": row[0],
            "name": row[1],
            "path": row[2],
            "cleaned_text": row[3],
            "cluster_id": row[4]
        })

    return formatted_result

def get_img_embedding():
    """
    Returns all image embeddings for clustering algorithm
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT id,image_embedding FROM images
    """

    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    return results

def get_text_embedding():
    """
    Returns all text embeddings for clustering algorithm
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT id, text_embedding FROM images
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

def update_cluster_ids(cluster_mapping):
    """
    Updates the cluster_id for a batch of images.
    cluster_mapping should be a list of tuples: (cluster_id, image_id)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executemany("UPDATE images SET cluster_id = ? WHERE id = ?", cluster_mapping)
    
    conn.commit()
    conn.close()

def get_cluster_with_image():
    """
    Returns all images names with their cluster ids for rendering on ui"""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT id, name, cluster_id FROM images order by cluster_id
    """
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()

    formatted_result = []
    for row in result:
        formatted_result.append({
            "id":row[0],
            "name": row[1],
            "cluster_id":row[2]
        })

    return formatted_result

# if __name__ == "__main__":
# Test initialization when running this script directly
# init_db()
    
