from src.ingestion.text_splitter import (
    split_documents
)

from src.utils.config import (
    EMBEDDING_MODEL,
    CHROMA_DB_PATH,
    CHROMA_COLLECTION
)


def ingest_uploaded_pdf(file_path):

    # Import heavy dependencies at call time to avoid import-time failures
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings

    # ----------------------------
    # Load PDF
    # ----------------------------

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # ----------------------------
    # Split into chunks
    # ----------------------------

    chunks = split_documents(documents)

    # ----------------------------
    # Embeddings
    # ----------------------------

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # ----------------------------
    # Open existing Chroma DB
    # ----------------------------

    vectordb = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings,
        collection_name=CHROMA_COLLECTION
    )

    # ----------------------------
    # Add chunks
    # ----------------------------

    vectordb.add_documents(chunks)
    vectordb.persist()

    return len(chunks)