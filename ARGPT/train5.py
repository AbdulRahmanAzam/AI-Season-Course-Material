"""
FILE 5: Training — teaching ARGPT to predict the next token
============================================================
The loop is shorter than you expect. Five steps, forever:

    1. grab a random batch of text
    2. ask the model to predict it
    3. measure how wrong it was          (loss)
    4. work out which way each weight should move   (loss.backward)
    5. nudge every weight that way       (optimizer.step)

There is no step 6. That is how every neural network on earth is trained.

Run me:  python train5.py
"""

import json
import os
import time
from dataclasses import asdict

import torch

from config1 import TINY
from data3 import get_batch
from generate6 import generate
from model4 import ARGPT
from tokenizer2 import tokenizer_from_dict


@torch.no_grad()                      # no gradients here, we are only measuring
def estimate_loss(model, cfg, folder, device):
    """
    Average the loss over a few batches instead of trusting a single one.
    One batch is noisy; ten batches tell the truth.
    """
    model.eval()                      # switch dropout off while measuring
    out = {}
    for split in ("train", "val"):
        losses = torch.zeros(cfg.eval_iters)
        for i in range(cfg.eval_iters):
            x, y = get_batch(split, folder, cfg.block_size, cfg.batch_size, device)
            _, loss = model(x, y)
            losses[i] = loss.item()
        out[split] = losses.mean().item()
    model.train()                     # dropout back on
    return out


def train(cfg):
    torch.manual_seed(1337)           # same run every time, so demos are repeatable
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device: {device}")

    folder = os.path.join(cfg.data_dir, cfg.dataset)

    # Load the tokenizer data3.py saved. It gives us two things: the vocab_size
    # (the DATA decides it, not you -- model and tokenizer must agree), and a way
    # to turn tokens back into text so we can print samples WHILE it trains.
    with open(os.path.join(folder, "tokenizer.json")) as f:
        tokenizer = json.load(f)
    tok = tokenizer_from_dict(tokenizer)
    cfg.vocab_size = tok.vocab_size

    model = ARGPT(cfg).to(device)
    print(f"ARGPT: {model.num_params()/1e6:.2f}M parameters, vocab {cfg.vocab_size}")

    # AdamW is the optimizer everyone uses. It decides how far to move each
    # weight, giving weights that keep moving the same direction a bigger push.
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.learning_rate)

    print(f"training for {cfg.max_iters} steps ...")
    t0 = time.time()

    for step in range(1, cfg.max_iters + 1):
        x, y = get_batch("train", folder, cfg.block_size, cfg.batch_size, device)  # 1. a batch
        _, loss = model(x, y)                    # 2 + 3. predict, and score how wrong

        opt.zero_grad()                          # clear last step's gradients
        loss.backward()                          # 4. which way should each weight go
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)   # guardrail: no wild jumps
        opt.step()                               # 5. move every weight a little

        if step % cfg.eval_interval == 0 or step == cfg.max_iters:
            l = estimate_loss(model, cfg, folder, device)
            print(f"\nstep {step:5d} | train loss {l['train']:.3f} | "
                  f"val loss {l['val']:.3f} | {time.time()-t0:.0f}s")

            # WATCH IT LEARN. This is the best part of the whole session.
            # Noise -> letter soup -> word shapes -> names and line breaks.
            sample = generate(model, tok, "\n", 120, device=device)
            print("  " + sample.replace("\n", "\n  "))

    # ---------- save everything needed to use this model later ----------
    os.makedirs(cfg.out_dir, exist_ok=True)
    path = os.path.join(cfg.out_dir, f"{cfg.dataset}{cfg.name}{tokenizer['type']}.pt")

    # Three things go in the file, and all three are needed:
    #   model     the weights
    #   cfg       the shape, so we can rebuild the same model later
    #   tokenizer without it, the numbers cannot become text again
    # asdict() stores a plain dict, not a Python object, so loading is safe.
    torch.save({"model": model.state_dict(),
                "cfg": asdict(cfg),
                "tokenizer": tokenizer}, path)
    print(f"\nsaved -> {path}")
    return path


if __name__ == "__main__":
    # ---------- DEMO: train the small one on your own laptop ----------
    train(TINY)

# NOTE:
# - Watch the two losses. Both falling = learning. Train falls but val rises =
#   memorising the training text instead of learning the language.
# - On Shakespeare, char level: ~4.2 at the start, ~1.6 is decent.
# - This exact function is what runs on the GPU in modal_app7.py. Not a copy of
#   it -- literally this function, imported.
