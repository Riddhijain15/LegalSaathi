from src.agents.router import (
    get_router,
    classify_question
)

from src.retrieval.retriever import get_retriever
from src.retrieval.qa_chain import get_llm

from src.translation.language_detector import (
    detect_language
)

from src.translation.translator import (
    translate_to_english,
    translate_from_english
)

# Initialize components
router = get_router()

retriever = get_retriever()

llm = get_llm()

print("\n✅ Multilingual LegalSaathi Ready!\n")

while True:

    question = input("\nQuestion: ")

    if question.lower() == "exit":

        print("\nGoodbye!")

        break

    # Detect language
    language = detect_language(question)

    print("\nDetected Language:", language)

    # Translate to English if needed
    if language != "en":

        english_question = translate_to_english(
            question
        )

        print(
            "\nTranslated Question:",
            english_question
        )

    else:

        english_question = question

    # Classify question
    route = classify_question(
        english_question,
        router
    )

    print("\nRoute:", route)

    # ==================================================
    # GENERAL LLM
    # ==================================================

    if route == "GENERAL_LLM":

        response = llm.invoke(
            english_question
        )

        answer = response.content

    # ==================================================
    # LEGAL RAG
    # ==================================================

    else:

        docs = retriever.invoke(
            english_question
        )

        if len(docs) == 0:

            answer = (
                "I could not find this information "
                "in the provided legal documents."
            )

        else:

            context = "\n\n".join(
                [
                    doc.page_content
                    for doc in docs
                ]
            )

            prompt = f"""
You are LegalSaathi,
an expert Indian legal assistant.

Instructions:

1. Use ONLY the context provided.
2. Give a detailed answer.
3. If information is not available,
   say:
   "I could not find this information
   in the provided legal documents."

Context:
{context}

Question:
{english_question}

Answer:
"""

            response = llm.invoke(
                prompt
            )

            answer = response.content

    # Translate answer back
    if language != "en":

        answer = translate_from_english(
            answer,
            language
        )

    print("\n")
    print("=" * 80)
    print("ANSWER")
    print("=" * 80)

    print(answer)

    print("\n" + "=" * 80)