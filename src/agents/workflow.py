"""
LegalSaathi agentic workflow — built with LangGraph.

Graph structure:

    retrieve --> relevance_check --(relevant)--> respond
                      ^                     |
                      |__(not_relevant, retry)__|
                      |
                      +--(not_relevant, max attempts)--> respond (graceful fail)

This is what makes the system agentic rather than a one-shot RAG chain:
the agent evaluates whether its own retrieval was good enough, and
decides whether to retry with a reformulated query before answering.
"""

from typing import TypedDict, List, Dict

from langgraph.graph import StateGraph, END

from src.retrieval.retriever import get_retriever
from src.retrieval.qa_chain import get_llm
from src.utils.config import MAX_RETRY_ATTEMPTS
from src.agents.prompts import (
    RELEVANCE_CHECK_PROMPT,
    QUERY_REFORMULATION_PROMPT,
    REFORMULATION_HINTS,
    LEGAL_ANSWER_PROMPT,
    CANNOT_ANSWER_TEMPLATE,
)


# ---------------------------------------------------------------------
# State — threaded through every node
# ---------------------------------------------------------------------

class AgentState(TypedDict):
    original_question: str     # the user's question, never changes
    query: str                  # current search query (may be reformulated)
    chunks: List               # raw retrieved LangChain Document objects
    sources: List[Dict]        # chunk metadata for citation display
    relevance: str              # "relevant" / "not_relevant" / ""
    attempts: int                # retry counter
    can_answer: bool            # False if max retries exhausted
    answer: str                  # final formatted answer


retriever = get_retriever()
llm = get_llm()


# ---------------------------------------------------------------------
# Node 1 — Retrieve
# ---------------------------------------------------------------------

def retrieve_node(state: AgentState) -> AgentState:
    docs = retriever.invoke(state["query"])

    state["chunks"] = docs
    state["sources"] = [
        {
            "chunk": i + 1,
            "source": doc.metadata.get("source", "Unknown Document"),
            "page": doc.metadata.get("page", "N/A"),
        }
        for i, doc in enumerate(docs)
    ]
    state["attempts"] += 1

    print(f"[retrieve_node] attempt={state['attempts']} query='{state['query'][:60]}' chunks={len(docs)}")
    return state


# ---------------------------------------------------------------------
# Node 2 — Relevance check
# ---------------------------------------------------------------------

def relevance_check_node(state: AgentState) -> AgentState:
    docs = state["chunks"]

    if not docs:
        state["relevance"] = "not_relevant"
        print("[relevance_check_node] zero chunks -> not_relevant")
        return state

    chunks_summary = "\n---\n".join(doc.page_content[:300] for doc in docs)

    prompt = RELEVANCE_CHECK_PROMPT.format(
        question=state["original_question"],
        chunks_summary=chunks_summary,
    )

    response = llm.invoke(prompt)
    decision = response.content.strip().lower()

    state["relevance"] = "relevant" if "not_relevant" not in decision and "relevant" in decision else "not_relevant"

    print(f"[relevance_check_node] decision={state['relevance']}")
    return state


# ---------------------------------------------------------------------
# Node 2b — Reformulate query (only runs on retry)
# ---------------------------------------------------------------------

def reformulate_node(state: AgentState) -> AgentState:
    attempt_number = state["attempts"] + 1
    hint = REFORMULATION_HINTS.get(attempt_number, "Try a different phrasing.")

    prompt = QUERY_REFORMULATION_PROMPT.format(
        attempt_number=attempt_number,
        original_question=state["original_question"],
        previous_query=state["query"],
        strategy_hint=hint,
    )

    response = llm.invoke(prompt)
    new_query = response.content.strip()

    print(f"[reformulate_node] '{state['query']}' -> '{new_query}'")
    state["query"] = new_query
    return state


# ---------------------------------------------------------------------
# Node 3 — Respond
# ---------------------------------------------------------------------

def respond_node(state: AgentState) -> AgentState:
    # True hard failure: no chunks were ever retrieved
    if not state["chunks"]:
        print("[respond_node] no chunks ever retrieved -> graceful fallback")
        state["answer"] = CANNOT_ANSWER_TEMPLATE
        return state

    # Max attempts hit, but we still have chunks from the last attempt —
    # make a best-effort answer instead of refusing outright, since the
    # relevance judge can be overly conservative
    if state["relevance"] == "not_relevant" and not state["can_answer"]:
        print("[respond_node] max attempts exhausted but chunks exist -> best-effort answer")

    context = "\n\n".join(doc.page_content for doc in state["chunks"])

    prompt = LEGAL_ANSWER_PROMPT.format(
        context=context,
        question=state["original_question"],
    )

    response = llm.invoke(prompt)
    state["answer"] = response.content
    return state

    prompt = LEGAL_ANSWER_PROMPT.format(
        context=context,
        question=state["original_question"],
    )

    response = llm.invoke(prompt)
    state["answer"] = response.content
    return state


# ---------------------------------------------------------------------
# Conditional routing after relevance check
# ---------------------------------------------------------------------

def route_after_relevance_check(state: AgentState) -> str:
    if state["relevance"] == "relevant":
        return "respond"

    if state["attempts"] >= MAX_RETRY_ATTEMPTS:
        state["can_answer"] = False
        print(f"[router] max attempts ({MAX_RETRY_ATTEMPTS}) reached -> graceful fail")
        return "respond"

    print(f"[router] not relevant, attempt {state['attempts']}/{MAX_RETRY_ATTEMPTS} -> retrying")
    return "reformulate"


# ---------------------------------------------------------------------
# Build and compile the graph
# ---------------------------------------------------------------------

def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("relevance_check", relevance_check_node)
    graph.add_node("reformulate", reformulate_node)
    graph.add_node("respond", respond_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "relevance_check")

    graph.add_conditional_edges(
        "relevance_check",
        route_after_relevance_check,
        {
            "respond": "respond",
            "reformulate": "reformulate",
        },
    )

    graph.add_edge("reformulate", "retrieve")
    graph.add_edge("respond", END)

    return graph.compile()


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


def run_agent(question: str) -> dict:
    """
    Main entry point — runs the full agentic graph for one question.
    Returns: {answer, sources, attempts, can_answer}
    """
    agent = get_agent()

    initial_state: AgentState = {
        "original_question": question,
        "query": question,
        "chunks": [],
        "sources": [],
        "relevance": "",
        "attempts": 0,
        "can_answer": True,
        "answer": "",
    }

    final_state = agent.invoke(initial_state)

    return {
        "answer": final_state["answer"],
        "sources": final_state["sources"],
        "attempts": final_state["attempts"],
        "can_answer": final_state["can_answer"],
    }