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

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Groq — llama-3.3-70b-versatile (free) |
| Agent framework | LangGraph |
| RAG framework | LangChain |
| Vector store | ChromaDB (persistent local) |
| Embeddings | HuggingFace — all-MiniLM-L6-v2 |
| PDF processing | PyPDF |
| Translation | deep-translator |
| Language detection | langdetect |
| UI | Streamlit |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/legalsaathi.git
cd legalsaathi
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

Get a free Groq API key at [console.groq.com](https://console.groq.com) — no credit card required.

```bash
cp .env.example .env
```

Open `.env` and add your key:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Add legal PDFs

Download Indian labour law PDFs from [indiacode.nic.in](https://indiacode.nic.in) or [legislative.gov.in](https://legislative.gov.in) and place them in `data/pdfs/`.

### 6. Ingest documents into ChromaDB

```bash
python test_ingestion.py
```

You should see the chunk count printed. This step only needs to run once — ChromaDB persists the vectors to disk.

### 7. Run the Streamlit UI

```bash
streamlit run src/ui/app.py
```

Or run in terminal:

```bash
python agentic_legal_saathi.py
```

---

## Sample Queries

```
# English
What is the minimum wage for a daily worker?
Am I entitled to maternity leave?
Are men and women paid equal wages?
What happens if my employer doesn't pay me on time?
What is MNREGA and how do I apply?

# Hindi
न्यूनतम मजदूरी क्या है?
मुझे ओवरटाइम का पैसा कब मिलना चाहिए?
मातृत्व लाभ के लिए मेरे क्या अधिकार हैं?
```

---

## Key Design Decisions

**Why ChromaDB over FAISS?** ChromaDB stores chunk metadata (source document, page number) alongside vectors, enabling source citations in every answer. FAISS is faster but supports no metadata, so citations are impossible.

**Why MMR retrieval?** Maximal Marginal Relevance balances relevance with diversity — preventing 4 chunks from the same section being returned while a more relevant chunk from another Act is missed.

**Why Groq over OpenAI?** Free tier, no credit card, comparable quality for structured legal explanation. Makes this project reproducible for anyone without API cost.

**Why the relevance check loop?** In a legal context, a confident wrong answer is worse than no answer. The agent judges its own retrieval before responding, and retries with a reformulated query rather than answering from weakly-relevant chunks.

---

## Disclaimer

LegalSaathi provides general information based on publicly available Indian labour law documents. It is not a substitute for professional legal advice. For specific legal matters, consult a qualified lawyer or your nearest District Labour Officer.

---

## Built With

- [LangChain](https://python.langchain.com)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Groq](https://groq.com)
- [ChromaDB](https://www.trychroma.com)
- [HuggingFace Sentence Transformers](https://huggingface.co/sentence-transformers)
- [Streamlit](https://streamlit.io)
- [India Code](https://indiacode.nic.in) — source of all legal documents
