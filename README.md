# Advanced RAG Chatbot

An AI-powered Retrieval-Augmented Generation chatbot that allows users to upload PDF documents and ask questions based on their content.

## Features

- Upload multiple PDF documents
- Extract text from PDFs
- Semantic search using Sentence Transformers
- Vector storage using ChromaDB
- AI responses using Ollama and Llama 3.2
- Select specific PDFs for question answering
- Source citations with page numbers
- Conversation history using SQLite
- PDF summarization
- Delete uploaded documents

## Technologies

- Python
- FastAPI
- Streamlit
- Ollama
- Llama 3.2
- ChromaDB
- Sentence Transformers
- SQLite
- PyPDF

## Requirements

- Python 3.10 or newer
- Ollama
- Llama 3.2 model

## Installation

Install dependencies:

    pip install -r requirements.txt

Make sure Ollama is running and Llama 3.2 is available.

## Run the Backend

    python -m uvicorn backend.main:app --reload

## Run the Frontend

Open another terminal:

    python -m streamlit run frontend/app.py

Open the application:

http://localhost:8501

Backend API documentation:

http://127.0.0.1:8000/docs

## Project Structure

    advanced-rag-chatbot/
    ├── backend/
    ├── frontend/
    ├── .gitignore
    ├── README.md
    └── requirements.txt

## Note

Uploaded PDFs, local databases, ChromaDB storage, and virtual environments are excluded from GitHub.
