"""
FILE 4: The Model — ARGPT itself
=================================
This is the file you came for.

A GPT is a stack of identical blocks. Each block does exactly two things:

    1. Attention — tokens look at each other and share information
    2. MLP       — each token thinks quietly about what it just heard

Repeat that N times, then guess the next token. That is a language model.
Everything else in this file is plumbing.

Three letters appear in every shape comment below:
    B = batch    how many sequences we process at once
    T = time     how many tokens in each sequence
    C = channels n_embd, the size of one token's vector

Run me:  python model4.py
"""

import math

import torch
import torch.nn as nn
from torch.nn import functional as F


class SelfAttention(nn.Module):
    """
    Every token does three things at once:
        query (q) — "here is what I am looking for"
        key   (k) — "here is what I am about"
        value (v) — "here is what I will tell you if you pick me"

    A token's query is compared against every other token's key. Good matches
    get a high score, and the token receives a blend of those tokens' values.

    "Causal" means a token may only look BACKWARD. It must never see the
    future, because when we generate text the future does not exist yet.
    """

    def __init__(self, cfg):
        super().__init__()
        assert cfg.n_embd % cfg.n_head == 0, "n_embd must divide evenly by n_head"
        self.n_head = cfg.n_head

        # one wide Linear produces q, k and v together in a single matmul
        self.qkv = nn.Linear(cfg.n_embd, 3 * cfg.n_embd)
        self.proj = nn.Linear(cfg.n_embd, cfg.n_embd)
        self.dropout = nn.Dropout(cfg.dropout)

        # a lower-triangular square of 1s. register_buffer = saved with the
        # model but never trained, because it is a rule, not a parameter.
        self.register_buffer("mask", torch.tril(torch.ones(cfg.block_size, cfg.block_size)))

    def forward(self, x):
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)          # each is (B, T, C)

        # split C across the heads -> (B, n_head, T, head_size)
        # every head gets its own slice and learns its own kind of relationship
        head_size = C // self.n_head
        q = q.view(B, T, self.n_head, head_size).transpose(1, 2)
        k = k.view(B, T, self.n_head, head_size).transpose(1, 2)
        v = v.view(B, T, self.n_head, head_size).transpose(1, 2)

        # ---------- THE ATTENTION FORMULA ----------
        # how well does each query match each key?
        att = (q @ k.transpose(-2, -1)) / math.sqrt(head_size)
        # blank out the future: -inf becomes 0 after softmax
        att = att.masked_fill(self.mask[:T, :T] == 0, float("-inf"))
        # turn raw scores into percentages that add up to 1
        att = F.softmax(att, dim=-1)
        att = self.dropout(att)
        # collect a weighted mix of everyone's values
        y = att @ v
        #
        # PyTorch ships a fused version of those four lines:
        #     y = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        # Identical maths, noticeably faster. We wrote it out so you can see it.
        # -------------------------------------------

        y = y.transpose(1, 2).reshape(B, T, C)         # glue the heads back together
        return self.dropout(self.proj(y))


class MLP(nn.Module):
    """
    Attention was tokens talking. This is one token thinking alone.

    Widen to 4x, apply a non-linearity, come back down. The 4x is not magic,
    it is just the ratio the original paper used and everyone kept.
    """

    def __init__(self, cfg):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(cfg.n_embd, 4 * cfg.n_embd),
            nn.GELU(),                                 # a smooth ReLU
            nn.Linear(4 * cfg.n_embd, cfg.n_embd),
            nn.Dropout(cfg.dropout),
        )

    def forward(self, x):
        return self.net(x)


class Block(nn.Module):
    """
    One transformer block: talk, then think.

    Notice `x = x + ...` instead of `x = ...`. That is a residual connection.
    Each block ADDS a small correction rather than replacing everything.
    Without it, deep networks simply refuse to train.

    LayerNorm comes BEFORE each part (pre-norm). It keeps the numbers in a
    sane range so training does not blow up.
    """

    def __init__(self, cfg):
        super().__init__()
        self.ln1 = nn.LayerNorm(cfg.n_embd)
        self.attn = SelfAttention(cfg)
        self.ln2 = nn.LayerNorm(cfg.n_embd)
        self.mlp = MLP(cfg)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))                 # talk to the other tokens
        x = x + self.mlp(self.ln2(x))                  # think about what you heard
        return x


