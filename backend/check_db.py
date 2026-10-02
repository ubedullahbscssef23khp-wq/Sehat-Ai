import sqlite3
import os
conn = sqlite3.connect("backend/data/sehat.sqlite")
cursor = conn.cursor()
cursor.execute("SELECT count(*) FROM messages")
print(f"Messages count: {cursor.fetchone()[0]}")
