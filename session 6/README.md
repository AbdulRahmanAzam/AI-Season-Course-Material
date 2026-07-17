# LangChain — Session Code

All demos use the **free Groq API** with **Llama 3.3 70B**. Get a free key here: https://console.groq.com/keys

LangChain is not a new AI - it's a standard box of building blocks (prompts, models,
memory, tools, retrievers) that wraps SDKs you've already used by hand, so you stop
rewriting the same plumbing every project.

## Setup (one time)

```bash
pip install -r requirements.txt
```

1. Copy `.env.example` to `.env`
2. Paste your Groq API key inside `.env`
3. Pre-download the embeddings model (only needed once, do this **before** class):

```bash
python 06_rag_basics.py
```

## Files (run in order)

| File | Topic | What students learn |
|------|-------|---------------------|
| `00_hello_langchain.py` | First call | `ChatGroq`, `.invoke()`, roles, `.stream()` |
| `01_prompt_templates.py` | Prompt Templates | Fill-in-the-blank prompts, reused with many inputs, few-shot |
| `02_chains_lcel.py` | Chains (LCEL) | The `\|` pipe: `prompt \| llm \| parser`, `.batch()` |
| `02b_runnable_types.py` | Runnable Types | Every kind of Runnable: `RunnableSequence`, `RunnableLambda`, `RunnableParallel`, `RunnablePassthrough` |
| `03_structured_output.py` | Structured Output | Get real Python objects back, not raw text to parse |
| `04_memory_chatbot.py` | Memory | The model remembers a conversation by `session_id` |
| `05_tools_and_agents.py` | Tools + Agents | `create_agent()` runs the tool-calling loop for you |
| `06_rag_basics.py` | RAG | Embeddings + FAISS vector store + retriever, no manual cosine similarity |
| `07_bonus_agent_with_rag_tool.py` | Bonus: Agent + RAG | *(optional)* a retriever as just another tool |

Run any file like:

```bash
python 00_hello_langchain.py
```

## Tips for the live session

- **The big idea to repeat all session:** everything in LangChain is a "Runnable."
  You connect them with `|` exactly like Unix pipes: `prompt | model | parser`.
  Once a student sees the pipe and knows `invoke` / `batch` / `stream` work the
  same way on *any* Runnable, they understand LangChain.
- **Callbacks to Session 5 (say these out loud, they land well):**
  - `00` - same `groq.Groq` client and same `llama-3.3-70b-versatile` model as Session 5 FILE 8, now wrapped in `ChatGroq`.
  - `02` - no more `response.choices[0].message.content`; the parser does it.
  - `03` - same idea as the receipt → JSON cleanup in Session 5 FILE 4, minus the manual parsing.
  - `04` - same idea as the `conversation.append(...)` memory in Session 5 FILE 7, now automatic.
  - `05` - direct sequel to Session 5 FILE 7's manual vs. automatic tool calling.
  - `06` - same retrieve-then-answer idea as Session 5 FILE 6's multimodal RAG.
- **Error 429 (rate limit):** Groq's free tier has rate limits. Wait 30-60 seconds and run again.
- **First run of `06`/`07` is slow:** downloading the ~80MB embedding model. That's why setup step 3 exists - do it before class.
