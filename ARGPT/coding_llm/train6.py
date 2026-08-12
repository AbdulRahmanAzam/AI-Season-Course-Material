"""
FILE 6: Training - the same five steps, with the grown-up trimmings
====================================================================
The loop underneath is the one from the main session and it has not
changed:

    1. grab a batch      2. predict      3. measure how wrong
    4. work out which way each weight should move      5. move them

Four things are wrapped around it, and each one is worth a minute of
class time because each one is the difference between "it trained" and
"it trained well".

    LEARNING RATE SCHEDULE
        Start near zero and ramp up over 200 steps (warmup), then decay
        along a cosine curve to almost nothing. Big steps early while the
        model knows nothing; tiny steps at the end so it can settle instead
        of bouncing around the answer.

    WEIGHT DECAY ON THE RIGHT THINGS
        Nudge the big matrices toward zero, leave the norms and biases
        alone. Decaying a LayerNorm gain is meaningless and mildly harmful,
        and every serious training script splits the parameters like this.

    BFLOAT16
        Do the maths in 16 bits instead of 32. Roughly twice the speed and
        half the memory on any card from 2020 onward. bf16 keeps float32's
        exponent range, so unlike fp16 it does not need loss scaling - a
        real headache that simply evaporated.

    TOKEN ACCURACY
        Loss is in nats and means nothing to a beginner. "It gets 94% of the
        answer tokens exactly right" means something to everybody. Same
        measurement, readable units.

Run me:  python train6.py                    # ~11M model
         python train6.py --preset quick     # ~2 min, for a live demo
         python train6.py --preset big       # ~26M model
"""

import argparse
import json
import math
import os
import time
from dataclasses import asdict

import torch

from model5 import BIG, LAPTOP, QUICK, ARGPTCoder
from pack4 import BLOCK, get_batch, load
from tokenizer3 import load_tokenizer

# What we ask it every few hundred steps, so the class can watch it learn.
WATCH = [
    "write a function to reverse a string",
    "what is a list comprehension",
]


def lr_at(step, cfg):
    """Warm up, then cosine decay. Two lines that reliably buy you 0.1 loss."""
    if step < cfg.warmup:
        return cfg.learning_rate * step / max(1, cfg.warmup)
    progress = (step - cfg.warmup) / max(1, cfg.max_iters - cfg.warmup)
    progress = min(1.0, progress)
    return cfg.min_lr + 0.5 * (cfg.learning_rate - cfg.min_lr) * (
        1 + math.cos(math.pi * progress))


def make_optimizer(model, cfg):
    """
    Weight decay on the matrices, none on the 1-D parameters.

    Anything with 2 or more dimensions is a weight matrix and benefits from
    being pulled gently toward zero. Anything 1-D is a norm gain or a bias,
    where decay does nothing useful.
    """
    decay = [p for p in model.parameters() if p.requires_grad and p.dim() >= 2]
    no_decay = [p for p in model.parameters() if p.requires_grad and p.dim() < 2]
    groups = [{"params": decay, "weight_decay": cfg.weight_decay},
              {"params": no_decay, "weight_decay": 0.0}]
    print(f"  decayed tensors  {len(decay)}  ({sum(p.numel() for p in decay):,} params)")
    print(f"  untouched        {len(no_decay)}  ({sum(p.numel() for p in no_decay):,} params)")
    return torch.optim.AdamW(groups, lr=cfg.learning_rate, betas=(0.9, 0.95))


@torch.no_grad()
def evaluate(model, cfg, device, autocast):
    """
    Average loss and token accuracy over a few batches of each split.

    Accuracy here means: of the tokens we actually score - the answer
    tokens - how many does the model's top guess get exactly right?
    """
    model.eval()
    out = {}
    for split in ("train", "val"):
        losses = torch.zeros(cfg.eval_iters)
        right = total = 0
        for i in range(cfg.eval_iters):
            x, y, mask = get_batch(split, cfg.batch_size, device, cfg.data_dir)
            with autocast:
                logits, loss = model(x, y, mask)
            losses[i] = loss.item()
            hits = (logits.argmax(-1) == y).float() * mask
            right += hits.sum().item()
            total += mask.sum().item()
        out[split] = (losses.mean().item(), right / max(1, total))
    model.train()
    return out


