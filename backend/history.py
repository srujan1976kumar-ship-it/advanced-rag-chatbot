
import os
import json

import psycopg
from psycopg.rows import dict_row


# --------------------------------------------------
# PostgreSQL configuration
# --------------------------------------------------

DB_CONFIG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": int(os.getenv("PG_PORT", "5433")),
    "dbname": os.getenv("PG_DATABASE", "ragdb"),
    "user": os.getenv("PG_USER", "raguser"),
    "password": os.getenv("PG_PASSWORD", ""),
}


# --------------------------------------------------
# Database connection
# --------------------------------------------------

def get_connection():

    if not DB_CONFIG["password"]:
        raise RuntimeError(
            "PG_PASSWORD environment variable is missing."
        )

    return psycopg.connect(
        **DB_CONFIG,
        row_factory=dict_row
    )


# --------------------------------------------------
# Initialize database
# --------------------------------------------------

def init_db():

    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sources JSONB,
                created_at TIMESTAMP
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

    with get_connection() as conn:

        conn.execute(
            """
            INSERT INTO chat_messages
                (id, session_id, role, content, sources, created_at)
            VALUES (
                (SELECT COALESCE(MAX(id), 0) + 1 FROM chat_messages),
                %s, %s, %s, %s::jsonb, CURRENT_TIMESTAMP
            )
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

    with get_connection() as conn:

        rows = conn.execute(
            """
            SELECT role, content, sources
            FROM chat_messages
            WHERE session_id = %s
            ORDER BY id
            """,
            (session_id,)
        ).fetchall()

        return [
            {
                "role": row["role"],
                "content": row["content"],
                "sources": row["sources"] or []
            }
            for row in rows
        ]


# --------------------------------------------------
# Clear chat history
# --------------------------------------------------

def clear_history(session_id):

    with get_connection() as conn:

        conn.execute(
            """
            DELETE FROM chat_messages
            WHERE session_id = %s
            """,
            (session_id,)
        )


# --------------------------------------------------
# Initialize database on startup
# --------------------------------------------------

init_db()
