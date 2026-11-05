
import os
import chromadb
import uuid

from pathlib import Path
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader


# --------------------------------------------------
# Initialize embedding model
# --------------------------------------------------

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# --------------------------------------------------
# Persistent ChromaDB configuration
# --------------------------------------------------

CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    str(
        Path(__file__).resolve().parent.parent
        / "chroma_db"
    )
)

Path(CHROMA_PATH).mkdir(
    parents=True,
    exist_ok=True
)

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_or_create_collection(
    name="rag_documents"
)


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
# Process PDF and index its content
# --------------------------------------------------

def process_pdf(file_path):

    reader = PdfReader(file_path)

    all_chunks = []
    metadatas = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text() or ""

        chunks = split_text(text)

        for chunk in chunks:

            all_chunks.append(chunk)

            metadatas.append({
                "source": Path(file_path).name,
                "page": page_number
            })

    if not all_chunks:
        raise ValueError(
            "No readable text found in PDF"
        )

    embeddings = embedding_model.encode(
        all_chunks
    ).tolist()

    ids = [
        str(uuid.uuid4())
        for _ in all_chunks
    ]

    collection.add(
        ids=ids,
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(all_chunks)


# --------------------------------------------------
# Retrieve relevant document chunks
# --------------------------------------------------

def retrieve_documents(
    question,
    top_k=4,
    document_ids=None
):

    if collection.count() == 0:
        return []

    query_embedding = embedding_model.encode(
        question
    ).tolist()

    query_args = {
        "query_embeddings": [query_embedding],
        "n_results": min(
            top_k,
            collection.count()
        ),
        "include": [
            "documents",
            "metadatas",
            "distances"
        ]
    }

    if document_ids:

        query_args["where"] = {
            "source": {
                "$in": document_ids
            }
        }

    results = collection.query(
        **query_args
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    retrieved = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        retrieved.append({
            "text": document,
            "source": metadata["source"],
            "page": metadata["page"],
            "distance": float(distance)
        })

    return retrieved


# --------------------------------------------------
# Delete document and its indexed chunks
# --------------------------------------------------

def delete_document(document_id):

    result = collection.get(
        where={
            "source": document_id
        },
        include=["metadatas"]
    )

    chunk_count = len(
        result["ids"]
    )

    if chunk_count > 0:

        collection.delete(
            where={
                "source": document_id
            }
        )

    return chunk_count
