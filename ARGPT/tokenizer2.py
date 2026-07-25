"""
FILE 2: Tokenizer — turning text into numbers
==============================================
A neural network cannot read letters. It only multiplies numbers.
So step one of every LLM is: decide how text becomes a list of integers.

We build TWO tokenizers:

  1. CharTokenizer — one number per character. ~15 lines. Instantly clear.
  2. BPETokenizer  — the real thing. Same algorithm GPT-4 uses.

Both expose the same two methods, so the rest of ARGPT does not care
which one you picked:

    encode("hello")  ->  [46, 43, 50, 50, 53]
    decode([46, 43, 50, 50, 53])  ->  "hello"

Run me:  python tokenizer2.py
"""

import json
import re
from collections import Counter


# ============================================================
# 1. CHARACTER LEVEL — the easy one
# ============================================================

class CharTokenizer:
    """
    One integer per character. That is the entire idea.

    Shakespeare has 65 unique characters, so vocab_size = 65.
    Simple, but every single letter costs one token, so sequences get long.
    """

    def train(self, text):
        chars = sorted(set(text))                       # every unique character
        self.itos = dict(enumerate(chars))              # 0 -> 'a'
        self.stoi = {c: i for i, c in self.itos.items()}  # 'a' -> 0
        self.vocab_size = len(chars)

    def encode(self, text):
        return [self.stoi[c] for c in text]

    def decode(self, ids):
        return "".join(self.itos[i] for i in ids)

    def to_dict(self):
        return {"type": "char", "chars": "".join(self.itos[i] for i in range(self.vocab_size))}

    def from_dict(self, d):
        self.itos = dict(enumerate(d["chars"]))
        self.stoi = {c: i for i, c in self.itos.items()}
        self.vocab_size = len(self.itos)

    def save(self, path):
        _save(self, path)


# ============================================================
# 2. BYTE PAIR ENCODING — what real LLMs use
# ============================================================

# Before merging we split text into word-ish chunks, so a merge can never
# glue the end of one word onto the start of the next. GPT-2 does this too.
SPLIT = re.compile(r"\s*\w+|\s*[^\s\w]+|\s+")


def _merge(ids, pair, new_id):
    """Walk through ids and replace every occurrence of `pair` with `new_id`."""
    out, i = [], 0
    while i < len(ids):
        if i < len(ids) - 1 and (ids[i], ids[i + 1]) == pair:
            out.append(new_id)
            i += 2
        else:
            out.append(ids[i])
            i += 1
    return out


class BPETokenizer:
    """
    Byte Pair Encoding.

    The whole algorithm in one sentence:
        find the two tokens that sit next to each other most often,
        glue them into one new token, and repeat.

    Round 1:  ("t", "h")  is the most common pair  ->  new token "th"
    Round 2:  ("th", "e") is the most common pair  ->  new token "the"

    Common words end up as ONE token. Rare words stay in pieces.
    That is exactly why "the" costs 1 token but a rare name costs 4.

    We start from the 256 possible bytes, so ANY text can be encoded --
    emoji, Urdu, code, anything. Nothing is ever out-of-vocabulary.
    """

    def train(self, text, vocab_size=1024, verbose=False):
        chunks = [list(c.encode("utf-8")) for c in SPLIT.findall(text)]
        self.merges = {}                                  # (a, b) -> new_id
        self.vocab = {i: bytes([i]) for i in range(256)}  # id -> the bytes it means

        for new_id in range(256, vocab_size):
            # count every adjacent pair across the whole corpus
            pairs = Counter()
            for chunk in chunks:
                pairs.update(zip(chunk, chunk[1:]))
            if not pairs:
                break

            best, count = pairs.most_common(1)[0]         # the winner
            chunks = [_merge(c, best, new_id) for c in chunks]
            self.merges[best] = new_id
            self.vocab[new_id] = self.vocab[best[0]] + self.vocab[best[1]]

            if verbose and new_id < 256 + 10:             # show the first 10
                print(f"  merge {new_id}: {self._show(best[0])!r} + "
                      f"{self._show(best[1])!r} -> {self._show(new_id)!r}   "
                      f"({count:,} times)")

        self.vocab_size = vocab_size
        self._cache = {}

    def _show(self, i):
        return self.vocab[i].decode("utf-8", errors="replace")

    def _encode_chunk(self, chunk):
        ids = list(chunk.encode("utf-8"))
        while len(ids) >= 2:
            # apply merges in the order we learned them (lowest id first)
            pair = min(zip(ids, ids[1:]), key=lambda p: self.merges.get(p, float("inf")))
            if pair not in self.merges:
                break
            ids = _merge(ids, pair, self.merges[pair])
        return ids

    def encode(self, text):
        out = []
        for chunk in SPLIT.findall(text):
            if chunk not in self._cache:                  # cache repeated words
                self._cache[chunk] = self._encode_chunk(chunk)
            out.extend(self._cache[chunk])
        return out

    def decode(self, ids):
        raw = b"".join(self.vocab[i] for i in ids)
        return raw.decode("utf-8", errors="replace")      # a half token may be invalid

    def to_dict(self):
        return {"type": "bpe",
                "merges": [[a, b, i] for (a, b), i in self.merges.items()],
                "vocab_size": self.vocab_size}

    def from_dict(self, d):
        self.merges = {(a, b): i for a, b, i in d["merges"]}
        self.vocab_size = d["vocab_size"]
        self.vocab = {i: bytes([i]) for i in range(256)}
        for (a, b), i in self.merges.items():
            self.vocab[i] = self.vocab[a] + self.vocab[b]
        self._cache = {}

    def save(self, path):
        _save(self, path)


# ============================================================
# Saving / loading — so serve8.py can rebuild the exact tokenizer
# ============================================================

def _save(tok, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tok.to_dict(), f)


def tokenizer_from_dict(d):
    tok = CharTokenizer() if d["type"] == "char" else BPETokenizer()
    tok.from_dict(d)
    return tok


def load_tokenizer(path):
    with open(path, encoding="utf-8") as f:
        return tokenizer_from_dict(json.load(f))


if __name__ == "__main__":
    sample = "the cat sat on the mat. the cat ate the rat. " * 200

    # ---------- DEMO 1: character level ----------
    print("=" * 55)
    print("CHARACTER TOKENIZER")
    print("=" * 55)
    c = CharTokenizer()
    c.train(sample)
    print(f"vocab size: {c.vocab_size}")
    print(f"'the cat' -> {c.encode('the cat')}")
    print(f"back again -> {c.decode(c.encode('the cat'))!r}")

    # ---------- DEMO 2: BPE, watch the merges happen ----------
    print()
    print("=" * 55)
    print("BPE TOKENIZER - watch it invent words")
    print("=" * 55)
    b = BPETokenizer()
    b.train(sample, vocab_size=290, verbose=True)
    ids = b.encode("the cat sat")
    print(f"\n'the cat sat' -> {ids}")
    print(f"each token   -> {[b._show(i) for i in ids]}")
    print(f"back again   -> {b.decode(ids)!r}")

    # ---------- DEMO 3: why BPE wins ----------
    print()
    text = "the cat sat on the mat"
    print(f"char tokenizer: {len(c.encode(text))} tokens")
    print(f"bpe  tokenizer: {len(b.encode(text))} tokens  <- fewer tokens, same text")

# NOTE:
# - Fewer tokens = the model sees more real text inside the same block_size.
# - BPE starts from bytes, so it can encode ANY language. Nothing is unknown.
# - The tokenizer is trained on data BEFORE the model exists. It is not learned
#   by the neural network. It is just counting.