class ARGPT(nn.Module):
    """The whole model. Roughly 100 lines above this point is all it took."""

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.tok_emb = nn.Embedding(cfg.vocab_size, cfg.n_embd)   # WHAT the token is
        self.pos_emb = nn.Embedding(cfg.block_size, cfg.n_embd)   # WHERE it sits
        self.drop = nn.Dropout(cfg.dropout)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layer)])
        self.ln_f = nn.LayerNorm(cfg.n_embd)
        self.head = nn.Linear(cfg.n_embd, cfg.vocab_size, bias=False)

        # Weight tying: the matrix that turns tokens INTO vectors is reused to
        # turn vectors BACK INTO tokens. Saves parameters and trains better.
        self.head.weight = self.tok_emb.weight

        self.apply(self._init_weights)

    def _init_weights(self, m):
        if isinstance(m, (nn.Linear, nn.Embedding)):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)
            if isinstance(m, nn.Linear) and m.bias is not None:
                nn.init.zeros_(m.bias)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        assert T <= self.cfg.block_size, f"sequence of {T} is longer than block_size"

        pos = torch.arange(T, device=idx.device)
        x = self.drop(self.tok_emb(idx) + self.pos_emb(pos))   # what + where

        for block in self.blocks:
            x = block(x)

        logits = self.head(self.ln_f(x))               # (B, T, vocab_size)

        if targets is None:                            # generating, no answer key
            return logits, None

        # cross_entropy wants a flat list, so squash B and T together.
        # It asks: how surprised was the model by the correct next token?
        loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss

    def num_params(self):
        return sum(p.numel() for p in self.parameters())


if __name__ == "__main__":
    # ---------- DEMO: build ARGPT and push one batch through it ----------
    from config import TINY

    cfg = TINY
    cfg.vocab_size = 65                                # Shakespeare, char level
    model = ARGPT(cfg)

    print("=" * 55)
    print(f"ARGPT: {cfg.n_layer} layers, {cfg.n_head} heads, {cfg.n_embd} dims")
    print(f"parameters: {model.num_params():,}")
    print("=" * 55)

    x = torch.randint(0, cfg.vocab_size, (2, cfg.block_size))   # fake batch
    logits, loss = model(x, targets=x)
    print(f"input   {tuple(x.shape)}   (B, T)")
    print(f"logits  {tuple(logits.shape)}   (B, T, vocab)  a score for every")
    print(f"                                possible next token, at every position")
    print(f"loss    {loss.item():.3f}")
    print(f"random guessing would be ln({cfg.vocab_size}) = "
          f"{math.log(cfg.vocab_size):.3f}, so an untrained model lands near there")

    # ---------- DEMO 2: SEE the causal mask ----------
    # The mask is the ONE thing that makes this a GPT: a token may look at
    # itself and everything before it, but never at the future. Here is the
    # actual buffer for the first 6 positions.  1 = allowed to look, 0 = blocked.
    print("\n" + "=" * 55)
    print("THE CAUSAL MASK - who is each token allowed to look at?")
    print("=" * 55)
    mask = model.blocks[0].attn.mask[:6, :6]
    print("       " + "".join(f" tok{j}" for j in range(6)))
    for i, row in enumerate(mask):
        print(f"  tok{i} " + "".join(f"    {int(v)}" for v in row))
    print("\nA triangle. Token 0 sees only itself. Token 5 sees everyone before")
    print("it. The 0s in the top-right corner are the future -- blocked.")

# NOTE:
# - Nothing here knows about English. It only learns which number tends to
#   follow which other numbers. Grammar is a side effect of doing that well.
# - The mask is the only thing making this a GPT instead of a BERT.
# - Loss is measured in nats. Lower means less surprised. 0 would be perfect.
