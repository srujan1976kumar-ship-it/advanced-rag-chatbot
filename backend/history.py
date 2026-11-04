
import sqlite3
import json
from pathlib import Path

DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "chat_history.db"
)


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sources TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_message(session_id, role, content, sources=None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO messages
            (session_id, role, content, sources)
            VALUES (?, ?, ?, ?)
            """,
            (
                session_id,
                role,
                content,
                json.dumps(sources or [])
            )
        )


def get_history(session_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute(
            """
            SELECT role, content, sources
            FROM messages
            WHERE session_id = ?
            ORDER BY id
            """,
            (session_id,)
        ).fetchall()

        return [
            {
                "role": row["role"],
                "content": row["content"],
                "sources": json.loads(row["sources"] or "[]")
            }
            for row in rows
        ]


def clear_history(session_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "DELETE FROM messages WHERE session_id = ?",
            (session_id,)
        )


init_db()
