from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from src.utils.config import (
    EMBEDDING_MODEL,
    CHROMA_DB_PATH,
    CHROMA_COLLECTION,
    TOP_K_RESULTS
)


def get_vector_db():

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    vectordb = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings,
        collection_name=CHROMA_COLLECTION
    )

    print("Documents in DB:", vectordb._collection.count())

    return vectordb


def get_retriever():

    vectordb = get_vector_db()

    retriever = vectordb.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": TOP_K_RESULTS,
            "fetch_k": 10
        }
    )

    return retriever

