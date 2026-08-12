"""
FILE 3: A tokenizer that knows about special tokens (and is 10x faster)
=======================================================================
Two upgrades over tokenizer2.py from the main session.

UPGRADE 1 - SPECIAL TOKENS THAT NEVER SPLIT
    Plain BPE would chew <|assistant|> into something like
    < | ass ist ant | > - seven tokens, and the model has to learn that
    this particular seven-token sequence is magic. Fragile and wasteful.

    Instead we cut the text on the special tokens FIRST, BPE only the
    ordinary parts, and give each special its own id above the BPE range.
    Now <|assistant|> is one token that appears nowhere else, ever. It is
    an unmistakable signal.

UPGRADE 2 - COUNT EACH WORD ONCE
    tokenizer2.py holds one entry per word occurrence and re-counts every
    adjacent pair from scratch on every merge. Training it on our corpus
    takes 149 seconds.

    But our corpus is 400 KB of about 7,000 DISTINCT words. "return"
    appears 300 times and gets counted 300 times, 2000 times over.

    So: hold {word: how_often} instead of a list of words. Counting a pair
    means adding `how_often` once instead of adding 1 three hundred times.
    Identical merges, about ten times faster.

    That is the entire optimisation, and it is the same one in the original
    BPE paper from 2015.

Run me:  python tokenizer3.py                  # trains on data/corpus.txt
"""

import json
import os
import re
import time
from collections import Counter

from chat_format1 import SPECIALS

# Same word-splitting rule as tokenizer2.py: a merge can never glue the end
# of one word onto the start of the next.
SPLIT = re.compile(r"\s*\w+|\s*[^\s\w]+|\s+")

# Cut the text on special tokens before anything else touches it. The
# capturing group keeps the specials in the output of re.split.
SPECIAL_SPLIT = re.compile("(" + "|".join(re.escape(s) for s in SPECIALS) + ")")


def _merge(ids, pair, new_id):
    """Replace every occurrence of `pair` in `ids` with the single `new_id`."""
    out, i = [], 0
    while i < len(ids):
        if i < len(ids) - 1 and (ids[i], ids[i + 1]) == pair:
            out.append(new_id)
            i += 2
        else:
            out.append(ids[i])
            i += 1
    return out


class ChatTokenizer:
    """
    Byte pair encoding, plus the four special tokens from chat_format1.py.

    Ids are laid out like this:

        0 .. 255            the raw bytes, so nothing is ever unknown
        256 .. bpe_size-1   the merges BPE learned
        bpe_size ..         <|pad|> <|user|> <|assistant|> <|end|>

    The specials go LAST so that adding one later does not renumber
    everything and invalidate every checkpoint you ever trained.
    """

    # ---------- training ----------

    def train(self, text, vocab_size=2048, verbose=False):
        # {word_as_byte_tuple: how many times it appears}
        words = Counter(SPLIT.findall(text))
        chunks = Counter()
        for word, count in words.items():
            chunks[tuple(word.encode("utf-8"))] += count

        self.merges = {}
        self.vocab = {i: bytes([i]) for i in range(256)}
        self.id_to_special = {}          # filled in by _finish() at the end

        for new_id in range(256, vocab_size):
            # count every adjacent pair, weighted by how often the word occurs
            pairs = Counter()
            for ids, count in chunks.items():
                for pair in zip(ids, ids[1:]):
                    pairs[pair] += count
            if not pairs:
                break

            best, count = pairs.most_common(1)[0]

            # rebuild only the words that actually contain the winning pair
            merged = Counter()
            for ids, n in chunks.items():
                if best[0] in ids:
                    ids = tuple(_merge(list(ids), best, new_id))
                merged[ids] += n
            chunks = merged

            self.merges[best] = new_id
            self.vocab[new_id] = self.vocab[best[0]] + self.vocab[best[1]]

            if verbose and new_id < 256 + 12:
                print(f"  merge {new_id}: {self.show(best[0])!r} + "
                      f"{self.show(best[1])!r} -> {self.show(new_id)!r}   "
                      f"({count:,} times)")

        self.bpe_size = vocab_size
        self._finish()

    def _finish(self):
        """Work out the special-token ids and reset the encode cache."""
        self.special_to_id = {s: self.bpe_size + i for i, s in enumerate(SPECIALS)}
        self.id_to_special = {i: s for s, i in self.special_to_id.items()}
        self.vocab_size = self.bpe_size + len(SPECIALS)
        self._cache = {}

    def show(self, i):
        """What does token id `i` actually mean, as text?"""
        if i in self.id_to_special:
            return self.id_to_special[i]
        return self.vocab[i].decode("utf-8", errors="replace")

    # ---------- using it ----------

    def _encode_word(self, word):
        ids = list(word.encode("utf-8"))
        while len(ids) >= 2:
            # apply the merges in the order we learned them, lowest id first
            pair = min(zip(ids, ids[1:]),
                       key=lambda p: self.merges.get(p, float("inf")))
            if pair not in self.merges:
                break
            ids = _merge(ids, pair, self.merges[pair])
        return ids

    def encode_plain(self, text):
        """BPE only. Assumes there are no special tokens in `text`."""
        out = []
        for word in SPLIT.findall(text):
            if word not in self._cache:
                self._cache[word] = self._encode_word(word)
            out.extend(self._cache[word])
        return out

    def encode(self, text):
        """The one you call. Handles special tokens and ordinary text."""
        out = []
        for part in SPECIAL_SPLIT.split(text):
            if not part:
                continue
            if part in self.special_to_id:
                out.append(self.special_to_id[part])
            else:
                out.extend(self.encode_plain(part))
        return out

    def decode(self, ids):
        """
        Ids back to text.

        We buffer the ordinary ids and decode them together, because a
        single BPE token can be half of a multi-byte character. Decoding
        one at a time would produce broken characters.
        """
        out, buffer = [], []
        for i in ids:
            if i in self.id_to_special:
                if buffer:
                    out.append(b"".join(self.vocab[j] for j in buffer)
                               .decode("utf-8", errors="replace"))
                    buffer = []
                out.append(self.id_to_special[i])
            else:
                buffer.append(i)
        if buffer:
            out.append(b"".join(self.vocab[j] for j in buffer)
                       .decode("utf-8", errors="replace"))
        return "".join(out)

    # ---------- saving ----------

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"merges": [[a, b, i] for (a, b), i in self.merges.items()],
                       "bpe_size": self.bpe_size,
                       "specials": SPECIALS}, f)

    def load_dict(self, d):
        self.merges = {(a, b): i for a, b, i in d["merges"]}
        self.bpe_size = d["bpe_size"]
        self.vocab = {i: bytes([i]) for i in range(256)}
        for (a, b), i in self.merges.items():
            self.vocab[i] = self.vocab[a] + self.vocab[b]
        self._finish()
        return self


