"""
FILE 7: Modal — the same code, on a real GPU
=============================================
Nothing about ARGPT changes here.

train5.py is imported and called exactly the way you called it on your
laptop. The only thing that changes is WHERE that function runs. Read the
train_on_gpu function below and count how many lines are about machine
learning. It is one.

WHY IS THIS FILE NOT CALLED modal.py?
    Because a file named modal.py would shadow the modal package. `import
    modal` would then import THIS FILE instead of the real library, and the
    very first line would fail with:
        AttributeError: module 'modal' has no attribute 'App'
    Never name a file after a package you import. This bites everyone once.

Setup (do this ONCE, before class):
    pip install modal
    modal setup
    modal run modal_app7.py        <- first run builds the image, takes a few
                                     minutes. Modal caches it after that.

Run me:  modal run modal_app7.py
         modal run modal_app7.py --dataset tinystories --tokenizer bpe
"""

import modal

app = modal.App("argpt")

# The recipe for the machine our code will run on. Modal builds this once
# and caches it. torch is a ~2.3 GB download, so the FIRST build is slow.
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch", "numpy", "requests")
    .workdir("/root/argpt")
    .add_local_dir(".", "/root/argpt",
                   ignore=["data", "out", "__pycache__", ".venv", "*.bin", "*.pt"])
)

# A Volume is a disk that survives after the container is destroyed.
# Without it, your trained model dies with the container.
vol = modal.Volume.from_name("argpt-checkpoints", create_if_missing=True)

# "L4" is $0.80/hour and supports bf16. The free tier gives $30/month, which
# is about 37 hours of this card. Swap to "A100-40GB" for a serious run.
GPU = "L4"


@app.function(image=image, gpu=GPU, volumes={"/ckpt": vol}, timeout=60 * 60)
def train_on_gpu(dataset="shakespeare", tokenizer="char", max_iters=5000):
    import sys
    from dataclasses import replace

    sys.path.insert(0, "/root/argpt")     # so our files are importable

    import torch
    from config1 import SMALL
    from data3 import prepare
    from train5 import train

    print(f"GPU: {torch.cuda.get_device_name(0)}")

    # Keep data and checkpoints on the Volume so the next run reuses them.
    cfg = replace(SMALL, dataset=dataset, max_iters=max_iters,
                  data_dir="/ckpt/data", out_dir="/ckpt")

    prepare(dataset, tokenizer, data_dir="/ckpt/data")   # download + tokenize
    train(cfg)                                           # the exact same function

    # WITHOUT THIS LINE THE CHECKPOINT IS LOST WHEN THE CONTAINER EXITS.
    vol.commit()
    print("checkpoint committed to volume 'argpt-checkpoints'")


@app.function(image=image, gpu=GPU, volumes={"/ckpt": vol}, timeout=10 * 60)
def sample_from_gpu(dataset="shakespeare", tokenizer="char", prompt="\n", tokens=400, temperature=0.8):
    import sys

    sys.path.insert(0, "/root/argpt")
    from generate6 import generate, load_argpt

    model, tok = load_argpt(f"/ckpt/{dataset}small{tokenizer}.pt", device="cuda")
    return generate(model, tok, prompt, tokens, temperature, device="cuda")


@app.local_entrypoint()
def main(dataset: str = "shakespeare", tokenizer: str = "char", max_iters: int = 5000):
    """This part runs on YOUR laptop. .remote() is what jumps to the GPU."""
    print("training on Modal ...")
    train_on_gpu.remote(dataset, tokenizer, max_iters)

    print("\nsampling from the trained model:")
    print("=" * 55)
    print(sample_from_gpu.remote(dataset=dataset, tokenizer=tokenizer, prompt="\n", tokens=400))
    print("=" * 55)

# NOTE:
# - .remote() runs on Modal. .local() runs right here. Same function either way.
# - The checkpoint filename is <dataset><name><tokenizer>.pt, e.g. codingsmallbpe.pt,
#   codingsmallchar.pt, shakespearesmallchar.pt. Same volume holds all side by side.
# - Check your checkpoint survived:  modal volume ls argpt-checkpoints
# - Pull it down to your laptop:     modal volume get argpt-checkpoints codingsmallbpe.pt out/
# - Watch it live in the dashboard:  https://modal.com/apps
# - You are billed per second the container is alive, not per month. A 10 minute
#   training run on L4 costs about 13 cents.
