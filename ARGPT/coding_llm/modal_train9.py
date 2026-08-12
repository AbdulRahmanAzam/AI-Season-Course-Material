"""
FILE 9: The whole pipeline on a rented GPU
===========================================
Nothing about the model changes here. train6.py is imported and called
exactly the way you called it on your laptop. The only thing that changes
is WHERE that function runs.

Count the lines in train_on_gpu() that are about machine learning. It is
one: `train(cfg)`. Everything else is describing a machine.

WHY THIS FILE IS NOT CALLED modal.py
    A file named modal.py shadows the modal package, so `import modal`
    imports YOUR file and the very next line dies with
        AttributeError: module 'modal' has no attribute 'App'
    Never name a file after a package you import. This bites everyone once.

ON WINDOWS, DO THIS FIRST
    set PYTHONIOENCODING=utf-8

    Modal's CLI prints a tick character when it finishes. The default
    Windows console code page cannot encode it, so the whole command dies
    with a baffling error that has nothing to do with your code:

        'charmap' codec can't encode character '\\u2713' in position 0

    It happens AFTER the GPU work has already succeeded, which makes it
    look like training failed when it did not. One environment variable.

Setup, ONCE, before class:
    pip install modal
    modal setup                    # opens a browser
    modal run modal_train9.py --iters 20    # builds the image, a few minutes

Run me:  modal run modal_train9.py
         modal run modal_train9.py --preset laptop --iters 3000
"""

import modal

app = modal.App("argpt-coder")

# The recipe for the machine our code will run on. Modal builds it once and
# caches it - torch is a 2.3 GB download, so the FIRST build is slow and
# every one after that starts in seconds.
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch", "numpy")
    .workdir("/root/coder")
    .add_local_dir(".", "/root/coder",
                   ignore=["data", "out", "__pycache__", ".venv", "*.bin", "*.pt"])
)

# A Volume is a disk that outlives the container. Without it your trained
# model dies the moment the machine is torn down.
vol = modal.Volume.from_name("argpt-coder", create_if_missing=True)

# L4 is $0.80/hour billed by the second and supports bfloat16. The free tier
# is $30/month, about 37 hours of this card. A full run here is ~15 minutes,
# so roughly 20 cents.
GPU = "L4"


@app.function(image=image, gpu=GPU, volumes={"/ckpt": vol}, timeout=60 * 60)
def train_on_gpu(preset="big", iters=None, batch=None, per_task=60, vocab=2048):
    import sys
    sys.path.insert(0, "/root/coder")

    import json
    import os
    import torch

    from build_data2 import build, write_corpus, write_jsonl, verify
    from model5 import BIG, LAPTOP, QUICK
    from pack4 import pack
    from tasks import ALL_TASKS
    from tokenizer3 import ChatTokenizer
    from train6 import train

    print(f"GPU: {torch.cuda.get_device_name(0)}")

    data_dir = "/ckpt/data"
    os.makedirs(data_dir, exist_ok=True)

    # ---------- the whole prep pipeline, files 2 to 4, in eight lines ----------
    print(f"\n[1/3] curriculum: {verify(ALL_TASKS)} code samples pass their tests")
    train_rows, val_rows = build(per_task=per_task)
    write_jsonl(os.path.join(data_dir, "train.jsonl"), train_rows)
    write_jsonl(os.path.join(data_dir, "val.jsonl"), val_rows)
    write_corpus(os.path.join(data_dir, "corpus.txt"))
    print(f"      {len(train_rows):,} train / {len(val_rows):,} val conversations")

    print("[2/3] training the tokenizer")
    tok = ChatTokenizer()
    tok.train(open(os.path.join(data_dir, "corpus.txt"), encoding="utf-8").read(),
              vocab_size=vocab)
    tok.save(os.path.join(data_dir, "tokenizer.json"))

    print("[3/3] packing with the loss mask")
    for split in ("train", "val"):
        pack(split, tok, data_dir)

    # ---------- the one line that is about machine learning ----------
    cfg = {"quick": QUICK, "laptop": LAPTOP, "big": BIG}[preset]
    cfg.data_dir = data_dir
    cfg.out_dir = "/ckpt"
    if iters:
        cfg.max_iters = iters
    if batch:
        cfg.batch_size = batch

    path = train(cfg)

    # WITHOUT THIS LINE THE CHECKPOINT IS LOST WHEN THE CONTAINER EXITS.
    vol.commit()
    print(f"committed {path} to volume 'argpt-coder'")
    return path


@app.function(image=image, gpu=GPU, volumes={"/ckpt": vol}, timeout=15 * 60)
def ask_the_gpu(questions, preset="big", temperature=0.2):
    import sys
    sys.path.insert(0, "/root/coder")

    from chat7 import answer, load_model

    model, tok = load_model(f"/ckpt/coder-{preset}.pt", device="cuda")
    return [(q, answer(model, tok, q, temperature=temperature, device="cuda"))
            for q in questions]


@app.local_entrypoint()
def main(preset: str = "big", iters: int = 0, batch: int = 0, per_task: int = 60):
    """This part runs on YOUR laptop. .remote() is what jumps to the GPU."""
    print("training on Modal ...")
    train_on_gpu.remote(preset, iters or None, batch or None, per_task)

    print("\nasking the model we just trained:")
    print("=" * 62)
    demo = ["write a function to check if a number is prime",
            "how do i remove duplicates from a list",
            "what is a list comprehension"]
    for question, reply in ask_the_gpu.remote(demo, preset):
        print(f"\nyou>   {question}\nargpt> {reply}")
    print("=" * 62)
    print("\npull the checkpoint down to your laptop with:")
    print(f"  modal volume get argpt-coder coder-{preset}.pt out/")

# NOTE:
# - .remote() runs on Modal. .local() runs right here. Same function either way.
# - Check the checkpoint survived:  modal volume ls argpt-coder
# - Pull it down:                   modal volume get argpt-coder coder-big.pt out/
# - Watch it live:                  https://modal.com/apps
# - Billed per second the container is alive, not per month. Fifteen minutes
#   on an L4 is about 20 cents.
# - The data prep runs on the GPU box too. That is slightly wasteful - the
#   GPU sits idle for 30 seconds while BPE runs on the CPU - but it keeps
#   the whole pipeline in one place, which for teaching is worth 30 seconds.
