import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env")

# LLM Settings
LLM_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 1024

# Embeddings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ChromaDB
CHROMA_DB_PATH = "./chroma_db"
CHROMA_COLLECTION = "legal_docs"

# PDF Processing
PDF_FOLDER = "./data/pdfs"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

MAX_RETRY_ATTEMPTS = 3
TOP_K_RESULTS = 4
