"""
FILE 8: Serve — turning ARGPT into an API
==========================================
Sessions 1 to 6 you called somebody else's API. Now you become the API.

This file puts the model you trained behind a URL. Anyone -- including the
agent you built in Session 6 -- can POST to it and get text back.

The one idea that matters here is @modal.enter().
    Loading model weights onto a GPU takes a few seconds. If we did that
    inside the request handler, EVERY request would pay that cost.
    @modal.enter() runs once when a container starts, so the weights are
    already sitting in GPU memory when the first request arrives.

Deploy me:  modal deploy serve8.py
Test me:    curl -X POST <your-url> -H "Content-Type: application/json" \
                 -d '{"prompt": "ROMEO:", "max_tokens": 200}'
"""

import modal

app = modal.App("argpt-serve")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch", "numpy", "requests", "fastapi[standard]")
    .workdir("/root/argpt")
    .add_local_dir(".", "/root/argpt",
                   ignore=["data", "out", "__pycache__", ".venv", "*.bin", "*.pt"])
)

# The same Volume modal_app7.py wrote the checkpoint into.
vol = modal.Volume.from_name("argpt-checkpoints", create_if_missing=True)

# Checkpoints are named <dataset><name><tokenizer>.pt (e.g. codingsmallbpe.pt,
# shakespearesmallchar.pt). One deploy serves ONE checkpoint -- change this
# and re-run `modal deploy serve8.py` to switch which model is behind the URL.
CKPT = "/ckpt/shakespearesmallchar.pt"


@app.cls(
    image=image,
    gpu="L4",
    volumes={"/ckpt": vol},
    scaledown_window=300,   # stay warm 5 min after the last request, then stop
)                           # billing stops with it, so an idle model is free
class ARGPTServer:

    @modal.enter()
    def load(self):
        """Runs ONCE per container, not once per request."""
        import sys

        sys.path.insert(0, "/root/argpt")
        from generate6 import load_argpt

        self.model, self.tok = load_argpt(CKPT, device="cuda")
        print("ARGPT loaded and waiting")

    @modal.fastapi_endpoint(method="POST")
    def chat(self, item: dict):
        import sys

        sys.path.insert(0, "/root/argpt")
        from generate6 import generate

        text = generate(
            self.model, self.tok,
            prompt=item.get("prompt", "\n"),
            max_new_tokens=item.get("max_tokens", 200),
            temperature=item.get("temperature", 0.8),
            device="cuda",
        )
        return {"text": text}

# NOTE:
# - `modal serve serve8.py`  = temporary URL that reloads as you edit. Use while
#   building. `modal deploy serve8.py` = permanent URL. Use when you are done.
# - The URL is printed when you deploy. It looks like:
#       https://<your-workspace>--argpt-serve-argptserver-chat.modal.run
# - First request after 5 idle minutes is slow: the container has to cold start.
#   That is the trade you make for not paying while nobody is using it.
# - Try deleting @modal.enter() and moving the load into chat(). Time both.
#   That comparison teaches more than any explanation.
