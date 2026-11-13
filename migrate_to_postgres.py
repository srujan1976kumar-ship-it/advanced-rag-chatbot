
import json
import os
from pathlib import Path

import psycopg
from pgvector.psycopg import register_vector


# --------------------------------------------------
# Configuration
# --------------------------------------------------

EXPORT_DIR = Path(__file__).resolve().parent / "migration-export"


def load_json(filename):
    """Load a JSON export file."""
    file_path = EXPORT_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Export file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def prepare_sources(sources):
    """Convert SQLite sources into valid PostgreSQL JSON data."""
    if sources is None or sources == "":
        return None

    if isinstance(sources, str):
        try:
            parsed = json.loads(sources)
            return json.dumps(parsed)
        except json.JSONDecodeError:
            # Preserve plain text if the original value isn't JSON.
            return json.dumps(sources)

    return json.dumps(sources)


def main():
    # Read password from environment; never hardcode it.
    password = os.environ.get("PG_PASSWORD")

    if not password:
        raise RuntimeError(
            "PG_PASSWORD is missing. Set it in PowerShell first."
        )

    # Load exported data.
    documents = load_json("chroma_records.json")
    messages = load_json("chat_history.json")

    print("Loaded document records:", len(documents))
    print("Loaded chat messages:", len(messages))

    # Validate before inserting.
    for item in documents:
        if len(item["embedding"]) != 384:
            raise ValueError(
                f"Incorrect embedding dimensions for record {item['id']}"
            )

        if not item.get("content"):
            raise ValueError(
                f"Missing document content for record {item['id']}"
            )

        metadata = item.get("metadata") or {}

        if "source" not in metadata or "page" not in metadata:
            raise ValueError(
                f"Missing metadata for record {item['id']}"
            )

    # Connect to local PostgreSQL.
    with psycopg.connect(
        host="localhost",
        port=5433,
        dbname="ragdb",
        user="raguser",
        password=password,
    ) as connection:

        register_vector(connection)

        with connection.cursor() as cursor:

            # Insert document chunks and embeddings.
            for item in documents:
                metadata = item["metadata"]

                cursor.execute(
                    """
                    INSERT INTO documents
                        (id, content, source, page, embedding)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        item["id"],
                        item["content"],
                        metadata["source"],
                        int(metadata["page"]),
                        item["embedding"],
                    ),
                )

            # Insert chat history.
            for item in messages:
                cursor.execute(
                    """
                    INSERT INTO chat_messages
                        (id, session_id, role, content, sources, created_at)
                    VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        item["id"],
                        item["session_id"],
                        item["role"],
                        item["content"],
                        prepare_sources(item.get("sources")),
                        item["created_at"],
                    ),
                )

        # Commit both sets of records together.
        connection.commit()

        # Verify database counts.
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM documents")
            document_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM chat_messages")
            message_count = cursor.fetchone()[0]

    print("\nMigration completed successfully.")
    print("Documents in PostgreSQL:", document_count)
    print("Chat messages in PostgreSQL:", message_count)


if __name__ == "__main__":
    main()
