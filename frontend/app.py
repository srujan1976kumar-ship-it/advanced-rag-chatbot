
import os
from io import BytesIO

import requests
import streamlit as st

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet


# ==================================================
# 1. BACKEND CONFIGURATION
# ==================================================

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


# ==================================================
# 2. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Advanced RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)


# ==================================================
# 3. CUSTOM UI STYLING
# ==================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #101827, #17243a);
    color: #f1f5f9;
}

h1 {
    color: #60a5fa !important;
    font-weight: 800 !important;
}

h2, h3 {
    color: #bfdbfe !important;
}

section[data-testid="stSidebar"] {
    background: #111c2e;
    border-right: 1px solid #334155;
}

div[data-testid="stChatMessage"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 12px;
}

.stButton > button {
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 9px;
    padding: 9px 16px;
    font-weight: 600;
}

.stButton > button:hover {
    background: #1d4ed8;
    color: white;
}

.stTextInput input,
.stChatInput input {
    background: #1e293b;
    color: white;
    border: 1px solid #475569;
    border-radius: 10px;
}

div[data-testid="stFileUploader"] {
    background: #1e293b;
    border-radius: 12px;
    padding: 10px;
}

div[data-testid="stExpander"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
}

hr {
    border-color: #334155;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# 4. SESSION STATE
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []

if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False

if "document_selector" not in st.session_state:
    st.session_state.document_selector = []

if "suggested_question" not in st.session_state:
    st.session_state.suggested_question = None


# ==================================================
# 5. LOAD DOCUMENTS FROM BACKEND
# ==================================================

try:
    response = requests.get(
        f"{API_URL}/documents",
        timeout=30
    )

    if response.ok:
        result = response.json()

        st.session_state.uploaded_docs = (
            result.get("documents", [])
        )
    else:
        st.error(
            f"Could not load documents: {response.text}"
        )

except requests.RequestException as error:
    st.error(
        f"Document loading failed: {error}"
    )


# ==================================================
# 6. SYNCHRONIZE DOCUMENT SELECTION
# ==================================================

valid_document_ids = {
    doc["document_id"]
    for doc in st.session_state.uploaded_docs
}

if not st.session_state.document_selector:
    st.session_state.document_selector = list(
        valid_document_ids
    )
else:
    st.session_state.document_selector = [
        doc_id
        for doc_id in st.session_state.document_selector
        if doc_id in valid_document_ids
    ]


# ==================================================
# 7. LOAD SAVED CHAT HISTORY
# ==================================================

if not st.session_state.history_loaded:

    try:
        saved = requests.get(
            f"{API_URL}/history/local-user",
            timeout=30
        )

        if saved.ok:
            st.session_state.messages = (
                saved.json().get("messages", [])
            )

        st.session_state.history_loaded = True

    except requests.RequestException as error:
        st.warning(
            f"Could not load chat history: {error}"
        )

        st.session_state.history_loaded = True


# ==================================================
# 8. SIDEBAR - DOCUMENT MANAGER
# ==================================================

with st.sidebar:

    st.title("📚 Document Manager")

    st.write(
        "Upload PDF documents to chat with them."
    )

    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )

    # ----------------------------------------------
    # Upload PDF documents
    # ----------------------------------------------

    if st.button(
        "Upload Documents",
        use_container_width=True
    ):

        if not uploaded_files:
            st.warning(
                "Please select a PDF first."
            )

        else:

            for uploaded_file in uploaded_files:

                try:
                    response = requests.post(
                        f"{API_URL}/upload",
                        files={
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                "application/pdf"
                            )
                        },
                        timeout=180
                    )

                    if response.ok:

                        result = response.json()

                        new_document = {
                            "filename": result["filename"],
                            "document_id": result["document_id"],
                            "chunks": result["chunks_created"]
                        }

                        existing_ids = {
                            doc["document_id"]
                            for doc in st.session_state.uploaded_docs
                        }

                        if result["document_id"] not in existing_ids:

                            st.session_state.uploaded_docs.append(
                                new_document
                            )

                            st.session_state.document_selector.append(
                                result["document_id"]
                            )

                        st.success(
                            f"{uploaded_file.name}: "
                            f"{result['chunks_created']} chunks indexed"
                        )

                    else:
                        st.error(response.text)

                except requests.RequestException as error:
                    st.error(
                        f"Upload failed: {error}"
                    )


    # ----------------------------------------------
    # Display uploaded documents
    # ----------------------------------------------

    st.divider()

    st.subheader("Uploaded Documents")

    if st.session_state.uploaded_docs:

        for document in st.session_state.uploaded_docs:

            st.write(
                f"📄 {document['filename']} "
                f"({document['chunks']} chunks)"
            )

            if st.button(
                f"Delete {document['filename']}",
                key=f"delete_{document['document_id']}"
            ):

                try:
                    response = requests.delete(
                        f"{API_URL}/documents/"
                        f"{document['document_id']}",
                        timeout=30
                    )

                    if response.ok:

                        st.session_state.uploaded_docs = [
                            doc
                            for doc in st.session_state.uploaded_docs
                            if doc["document_id"]
                            != document["document_id"]
                        ]

                        st.session_state.document_selector = [
                            doc_id
                            for doc_id in st.session_state.document_selector
                            if doc_id != document["document_id"]
                        ]

                        st.success(
                            "Document deleted successfully!"
                        )

                        st.rerun()

                    else:
                        st.error(response.text)

                except requests.RequestException as error:
                    st.error(
                        f"Deletion failed: {error}"
                    )

    else:
        st.caption(
            "No documents uploaded."
        )


    # ----------------------------------------------
    # Select documents
    # ----------------------------------------------

    st.divider()

    st.subheader("🎯 Document Selection")

    document_options = {
        doc["document_id"]: doc["filename"]
        for doc in st.session_state.uploaded_docs
    }

    st.multiselect(
        "Choose PDFs for AI answers",
        options=list(document_options.keys()),
        format_func=lambda doc_id: document_options[doc_id],
        key="document_selector"
    )


    # ----------------------------------------------
    # Clear chat history
    # ----------------------------------------------

    st.divider()

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        try:
            response = requests.delete(
                f"{API_URL}/history/local-user",
                timeout=30
            )

            if response.ok:

                st.session_state.messages = []

                st.success(
                    "Chat history cleared."
                )

                st.rerun()

            else:
                st.error(response.text)

        except requests.RequestException as error:
            st.error(
                f"Could not clear chat: {error}"
            )


    # ----------------------------------------------
    # Backend health status
    # ----------------------------------------------

    st.divider()

    st.subheader("Backend Status")

    try:
        health = requests.get(
            f"{API_URL}/health",
            timeout=10
        )

        if health.ok:

            health_data = health.json()

            st.success(
                "Backend connected"
            )

            st.caption(
                f"Indexed chunks: "
                f"{health_data['documents_indexed']}"
            )

            if not health_data.get("llm_configured"):
                st.warning(
                    "OpenAI API key is not configured."
                )

        else:
            st.error(
                "Backend unavailable"
            )

    except requests.RequestException:
        st.error(
            "Cannot connect to backend"
        )


