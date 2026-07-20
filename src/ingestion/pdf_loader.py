from langchain_community.document_loaders import PyPDFDirectoryLoader
from src.utils.logger import setup_logger
from src.utils.config import PDF_FOLDER

logger = setup_logger(__name__)

def load_pdfs():
    """
    Load all PDFs from data/pdfs folder.
    """

    loader = PyPDFDirectoryLoader(PDF_FOLDER)

    documents = loader.load()

    logger.info(f"Loaded {len(documents)} pages.")

    return documents