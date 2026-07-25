"""
FILE 1: Config — the control panel
===================================
Every number that shapes ARGPT lives in this one file.

Why bother? Because in the next 9 files you will never see a magic number.
When you want a bigger or smarter model, you change ONE line here and
nothing else.

This is the only file you should edit while experimenting.

Run me:  python config1.py
"""

from dataclasses import dataclass


@dataclass
class Config:
    # ---------- which preset this is ----------
    name: str = "tiny"         # sets the checkpoint filename: out/<name>.pt

    # ---------- the shape of the model ----------
    block_size: int = 128      # how many tokens the model can look back at
    n_layer: int = 4           # how many transformer blocks we stack
    n_head: int = 4            # attention heads inside each block
    n_embd: int = 128          # size of the vector that represents one token
    dropout: float = 0.1       # fraction of neurons randomly switched off

    # vocab_size is NOT set by you. data3.py decides it and train5.py fills it in.
    vocab_size: int = 0

    # ---------- how we train it ----------
    batch_size: int = 32       # how many sequences we learn from at once
    max_iters: int = 2000      # how many training steps
    eval_interval: int = 250   # print train/val loss every N steps
    eval_iters: int = 50       # how many batches to average for that loss
    learning_rate: float = 3e-4

    # ---------- where files live ----------
    dataset: str = "shakespeare"
    data_dir: str = "data"
    out_dir: str = "out"


# RULE: n_embd must divide evenly by n_head.
#       Each head gets n_embd / n_head numbers to work with.
#       128 / 4 = 32  OK        384 / 6 = 64  OK        100 / 3  BROKEN


# Your laptop, no GPU, about 2 minutes.
# The output will be bad. That is fine — you are here to watch loss drop.
TINY = Config()

# A Modal GPU, about 10 minutes.
# Same code, bigger numbers. The output actually becomes readable.
SMALL = Config(
    name="small",
    block_size=256,
    n_layer=6,
    n_head=6,
    n_embd=384,
    batch_size=64,
    max_iters=5000,
    learning_rate=1e-3,
)


if __name__ == "__main__":
    # ---------- DEMO: how big is each model? ----------
    for name, cfg in [("TINY", TINY), ("SMALL", SMALL)]:
        # rough count: embeddings + 12 * n_embd^2 per block is the bulk of it
        approx = cfg.n_layer * 12 * cfg.n_embd**2
        print(f"{name:6s} {cfg.n_layer} layers x {cfg.n_embd} dims "
              f"-> roughly {approx/1e6:.1f}M parameters")

# NOTE:
# - Bigger n_embd and n_layer = smarter model, slower training, more memory.
# - block_size is the model's memory. It cannot see further back than this.
# - Everything here is a guess that people tuned by trying. There is no formula.
