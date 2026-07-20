import sys
import os

# Fix imports for Streamlit
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../.."
        )
    )
)

import streamlit as st

from src.agents.legal_agent import get_response

from src.ingestion.upload_processor import (
    ingest_uploaded_pdf
)


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="LegalSaathi",
    page_icon="⚖️",
    layout="wide"
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("⚖️ LegalSaathi")

st.markdown(
    """
    AI-Powered Legal Assistant

    Agentic RAG + Groq + ChromaDB + Multilingual Support
    """
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.title("⚖️ LegalSaathi")

st.sidebar.success("System Ready")
st.sidebar.subheader(
    "Uploaded Documents"
)

if os.path.exists("uploads"):
    files = sorted(os.listdir("uploads"))
else:
    files = []

if files:
    for file in files:
        st.sidebar.write(f"📄 {file}")
else:
    st.sidebar.write("No uploaded files yet.")

st.sidebar.subheader(
    "Database"
)

st.sidebar.write(
    f"Documents: {len(files)}"
)
# --------------------------------------------------
# PDF Upload
# --------------------------------------------------

st.sidebar.subheader(
    "📄 Upload Legal PDF"
)

uploaded_files = st.sidebar.file_uploader(
    "Choose PDF(s)",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    os.makedirs("uploads", exist_ok=True)
    duplicate_count = 0
    processed_count = 0
    errors = []

    for uploaded_file in uploaded_files:
        file_path = os.path.join("uploads", uploaded_file.name)

        if os.path.exists(file_path):
            duplicate_count += 1
            continue

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            ingest_uploaded_pdf(file_path)
            processed_count += 1
        except Exception as e:
            errors.append(f"{uploaded_file.name}: {str(e)}")

    if processed_count:
        st.sidebar.success(
            f"✅ Processed {processed_count} file(s)."
        )

    if duplicate_count:
        st.sidebar.warning(
            f"⚠️ {duplicate_count} duplicate file(s) skipped."
        )

    if errors:
        st.sidebar.error("❌ Errors while processing:\n" + "\n".join(errors))

    files = sorted(os.listdir("uploads"))
    st.sidebar.markdown(f"**Total uploaded files:** {len(files)}")
    for file in files:
        st.sidebar.write(f"📄 {file}")


# --------------------------------------------------
# Features
# --------------------------------------------------

st.sidebar.markdown(
    """
### Features

✅ Agentic Routing

✅ Legal RAG

✅ Groq LLM

✅ ChromaDB

✅ Multilingual Support

✅ Streamlit UI

---
Built with LangChain + LangGraph
"""
)


# --------------------------------------------------
# Clear Chat
# --------------------------------------------------

if st.sidebar.button(
    "🗑️ Clear Chat"
):

    st.session_state.messages = []

    st.rerun()


# --------------------------------------------------
# Chat History Initialization
# --------------------------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []


# --------------------------------------------------
# Display Previous Messages
# --------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("📚 Sources Used"):
                for source in message["sources"]:
                    filename = os.path.basename(source["source"])
                    st.markdown(f"**📄 {filename}** — Page {source['page']}, Chunk {source['chunk']}")


# --------------------------------------------------
# Chat Input
# --------------------------------------------------

question = st.chat_input(
    "Ask a legal question..."
)


# --------------------------------------------------
# Process User Query
# --------------------------------------------------

if question:

    # User Message
    with st.chat_message("user"):
        st.markdown(question)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Assistant Response
    with st.spinner("Analyzing legal documents..."):

        try:

            result = get_response(question)

            answer = result["answer"]
            sources = result["sources"]

        except Exception as e:

            answer = f"Error: {str(e)}"
            sources = []

    with st.chat_message("assistant"):

        st.markdown(answer)

        # -----------------------------
        # Source Citations
        # -----------------------------
        if sources:

            with st.expander("📚 Sources Used"):

                for source in sources:

                    filename = os.path.basename(
                        source["source"]
                    )

                    st.markdown(
                        f"""
**📄 Document:** {filename}

- **Page:** {source['page']}
- **Chunk:** {source['chunk']}

---
"""
                    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources
        }
    )