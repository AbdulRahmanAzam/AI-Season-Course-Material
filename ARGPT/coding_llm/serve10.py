"""
FILE 10: You become the API
============================
Sessions 1 to 6 you called somebody else's URL. Now other people can call
yours.

The interesting line in this file is @modal.enter(). It marks code that
runs ONCE when the container starts, not once per request. Loading a
checkpoint takes a couple of seconds; doing it inside the request handler
would make every single call pay that cost. That mistake is the number one
reason home-made model APIs feel slow, and it is one decorator to avoid.

Deploy:  modal deploy serve10.py           # prints your URL

Then, from anywhere:
    curl -X POST https://YOU--argpt-coder-api-chat.modal.run \\
         -H "Content-Type: application/json" \\
         -d '{"question": "write a function to reverse a string"}'
"""

import modal

app = modal.App("argpt-coder-api")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch", "numpy", "fastapi[standard]")
    .workdir("/root/coder")
    .add_local_dir(".", "/root/coder",
                   ignore=["data", "out", "__pycache__", ".venv", "*.bin", "*.pt"])
)

vol = modal.Volume.from_name("argpt-coder", create_if_missing=True)

# The API key. It lives in Modal, never in this file:
#     modal secret create argpt-coder-key ARGPT_API_KEY=your-key-here
# Inside the container it arrives as an ordinary environment variable.
# This is the ONLY thing standing between your Modal credits and the whole
# internet, so do not paste the key into a slide.
KEY = modal.Secret.from_name("argpt-coder-key")

# HOW MODAL BILLS YOU, AND WHAT THIS NUMBER DOES
#
# You are charged for every second a CONTAINER IS ALIVE, not per request.
# After the last request finishes, Modal keeps the container warm for
# `scaledown_window` seconds in case another one arrives, then kills it.
#
# So this number is the whole billing decision, and it is a genuine trade:
#
#   scaledown_window=5     the container dies ~5s after your answer. You pay
#                          for almost nothing idle - but EVERY question then
#                          pays the ~12 second cold start again.
#                          One question  = ~15s billed = about 0.25 cents.
#
#   scaledown_window=120   stays warm two minutes. Follow-up questions answer
#                          in 1.5s instead of 14s.
#                          20 questions over 5 min = ~300s = about 5 cents.
#
# Run the numbers before you assume the short window is cheaper. For a live
# demo where you ask ten questions in a row, 120 costs about the same AND is
# ten times more responsive. For an endpoint that gets one question an hour,
# 5 is clearly right.
SCALEDOWN_SECONDS = 5

# Modal renamed this decorator from web_endpoint to fastapi_endpoint. Older
# installs only have the old name, so take whichever exists. Worth showing a
# class: libraries move, and one getattr beats an afternoon of confusion.
endpoint = getattr(modal, "fastapi_endpoint", None) or modal.web_endpoint


@app.cls(image=image, gpu="T4", volumes={"/ckpt": vol}, secrets=[KEY],
         scaledown_window=SCALEDOWN_SECONDS)
class Coder:
    preset: str = modal.parameter(default="big")

    @modal.enter()
    def load(self):
        """
        Runs ONCE per container, before the first request.

        Everything expensive belongs in here: reading the checkpoint,
        building the model, moving weights to the GPU.
        """
        import sys
        sys.path.insert(0, "/root/coder")

        from chat7 import load_model

        self.model, self.tok = load_model(f"/ckpt/coder-{self.preset}.pt",
                                          device="cuda")
        print(f"loaded {self.model.num_params()/1e6:.1f}M parameters")

    @endpoint(method="POST")
    def chat(self, payload: dict):
        """One question in, one answer out. This runs per request."""
        import os
        import sys
        import time

        sys.path.insert(0, "/root/coder")
        from fastapi.responses import JSONResponse

        # ---------- the door ----------
        # compare_digest instead of == so the comparison takes the same time
        # whether the first character is wrong or the last one is. A plain ==
        # leaks the key one character at a time to anyone patient enough to
        # measure. This is called a timing attack and it is not theoretical.
        #
        # BUT NOTICE WHERE THIS CHECK IS. It runs INSIDE the container, which
        # means a request with a rubbish key has already woken a GPU, loaded
        # 26M parameters, and started billing you before it gets rejected.
        # The key protects your MODEL. It does not protect your WALLET.
        #
        # The real fix is to reject at Modal's edge, before any container
        # exists - one argument:
        #
        #     @endpoint(method="POST", requires_proxy_auth=True)
        #
        # Then callers need Modal-Key and Modal-Secret headers from
        # `modal token new`, so your students cannot just curl it from their
        # laptops. That trade is why this file keeps the simple version, and
        # why saying so out loud beats teaching the habit silently.
        import hmac
        supplied = str(payload.get("api_key", ""))
        if not hmac.compare_digest(supplied, os.environ["ARGPT_API_KEY"]):
            return JSONResponse({"error": "bad or missing api_key"}, status_code=401)

        from chat7 import answer

        question = payload.get("question", "").strip()
        if not question:
            return JSONResponse({"error": 'send {"question": "..."}'}, status_code=400)

        started = time.time()
        reply = answer(self.model, self.tok, question,
                       history=payload.get("history", []),
                       temperature=float(payload.get("temperature", 0.2)),
                       max_tokens=int(payload.get("max_tokens", 320)),
                       device="cuda")
        return {"question": question, "answer": reply,
                "model": f"argpt-coder-{self.preset}",
                "parameters": self.model.num_params(),
                "generate_seconds": round(time.time() - started, 2)}


@app.local_entrypoint()
def main(question: str = "write a function to check if a number is prime"):
    """Test it without deploying: this calls the endpoint's logic over Modal."""
    import os

    key = os.environ.get("ARGPT_API_KEY")
    if not key and os.path.exists(".api_key.txt"):
        key = open(".api_key.txt").read().strip()
    if not key:
        raise SystemExit("Set ARGPT_API_KEY, or put the key in .api_key.txt")

    print("starting a container and asking it one question ...")
    reply = Coder().chat.remote({"question": question, "api_key": key})
    print("=" * 62)
    print(f"you>   {question}")
    print(f"argpt> {reply['answer']}")
    print("=" * 62)

# NOTE:
# - `modal run serve10.py` tests it. `modal deploy serve10.py` puts it live
#   on a permanent URL and prints that URL. On Windows, run
#   `set PYTHONIOENCODING=utf-8` first or the CLI dies on its own tick mark.
# - MEASURED on this exact code: first request 14.0 seconds, second request
#   1.5 seconds. That 12.5 second gap is the container booting and @enter()
#   loading the weights. Ask the class to guess which line saved 12 seconds
#   on every request after the first.
# - scaledown_window=120 means the container shuts down after two idle
#   minutes, so an idle API costs nothing. The first request after that
#   pays the cold start again - the classic serverless trade.
# - Stop the deployment with:  modal app stop argpt-coder-api
# - This runs on a T4 because without a KV cache every generated token is a
#   full forward pass, and a CPU would take half a minute per answer. Add
#   the cache and this becomes a CPU service costing a tenth as much.
# - There is no API key on this endpoint. Anyone with the URL can call it.
#   Fine for a class demo, not fine for anything real - Modal has
#   modal.Secret and proxy auth for when it matters.
