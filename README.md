# ⚖️ LegalSaathi — Agentic Legal Assistant for Rural India

An AI-powered legal assistant that helps rural workers in India understand their labour rights in **Hindi and English** — using Retrieval-Augmented Generation (RAG) over real Indian legal documents, powered by an agentic reasoning loop built with LangGraph.

---

## The Problem

Over 800 million Indians have no practical access to legal help. Lawyers are expensive, legal documents are impossible to understand, and rural workers are often unaware of rights they are legally entitled to — fair wages, safe working conditions, maternity benefits, and employment guarantees.

LegalSaathi makes these rights accessible to anyone, in any language, for free.

---

## Demo

Ask in Hindi or English. Get a plain-language answer with the exact Act and section it came from.

```
Question: न्यूनतम मजदूरी क्या है

Answer: न्यूनतम वेतन वह न्यूनतम राशि है जो नियोक्ता को किसी कर्मचारी
को उसके काम के लिए भुगतान करने के लिए आवश्यक होती है...

Legal Basis: न्यूनतम वेतन अधिनियम, 1948, धारा 3(2) और धारा 7(1)

What You Should Do Next:
1. Check if your employment is a scheduled employment under the Minimum Wages Act.
2. Find the minimum wage rate fixed by the appropriate Government for your type.
3. Verify with your employer that you are being paid at least this rate.

Sources: minimum-wages-act-1948.pdf (page 3), code_on_wages.pdf (page 8)
```

---

## Architecture

```
User Query (Hindi or English)
        │
        ▼
Language Detection (langdetect)
        │
        ▼ [if Hindi]
Translate to English (deep-translator)
        │
        ▼
Router — LEGAL_RAG or GENERAL_LLM (Groq)
        │
        ▼ [LEGAL_RAG]
┌────────────────────────────────────────┐
│         LangGraph Agent                │
│                                        │
│  retrieve_node                         │
│      │                                 │
│      ▼                                 │
│  relevance_check_node ──(relevant)──▶ respond_node
│      │                                 │
│      └──(not_relevant, retry)──▶ reformulate_node
│                │                       │
│                └──────▶ retrieve_node  │
│                         (max 3 tries)  │
└────────────────────────────────────────┘
        │
        ▼
Structured Answer:
  Answer + Legal Basis + Next Steps + Sources
        │
        ▼ [if Hindi]
Translate back to Hindi
        │
        ▼
Streamlit UI
```

### What makes it agentic

A plain RAG pipeline retrieves once and answers. LegalSaathi's agent **evaluates its own retrieval quality** before answering. If the retrieved chunks are not sufficiently relevant to the question, it reformulates the search query and retries — up to 3 times — before falling back gracefully. This prevents hallucination in a domain where a wrong answer has real consequences.

