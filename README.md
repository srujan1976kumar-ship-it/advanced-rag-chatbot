# 🤖 Advanced RAG Chatbot

An AI-powered document question-answering application built using **Retrieval-Augmented Generation (RAG)**. Upload PDF documents, retrieve relevant content using vector similarity search, and generate document-grounded answers with source citations.

## 🚀 Features

- Upload and manage multiple PDF documents.
- Extract and process PDF text automatically.
- Split documents into overlapping text chunks.
- Generate 384-dimensional embeddings using SentenceTransformers.
- Store document embeddings in PostgreSQL using pgvector.
- Retrieve relevant content using cosine similarity search.
- Display source filenames and page numbers.
- Filter retrieval by selected documents.
- Maintain conversation history using PostgreSQL.
- Delete uploaded documents and their indexed chunks.
- Export conversations as TXT and PDF files.
- Interactive Streamlit frontend.
- FastAPI backend with REST API endpoints.
- Docker-based containerized deployment.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.11 | Backend programming |
| FastAPI | Backend REST API |
| Streamlit | Frontend interface |
| PostgreSQL 16 | Relational database |
| pgvector | Vector similarity search |
| SentenceTransformers | Text embeddings |
| all-MiniLM-L6-v2 | Embedding model |
| OpenAI API (optional) | LLM answer generation |
| PyPDF | PDF text extraction |
| ReportLab | PDF export |
| Docker | Containerization |

## 🏗️ Architecture

```text
             USER
               |
               v
       STREAMLIT FRONTEND
               |
               v
         FASTAPI BACKEND
               |
       +-------+-------+
       |               |
       v               v
  PDF PROCESSING   CHAT HISTORY
       |               |
       v               v
  TEXT CHUNKING    POSTGRESQL
       |
       v
  SENTENCE TRANSFORMERS
       |
       v
  384-D EMBEDDINGS
       |
       v
  POSTGRESQL + PGVECTOR
       |
       v
  COSINE SIMILARITY SEARCH
       |
       v
  RETRIEVED DOCUMENT CONTEXT
       |
       v
  LLM ANSWER GENERATION
       |
       v
  ANSWER WITH CITATIONS
```

**Note:** LLM answer generation is optional and requires an appropriately configured API key. It is currently disabled in the local setup.

## 📁 Project Structure

```text
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
├── data/
├── backup-before-cloud-migration/
├── migration-export/
│
├── Dockerfile.backend
├── Dockerfile.frontend
├── requirements.txt
├── requirements.frontend.txt
├── migrate_to_postgres.py
├── .dockerignore
├── .gitignore
└── README.md
```

Private backups and migration exports are local-only and should not be committed to GitHub.

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/srujan1976kumar-ship-it/advanced-rag-chatbot.git
cd advanced-rag-chatbot
```

### 2. Create a virtual environment

```powershell
py -3.11 -m venv .venv
```

### 3. Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Configure PostgreSQL

Create a PostgreSQL database and enable pgvector:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Configure the database connection using environment variables:

```powershell
$env:PG_HOST="localhost"
$env:PG_PORT="5433"
$env:PG_DATABASE="ragdb"
$env:PG_USER="raguser"
```

Set `PG_PASSWORD` securely in your terminal. Never commit database passwords.

## 🐳 Docker Setup

The project uses three Docker containers:

| Container | Service |
|---|---|
| rag-postgres | PostgreSQL + pgvector |
| rag-backend-pg | FastAPI backend |
| rag-frontend-pg | Streamlit frontend |

The application has been tested locally using Docker.

### Local application URLs

- Frontend: http://localhost:8502
- Backend: http://localhost:8000
- API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Check running containers

```powershell
docker ps
```

### Stop application containers

```powershell
docker stop rag-frontend-pg rag-backend-pg rag-postgres
```

### Start existing containers

```powershell
docker start rag-postgres
docker start rag-backend-pg
docker start rag-frontend-pg
```

## 💡 How It Works

1. The user uploads a PDF through Streamlit.
2. FastAPI receives and validates the PDF.
3. PyPDF extracts text from each page.
4. Extracted text is split into overlapping chunks.
5. SentenceTransformers generates 384-dimensional embeddings.
6. PostgreSQL stores document chunks, metadata, and embeddings.
7. The user's question is converted into an embedding.
8. pgvector performs cosine-distance similarity search.
9. Relevant document chunks are retrieved.
10. The optional LLM uses the retrieved context to generate an answer with source citations.

## 🧪 Testing and Verification

The PostgreSQL + pgvector migration has been tested locally.

| Test | Result |
|---|---|
| PostgreSQL connection | Passed |
| pgvector extension | Passed |
| PDF document migration | Passed |
| Document chunk count | 34 |
| Embedding dimensions | 384 |
| Chat history table | Passed |
| Docker backend | Passed |
| Docker frontend | Passed |
| API health check | Passed |
| Document listing | Passed |
| Vector retrieval | Passed |
| PDF upload and deletion | Passed |

## 🎯 Project Objective

To build an intelligent document assistant that combines semantic search and Retrieval-Augmented Generation to retrieve relevant information from PDF documents and provide accurate, context-aware answers with source citations.

## 🔮 Future Enhancements

- Enable optional LLM answer generation.
- Add document reranking.
- Support DOCX and additional file formats.
- Add user authentication.
- Improve retrieval evaluation.
- Add document comparison and analytics.
- Introduce automated deployment workflows.

## 👨‍💻 Author

**Sai Srujan**

GitHub: https://github.com/srujan1976kumar-ship-it

---

*Built with Python, FastAPI, Streamlit, PostgreSQL, pgvector, SentenceTransformers, and Docker.*