# ==================================================
# 9. MAIN DASHBOARD
# ==================================================

st.title("🤖 Advanced RAG Chatbot")

st.markdown(
    "### Intelligent Document Question Answering"
)

st.caption(
    "Upload PDFs, select documents, and get "
    "AI-powered answers with page citations."
)


# ==================================================
# 10. DASHBOARD STATISTICS
# ==================================================

col1, col2, col3 = st.columns(3)

total_pdfs = len(
    st.session_state.uploaded_docs
)

total_chunks = sum(
    doc.get("chunks", 0)
    for doc in st.session_state.uploaded_docs
)

selected_pdfs = len(
    st.session_state.document_selector
)

with col1:
    st.metric(
        "📚 Total PDFs",
        total_pdfs
    )

with col2:
    st.metric(
        "🧩 Indexed Chunks",
        total_chunks
    )

with col3:
    st.metric(
        "🎯 Selected PDFs",
        selected_pdfs
    )


st.divider()


# ==================================================
# 11. DOCUMENT OVERVIEW
# ==================================================

st.subheader("📂 Document Overview")

if st.session_state.uploaded_docs:

    for doc in st.session_state.uploaded_docs:

        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.write(
                f"📄 **{doc['filename']}**"
            )

        with col2:
            st.caption(
                f"{doc.get('chunks', 0)} chunks"
            )

        with col3:

            if doc["document_id"] in (
                st.session_state.document_selector
            ):
                st.success("Selected")
            else:
                st.caption("Not selected")

else:
    st.info(
        "No PDF documents uploaded yet."
    )


st.divider()


# ==================================================
# 12. DISPLAY PREVIOUS MESSAGES
# ==================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )

        if message.get("sources"):

            with st.expander("📚 View Sources"):

                for source in message["sources"]:

                    st.write(
                        f"📄 **{source['filename']}** "
                        f"— Page {source['page']}"
                    )

                    distance = source.get("distance")

                    if distance is not None:
                        st.caption(
                            f"Retrieval distance: {distance:.4f} "
                            "(lower is a closer match)"
                        )


