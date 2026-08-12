"""
FILE 5: The model - a 2024 transformer instead of a 2019 one
=============================================================
model4.py in the main session is a GPT-2. Correct, readable, and the right
thing to learn first. This is the same skeleton with the three swaps that
Llama and every model since actually made, plus the masked loss that
instruction tuning needs.

    LayerNorm            ->  RMSNorm      cheaper, works just as well
    learned positions    ->  RoPE         no parameters, understands distance
    GELU MLP             ->  SwiGLU       a gate on the hidden layer
    hand-written softmax ->  flash attn   same maths, 2-4x faster, less memory

modern_upgrades10.py showed you these side by side as a demo. Here they are
wired into a model that we are about to train for real.

WHAT IS NOT DIFFERENT
    Attention. Residuals. Predict the next token. The core you learned in
    model4.py is untouched, and that is the point worth making out loud:
    six years of progress changed the trimmings, not the idea.

THE ONE GENUINELY NEW THING: masked loss
    forward() takes a `mask` and scores only the tokens where it is 1.
    Look for it at the bottom of forward(). It is four lines and it is what
    turns "a model that continues text" into "a model that answers you".

Run me:  python model5.py
"""

import math
from dataclasses import dataclass

import torch
import torch.nn as nn
from torch.nn import functional as F


# ============================================================
# The control panel
# ============================================================

@dataclass
class Config:
    name: str = "laptop"

    # ---------- shape ----------
    block_size: int = 288      # our longest conversation is 265 tokens
    n_layer: int = 6
    n_head: int = 6
    n_embd: int = 384
    dropout: float = 0.05      # low: we WANT this model to memorise its curriculum
    vocab_size: int = 0        # filled in from the tokenizer by train6.py

    # ---------- training ----------
    batch_size: int = 24
    max_iters: int = 4000
    warmup: int = 200          # steps spent ramping the learning rate up
    eval_interval: int = 250
    eval_iters: int = 40
    learning_rate: float = 6e-4
    min_lr: float = 6e-5
    weight_decay: float = 0.1
    grad_clip: float = 1.0

    # ---------- where things live ----------
    data_dir: str = "data"
    out_dir: str = "out"


# One epoch of our dataset is about 150 steps, so max_iters/150 is roughly
# how many times the model reads the whole curriculum. 20 to 25 passes is
# where the code starts coming out reliably correct.

# A live demo you can run start to finish while talking. It genuinely
# answers the common questions and fumbles the rest, which is a useful
# thing for a class to see.
QUICK = Config(name="quick", n_layer=4, n_head=4, n_embd=256,
               batch_size=32, max_iters=1500, eval_interval=250)

# The practical default. ~11M parameters.
LAPTOP = Config(name="laptop", max_iters=3000)

# The one to demo with. ~26M parameters. Needs about 3.8 GB of VRAM at
# batch 32 - pass --batch 16 if your card is smaller.
BIG = Config(name="big", n_layer=8, n_head=8, n_embd=512,
             batch_size=32, max_iters=3500, learning_rate=5e-4,
             eval_interval=500)


# ============================================================
# 1. RMSNorm  (replaces LayerNorm)
# ============================================================

class RMSNorm(nn.Module):
    """
    LayerNorm centres the values then scales them. Somebody tried dropping
    the centring. Nothing got worse and it ran faster, so everyone dropped
    it. That is the whole innovation - one less mean to compute, and one
    less bias vector per norm.
    """

    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(dim))
        self.eps = eps

    def forward(self, x):
        rms = torch.rsqrt(x.float().pow(2).mean(-1, keepdim=True) + self.eps)
        return (x.float() * rms).type_as(x) * self.weight


# ============================================================
# 2. RoPE  (replaces learned position embeddings)
# ============================================================

def rope_tables(head_size, max_len, device, dtype=torch.float32):
    """
    Precompute the rotation angles once. They are not learned, so this is a
    buffer, not a parameter - it costs zero of the model's capacity.
    """
    freqs = 1.0 / (10000 ** (torch.arange(0, head_size, 2, device=device).float()
                             / head_size))
    angles = torch.outer(torch.arange(max_len, device=device).float(), freqs)
    return angles.cos().to(dtype), angles.sin().to(dtype)


def apply_rope(x, cos, sin):
    """
    model4.py said "position 5 gets learned vector number 5". RoPE instead
    ROTATES each token's vector by an angle set by its position.

    The payoff: when a query at position 8 meets a key at position 3, the
    two rotations partly cancel and what survives depends on the GAP, not
    on where the pair sits in the text. So the model learns about distance
    once and it means the same thing everywhere.
    """
    T = x.shape[-2]
    x1, x2 = x[..., ::2], x[..., 1::2]          # split each vector into pairs
    c = cos[:T].view(1, 1, T, -1)
    s = sin[:T].view(1, 1, T, -1)
    out = torch.stack([x1 * c - x2 * s, x1 * s + x2 * c], dim=-1)
    return out.flatten(-2)


# ============================================================
# 3. Attention, with the fused kernel
# ============================================================

