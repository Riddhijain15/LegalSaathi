from langchain_groq import ChatGroq

from src.utils.config import (
    GROQ_API_KEY,
    LLM_MODEL
)


def get_router():

    return ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=LLM_MODEL,
        temperature=0
    )

def classify_question(question, llm):

    prompt = f"""
You are a classifier.

Classify the question into ONE category.

LEGAL_RAG:
Any question related to Indian labour law, worker rights, wages,
employment, government schemes (like MNREGA), legal acts, or anything
that could be answered using legal documents — including "what is"
or definition-style questions about these topics.

GENERAL_LLM:
ONLY greetings, small talk, or questions completely unrelated to
Indian labour law or worker rights (e.g. "hello", "what is the capital
of France", "write me a poem").

Respond with ONLY:

LEGAL_RAG

or

GENERAL_LLM

Question:
{question}
"""

    response = llm.invoke(prompt)

    return response.content.strip()