def train(cfg, resume=None):
    torch.manual_seed(1337)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # bf16 on a modern GPU, plain float32 everywhere else
    use_bf16 = device == "cuda" and torch.cuda.is_bf16_supported()
    autocast = (torch.autocast("cuda", dtype=torch.bfloat16) if use_bf16
                else torch.autocast("cpu", enabled=False))
    if device == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True

    print("=" * 62)
    print(f"TRAINING  preset={cfg.name}  device={device}"
          f"{'  bfloat16' if use_bf16 else ''}")
    print("=" * 62)

    # ---------- the tokenizer decides vocab_size, never you ----------
    tok_path = os.path.join(cfg.data_dir, "tokenizer.json")
    if not os.path.exists(tok_path):
        raise SystemExit("Run these first:\n  python build_data2.py\n"
                         "  python tokenizer3.py\n  python pack4.py")
    tok = load_tokenizer(tok_path)
    cfg.vocab_size = tok.vocab_size

    tokens, flags, lengths = load("train", cfg.data_dir)
    print(f"  {len(tokens):,} training conversations, "
          f"{int(flags.sum()):,} scored tokens, vocab {cfg.vocab_size}")

    model = ARGPTCoder(cfg).to(device)
    print(f"  ARGPT-Coder: {model.num_params()/1e6:.1f}M parameters")
    opt = make_optimizer(model, cfg)

    start = 1
    if resume and os.path.exists(resume):
        ckpt = torch.load(resume, map_location=device, weights_only=True)
        model.load_state_dict(ckpt["model"])
        start = ckpt.get("step", 0) + 1
        print(f"  resumed from {resume} at step {start}")

    os.makedirs(cfg.out_dir, exist_ok=True)
    path = os.path.join(cfg.out_dir, f"coder-{cfg.name}.pt")
    tok_dict = json.load(open(tok_path, encoding="utf-8"))

    def save(step):
        torch.save({"model": model.state_dict(),
                    "cfg": asdict(cfg),
                    "tokenizer": tok_dict,
                    "step": step}, path)

    print(f"\n  training for {cfg.max_iters} steps, saving to {path}\n")
    best = float("inf")
    seen = 0
    t0 = time.time()

    for step in range(start, cfg.max_iters + 1):
        # ---------- the learning rate for THIS step ----------
        lr = lr_at(step, cfg)
        for group in opt.param_groups:
            group["lr"] = lr

        # ---------- the five steps ----------
        x, y, mask = get_batch("train", cfg.batch_size, device, cfg.data_dir)  # 1
        with autocast:
            _, loss = model(x, y, mask)                                        # 2, 3
        opt.zero_grad(set_to_none=True)
        loss.backward()                                                        # 4
        torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip)
        opt.step()                                                             # 5
        seen += x.numel()

        # ---------- watch it learn ----------
        if step % cfg.eval_interval == 0 or step == cfg.max_iters:
            scores = evaluate(model, cfg, device, autocast)
            (tr_loss, tr_acc), (va_loss, va_acc) = scores["train"], scores["val"]
            elapsed = time.time() - t0
            print(f"step {step:5d} | lr {lr:.1e} | "
                  f"train {tr_loss:.3f} ({tr_acc:6.1%}) | "
                  f"val {va_loss:.3f} ({va_acc:6.1%}) | "
                  f"{elapsed:5.0f}s | {seen/elapsed/1000:.0f}k tok/s", flush=True)

            if va_loss < best:
                best = va_loss
                save(step)

            # THE MOMENT. Around step 500 this turns from word salad into
            # real Python. Stop talking and let the class read it.
            from chat7 import answer
            for question in WATCH:
                reply = answer(model, tok, question, max_tokens=120,
                               temperature=0.2, device=device)
                first = reply.strip().split("\n")
                preview = "\n           ".join(first[:6])
                print(f"    ask:   {question}\n    reply: {preview}\n")

    print("=" * 62)
    print(f"done in {(time.time()-t0)/60:.1f} minutes")
    print(f"best val loss {best:.3f}, saved to {path}")
    print("=" * 62)
    print(f"\nnext:  python evaluate8.py --ckpt {path}")
    print(f"       python chat7.py --ckpt {path}")
    return path


if __name__ == "__main__":
    PRESETS = {"quick": QUICK, "laptop": LAPTOP, "big": BIG}

    p = argparse.ArgumentParser()
    p.add_argument("--preset", default="laptop", choices=list(PRESETS))
    p.add_argument("--iters", type=int, default=None, help="override max_iters")
    p.add_argument("--batch", type=int, default=None, help="override batch_size")
    p.add_argument("--resume", default=None)
    args = p.parse_args()

    cfg = PRESETS[args.preset]
    if args.iters:
        cfg.max_iters = args.iters
    if args.batch:
        cfg.batch_size = args.batch
    cfg.block_size = max(cfg.block_size, BLOCK)

    train(cfg, resume=args.resume)

# NOTE:
# - Watch train accuracy and val accuracy together. Both climbing = it is
#   learning. Train climbing while val stalls = it is memorising the exact
#   sentences instead of the meaning. Because our val split is held-out
#   PHRASINGS of the same tasks, this gap is a real measurement and not a
#   formality.
# - Loss around 0.30 and accuracy above 90% is where the answers become
#   reliably correct code. Below 1.0 it is still inventing function names.
# - This is the same train() that modal_train8.py calls on a rented GPU.
#   Not a copy of it - literally this function, imported.