class SelfAttention(nn.Module):
    """
    Identical idea to model4.py: query, key, value, look backwards only.

    The difference is the four hand-written lines

        att = (q @ k.transpose(-2,-1)) / sqrt(d)
        att = att.masked_fill(mask == 0, -inf)
        att = softmax(att)
        y   = att @ v

    are replaced by one call to F.scaled_dot_product_attention. Same maths,
    but PyTorch runs it as a single fused GPU kernel that never builds the
    full T x T attention matrix in memory. That matrix is what makes long
    contexts expensive, and not materialising it is why modern models can
    read 100,000 tokens.
    """

    def __init__(self, cfg):
        super().__init__()
        assert cfg.n_embd % cfg.n_head == 0, "n_embd must divide evenly by n_head"
        assert (cfg.n_embd // cfg.n_head) % 2 == 0, "head size must be even for RoPE"
        self.n_head = cfg.n_head
        self.head_size = cfg.n_embd // cfg.n_head
        self.dropout = cfg.dropout

        self.qkv = nn.Linear(cfg.n_embd, 3 * cfg.n_embd, bias=False)
        self.proj = nn.Linear(cfg.n_embd, cfg.n_embd, bias=False)
        self.resid_drop = nn.Dropout(cfg.dropout)

    def forward(self, x, cos, sin):
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)

        # (B, T, C) -> (B, n_head, T, head_size); every head gets its own slice
        q = q.view(B, T, self.n_head, self.head_size).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_size).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_size).transpose(1, 2)

        # rotate q and k by position. v is NOT rotated - only the matching
        # of queries to keys should care about distance, not the content.
        q = apply_rope(q, cos, sin)
        k = apply_rope(k, cos, sin)

        y = F.scaled_dot_product_attention(
            q, k, v,
            is_causal=True,                       # the triangle, done for us
            dropout_p=self.dropout if self.training else 0.0,
        )

        y = y.transpose(1, 2).reshape(B, T, C)    # glue the heads back together
        return self.resid_drop(self.proj(y))


# ============================================================
# 4. SwiGLU  (replaces the GELU MLP)
# ============================================================

class SwiGLU(nn.Module):
    """
    Our old MLP: widen, GELU, narrow.

    SwiGLU adds a second parallel path that acts as a per-neuron GATE. One
    path decides the content, the other decides how much of it gets through.

        old:     W2( gelu(W1 x) )
        swiglu:  W2( silu(W1 x) * W3 x )

    Three matrices instead of two, so the hidden size shrinks to about 2/3
    to keep the parameter count fair.
    """

    def __init__(self, cfg):
        super().__init__()
        hidden = 32 * round(cfg.n_embd * 8 / 3 / 32)     # nice round number
        self.gate = nn.Linear(cfg.n_embd, hidden, bias=False)
        self.up = nn.Linear(cfg.n_embd, hidden, bias=False)
        self.down = nn.Linear(hidden, cfg.n_embd, bias=False)
        self.drop = nn.Dropout(cfg.dropout)

    def forward(self, x):
        return self.drop(self.down(F.silu(self.gate(x)) * self.up(x)))


# ============================================================
# 5. One block, and the whole model
# ============================================================

class Block(nn.Module):
    """Talk to the other tokens, then think about what you heard."""

    def __init__(self, cfg):
        super().__init__()
        self.norm1 = RMSNorm(cfg.n_embd)
        self.attn = SelfAttention(cfg)
        self.norm2 = RMSNorm(cfg.n_embd)
        self.mlp = SwiGLU(cfg)

    def forward(self, x, cos, sin):
        x = x + self.attn(self.norm1(x), cos, sin)
        x = x + self.mlp(self.norm2(x))
        return x


