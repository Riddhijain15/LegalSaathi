from src.agents.legal_agent import get_response

print("\n✅ Testing Full Agentic Pipeline (type 'exit' to quit)\n")

while True:
    question = input("\nQuestion: ")

    if question.lower() == "exit":
        print("\nGoodbye!")
        break

    result = get_response(question)

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(result["answer"])

    if result["sources"]:
        print("\n" + "-" * 80)
        print("SOURCES")
        print("-" * 80)
        for s in result["sources"]:
            print(f"  - {s['source']} (page {s['page']})")

    print("=" * 80)
    