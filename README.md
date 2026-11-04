# 🤖 Advanced RAG Chatbot

An AI-powered document question-answering application built using Retrieval-Augmented Generation (RAG). Upload PDF documents, ask questions, and receive document-grounded answers with source citations.

## 🚀 Features

- Upload multiple PDF documents.
- Extract and process PDF text.
- Generate embeddings using SentenceTransformers.
- Store document vectors using ChromaDB.
- Retrieve relevant document sections.
- Generate answers using the local Ollama LLM.
- Select multiple PDFs for question answering.
- Display source filenames and page numbers.
- View retrieval distance for retrieved sources.
- Maintain chat history using SQLite.
- Delete uploaded documents.
- Export conversations as TXT and PDF files.
- Streamlit-based interactive user interface.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | Backend API |
| Streamlit | Frontend interface |
| Ollama | Local language model |
| Llama 3.2 | Text generation |
| ChromaDB | Vector database |
| SentenceTransformers | Text embeddings |
| SQLite | Chat history |
| PyPDF | PDF text extraction |
| ReportLab | PDF export |

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
├── chroma_db/
├── README.md
├── requirements.txt
└── .gitignore
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/srujan1976kumar-ship-it/advanced-rag-chatbot.git
cd advanced-rag-chatbot
```

### 2. Create a virtual environment

Windows:

```powershell
py -m venv .venv
```

### 3. Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Install and start Ollama

Install Ollama, then download the model:

```bash
ollama pull llama3.2
```

Make sure the Ollama service is running.

## ▶️ Run the Application

### Start the FastAPI backend

Open the first terminal:

```powershell
python -m uvicorn backend.main:app --reload
```

Backend:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

### Start the Streamlit frontend

Open a second terminal:

```powershell
python -m streamlit run frontend/app.py
```

Frontend:

`http://localhost:8501`

## 💡 How It Works

1. Upload PDF documents through the Streamlit interface.
2. Extract text from the uploaded documents.
3. Split the text into smaller chunks.
4. Generate embeddings for the chunks.
5. Store embeddings and metadata in ChromaDB.
6. Convert the user's question into an embedding.
7. Retrieve relevant document chunks.
8. Send the retrieved context to the Ollama language model.
9. Display the generated answer with source references.

## 🎯 Project Objective

To develop an intelligent document assistant that uses Retrieval-Augmented Generation to retrieve relevant information from uploaded PDF documents and provide context-aware answers with source citations.

## 🔮 Future Enhancements

- Support additional document formats.
- Improve retrieval and reranking.
- Add user authentication.
- Add document comparison.
- Improve response evaluation.
- Add more advanced document analytics.

## 👨‍💻 Author

**Sai Srujan**

GitHub: https://github.com/srujan1976kumar-ship-it

---

*Built with Python, FastAPI, Streamlit, ChromaDB, and Ollama.*