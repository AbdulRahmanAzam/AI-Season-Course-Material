# AI Season RAG — Code v2 (LangChain style)

Simpler teaching version modeled after [rag-for-beginners](../rag-for-beginners/):

- **Flat numbered scripts** (no `utils/` package)
- **LangChain** loaders, splitters, Chroma, retrievers
- **Local embeddings** via `HuggingFaceEmbeddings` (free, no OpenAI key)
- **Groq LLM** via `ChatGroq` (not OpenAI)
- **Mock mode** when `GROQ_API_KEY` is missing

Session: **How AI Answers From Your Data**

---

## Setup (Windows PowerShell)

```powershell
cd rag-session-code-v2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Optional Groq key in `.env`:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

---

## Scripts (run in order for first demo)

| File | What it does |
|------|----------------|
| `1_file_conversion.py` | PDF/DOCX/TXT from `data/raw/` -> `docs/` |
| `2_ingestion_pipeline.py` | Load, chunk, embed, store in `db/chroma_db` |
| `3_retrieval_pipeline.py` | Similarity search only |
| `4_answer_generation.py` | Retrieve + Groq (or mock) answer |
| `5_recursive_chunking_demo.py` | Compare chunking strategies |
| `6_retrieval_methods.py` | Similarity / threshold / MMR demos |
| `7_full_rag_pipeline.py` | End-to-end RAG with sources |
| `8_failure_experiments.py` | Out-of-scope, top_k, weak prompts |
| `9_hybrid_retrieval.py` | Vector + BM25 hybrid search |
| `10_streamlit_app.py` | Interactive AI Season assistant |

### Quick start

```powershell
python 1_file_conversion.py
python 2_ingestion_pipeline.py
python 3_retrieval_pipeline.py
python 4_answer_generation.py
python 7_full_rag_pipeline.py
streamlit run 10_streamlit_app.py
```

---

## vs rag-for-beginners

| rag-for-beginners | This project |
|-------------------|--------------|
| `OpenAIEmbeddings` | `HuggingFaceEmbeddings` (local) |
| `ChatOpenAI` | `ChatGroq` |
| `docs/` tech company files | Refund policy + university FAQ |
| No mock mode | Mock fallback for teaching |

## vs rag-session-practical-code (v1)

| v1 | v2 |
|----|-----|
| `utils/` modules + classes | Single-file scripts |
| Raw sentence-transformers + chromadb | LangChain wrappers |
| `examples/slide_XX.py` | `1_...py` numbering like rag-for-beginners |

---

## Troubleshooting

- **No vector store:** run `2_ingestion_pipeline.py` first
- **Slow first run:** embedding model downloads once (~80 MB)
- **Groq errors:** set `LLM_PROVIDER=mock` in `.env`
- **Re-index:** delete `db/chroma_db` and run ingestion again
