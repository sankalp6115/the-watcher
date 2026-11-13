import sqlite3 
import os
from sqlite_db import get_connection, search_text
from PIL import Image

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "watcher.db")
get_connection()
search_query = input("Enter your query: ")
result = search_text(search_query, 20)

for i in range(len(result)):
    print(result[i]["path"])
print(len(result))