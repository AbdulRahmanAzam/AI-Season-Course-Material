"""
FILE 10: Bonus — what Llama 3 and GPT-4 changed
================================================
model4.py is a GPT-2, which is 2019 architecture. It is the right thing to
learn first because every piece has an obvious explanation.

Modern models kept the exact same skeleton -- attention, MLP, residuals --
and swapped three parts. This file shows all three side by side with what
we used. Each one is small. None of them change what the model DOES.

    LayerNorm          ->  RMSNorm       (cheaper)
    learned positions  ->  RoPE          (generalises to longer text)
    GELU MLP           ->  SwiGLU        (works better, same cost)

Run me:  python modern_upgrades10.py
"""

import torch
import torch.nn as nn
from torch.nn import functional as F


# ============================================================
# 1. RMSNorm  replaces  LayerNorm
# ============================================================

class RMSNorm(nn.Module):
    """
    LayerNorm does two things: centre the values (subtract the mean), then
    scale them (divide by the standard deviation).

    Somebody tried removing the centring step. Nothing got worse and it ran
    faster. So everyone dropped it. That is the entire innovation.

        LayerNorm: (x - mean) / std * weight + bias
        RMSNorm:   x / sqrt(mean(x^2)) * weight
    """

    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(dim))
        self.eps = eps

    def forward(self, x):
        rms = torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps)
        return x * rms * self.weight


# ============================================================
# 2. RoPE  replaces  learned position embeddings
# ============================================================

def rope_tables(head_size, max_len, device="cpu"):
    """Precompute the rotation angles once, reuse them forever."""
    # low dimensions rotate fast, high dimensions rotate slowly -- so the
    # pattern of angles is unique for every position, like clock hands
    freqs = 1.0 / (10000 ** (torch.arange(0, head_size, 2, device=device) / head_size))
    angles = torch.outer(torch.arange(max_len, device=device), freqs)
    return angles.cos(), angles.sin()


def apply_rope(x, cos, sin):
    """
    model4.py said "position 5 gets vector #5", learned from scratch.
    RoPE instead ROTATES each token's vector by an angle based on its
    position. Nothing is learned and nothing is stored.

    The trick: when a query at position 8 meets a key at position 3, the
    rotations partly cancel and what survives depends on the GAP (5), not
    on the absolute positions. So the model learns about distance, and a
    gap of 5 means the same thing at position 3000 as at position 30.

    That is why modern models handle long context and ours cannot go past
    block_size.
    """
    B, H, T, D = x.shape
    x1, x2 = x[..., ::2], x[..., 1::2]            # split into pairs
    c, s = cos[:T].view(1, 1, T, -1), sin[:T].view(1, 1, T, -1)
    # rotate each pair like a point on a circle
    out = torch.stack([x1 * c - x2 * s, x1 * s + x2 * c], dim=-1)
    return out.flatten(-2)


# ============================================================
# 3. SwiGLU  replaces  the GELU MLP
# ============================================================

class SwiGLU(nn.Module):
    """
    Our MLP: widen -> GELU -> narrow.

    SwiGLU adds a second parallel path that acts as a GATE. One path decides
    the content, the other decides how much of it gets through, per neuron.

        ours:   W2( gelu(W1 x) )
        swiglu: W2( silu(W1 x) * W3 x )

    It costs a third matrix, so the hidden size is shrunk to about 2/3 to
    keep the parameter count fair. Slightly better results for the same size.
    """

    def __init__(self, dim, hidden=None):
        super().__init__()
        hidden = hidden or int(dim * 8 / 3)       # 4 * 2/3, keeps params equal
        self.gate = nn.Linear(dim, hidden, bias=False)
        self.up = nn.Linear(dim, hidden, bias=False)
        self.down = nn.Linear(hidden, dim, bias=False)

    def forward(self, x):
        return self.down(F.silu(self.gate(x)) * self.up(x))


if __name__ == "__main__":
    B, H, T, D, C = 2, 4, 16, 32, 128

    # ---------- DEMO 1: RMSNorm is cheaper, same job ----------
    print("=" * 55)
    x = torch.randn(B, T, C)
    ln, rms = nn.LayerNorm(C), RMSNorm(C)
    print(f"LayerNorm parameters: {sum(p.numel() for p in ln.parameters())}  (weight + bias)")
    print(f"RMSNorm   parameters: {sum(p.numel() for p in rms.parameters())}  (weight only)")
    print(f"both keep the shape:  {tuple(ln(x).shape)} -> {tuple(rms(x).shape)}")

    # ---------- DEMO 2: RoPE stores nothing ----------
    print("\n" + "=" * 55)
    q = torch.randn(B, H, T, D)
    cos, sin = rope_tables(D, max_len=512)
    print(f"learned position embeddings: {512 * C:,} trainable parameters")
    print(f"RoPE:                        0 trainable parameters")
    print(f"same shape out:              {tuple(apply_rope(q, cos, sin).shape)}")

    # ---------- DEMO 3: SwiGLU vs our MLP, matched size ----------
    print("\n" + "=" * 55)
    ours = nn.Sequential(nn.Linear(C, 4 * C), nn.GELU(), nn.Linear(4 * C, C))
    new = SwiGLU(C)
    print(f"our GELU MLP: {sum(p.numel() for p in ours.parameters()):,} parameters")
    print(f"SwiGLU:       {sum(p.numel() for p in new.parameters()):,} parameters")
    print("roughly the same budget, three matrices instead of two")

# NOTE:
# - Want to try these? In model4.py swap nn.LayerNorm for RMSNorm and the MLP
#   for SwiGLU. Both are drop-in. RoPE needs edits inside SelfAttention.
# - On a model this small you will barely see a difference. These wins matter
#   at billions of parameters and 100k token contexts.
# - Notice what did NOT change: attention, residuals, the training loop, the
#   next-token objective. The core you learned in model4.py is still the core.
