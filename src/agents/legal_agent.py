from src.agents.router import (
    get_router,
    classify_question
)

from src.retrieval.retriever import (
    get_retriever
)

from src.retrieval.qa_chain import (
    get_llm
)

from src.translation.language_detector import (
    detect_language
)

from src.translation.translator import (
    translate_to_english,
    translate_from_english
)


router = get_router()
retriever = get_retriever()
llm = get_llm()


def get_response(question):

    # ----------------------------------------
    # Detect Language
    # ----------------------------------------

    language = detect_language(question)
    print("Detected Language:", language)

    if language != "en":
        english_question = translate_to_english(question)
    else:
        english_question = question

    # ----------------------------------------
    # Route Question
    # ----------------------------------------

    route = classify_question(
        english_question,
        router
    )

    print("Route:", route)

    sources = []

    # ----------------------------------------
    # General Questions
    # ----------------------------------------

    if route == "GENERAL_LLM":

        response = llm.invoke(
            english_question
        )

        answer = response.content

    # ----------------------------------------
    # Legal Questions (RAG)
    # ----------------------------------------

    else:

        from src.agents.workflow import run_agent

        result = run_agent(english_question)

        answer = result["answer"]
        sources = result["sources"]

        print("Retrieval attempts used:", result["attempts"])

    print("Before Translation:", answer)

    # ----------------------------------------
    # Translate Back
    # ----------------------------------------

    if language != "en":

        answer = translate_from_english(
            answer,
            language
        )

    print("Final Answer:", answer)

    return {
        "answer": answer,
        "sources": sources
    }