# ==================================================
# 13. WELCOME SCREEN
# ==================================================

if not st.session_state.messages:

    st.markdown(
        "## 👋 Welcome to your AI Document Assistant"
    )

    st.write(
        "Ask questions about your uploaded PDFs. "
        "The chatbot will search your documents and "
        "provide answers with source references."
    )

    st.markdown("### 💡 Try asking")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "📄 Find key information",
            use_container_width=True
        ):

            st.session_state.suggested_question = (
                "What are the most important points "
                "in the selected documents?"
            )

            st.rerun()

    with col2:

        if st.button(
            "📚 Explain the main topics",
            use_container_width=True
        ):

            st.session_state.suggested_question = (
                "Explain the main topics covered "
                "in the selected documents."
            )

            st.rerun()


# ==================================================
# 14. CHAT INPUT AND AI RESPONSE
# ==================================================

suggested_question = (
    st.session_state.suggested_question
)

if suggested_question:

    prompt = suggested_question

    st.session_state.suggested_question = None

else:

    prompt = st.chat_input(
        "Ask a question about your documents..."
    )


if prompt:

    if not st.session_state.uploaded_docs:

        st.warning(
            "Please upload a PDF first."
        )

    elif not st.session_state.document_selector:

        st.warning(
            "Please select at least one PDF."
        )

    else:

        # Display user question
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner(
                "Searching documents and generating answer..."
            ):

                try:

                    # Corrected history selection
                    previous_history = [
                        {
                            "role": message["role"],
                            "content": message["content"]
                        }
                        for message in (
                            st.session_state.messages[:-1][-8:]
                        )
                    ]

                    response = requests.post(
                        f"{API_URL}/chat",
                        json={
                            "message": prompt,
                            "history": previous_history,
                            "session_id": "local-user",
                            "document_ids": (
                                st.session_state.document_selector
                            )
                        },
                        timeout=180
                    )

                    if response.ok:

                        result = response.json()

                        answer = result["answer"]

                        sources = result.get(
                            "sources",
                            []
                        )

                        st.markdown(answer)

                        if sources:

                            with st.expander("📚 View Sources"):

                                for source in sources:

                                    st.write(
                                        f"📄 **{source['filename']}** "
                                        f"— Page {source['page']}"
                                    )

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })

                    else:

                        st.error(
                            f"Request failed: {response.text}"
                        )

                        st.session_state.messages.pop()

                except requests.RequestException as error:

                    st.error(
                        f"Could not connect to backend: {error}"
                    )

                    st.session_state.messages.pop()


# ==================================================
# 15. TXT CONVERSATION EXPORT
# ==================================================

st.divider()

st.subheader("📥 Export Conversation")

if st.session_state.messages:

    export_text = "\n\n".join(
        f"{message['role'].capitalize()}:\n"
        f"{message['content']}"
        for message in st.session_state.messages
    )

    st.download_button(
        "⬇️ Download Chat History",
        data=export_text,
        file_name="rag_chat_history.txt",
        mime="text/plain",
        use_container_width=True
    )

else:
    st.info(
        "Start a conversation to enable chat export."
    )


# ==================================================
# 16. PDF CONVERSATION EXPORT
# ==================================================

def create_chat_pdf(messages):

    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "Advanced RAG Chatbot",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            "Conversation Export",
            styles["Heading2"]
        )
    )

    story.append(
        Spacer(1, 20)
    )

    for message in messages:

        role = message["role"].capitalize()

        story.append(
            Paragraph(
                role,
                styles["Heading3"]
            )
        )

        content = (
            message["content"]
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>")
        )

        story.append(
            Paragraph(
                content,
                styles["BodyText"]
            )
        )

        story.append(
            Spacer(1, 10)
        )

        for source in message.get("sources", []):

            source_text = (
                f"Source: {source['filename']} "
                f"- Page {source['page']}"
            )

            story.append(
                Paragraph(
                    source_text,
                    styles["Italic"]
                )
            )

        story.append(
            Spacer(1, 15)
        )

    pdf.build(story)

    buffer.seek(0)

    return buffer.getvalue()


if st.session_state.messages:

    pdf_data = create_chat_pdf(
        st.session_state.messages
    )

    st.download_button(
        "📄 Download Conversation as PDF",
        data=pdf_data,
        file_name="rag_chat_history.pdf",
        mime="application/pdf",
        use_container_width=True
    )
