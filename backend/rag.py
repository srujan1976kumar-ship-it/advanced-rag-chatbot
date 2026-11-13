
import os
import uuid

from pathlib import Path
from contextlib import contextmanager

import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader


# --------------------------------------------------
# Embedding model
# --------------------------------------------------

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


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


@contextmanager
def get_db_connection():
    """Create a PostgreSQL connection with pgvector registered."""

    if not DB_CONFIG["password"]:
        raise RuntimeError(
            "PG_PASSWORD environment variable is missing."
        )

    with psycopg.connect(**DB_CONFIG) as connection:
        register_vector(connection)
        yield connection


# --------------------------------------------------
# Split text into chunks
# --------------------------------------------------

def split_text(text, chunk_size=1000, overlap=150):

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# --------------------------------------------------
# Process PDF and store in PostgreSQL
# --------------------------------------------------

def process_pdf(file_path):

    reader = PdfReader(file_path)

    all_chunks = []
    metadatas = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""
        chunks = split_text(text)

        for chunk in chunks:
            all_chunks.append(chunk)

            metadatas.append({
                "source": Path(file_path).name,
                "page": page_number
            })

    if not all_chunks:
        raise ValueError("No readable text found in PDF")

    raw_embeddings = embedding_model.encode(all_chunks)

    embeddings = [
        Vector(embedding.tolist())
        for embedding in raw_embeddings
    ]

    with get_db_connection() as connection:
        with connection.cursor() as cursor:

            for chunk, metadata, embedding in zip(
                all_chunks, metadatas, embeddings
            ):

                cursor.execute(
                    """
                    INSERT INTO documents
                        (id, content, source, page, embedding)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        str(uuid.uuid4()),
                        chunk,
                        metadata["source"],
                        metadata["page"],
                        embedding
                    )
                )

    return len(all_chunks)


# --------------------------------------------------
# Retrieve relevant document chunks
# --------------------------------------------------

def retrieve_documents(question, top_k=4, document_ids=None):

    raw_embedding = embedding_model.encode(question)

    query_embedding = Vector(raw_embedding.tolist())

    with get_db_connection() as connection:
        with connection.cursor() as cursor:

            if document_ids:

                cursor.execute(
                    """
                    SELECT
                        content,
                        source,
                        page,
                        embedding <=> %s AS distance
                    FROM documents
                    WHERE source = ANY(%s)
                    ORDER BY embedding <=> %s
                    LIMIT %s
                    """,
                    (
                        query_embedding,
                        document_ids,
                        query_embedding,
                        top_k
                    )
                )

            else:

                cursor.execute(
                    """
                    SELECT
                        content,
                        source,
                        page,
                        embedding <=> %s AS distance
                    FROM documents
                    ORDER BY embedding <=> %s
                    LIMIT %s
                    """,
                    (
                        query_embedding,
                        query_embedding,
                        top_k
                    )
                )

            rows = cursor.fetchall()

    retrieved = []

    for content, source, page, distance in rows:

        retrieved.append({
            "text": content,
            "source": source,
            "page": page,
            "distance": float(distance)
        })

    return retrieved


# --------------------------------------------------
# Delete document from PostgreSQL
# --------------------------------------------------

def delete_document(document_id):

    with get_db_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM documents
                WHERE source = %s
                """,
                (document_id,)
            )

            deleted_count = cursor.rowcount

    return deleted_count


# --------------------------------------------------
# PostgreSQL collection compatibility wrapper
# --------------------------------------------------

class PostgreSQLCollection:

    def count(self):

        with get_db_connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    "SELECT COUNT(*) FROM documents"
                )

                return cursor.fetchone()[0]

    def get(self, where=None, include=None):

        with get_db_connection() as connection:
            with connection.cursor() as cursor:

                if where and "source" in where:

                    cursor.execute(
                        """
                        SELECT id, source, page
                        FROM documents
                        WHERE source = %s
                        """,
                        (where["source"],)
                    )

                else:

                    cursor.execute(
                        """
                        SELECT id, source, page
                        FROM documents
                        """
                    )

                rows = cursor.fetchall()

        return {
            "ids": [row[0] for row in rows],
            "metadatas": [
                {
                    "source": row[1],
                    "page": row[2]
                }
                for row in rows
            ]
        }


collection = PostgreSQLCollection()
