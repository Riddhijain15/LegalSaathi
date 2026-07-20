from src.ingestion.pdf_loader import load_pdfs
from src.ingestion.text_splitter import split_documents
from src.ingestion.vector_store import create_vector_store

print("Loading PDFs...")

documents = load_pdfs()

print(f"Loaded {len(documents)} pages")

print("Splitting documents...")

chunks = split_documents(documents)

print(f"Created {len(chunks)} chunks")

print("Creating vector database...")

create_vector_store(chunks)

print("DONE!")