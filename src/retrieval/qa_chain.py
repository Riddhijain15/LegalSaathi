from langchain_groq import ChatGroq

from src.utils.config import (
    GROQ_API_KEY,
    LLM_MODEL,
    LLM_TEMPERATURE
)


def get_llm():

    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=LLM_MODEL,
        temperature=LLM_TEMPERATURE
    )

    return llm