"""
FILE 9: The payoff — your agent calls your model
=================================================
In Session 6 you wrapped Groq's Llama in a LangChain object and built a
chain on top of it. ARGPT is now behind a URL just like Groq is. So it
plugs into exactly the same slot.

Nothing about LangChain knows or cares that this model is 10 million
parameters and was trained by you an hour ago.

Run me:  python use_from_agent9.py --url https://...modal.run
"""

import argparse

import requests


def ask_argpt(url, prompt, max_tokens=200, temperature=0.8):
    """The raw call. This is all your deployed endpoint needs."""
    r = requests.post(url, json={"prompt": prompt,
                                 "max_tokens": max_tokens,
                                 "temperature": temperature}, timeout=120)
    r.raise_for_status()
    return r.json()["text"]


# ---------- the LangChain wrapper (same shape as Session 6) ----------
def build_langchain_llm(url):
    from langchain_core.language_models.llms import LLM

    class ARGPT(LLM):
        url: str
        temperature: float = 0.8
        max_tokens: int = 200

        @property
        def _llm_type(self):
            return "argpt"

        def _call(self, prompt, stop=None, run_manager=None, **kwargs):
            return ask_argpt(self.url, prompt, self.max_tokens, self.temperature)

    return ARGPT(url=url)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True, help="the URL modal deploy printed")
    args = p.parse_args()

    # ---------- DEMO 1: plain HTTP ----------
    print("=" * 55)
    print("DEMO 1: calling your own LLM over HTTP")
    print("=" * 55)
    print(ask_argpt(args.url, "ROMEO:", max_tokens=150))

    # ---------- DEMO 2: the same model inside a LangChain chain ----------
    print("\n" + "=" * 55)
    print("DEMO 2: the same model, as a LangChain LLM")
    print("=" * 55)
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import PromptTemplate

    chain = (PromptTemplate.from_template("{character}:")
             | build_langchain_llm(args.url)
             | StrOutputParser())
    print(chain.invoke({"character": "JULIET"}))

# NOTE:
# - Be honest with yourself about what you built. ARGPT can continue text in
#   the style it was trained on. It cannot follow instructions, use tools, or
#   answer questions -- because we only did the PRETRAINING step.
# - ChatGPT is this, plus vastly more data, plus instruction tuning, plus RLHF.
#   You have built the foundation the rest is bolted onto.
# - That gap between "predicts text" and "follows instructions" is exactly what
#   the agent sessions were working around. Now you know what was underneath.
