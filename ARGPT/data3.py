"""
FILE 3: Data — the reusable one
================================
This file knows nothing about ARGPT. That is deliberate.

Every LLM you build after today can reuse this file unchanged. It does
three jobs and then gets out of the way:

    1. download a text file
    2. tokenize it into numbers
    3. save those numbers as train.bin and val.bin

Any model that can read train.bin / val.bin works with this file.
That is the whole reason it lives separately from model4.py.

Run me:  python data3.py --dataset shakespeare --tokenizer char
         python data3.py --dataset tinystories --tokenizer bpe
"""

import argparse
import os

import numpy as np
import requests
import torch

from tokenizer2 import BPETokenizer, CharTokenizer

# RULE THIS FILE OBEYS: it imports nothing else from this project.
# No config, no model. Every function takes plain numbers and strings.
# That is the only reason you can copy it into your next project unchanged.

DATASETS = {
    # 1.1 MB. Downloads in seconds, trains in minutes. Use this in class.
    "shakespeare": "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt",

    # 19 MB of simple stories written for 4-year-olds. This is the VALID split
    # on purpose -- the train split is ~2 GB and we do not need it. Small models
    # trained on this produce genuinely readable English.
    "tinystories": "https://huggingface.co/datasets/roneneldan/TinyStories/resolve/main/TinyStories-valid.txt",

    # Your own text. Put it at data/custom/input.txt and it just works.
    "custom": None,

    # ~11 MB of real code + docstrings/comments from TheAlgorithms
    # (Python, JavaScript, C++, Java repos, MIT licensed). Already sitting at
    # data/coding/input.txt -- nothing to download.
    "coding": None,
}


def download(name, data_dir="data"):
    """Fetch the raw text once and keep it on disk."""
    folder = os.path.join(data_dir, name)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "input.txt")

    if os.path.exists(path):
        return path

    url = DATASETS[name]
    if url is None:
        raise FileNotFoundError(f"Put your own text file at: {path}")

    print(f"downloading {name} ...")
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    with open(path, "w", encoding="utf-8") as f:
        f.write(r.text)
    return path


def prepare(dataset="shakespeare", tokenizer="char", data_dir="data", vocab_size=1024):
    """text  ->  train.bin + val.bin + tokenizer.json"""
    folder = os.path.join(data_dir, dataset)
    with open(download(dataset, data_dir), encoding="utf-8") as f:
        text = f.read()
    print(f"{len(text):,} characters of raw text")

    # ---------- build the tokenizer ----------
    if tokenizer == "char":
        tok = CharTokenizer()
        tok.train(text)
    else:
        tok = BPETokenizer()
        # We train BPE on a 200 KB sample, not the whole file. Counting pairs
        # in pure Python is slow, and a sample gives almost the same merges.
        tok.train(text[:200_000], vocab_size=vocab_size, verbose=True)
    tok.save(os.path.join(folder, "tokenizer.json"))
    print(f"tokenizer: {tokenizer}, vocab size {tok.vocab_size}")

    # ---------- turn the whole text into numbers ----------
    # uint16 holds 0..65535. Fine for char (65) and our BPE (1024). If you ever
    # use a Llama-style 128k vocab, switch this to uint32.
    assert tok.vocab_size < 65536, "vocab too big for uint16 - use uint32"
    ids = np.array(tok.encode(text), dtype=np.uint16)
    assert ids.max() < tok.vocab_size, "a token id escaped the vocab"

    n = int(0.9 * len(ids))          # last 10% is held back to check honesty
    ids[:n].tofile(os.path.join(folder, "train.bin"))
    ids[n:].tofile(os.path.join(folder, "val.bin"))

    print(f"{len(ids):,} tokens -> train.bin ({n:,}) + val.bin ({len(ids)-n:,})")
    return tok


# ============================================================
# Reading the data back during training
# ============================================================

# We load each .bin into memory once and keep it here. Shakespeare is ~1 MB
# and TinyStories ~19 MB, so this costs nothing and is simpler and faster than
# re-reading the disk on every one of the thousands of training steps.
_loaded = {}


def get_batch(split, folder, block_size, batch_size, device="cpu"):
    """
    Grab `batch_size` random windows of text.

    x = tokens 0..127          "the cat sat on the ma"
    y = tokens 1..128          "he cat sat on the mat"

    y is just x shifted one step left. That single trick is the entire
    training signal: at every position, predict the next token.
    """
    if (folder, split) not in _loaded:
        path = os.path.join(folder, f"{split}.bin")
        _loaded[(folder, split)] = np.fromfile(path, dtype=np.uint16)
    data = _loaded[(folder, split)]

    # pick batch_size random start points, then slice a window at each one
    starts = torch.randint(len(data) - block_size - 1, (batch_size,))
    x = torch.stack([torch.from_numpy(data[i:i + block_size].astype(np.int64))
                     for i in starts])
    y = torch.stack([torch.from_numpy(data[i + 1:i + 1 + block_size].astype(np.int64))
                     for i in starts])
    return x.to(device), y.to(device)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="shakespeare", choices=list(DATASETS))
    p.add_argument("--tokenizer", default="char", choices=["char", "bpe"])
    p.add_argument("--vocab_size", type=int, default=1024)
    args = p.parse_args()

    # ---------- DEMO 1: build the dataset ----------
    print("=" * 55)
    tok = prepare(args.dataset, args.tokenizer, vocab_size=args.vocab_size)

    # ---------- DEMO 2: look at one real batch ----------
    print("\n" + "=" * 55)
    print("ONE BATCH, AS THE MODEL SEES IT")
    print("=" * 55)
    x, y = get_batch("train", os.path.join("data", args.dataset),
                     block_size=128, batch_size=32)
    print(f"x shape: {tuple(x.shape)}   (batch_size, block_size)")
    print(f"y shape: {tuple(y.shape)}   same shape, shifted by one\n")
    print(f"x starts: {tok.decode(x[0][:40].tolist())!r}")
    print(f"y starts: {tok.decode(y[0][:40].tolist())!r}   <- one step ahead")

# NOTE:
# - train.bin / val.bin are just raw numbers on disk. No format, no library.
# - val.bin is text the model NEVER trains on. If train loss falls but val loss
#   rises, the model is memorising instead of learning.
# - Want to train on your own writing? Drop it in data/custom/input.txt.
