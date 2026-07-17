# Raw HTTP vs SDK vs LangChain

Same question, asked 3 different ways per provider, then one way for all providers.

| File | Provider | Custom method | Usual (SDK) method |
|------|----------|----------------|---------------------|
| `01_groq_calls.py` | Groq | `requests.post()` to `api.groq.com/openai/v1/chat/completions` | `groq.Groq()` |
| `02_gemini_calls.py` | Gemini | `requests.post()` to `generativelanguage.googleapis.com` | `google.genai.Client()` |
| `03_openai_calls.py` | OpenAI SDK, via DigitalOcean | `requests.post()` to `inference.do-ai.run/v1` | `openai.OpenAI()` with `base_url` swapped |
| `04_langchain_standardizes.py` | All three | -- | `ChatGroq` / `ChatGoogleGenerativeAI` / `ChatOpenAI`, all called the same way |

**The point:** files 1-3 each need their own headers, JSON shape, and response
parsing -- three different mental models. File 4 collapses all three into
`llm.invoke(question)` / `response.content`, every time, regardless of provider.

**The DigitalOcean twist (file 3):** DigitalOcean's Gradient AI Serverless
Inference endpoint speaks the same API shape as OpenAI. Point the official
`openai` SDK at `https://inference.do-ai.run/v1/` with a DigitalOcean model
access key instead of an OpenAI key, and every other line of code is identical.

## Setup

```bash
pip install -r ../requirements.txt
```

Add these to the `.env` in the parent `session 6` folder (this folder reads it
automatically -- `load_dotenv()` walks up to find it):

```
GROQ_API_KEY=...                    # already set if you did session 6 setup
GEMINI_API_KEY=...                  # free key: https://aistudio.google.com/apikey
DIGITAL_OCEAN_MODEL_ACCESS_KEY=...  # DigitalOcean control panel -> Gradient AI -> Serverless Inference
```

Run in order:

```bash
python 01_groq_calls.py
python 02_gemini_calls.py
python 03_openai_calls.py
python 04_langchain_standardizes.py
```