def load_tokenizer(path):
    with open(path, encoding="utf-8") as f:
        return ChatTokenizer().load_dict(json.load(f))


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--vocab", type=int, default=2048)
    p.add_argument("--corpus", default="data/corpus.txt")
    p.add_argument("--out", default="data/tokenizer.json")
    args = p.parse_args()

    if not os.path.exists(args.corpus):
        raise SystemExit(f"{args.corpus} is missing. Run: python build_data2.py")

    text = open(args.corpus, encoding="utf-8").read()

    # ---------- DEMO 1: watch it invent code ----------
    print("=" * 62)
    print(f"TRAINING BPE on {len(text)/1024:.0f} KB, target vocab {args.vocab}")
    print("=" * 62)
    tok = ChatTokenizer()
    t0 = time.time()
    tok.train(text, vocab_size=args.vocab, verbose=True)
    print(f"  ... {args.vocab - 256} merges in {time.time() - t0:.1f} seconds")
    tok.save(args.out)
    print(f"  saved -> {args.out}")

    # ---------- DEMO 2: the specials really are single tokens ----------
    print("\n" + "=" * 62)
    print("SPECIAL TOKENS ARE ONE TOKEN EACH")
    print("=" * 62)
    for s in SPECIALS:
        print(f"  {s:15s} -> id {tok.special_to_id[s]}   (a single token)")
    print(f"  ordinary BPE ids run 0 .. {tok.bpe_size - 1}")
    print(f"  total vocab_size = {tok.vocab_size}")

    # ---------- DEMO 3: a real chat turn, tokenized ----------
    print("\n" + "=" * 62)
    print("A CHAT TURN, TOKEN BY TOKEN")
    print("=" * 62)
    sample = "<|user|>\nreverse a string\n<|assistant|>\nreturn s[::-1]\n<|end|>"
    ids = tok.encode(sample)
    print(f"  {len(sample)} characters -> {len(ids)} tokens")
    print("  " + " | ".join(tok.show(i) for i in ids).replace("\n", "\\n"))
    assert tok.decode(ids) == sample, "encode then decode must give back the original"
    print("\n  decode(encode(x)) == x   confirmed")

    # ---------- DEMO 4: how well does it compress? ----------
    print("\n" + "=" * 62)
    print("COMPRESSION - fewer tokens means longer answers fit in block_size")
    print("=" * 62)
    for label, piece in [("English", "the quick brown fox jumps over the lazy dog"),
                         ("Python ", "def reverse_string(s):\n    return s[::-1]"),
                         ("unseen ", "def quantum_flux(zz):\n    return zz ** 0.5")]:
        n = len(tok.encode(piece))
        print(f"  {label}  {len(piece):4d} chars -> {n:3d} tokens "
              f"({len(piece)/n:.2f} chars per token)")
    print("\n  The third line is code the tokenizer has never seen. It still")
    print("  encodes fine, just into more tokens - that is byte-level BPE")
    print("  doing its job. Nothing is ever out of vocabulary.")

    print("\n" + "=" * 62)
    print("next:  python pack4.py")

# NOTE:
# - vocab_size is a trade. Bigger vocab = fewer tokens per sentence = faster
#   training, but a bigger embedding table. 2048 is right for a 130 KB
#   vocabulary of Python and plain English. GPT-4 uses about 100,000.
# - Never renumber the specials after training. The ids are baked into the
#   checkpoint's embedding table, and shifting them silently corrupts every
#   answer the model gives.
# - The encode cache is why encoding 3.5 MB takes under a second: our text
#   is the same few thousand words over and over.
