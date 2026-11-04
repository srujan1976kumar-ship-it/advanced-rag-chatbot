
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Advanced RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []

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

# Synchronize selected document IDs
valid_document_ids = {
    doc["document_id"]
    for doc in st.session_state.uploaded_docs
}

if "selected_document_ids" not in st.session_state:
    st.session_state.selected_document_ids = list(valid_document_ids)
else:
    st.session_state.selected_document_ids = [
        doc_id
        for doc_id in st.session_state.selected_document_ids
        if doc_id in valid_document_ids
    ]

# Load saved chat history
if "history_loaded" not in st.session_state:
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

    if st.button("Upload Documents", use_container_width=True):
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

                        st.session_state.uploaded_docs.append({
                            "filename": result["filename"],
                            "document_id": result["document_id"],
                            "chunks": result["chunks_created"]
                        })

                        if (
                            result["document_id"]
                            not in st.session_state.selected_document_ids
                        ):
                            st.session_state.selected_document_ids.append(
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
                            if doc["document_id"] != document["document_id"]
                        ]

                        st.session_state.selected_document_ids = [
                            doc_id
                            for doc_id in st.session_state.selected_document_ids
                            if doc_id != document["document_id"]
                        ]

                        st.success("Document deleted successfully!")
                        st.rerun()

                    else:
                        st.error(response.text)

                except requests.RequestException as error:
                    st.error(f"Deletion failed: {error}")

    else:
        st.caption("No documents uploaded.")

    # Document Selection
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
        key="selected_document_ids"
    )

    # Clear Chat
    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
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

# Main chatbot interface
st.title("🤖 Advanced RAG Chatbot")

st.caption(
    "Ask questions and get answers grounded in your uploaded documents."
)

st.divider()

# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("sources"):
            with st.expander("📚 View Sources"):
                for source in message["sources"]:
                    st.write(
                        f"📄 {source['filename']} "
                        f"— Page {source['page']}"
                    )

# Chat input
question = st.chat_input(
    "Ask something about your uploaded documents..."
)

if question:

    if not st.session_state.uploaded_docs:
        st.warning("Please upload a PDF document before chatting.")

    elif not st.session_state.selected_document_ids:
        st.warning("Please select at least one PDF.")

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
                                st.session_state.selected_document_ids
                            )
                        },
                        timeout=240
                    )

                    if response.ok:
                        result = response.json()

                        answer = result["answer"]
                        sources = result.get("sources", [])

                        st.markdown(answer)

                        with st.expander("📚 View Sources"):
                            for source in sources:
                                st.write(
                                    f"📄 {source['filename']} "
                                    f"— Page {source['page']}"
                                )

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })

                    else:
                        st.error(f"Chat failed: {response.text}")
                        st.session_state.messages.pop()

                except requests.RequestException as error:
                    st.error(f"Backend connection error: {error}")
                    st.session_state.messages.pop()
