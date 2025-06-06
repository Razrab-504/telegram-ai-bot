import sqlite3
import os
from typing import List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "chat_history.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    user_id INTEGER,
    role TEXT,
    content TEXT
)
""")
conn.commit()


def add_message(user_id: int, role: str, content: str):
    cursor.execute("INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)",
                   (user_id, role, content))
    conn.commit()


def get_user_history(user_id: int, limit: int = 10) -> List[dict]:
    cursor.execute("SELECT role, content FROM history WHERE user_id = ? ORDER BY rowid DESC LIMIT ?", (user_id, limit))
    rows = cursor.fetchall()
    return [{"role": role, "content": content} for role, content in reversed(rows)]


def trim_user_history(user_id: int, max_messages: int = 20):
    cursor.execute("SELECT rowid FROM history WHERE user_id = ? ORDER BY rowid DESC", (user_id,))
    rows = cursor.fetchall()
    if len(rows) > max_messages:
        to_delete = rows[max_messages:]
        ids = [str(row[0]) for row in to_delete]
        cursor.execute(f"DELETE FROM history WHERE rowid IN ({','.join(ids)})")
        conn.commit()