class ARGPTCoder(nn.Module):

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.tok_emb = nn.Embedding(cfg.vocab_size, cfg.n_embd)
        self.drop = nn.Dropout(cfg.dropout)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layer)])
        self.norm_f = RMSNorm(cfg.n_embd)
        self.head = nn.Linear(cfg.n_embd, cfg.vocab_size, bias=False)

        # weight tying: the table that turns a token into a vector is reused
        # to turn a vector back into a token. Fewer parameters, better results.
        self.head.weight = self.tok_emb.weight

        # NOTE: no pos_emb. RoPE handles position, and it is not learned.
        self.register_buffer("cos", torch.zeros(1), persistent=False)
        self.register_buffer("sin", torch.zeros(1), persistent=False)
        self._rope_len = 0

        self.apply(self._init_weights)
        # The residual stream has 2 * n_layer things added into it. Shrinking
        # the output projections keeps its variance from growing with depth,
        # which is what stops deep models diverging in the first 100 steps.
        scale = 0.02 / math.sqrt(2 * cfg.n_layer)
        for name, param in self.named_parameters():
            if name.endswith("proj.weight") or name.endswith("down.weight"):
                nn.init.normal_(param, mean=0.0, std=scale)

    def _init_weights(self, m):
        if isinstance(m, (nn.Linear, nn.Embedding)):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)
            if isinstance(m, nn.Linear) and m.bias is not None:
                nn.init.zeros_(m.bias)

    def _rope(self, T, device, dtype):
        """Build the rotation tables the first time, then reuse them."""
        if self._rope_len < T or self.cos.device != device:
            length = max(T, self.cfg.block_size)
            cos, sin = rope_tables(self.cfg.n_embd // self.cfg.n_head,
                                   length, device, dtype)
            self.cos, self.sin = cos, sin
            self._rope_len = length
        return self.cos[:T], self.sin[:T]

    def forward(self, idx, targets=None, mask=None):
        B, T = idx.shape
        x = self.drop(self.tok_emb(idx))
        cos, sin = self._rope(T, idx.device, x.dtype)

        for block in self.blocks:
            x = block(x, cos, sin)
        x = self.norm_f(x)

        if targets is None:
            # generating: only the LAST position can say anything new, so
            # do not pay for a full vocab projection at all T positions
            return self.head(x[:, -1:, :]), None

        logits = self.head(x)

        # ---------- THE MASKED LOSS ----------
        # reduction="none" gives us one loss number per token instead of an
        # average, so we can throw away the ones we do not want.
        per_token = F.cross_entropy(
            logits.view(-1, logits.size(-1)), targets.reshape(-1), reduction="none")

        if mask is None:
            return logits, per_token.mean()

        keep = mask.reshape(-1)
        # average over the SCORED tokens only. Dividing by keep.sum() and not
        # by the total makes the number comparable between batches, whatever
        # the mix of question and answer lengths happens to be.
        loss = (per_token * keep).sum() / keep.sum().clamp(min=1.0)
        return logits, loss
        # -------------------------------------

    def num_params(self):
        return sum(p.numel() for p in self.parameters())


if __name__ == "__main__":
    # ---------- DEMO 1: how big is each preset? ----------
    print("=" * 62)
    print("THE THREE PRESETS")
    print("=" * 62)
    for cfg in (QUICK, LAPTOP, BIG):
        cfg.vocab_size = 2052
        model = ARGPTCoder(cfg)
        print(f"  {cfg.name:7s} {cfg.n_layer} layers x {cfg.n_embd:4d} dims "
              f"x {cfg.n_head} heads -> {model.num_params()/1e6:5.1f}M parameters")

    # ---------- DEMO 2: push a batch through and see the masked loss ----------
    print("\n" + "=" * 62)
    print("THE MASK, MEASURED")
    print("=" * 62)
    cfg = QUICK
    model = ARGPTCoder(cfg)
    x = torch.randint(0, cfg.vocab_size, (4, 64))
    y = torch.randint(0, cfg.vocab_size, (4, 64))

    _, all_tokens = model(x, y)                       # score everything
    mask = torch.zeros(4, 64)
    mask[:, 40:] = 1                                  # score only the "answer"
    _, answer_only = model(x, y, mask)

    print(f"  loss over all 64 positions   : {all_tokens.item():.4f}")
    print(f"  loss over the last 24 only   : {answer_only.item():.4f}")
    print(f"  random guessing would be ln({cfg.vocab_size}) = "
          f"{math.log(cfg.vocab_size):.3f}")
    print("\n  Both land near the random-guess line because the weights are")
    print("  random. The point is that they are DIFFERENT numbers: the mask")
    print("  really is changing which tokens the gradient comes from.")

    # ---------- DEMO 3: RoPE costs nothing ----------
    print("\n" + "=" * 62)
    print("WHAT RoPE SAVED US")
    print("=" * 62)
    learned = LAPTOP.block_size * LAPTOP.n_embd
    print(f"  model4.py's learned positions : {learned:,} trainable parameters")
    print(f"  RoPE                          : 0 trainable parameters")
    print("  and RoPE keeps working past block_size, which learned")
    print("  embeddings physically cannot.")

    # ---------- DEMO 4: variable width batches are fine ----------
    print("\n" + "=" * 62)
    print("DYNAMIC WIDTH - the model does not care how wide the batch is")
    print("=" * 62)
    for T in (32, 96, 185, 288):
        out, _ = model(torch.randint(0, cfg.vocab_size, (2, T)))
        print(f"  T={T:3d}  ->  logits {tuple(out.shape)}   "
              f"(only the last position, because we are generating)")
    print("\n  That is what lets pack4.py trim each batch to its longest real")
    print("  row. With learned position embeddings this still works, but RoPE")
    print("  is what makes it free.")

    print("\n" + "=" * 62)
    print("next:  python train6.py")

# NOTE:
# - dropout is 0.05, much lower than the 0.1 in the main session. We are
#   deliberately teaching this model a fixed curriculum and we WANT it to
#   memorise the code. Overfitting is the goal here, not the enemy.
# - is_causal=True in scaled_dot_product_attention is the whole causal mask.
#   Delete it and you have built a BERT.
# - The padding at the end of each row is harmless: a token can only look
#   backwards, and the padding is always at the end, so no real token ever
#   sees a <|pad|>.
