"""
FILE 4: Packing - loss masking, the idea that makes instruction tuning work
============================================================================
We have conversations. The model wants rectangles of numbers. This file
turns one into the other, and does the single most important thing in the
whole folder while it is there.

THE SHIFT (same as the main session)
    x = tokens 0..n-1        y = tokens 1..n
    At every position, predict the next token. That is the only thing a
    language model is ever trained to do.

THE MASK (new, and the reason this works at all)
    In pretraining we score the model on every token. Here we must not.

        <|user|> how do i reverse a string <|assistant|> return s[::-1] <|end|>
        |------------- do NOT score -------------||------- score -------|

    If we scored the question too, the model would spend a large slice of
    its 25 million parameters learning to write plausible QUESTIONS. It
    would get good at sounding like a user. We want it good at answering.

    So we carry a 1/0 flag beside every token and multiply the loss by it.
    Ten lines of code. It is the difference between a model that answers
    you and a model that talks to itself.

PADDING, AND NOT WASTING COMPUTE ON IT
    Rows must be the same length to stack into a rectangle, so short ones
    get filled with <|pad|>. Our average conversation is 112 tokens and our
    longest is 265, so a fixed 288-wide rectangle is 61% padding - we would
    burn most of the GPU on filler.

    Fix: store each row's real length, and at batch time cut the batch down
    to the longest REAL row in it. Random batches of 32 rarely contain the
    265-token monster, so batches come out around 190 wide instead of 288.
    A third of the training time back, for three lines. Real frameworks
    call this dynamic padding.

Run me:  python pack4.py
"""

import argparse
import json
import os

import numpy as np

from chat_format1 import PAD, segments
from tokenizer3 import load_tokenizer

BLOCK = 288          # the longest conversation is 265 tokens, so nothing is lost


def encode_row(turns, tok):
    """
    One conversation -> (token ids, learn flags).

    chat_format1.segments() already told us which pieces are the answer.
    All we do here is encode each piece and repeat its flag once per token.
    """
    ids, learn = [], []
    for text, is_answer in segments(turns):
        piece = tok.encode(text)
        ids.extend(piece)
        learn.extend([1 if is_answer else 0] * len(piece))
    return ids, learn


def pack(split, tok, folder="data", block=BLOCK):
    """jsonl -> three .npy-free flat binary files the trainer can memory-map."""
    rows = [json.loads(line) for line in
            open(os.path.join(folder, f"{split}.jsonl"), encoding="utf-8")]

    pad_id = tok.special_to_id[PAD]
    width = block + 1                       # one extra, because y is x shifted

    tokens = np.full((len(rows), width), pad_id, dtype=np.uint16)
    flags = np.zeros((len(rows), width), dtype=np.uint8)
    lengths = np.zeros(len(rows), dtype=np.uint16)

    kept, dropped = 0, 0
    for row in rows:
        ids, learn = encode_row(row["turns"], tok)
        if len(ids) > width:                # too long to fit - leave it out
            dropped += 1
            continue
        tokens[kept, :len(ids)] = ids
        flags[kept, :len(ids)] = learn
        lengths[kept] = len(ids)
        kept += 1

    tokens, flags, lengths = tokens[:kept], flags[:kept], lengths[:kept]
    tokens.tofile(os.path.join(folder, f"{split}_tokens.bin"))
    flags.tofile(os.path.join(folder, f"{split}_learn.bin"))
    lengths.tofile(os.path.join(folder, f"{split}_len.bin"))

    real = int(lengths.sum())
    scored = int(flags.sum())
    print(f"  {split:5s} {kept:6,d} rows   avg length {lengths.mean():5.1f}"
          f"   scored tokens {scored:8,d} ({100*scored/real:.0f}% of real tokens)")
    if dropped:
        print(f"        {dropped} row(s) dropped for being longer than {width}")
    return kept


# ============================================================
# Reading it back during training
# ============================================================

_loaded = {}


def load(split, folder="data", block=BLOCK):
    """Read the three files once and keep them around."""
    if (folder, split) not in _loaded:
        width = block + 1
        tokens = np.fromfile(os.path.join(folder, f"{split}_tokens.bin"),
                             dtype=np.uint16).reshape(-1, width)
        flags = np.fromfile(os.path.join(folder, f"{split}_learn.bin"),
                            dtype=np.uint8).reshape(-1, width)
        lengths = np.fromfile(os.path.join(folder, f"{split}_len.bin"), dtype=np.uint16)
        _loaded[(folder, split)] = (tokens, flags, lengths)
    return _loaded[(folder, split)]


