
import os
import sqlite3
import json

from pathlib import Path


# --------------------------------------------------
# Persistent SQLite database configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = Path(
    os.getenv(
        "CHAT_DB_PATH",
        str(BASE_DIR / "chat_history.db")
    )
)

DB_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# Initialize database
# --------------------------------------------------

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


# --------------------------------------------------
# Save message
# --------------------------------------------------

def save_message(
    session_id,
    role,
    content,
    sources=None
):

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


# --------------------------------------------------
# Retrieve chat history
# --------------------------------------------------

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
                "sources": json.loads(
                    row["sources"] or "[]"
                )
            }
            for row in rows
        ]


# --------------------------------------------------
# Clear chat history
# --------------------------------------------------

def clear_history(session_id):

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute(
            """
            DELETE FROM messages
            WHERE session_id = ?
            """,
            (session_id,)
        )


# --------------------------------------------------
# Initialize database on startup
# --------------------------------------------------

init_db()
