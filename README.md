# AI Season — AI Agents Bootcamp: Course Material

Runnable code from **[AI Season](https://aiseason.tech)** Cohort 01 (July–August 2026) — a live
online **AI agents bootcamp** taught in Urdu and English by
[Abdul Rahman Azam](https://aiseason.tech/abdul-rahman-azam) from Karachi, Pakistan.

Every folder is a self-contained lesson: numbered scripts you run in order, a README that explains
what each file teaches, and a `requirements.txt`. The code is written for teaching — flat, readable
scripts rather than a framework you have to understand first.

> **Learn it live:** Cohort 02 of the AI Season bootcamp is enrolling now — 6 weeks, 12 live
> sessions, explained in Urdu with English code, open to students in Pakistan, India and worldwide.
> Details at **[aiseason.tech](https://aiseason.tech)**.

## What's inside

| Module | What you learn | Key tools |
|---|---|---|
| [`Session 1`](./Session%201) — LLM API basics | First model call, streaming, chat history, parameters (Python + JavaScript) | Model provider SDKs |
| [`session 3`](./session%203) — RAG over your documents | File conversion, chunking, embeddings, vector store, retrieval methods, hybrid search, answer generation, failure experiments, a Streamlit chat app | LangChain, Chroma, local embeddings, Groq |
| [`Session 4`](./Session%204) — Build an agent harness | The loop that turns an LLM into an agent: tools, memory, safety rules, a verifier and tests, built checkpoint by checkpoint | Python, pytest |
| [`session 5`](./session%205) — Multimodal agents | Vision-language models, audio, video, OCR pipelines, document understanding, multimodal RAG, tool calling | Gemini API (free tier) |
| [`session 6`](./session%206) — LangChain | Prompt templates, LCEL chains, runnables, structured output, memory, tools and agents, RAG basics, a leads agent | LangChain, FAISS, Groq |
| [`session 8`](./session%208) — Production patterns | Honest RAG that refuses when unsure; a self-correcting agent that fixes code until its tests pass | Python, pytest |
| [`session 12`](./session%2012) — Agent-to-agent (A2A) | Agent cards, agents delegating to agents, an orchestrator, the official A2A SDK, a two-agent debate | A2A protocol, Groq |
| [`ARGPT`](./ARGPT) — Build a language model from scratch | Tokenizer, transformer, training on a rented GPU, generation, serving it behind your own URL (~700 lines) | PyTorch, Modal |
| [`WhatsApp bot`](./WhatsApp%20bot) | A real WhatsApp bot answering messages with a LangChain chain | Node.js, Baileys, LangChain.js, Groq |

## Quick start

```bash
git clone https://github.com/AbdulRahmanAzam/AI-Season-Course-Material.git
cd "AI-Season-Course-Material/session 3"      # pick any module
python -m venv .venv
# Windows: .venv\Scripts\activate   ·   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                           # add a free API key where the README asks
```

Then run the numbered files in order. Several modules fall back to a **mock mode** when no API key
is set, so you can follow the logic offline. Free API tiers are rate-limited — if you see
`429 Too Many Requests`, wait a minute and retry.

## Suggested order for self-study

1. **Session 1** — get comfortable calling a model from code.
2. **session 3** — build RAG over your own PDFs (the most useful skill for real projects).
3. **Session 4** — write an agent loop by hand so frameworks stop being magic.
4. **session 6** — learn LangChain now that you know what it wraps.
5. **session 8** — make answers honest and agents self-correcting.
6. **session 5** and **session 12** — extend agents to images, audio and documents, then to other agents.
7. **ARGPT** — when you want to know what's inside a language model, build a small one.

## Free guides

- [How to learn AI in 2026 — a beginner's roadmap](https://aiseason.tech/learn-ai)
- [What are AI agents?](https://aiseason.tech/what-are-ai-agents)
- [How to build an AI agent in Python, step by step](https://aiseason.tech/how-to-build-an-ai-agent)
- [AI agent frameworks compared](https://aiseason.tech/ai-agent-frameworks)
- [AI agents glossary](https://aiseason.tech/ai-agents-glossary)

## About AI Season

AI Season is a live online AI agents bootcamp founded in Karachi by Abdul Rahman Azam. The
6-week, 12-session course takes students with basic Python to building, evaluating and deploying AI
agents with LangChain, LangGraph, RAG, tool calling, MCP, guardrails and production deployment —
explained in Urdu, coded in English.

[Website](https://aiseason.tech) · [Curriculum](https://aiseason.tech/curriculum) ·
[Enrol](https://aiseason.tech/enroll) · [LinkedIn](https://www.linkedin.com/company/aiseason/) ·
[Instagram](https://www.instagram.com/aiseason.tech/)