def get_batch(split, batch_size, device="cpu", folder="data", block=BLOCK, rng=None):
    """
    A batch of complete conversations.

    Returns x, y, mask - all the same shape.
        x     what the model reads
        y     what it should have said next
        mask  1 where we score it, 0 where we do not
    """
    import torch

    tokens, flags, lengths = load(split, folder, block)
    rng = rng or np.random
    pick = rng.randint(0, len(tokens), batch_size)

    # trim the whole batch to the longest REAL row in it, then keep one
    # extra column so y can be x shifted by one
    width = int(lengths[pick].max())
    rows = tokens[pick, :width].astype(np.int64)
    keep = flags[pick, :width].astype(np.float32)

    x = torch.from_numpy(rows[:, :-1]).to(device)
    y = torch.from_numpy(rows[:, 1:]).to(device)
    mask = torch.from_numpy(keep[:, 1:]).to(device)   # flag belongs to the TARGET
    return x, y, mask


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data")
    args = p.parse_args()

    tok = load_tokenizer(os.path.join(args.data, "tokenizer.json"))

    # ---------- STEP 1: pack both splits ----------
    print("=" * 62)
    print("PACKING conversations into rectangles of numbers")
    print("=" * 62)
    for split in ("train", "val"):
        pack(split, tok, args.data)

    # ---------- DEMO 1: look at one real training row ----------
    print("\n" + "=" * 62)
    print("ONE ROW, WITH THE MASK PRINTED BESIDE IT")
    print("=" * 62)
    x, y, mask = get_batch("train", batch_size=4)
    print(f"  x     {tuple(x.shape)}   what the model reads")
    print(f"  y     {tuple(y.shape)}   what it should say next")
    print(f"  mask  {tuple(mask.shape)}   1 = score this, 0 = ignore\n")

    row = 0
    shown = 0
    for i in range(x.shape[1]):
        token = tok.show(int(y[row, i]))
        flag = int(mask[row, i])
        if flag == 0 and shown > 60:
            continue
        mark = "SCORE " if flag else "ignore"
        print(f"  {mark} | {token!r}")
        shown += 1
        if shown > 74:
            print("  ... (rest of the answer, all SCORE)")
            break

    # ---------- DEMO 2: what the mask is worth ----------
    print("\n" + "=" * 62)
    print("WHY THE MASK MATTERS")
    print("=" * 62)
    tokens, flags, lengths = load("train")
    real = int(lengths.sum())
    scored = int(flags.sum())
    print(f"  real tokens in the training set : {real:,}")
    print(f"  tokens we actually score        : {scored:,}  ({100*scored/real:.0f}%)")
    print(f"  tokens we deliberately ignore   : {real-scored:,}  (the questions)")
    print("\n  Without the mask, nearly a fifth of every gradient would be")
    print("  teaching the model to imitate the person asking. That is capacity")
    print("  spent on the wrong half of the conversation.")

    # ---------- DEMO 3: dynamic padding, measured ----------
    print("\n" + "=" * 62)
    print("DYNAMIC PADDING - measured, not claimed")
    print("=" * 62)
    widths = [get_batch("train", 32)[0].shape[1] for _ in range(20)]
    avg = sum(widths) / len(widths)
    print(f"  fixed rectangle would be    : {BLOCK} columns every step")
    print(f"  trimmed batches average     : {avg:.0f} columns")
    print(f"  compute saved               : {100*(1-avg/BLOCK):.0f}%")

    print("\n" + "=" * 62)
    print("next:  python model5.py")

# NOTE:
# - The mask is applied in model5.py's forward(), not here. Here we only
#   record WHERE to apply it.
# - mask lines up with y, not x. The flag says "should we be scored on
#   predicting this token", and y is the token being predicted. Getting
#   this off by one is the classic bug and it is nearly invisible: the
#   model still trains, just slightly wrong.
# - Rows are whole conversations, so a row never runs into the next one.
#   Pretraining packs a continuous stream instead, because there the text
#   genuinely does continue.
