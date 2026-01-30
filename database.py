import sqlite3
from datetime import datetime

DB_NAME = "changes.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pages (
                url TEXT PRIMARY KEY,
                content_hash TEXT,
                status TEXT NOT NULL,
                last_checked TEXT NOT NULL,
                last_changed TEXT,
                last_error TEXT
            )
            """
        )
        conn.commit()


def get_page(url: str):
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT content_hash FROM pages WHERE url = ?", (url,)
        )
        row = cursor.fetchone()
        return row[0] if row else None


def save_page(url, content_hash, status, error_message=None):
    now = datetime.utcnow().isoformat()

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT last_changed FROM pages WHERE url = ?", (url,)
        ).fetchone()

        last_changed = existing[0] if existing else None
        if status == "CHANGED":
            last_changed = now

        conn.execute(
            """
            INSERT OR REPLACE INTO pages
            (url, content_hash, status, last_checked, last_changed, last_error)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (url, content_hash, status, now, last_changed, error_message),
        )
        conn.commit()

def get_all_pages():
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT url, status, last_checked, last_changed, last_error
            FROM pages
            ORDER BY last_checked DESC
            """
        )
        return cursor.fetchall()

