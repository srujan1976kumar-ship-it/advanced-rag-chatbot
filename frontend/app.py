
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Advanced RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)
# Custom UI styling
st.markdown("""
<style>

/* Main application */
.stApp {
    background: linear-gradient(135deg, #101827, #17243a);
    color: #f1f5f9;
}

/* Main title */
h1 {
    color: #60a5fa !important;
    font-weight: 800 !important;
}

/* Section headings */
h2, h3 {
    color: #bfdbfe !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #111c2e;
    border-right: 1px solid #334155;
}

/* Chat messages */
div[data-testid="stChatMessage"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 12px;
}

/* Buttons */
.stButton > button {
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 9px;
    padding: 9px 16px;
    font-weight: 600;
    transition: 0.2s;
}

.stButton > button:hover {
    background: #1d4ed8;
    border: none;
    color: white;
}

/* Text input */
.stTextInput input,
.stChatInput input {
    background: #1e293b;
    color: white;
    border: 1px solid #475569;
    border-radius: 10px;
}

/* File uploader */
div[data-testid="stFileUploader"] {
    background: #1e293b;
    border-radius: 12px;
    padding: 10px;
}

/* Expanders */
div[data-testid="stExpander"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
}

/* Dividers */
hr {
    border-color: #334155;
}

</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []

if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False


# Load documents from backend
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
        st.error(f"Could not load documents: {response.text}")

except requests.RequestException as error:
    st.error(f"Document loading failed: {error}")


# Synchronize selected document IDs BEFORE creating the widget
valid_document_ids = {
    doc["document_id"]
    for doc in st.session_state.uploaded_docs
}

if "document_selector" not in st.session_state:
    st.session_state.document_selector = list(valid_document_ids)
else:
    st.session_state.document_selector = [
        doc_id
        for doc_id in st.session_state.document_selector
        if doc_id in valid_document_ids
    ]


# Load saved chat history
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
        st.warning(f"Could not load chat history: {error}")
        st.session_state.history_loaded = True


# Sidebar
with st.sidebar:

    st.title("📚 Document Manager")
    st.write("Upload PDF documents to chat with them.")

    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )

    # Upload documents
    if st.button(
        "Upload Documents",
        use_container_width=True
    ):

        if not uploaded_files:
            st.warning("Please select a PDF first.")

        else:
            for uploaded_file in uploaded_files:

                if any(
                    doc["filename"] == uploaded_file.name
                    for doc in st.session_state.uploaded_docs
                ):
                    st.info(
                        f"{uploaded_file.name} already uploaded."
                    )
                    continue

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

                        st.session_state.uploaded_docs.append(
                            new_document
                        )

                        if (
                            result["document_id"]
                            not in st.session_state.document_selector
                        ):
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
                    st.error(f"Upload failed: {error}")


    # Uploaded documents
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
                        f"{API_URL}/documents/{document['document_id']}",
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
                    st.error(f"Deletion failed: {error}")

    else:
        st.caption("No documents uploaded.")


    # Document selection
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


    # Clear chat
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
                st.success("Chat history cleared.")
                st.rerun()

            else:
                st.error(response.text)

        except requests.RequestException as error:
            st.error(f"Could not clear chat: {error}")


    # Backend health
    st.divider()

    try:
        health = requests.get(
            f"{API_URL}/health",
            timeout=5
        )

        if health.ok:
            st.success("Backend connected")

            st.caption(
                f"Indexed chunks: "
                f"{health.json()['documents_indexed']}"
            )

        else:
            st.error("Backend unavailable")

    except requests.RequestException:
        st.error("Cannot connect to backend")


# Main chatbot dashboard
st.title("🤖 Advanced RAG Chatbot")

st.markdown(
    "### Intelligent Document Question Answering"
)

st.caption(
    "Upload PDFs, select documents, and get AI-powered answers with page citations."
)

# Dashboard statistics
col1, col2, col3 = st.columns(3)

total_pdfs = len(st.session_state.uploaded_docs)

total_chunks = sum(
    doc.get("chunks", 0)
    for doc in st.session_state.uploaded_docs
)

selected_pdfs = len(
    st.session_state.document_selector
)

with col1:
    st.metric("📚 Total PDFs", total_pdfs)

with col2:
    st.metric("🧩 Indexed Chunks", total_chunks)

with col3:
    st.metric("🎯 Selected PDFs", selected_pdfs)

st.divider()
# Document overview
st.subheader("📂 Document Overview")

if st.session_state.uploaded_docs:

    for doc in st.session_state.uploaded_docs:

        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.write(f"📄 **{doc['filename']}**")

        with col2:
            st.caption(
                f"{doc.get('chunks', 0)} chunks"
            )

        with col3:
            if doc["document_id"] in st.session_state.document_selector:
                st.success("Selected")
            else:
                st.caption("Not selected")

else:
    st.info("No PDF documents uploaded yet.")

st.divider()

# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

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


# Welcome screen and suggested questions
if not st.session_state.messages:

    st.markdown("## 👋 Welcome to your AI Document Assistant")

    st.write(
        "Ask questions about your uploaded PDFs. "
        "The chatbot will search your documents and provide "
        "answers with source references."
    )

    st.markdown("### 💡 Try asking")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "📝 Summarize my documents",
            use_container_width=True
        ):
            st.session_state.suggested_question = (
                "Summarize the selected documents."
            )
            st.rerun()

        if st.button(
            "🔍 Find key information",
            use_container_width=True
        ):
            st.session_state.suggested_question = (
                "What are the most important points in the selected documents?"
            )
            st.rerun()

    with col2:
        if st.button(
            "📚 Explain the main topics",
            use_container_width=True
        ):
            st.session_state.suggested_question = (
                "Explain the main topics covered in the selected documents."
            )
            st.rerun()

        if st.button(
            "❓ Ask about a specific topic",
            use_container_width=True
        ):
            st.session_state.suggested_question = (
                "Explain a specific topic covered in the selected documents."
            )
            st.rerun()


# Chat input
question = st.chat_input(
    "Ask something about your uploaded documents..."
)

# Use a suggested question when a suggestion button is clicked
if not question:
    question = st.session_state.pop(
        "suggested_question",
        None
    )

if question:

    if not st.session_state.uploaded_docs:

        st.warning(
            "Please upload a PDF document before chatting."
        )

    elif not st.session_state.document_selector:

        st.warning(
            "Please select at least one PDF."
        )

    else:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):

            with st.spinner(
                "Searching documents and generating answer..."
            ):

                try:
                    response = requests.post(
                        f"{API_URL}/chat",
                        json={
                            "message": question,
                            "session_id": "local-user",
                            "history": [
                                {
                                    "role": message["role"],
                                    "content": message["content"]
                                }
                                for message in
                                st.session_state.messages[:-1][-8:]
                            ],
                            "document_ids": (
                                st.session_state.document_selector
                            )
                        },
                        timeout=240
                    )

                    if response.ok:

                        result = response.json()

                        answer = result["answer"]
                        sources = result.get("sources", [])

                        st.markdown(answer)

                        if sources:

                            with st.expander("📚 View Sources"):

                                for source in sources:

                                    st.write(
                                        f"📄 **{source['filename']}** "
                                        f"— Page {source['page']}"
                                    )

                                    distance = source.get("distance")

                                    if distance is not None:
                                        st.caption(
                                            f"Retrieval distance: "
                                            f"{distance:.4f} "
                                            "(lower is a closer match)"
                                        )

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })

                    else:
                        st.error(
                            f"Chat failed: {response.text}"
                        )
                        st.session_state.messages.pop()

                except requests.RequestException as error:
                    st.error(
                        f"Backend connection error: {error}"
                    )
                    st.session_state.messages.pop()
                    # Export chat history
st.divider()
st.subheader("📥 Export Conversation")

if st.session_state.messages:

    export_text = "ADVANCED RAG CHATBOT - CONVERSATION\n"
    export_text += "=" * 45 + "\n\n"

    for message in st.session_state.messages:

        role = message["role"].upper()
        content = message["content"]

        export_text += f"{role}:\n{content}\n\n"

        if message.get("sources"):
            export_text += "SOURCES:\n"

            for source in message["sources"]:
                export_text += (
                    f"- {source['filename']} "
                    f"(Page {source['page']})\n"
                )

            export_text += "\n"

        export_text += "-" * 45 + "\n\n"

    st.download_button(
        label="⬇️ Download Chat History",
        data=export_text,
        file_name="rag_chat_history.txt",
        mime="text/plain",
        use_container_width=True
    )

else:
    st.info("Start a conversation to enable chat export.")
    # PDF conversation export
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


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

    story.append(Spacer(1, 20))

    for message in messages:
        role = message["role"].capitalize()

        story.append(
            Paragraph(role, styles["Heading3"])
        )

        content = (
            message["content"]
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>")
        )

        story.append(
            Paragraph(content, styles["BodyText"])
        )

        story.append(Spacer(1, 10))

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

        story.append(Spacer(1, 15))

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
