from src.retrieval.retriever import get_retriever
from src.retrieval.qa_chain import get_llm

print("Loading Retriever...")
retriever = get_retriever()

print("Loading LLM...")
llm = get_llm()

print("\n✅ LegalSaathi is Ready!\n")

while True:

    question = input("\nAsk a legal question (or type exit): ")

    if question.lower() == "exit":
        print("\nGoodbye!")
        break

    print("\n🔍 Retrieving relevant documents...\n")

    docs = retriever.invoke(question)

    if not docs:
        print("No relevant documents found.")
        continue

    # Display retrieved chunks
    print("=" * 80)
    print("RETRIEVED CHUNKS")
    print("=" * 80)

    for i, doc in enumerate(docs):

        print(f"\n📄 Chunk {i+1}\n")

        print(doc.page_content[:500])

        print("\n" + "-" * 80)

    # Create context
    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    print("\n")
    print("=" * 80)
    print("CONTEXT SENT TO LLM")
    print("=" * 80)

    print(context[:2000])

    print("\n")
    print("=" * 80)
    print("GENERATING ANSWER...")
    print("=" * 80)

    prompt = f"""
You are LegalSaathi, an expert Indian legal assistant.

Instructions:

1. Use ONLY the provided context.
2. Give a detailed answer.
3. Explain the concept clearly.
4. Mention important provisions if available.
5. If information is not available in the context,
   say:
   "I could not find this information in the provided legal documents."

Context:
{context}

Question:
{question}

Detailed Answer:
"""

    response = llm.invoke(prompt)

    print("\n")
    print("=" * 80)
    print("ANSWER")
    print("=" * 80)

    print(response.content)

    print("\n" + "=" * 80)