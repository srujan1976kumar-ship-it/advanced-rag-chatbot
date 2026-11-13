# 🤖 Advanced RAG Chatbot

An AI-powered document question-answering system built using
**Retrieval-Augmented Generation (RAG)**. Upload PDF documents, retrieve
relevant information through vector similarity search, and generate
document-grounded answers with source citations.

The application uses PostgreSQL and pgvector for persistent storage and
semantic retrieval, FastAPI for backend services, and Streamlit for the
interactive frontend.

## 🚀 Features

-   Upload and manage multiple PDF documents.
-   Automatically extract and process PDF text.
-   Split documents into overlapping text chunks.
-   Generate 384-dimensional embeddings using SentenceTransformers.
-   Store document embeddings in PostgreSQL with pgvector.
-   Perform cosine-distance vector similarity search.
-   Retrieve relevant document content with source filenames and page
    numbers.
-   Filter retrieval by selected documents.
-   Maintain persistent conversation history using PostgreSQL.
-   Delete uploaded documents and their indexed chunks.
-   Export conversations as TXT and PDF files.
-   Interactive Streamlit frontend.
-   FastAPI backend with REST API endpoints.
-   Docker Compose orchestration for the complete application.

## 🛠️ Technologies Used

  Technology              Purpose
  ----------------------- -------------------------------
  Python 3.11             Programming language
  FastAPI                 Backend REST API
  Streamlit               Frontend interface
  PostgreSQL 16           Persistent database
  pgvector                Vector similarity search
  SentenceTransformers    Text embeddings
  all-MiniLM-L6-v2        Embedding model
  OpenAI API (optional)   LLM answer generation
  PyPDF                   PDF text extraction
  ReportLab               PDF export
  Docker                  Containerization
  Docker Compose          Multi-container orchestration

## 🏗️ System Architecture

``` text
                 USER
                   |
                   v
           STREAMLIT FRONTEND
                   |
                   v
             FASTAPI BACKEND
                   |
          +--------+--------+
          |                 |
          v                 v
     PDF PROCESSING     CHAT HISTORY
          |                 |
          v                 |
     TEXT CHUNKING           |
          |                 |
          v                 |
   SENTENCE TRANSFORMERS     |
          |                 |
          v                 |
    384-D EMBEDDINGS         |
          |                 |
          v                 |
    POSTGRESQL + PGVECTOR
          |
          v
    COSINE SIMILARITY SEARCH
          |
          v
    RETRIEVED DOCUMENT CONTEXT
          |
          v
    OPTIONAL LLM GENERATION
          |
          v
    ANSWER WITH CITATIONS
```

**Note:** Document embedding and vector retrieval work locally. LLM
answer generation is optional and requires an appropriately configured
API key. It is disabled in the current local setup.

## 📁 Project Structure

``` text
advanced-rag-chatbot/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── rag.py
│   └── history.py
│
├── frontend/
│   └── app.py
│
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── requirements.txt
├── requirements.frontend.txt
├── migrate_to_postgres.py
├── .dockerignore
├── .gitignore
└── README.md
```

Private PDFs, database files, backups, migration exports, and
environment files are kept locally and excluded from Git.

## ⚙️ Installation and Setup

### 1. Clone the repository

``` bash
git clone https://github.com/srujan1976kumar-ship-it/advanced-rag-chatbot.git
cd advanced-rag-chatbot
```

### 2. Prerequisites

Install:

-   Docker Desktop
-   Docker Compose (included with Docker Desktop)
-   Git

Make sure Docker Desktop is running.

### 3. Configure environment variables

Create a `.env` file in the project root.

Add your PostgreSQL password locally:

``` env
PG_PASSWORD=YOUR_LOCAL_DATABASE_PASSWORD
```

Use a strong password. Never commit `.env` or share its contents.

### 4. Start the application

Run:

``` powershell
docker compose up -d --build
```

Docker Compose starts three services:

  Service      Container         Purpose
  ------------ ----------------- -----------------------------
  PostgreSQL   rag-postgres      Database and vector storage
  Backend      rag-backend-pg    FastAPI application
  Frontend     rag-frontend-pg   Streamlit interface

### 5. Verify containers

``` powershell
docker compose ps
```

Check backend health:

``` powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

### 6. Access the application

  Component            URL
  -------------------- ------------------------------
  Streamlit frontend   http://localhost:8502
  FastAPI backend      http://localhost:8000
  API documentation    http://localhost:8000/docs
  Health check         http://localhost:8000/health

## 🐳 Docker Compose Commands

Start all services:

``` powershell
docker compose up -d
```

Stop and remove Compose containers:

``` powershell
docker compose down
```

View running services:

``` powershell
docker compose ps
```

View backend logs:

``` powershell
docker compose logs --tail 50 backend
```

View all service logs:

``` powershell
docker compose logs
```

Restart services:

``` powershell
docker compose restart
```

**Data safety:** `docker compose down` removes the Compose containers
and network but preserves the named PostgreSQL volume. Do not use
`docker compose down -v` unless you intentionally want to delete the
database volume.

## 💡 How It Works

1.  The user uploads a PDF through the Streamlit interface.
2.  FastAPI receives and validates the PDF.
3.  PyPDF extracts text from each page.
4.  Extracted text is split into overlapping chunks.
5.  SentenceTransformers generates 384-dimensional embeddings.
6.  PostgreSQL stores document chunks, metadata, and embeddings.
7.  The user's question is converted into an embedding.
8.  pgvector performs cosine-distance similarity search.
9.  Relevant document chunks are retrieved.
10. The optional LLM generates a contextual answer using the retrieved
    information.
11. Source filenames and page numbers support answer verification.

## 🧪 Testing and Verification

The PostgreSQL + pgvector migration and Docker Compose setup have been
tested locally.

  Test                      Result
  ------------------------- -------------
  PostgreSQL connection     Passed
  pgvector extension        Passed
  PDF migration             Passed
  Document chunks           34 verified
  Embedding dimensions      384
  Chat history database     Verified
  Docker backend            Passed
  Docker frontend           Passed
  Docker Compose            Passed
  API health check          Passed
  Document listing          Passed
  Vector retrieval          Passed
  PDF upload and deletion   Passed

## 🎯 Project Objective

To develop an intelligent document assistant that combines semantic
search and Retrieval-Augmented Generation to retrieve relevant
information from PDF documents and provide context-aware answers with
source citations.

## 🔮 Future Enhancements

-   Enable optional LLM answer generation.
-   Implement document reranking.
-   Support DOCX and additional file formats.
-   Add user authentication and session management.
-   Improve retrieval evaluation.
-   Add document comparison and analytics.
-   Introduce automated deployment workflows.

## 👨‍💻 Author

**Sai Srujan**

GitHub: https://github.com/srujan1976kumar-ship-it

**Project Repository:**\
https://github.com/srujan1976kumar-ship-it/advanced-rag-chatbot

------------------------------------------------------------------------

*Built with Python, FastAPI, Streamlit, PostgreSQL, pgvector,
SentenceTransformers, and Docker.*
