import sqlite3

DB_FILE = "moviebot.db"

def get_conn():
    return sqlite3.connect(DB_FILE)

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            success BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()

def save_search(query, success):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO search_history (query, success) VALUES (?, ?);", (query, success))
        conn.commit()
