"""Slides 39-76: model4.py (the transformer), train5.py, generate6.py."""

from pptx.enum.text import PP_ALIGN
from theme import (BODY_TOP, CW, GRAY, GRAY_LT, INK, LINE, M, ORANGE, ORANGE_DK,
                   TINT, TINT2, WHITE, arrow, box, bullets, chip, code, divider,
                   grid, heading, label, para, rule, slide, table, twocol)


def build(prs):
    # ================================================================ FILE 4
    divider(prs, 4, "model4.py", "The transformer itself — the file you came for",
            ["A GPT is a stack of identical blocks: attention, then MLP",
             "Q, K, V, the attention formula written out by hand, and the causal mask",
             "About 130 lines. Nothing in it knows what English is."])

    # ---------------------------------------------------------------- 40
    s = slide(prs, "model4.py", "The whole forward pass, on one slide")
    y = BODY_TOP + 0.05
    cx = M + 0.25
    bw = 3.5

    chip(s, cx, y, bw, 0.5, "idx  (B, T)", sub="a batch of token ids", fill=WHITE, size=12.5)
    arrow(s, cx + bw / 2 - 0.1, y + 0.56, 0.2, 0.3, right=False)
    chip(s, cx, y + 0.92, bw, 0.62, "tok_emb(idx)  +  pos_emb(pos)",
         sub="WHAT the token is  +  WHERE it sits", fill=TINT, size=12.5)
    arrow(s, cx + bw / 2 - 0.1, y + 1.6, 0.2, 0.3, right=False)
    chip(s, cx, y + 1.96, bw, 0.5, "x  (B, T, C)", fill=WHITE, size=12.5)
    arrow(s, cx + bw / 2 - 0.1, y + 2.52, 0.2, 0.3, right=False)
    chip(s, cx, y + 2.88, bw, 0.85, "Block 1 → Block 2 → … → Block N",
         sub="each: attention, then MLP, both with residuals", fill=TINT, size=12.5)
    arrow(s, cx + bw / 2 - 0.1, y + 3.79, 0.2, 0.3, right=False)
    chip(s, cx, y + 4.15, bw, 0.5, "ln_f  →  head  (C → vocab)", fill=WHITE, size=12)
    arrow(s, cx + bw / 2 - 0.1, y + 4.71, 0.2, 0.28, right=False)
    chip(s, cx, y + 5.05, bw, 0.42, "logits  (B, T, vocab)", fill=ORANGE, edge=None,
         color=WHITE, size=12.5)

    x2 = M + 4.25
    w2 = CW - 4.25
    heading(s, x2, BODY_TOP, w2, "Three letters, everywhere in this file")
    table(s, x2, BODY_TOP + 0.32, w2, [
        ["", "Means", "TINY", "SMALL"],
        ["**B**", "batch — how many sequences at once", "32", "64"],
        ["**T**", "time — how many tokens per sequence (≤ block_size)", "128", "256"],
        ["**C**", "channels — n_embd, the size of one token's vector", "128", "384"],
    ], widths=[0.6, 5.2, 1.0, 1.1], size=11.5, row_h=0.46)

    heading(s, x2, BODY_TOP + 2.15, w2, "What the output actually is")
    para(s, x2, BODY_TOP + 2.5, w2, 1.2,
         "`logits` is a raw score for **every possible next token**, at **every position**, "
         "simultaneously. With B=32, T=128, vocab=65 that is 32 × 128 × 65 = **266,240 numbers "
         "per forward pass** — and 4,096 of them are real predictions we can score.", 12.5)

    box(s, x2, BODY_TOP + 3.8, w2, 1.5, "Say this out loud",
        ["A GPT is a stack of identical blocks. Each block does two things: **attention** (tokens "
         "look at each other and share information) and **MLP** (each token thinks quietly about "
         "what it just heard). Repeat N times, then guess. **Everything else in the file is "
         "plumbing.**"])

    # ---------------------------------------------------------------- 41
    s = slide(prs, "model4.py  ·  embeddings", "What the token is, plus where it sits")
    code(s, M, BODY_TOP, 7.2, 1.85, [
        "self.tok_emb = nn.Embedding(cfg.vocab_size, cfg.n_embd)   # WHAT",
        "self.pos_emb = nn.Embedding(cfg.block_size, cfg.n_embd)   # WHERE",
        "",
        "pos = torch.arange(T, device=idx.device)",
        "x = self.drop(self.tok_emb(idx) + self.pos_emb(pos))",
    ], size=11.5)

    y = BODY_TOP + 2.0
    heading(s, M, y, CW, "An nn.Embedding is a lookup table, nothing more")
    cell = 0.6
    grid(s, M + 0.9, y + 0.4, cell, [["3", "5", "4"]], texts=[["3", "5", "4"]],
         size=12, head_rows=["ids"], fills=[[WHITE] * 3])
    arrow(s, M + 2.85, y + 0.5, 0.45, 0.24)
    rows = [["0.31", "-1.2", "0.04", "…"], ["0.88", "0.15", "-0.7", "…"], ["-0.2", "0.44", "1.1", "…"]]
    grid(s, M + 3.5, y + 0.4, 0.7, rows, texts=rows, size=9.5, fills=[[TINT] * 4] * 3)
    label(s, M + 6.4, y + 0.45, 1.9,
          "← row 3\n← row 5\n← row 4", 11, GRAY, PP_ALIGN.LEFT)
    label(s, M + 3.5, y + 2.6, 2.8, "n_embd wide, learned", 10.5, ORANGE_DK)

    x2 = M + 7.55
    w2 = CW - 7.55
    heading(s, x2, BODY_TOP, w2, "Why position has to be added at all")
    para(s, x2, BODY_TOP + 0.32, w2, 1.5,
         "Attention is a **weighted sum** — sums have no order. Without `pos_emb`, "
         "*“dog bites man”* and *“man bites dog”* are literally the same input. "
         "We add position information in by hand.", 12.5)

    box(s, x2, BODY_TOP + 1.9, w2, 1.75, "Weight tying — a free win",
        ["`self.head.weight = self.tok_emb.weight`",
         "The matrix that turns tokens **into** vectors is reused to turn vectors **back into** "
         "token scores. It saves `vocab × n_embd` parameters and empirically trains better — "
         "the two jobs are inverses, so they should share a map."])

    # ---------------------------------------------------------------- 42
    s = slide(prs, "model4.py  ·  Q, K, V", "The three vectors every token produces")
    y = BODY_TOP
    xw = (CW - 0.8) / 3
    for i, (letter, name, quote, detail) in enumerate([
        ("q", "query", "“here is what I am looking for”",
         "A token in the middle of a quotation might be querying for “who opened this quote?”"),
        ("k", "key", "“here is what I am about”",
         "An opening quote mark advertises itself as exactly that."),
        ("v", "value", "“here is what I will tell you if you pick me”",
         "The actual information that gets copied over, which need not equal the key."),
    ]):
        x = M + i * (xw + 0.4)
        chip(s, x, y, xw, 0.62, f"{letter}   —   {name}", fill=ORANGE, edge=None,
             color=WHITE, size=15)
        box(s, x, y + 0.75, xw, 1.55, None, [f"~~{quote}~~", detail], size=12, fill=TINT)

    y = BODY_TOP + 2.55
    para(s, M, y, CW, 0.55,
         "A token's **query** is compared against every token's **key**. Good matches score high, "
         "and the token receives a **blend of those tokens' values**. That is the entire mechanism "
         "by which information moves between positions.", 13.5)

    code(s, M, y + 0.75, CW, 1.9, [
        "self.qkv  = nn.Linear(cfg.n_embd, 3 * cfg.n_embd)   # one wide matmul makes all three",
        "self.proj = nn.Linear(cfg.n_embd, cfg.n_embd)",
        "",
        "q, k, v = self.qkv(x).split(C, dim=2)               # each is (B, T, C)",
    ], size=12, title="ONE LINEAR, NOT THREE — WHY?")

    para(s, M, y + 2.8, CW, 0.5,
         "Three separate `(C → C)` layers would be mathematically identical. One `(C → 3C)` layer "
         "is **one** matrix multiply instead of three, which is meaningfully faster on a GPU — "
         "kernel launches are expensive. `.split(C, dim=2)` then chops the result into thirds.", 12.5)

    # ---------------------------------------------------------------- 43
    s = slide(prs, "model4.py  ·  multi-head", "Reshaping C into parallel heads, and back again")
    code(s, M, BODY_TOP, CW, 1.85, [
        "head_size = C // self.n_head                                  # 128 // 4 = 32",
        "q = q.view(B, T, self.n_head, head_size).transpose(1, 2)      # (B, 4, T, 32)",
        "...",
        "y = y.transpose(1, 2).reshape(B, T, C)                        # glue heads back: (B, T, 128)",
    ], size=11.5)

    y = BODY_TOP + 2.15
    steps = [("(B, T, 128)", "one wide vector\nper token"),
             (".view(B, T, 4, 32)", "same numbers,\nregrouped into 4"),
             (".transpose(1, 2)", "(B, 4, T, 32)\nheads become a\nbatch dimension"),
             ("attention runs\n4 times in parallel", "each head sees\nonly its 32 numbers"),
             (".reshape(B, T, 128)", "concatenated\nback together")]
    xw = 2.15
    gapw = 0.35
    x = M + 0.35
    for i, (a, b) in enumerate(steps):
        chip(s, x, y, xw, 0.85, a, size=11.5, fill=TINT if i in (2, 3) else WHITE)
        label(s, x, y + 0.95, xw, b, 10.5, GRAY)
        if i < 4:
            arrow(s, x + xw + 0.03, y + 0.32, gapw - 0.06, 0.2)
        x += xw + gapw

    y = BODY_TOP + 3.7
    bullets(s, M, y, CW, 1.5, [
        "**No parameters are added.** The same 128 numbers are simply grouped 4 ways. `n_head` "
        "changes *how the model is allowed to organise its attention*, not how big it is.",
        "Putting heads in the **batch dimension** is why this is fast: PyTorch runs all 4 heads as "
        "one batched matmul, not a Python loop.",
        "Each head learns a different relationship. In real trained models people have found heads "
        "that track matching brackets, subject→verb agreement, and “copy the previous occurrence "
        "of this token”.",
    ], size=13, gap=10)

    # ---------------------------------------------------------------- 44
    s = slide(prs, "model4.py  ·  the attention formula", "Four lines. This is the whole transformer.")
    code(s, M, BODY_TOP, CW, 2.15, [
        "att = (q @ k.transpose(-2, -1)) / math.sqrt(head_size)   # 1. match every query to every key",
        "att = att.masked_fill(self.mask[:T,:T] == 0, -inf)       # 2. blank out the FUTURE",
        "att = F.softmax(att, dim=-1)                             # 3. scores -> % that sum to 1",
        "att = self.dropout(att)                                  #    regularise",
        "y   = att @ v                                            # 4. collect a weighted mix of values",
    ], size=11.5)

    y = BODY_TOP + 2.45
    xw = (CW - 1.2) / 4
    for i, (n, t, sub) in enumerate([
        ("1", "SCORE", "every query dot every key\n(T × T numbers per head)"),
        ("2", "MASK", "future positions → −∞\nso softmax makes them 0"),
        ("3", "SOFTMAX", "each row now sums to 1.0\n“how much attention, in %”"),
        ("4", "GATHER", "weighted average of values\nthe information actually moves"),
    ]):
        x = M + i * (xw + 0.4)
        chip(s, x, y, 0.55, 0.55, n, fill=ORANGE, edge=None, color=WHITE, size=15)
        label(s, x + 0.7, y + 0.06, xw - 0.7, t, 13.5, INK, PP_ALIGN.LEFT)
        label(s, x, y + 0.72, xw, sub, 11, GRAY, PP_ALIGN.LEFT)

    box(s, M, y + 1.55, CW, 1.15, "For the sharp student who asks about speed",
        ["Those four lines are mathematically identical to PyTorch's fused "
         "`F.scaled_dot_product_attention(q, k, v, is_causal=True)`, which is what you would ship. "
         "It never materialises the T×T matrix in memory. **We wrote it out longhand so you can see "
         "it — that is the only reason.**"])

    # ---------------------------------------------------------------- 45
    s = slide(prs, "Dry run 1  ·  the scores", "Four tokens, one head, head_size = 2")
    heading(s, M, BODY_TOP, CW, "The setup — hand-picked numbers so the arithmetic is visible")
    code(s, M, BODY_TOP + 0.32, CW, 1.35, [
        "tokens:   1 \"the\"        2 \"cat\"        3 \"sat\"        4 \"on\"",
        "q:        [1, 0]         [0, 1]         [1, 1]         [ 1, -1]",
        "k:        [1, 0]         [0, 1]         [1, 1]         [-1,  1]",
        "v:        [1, 0]         [0, 1]         [1, 1]         [ 2,  0]",
    ], size=12)

    y = BODY_TOP + 2.0
    heading(s, M, y, CW, "Step 1 — q @ kᵀ : every query dotted with every key")
    cell = 0.68
    raw = [["1", "0", "1", "-1"], ["0", "1", "1", "1"], ["1", "1", "2", "0"], ["1", "-1", "0", "-2"]]
    grid(s, M + 1.05, y + 0.55, cell, raw, texts=raw, size=12,
         head_cols=["k:the", "k:cat", "k:sat", "k:on"],
         head_rows=["q:the", "q:cat", "q:sat", "q:on"])

    arrow(s, M + 4.2, y + 1.5, 0.6, 0.3)
    label(s, M + 3.95, y + 1.9, 1.1, "÷ √2\n= 1.414", 10.5, ORANGE_DK)

    sc = [["0.71", "0.00", "0.71", "-0.71"], ["0.00", "0.71", "0.71", "0.71"],
          ["0.71", "0.71", "1.41", "0.00"], ["0.71", "-0.71", "0.00", "-1.41"]]
    grid(s, M + 5.35, y + 0.55, cell, sc, texts=sc, size=10)

    label(s, M + 8.4, y + 0.7, 4.0,
          "Read row 3: token “sat” matches\n“sat” best (1.41), then “the” and\n“cat” equally (0.71), "
          "and “on”\nnot at all (0.00).", 12, INK, PP_ALIGN.LEFT)
    label(s, M + 8.4, y + 2.05, 4.0,
          "Nothing has been blocked yet.\nRight now token 1 can see token 4 —\n"
          "**that is the future, and it is cheating.**", 12, ORANGE_DK, PP_ALIGN.LEFT)

    # ---------------------------------------------------------------- 46
    s = slide(prs, "Dry run 2  ·  mask, then softmax", "Where the future gets deleted")
    y = BODY_TOP
    cell = 0.68
    heading(s, M, y, CW, "Step 2 — masked_fill(mask == 0, −inf)")
    msk = [["0.71", "−inf", "−inf", "−inf"], ["0.00", "0.71", "−inf", "−inf"],
           ["0.71", "0.71", "1.41", "−inf"], ["0.71", "-0.71", "0.00", "-1.41"]]
    fills = [[WHITE if c <= r else INK for c in range(4)] for r in range(4)]
    grid(s, M + 1.05, y + 0.5, cell, msk, texts=msk, size=9.5, fills=fills,
         head_cols=["the", "cat", "sat", "on"], head_rows=["the", "cat", "sat", "on"])

    arrow(s, M + 4.2, y + 1.4, 0.6, 0.3)
    label(s, M + 3.95, y + 1.8, 1.1, "softmax\nper row", 10.5, ORANGE_DK)

    heading(s, M + 5.35, y, 6.0, "Step 3 — softmax turns each row into percentages")
    sm = [["1.00", "0", "0", "0"], ["0.33", "0.67", "0", "0"],
          ["0.25", "0.25", "0.50", "0"], ["0.54", "0.13", "0.27", "0.06"]]
    sf = [[TINT2 if c <= r else INK for c in range(4)] for r in range(4)]
    grid(s, M + 5.35, y + 0.5, cell, sm, texts=sm, size=10, fills=sf)

    label(s, M + 8.5, y + 0.6, 3.9,
          "**e^(−inf) = 0.** The future does not\njust score low — it scores exactly\nzero. It cannot "
          "leak.", 12, INK, PP_ALIGN.LEFT)
    label(s, M + 8.5, y + 1.65, 3.9,
          "Every row sums to **1.00**. Token 1\nhas no choice but to attend 100%\nto itself.",
          12, GRAY, PP_ALIGN.LEFT)

    y = BODY_TOP + 3.4
    heading(s, M, y, CW, "Where row 3 came from — the arithmetic, in full")
    code(s, M, y + 0.32, CW, 1.35, [
        "row 3 scores after mask:   [0.71, 0.71, 1.41, -inf]",
        "e^x:                       [2.03, 2.03, 4.11, 0.00]      sum = 8.17",
        "divide by the sum:         [0.25, 0.25, 0.50, 0.00]      <- 25% / 25% / 50% / nothing",
    ], size=12)

    # ---------------------------------------------------------------- 47
    s = slide(prs, "Dry run 3  ·  gathering the values", "att @ v — where information actually moves")
    y = BODY_TOP
    cell = 0.68
    heading(s, M, y, 5.0, "attention weights")
    sm = [["1.00", "0", "0", "0"], ["0.33", "0.67", "0", "0"],
          ["0.25", "0.25", "0.50", "0"], ["0.54", "0.13", "0.27", "0.06"]]
    sf = [[TINT2 if c <= r else INK for c in range(4)] for r in range(4)]
    grid(s, M + 1.05, y + 0.45, cell, sm, texts=sm, size=10, fills=sf,
         head_rows=["the", "cat", "sat", "on"])

    label(s, M + 4.0, y + 1.35, 0.6, "@", 18, ORANGE)

    heading(s, M + 4.75, y, 2.5, "values")
    vv = [["1", "0"], ["0", "1"], ["1", "1"], ["2", "0"]]
    grid(s, M + 4.75, y + 0.45, cell, vv, texts=vv, size=12, fills=[[WHITE] * 2] * 4)

    label(s, M + 6.35, y + 1.35, 0.6, "=", 18, ORANGE)

    heading(s, M + 7.1, y, 3.0, "output y")
    yy = [["1.00", "0.00"], ["0.33", "0.67"], ["0.75", "0.75"], ["0.93", "0.40"]]
    grid(s, M + 7.1, y + 0.45, cell, yy, texts=yy, size=10, fills=[[TINT] * 2] * 4)

    label(s, M + 8.9, y + 0.5, 3.6,
          "Token 1 got only itself back.", 11.5, GRAY, PP_ALIGN.LEFT)
    label(s, M + 8.9, y + 1.2, 3.6,
          "Token 3 is now a blend:\n25% “the” + 25% “cat” + 50% itself.", 11.5, GRAY, PP_ALIGN.LEFT)
    label(s, M + 8.9, y + 2.15, 3.6,
          "**That blend is the information\ntransfer.** Nothing else in the\nmodel moves data between\n"
          "positions.", 11.5, INK, PP_ALIGN.LEFT)

    y = BODY_TOP + 3.45
    code(s, M, y, CW, 1.05, [
        "y[3] = 0.25 x [1,0]  +  0.25 x [0,1]  +  0.50 x [1,1]  +  0 x [2,0]  =  [0.75, 0.75]",
    ], size=12.5, title="ROW 3, WORKED OUT")
    para(s, M, y + 1.25, CW, 0.55,
         "Then `self.proj(y)` mixes the heads' outputs back together and `self.dropout` regularises "
         "— and that is `SelfAttention.forward` finished.", 12.5, GRAY)

    # ---------------------------------------------------------------- 48
    s = slide(prs, "Why divide by √head_size?",
              "The one line that stops training from stalling")
    para(s, M, BODY_TOP, CW, 0.45,
         "Dot products of two `head_size`-dimensional vectors grow with the dimension. Big scores "
         "make softmax **saturate** — one weight ≈ 1, the rest ≈ 0 — and a flat softmax has almost "
         "no gradient. Training stops.", 13)

    y = BODY_TOP + 0.75
    table(s, M, y, 7.0, [
        ["head_size", "typical |q·k|", "std of scores", "after ÷ √d"],
        ["2", "1.0", "1.44", "**1.02**"],
        ["64", "6.4", "7.94", "**0.99**"],
        ["512", "18.6", "23.29", "**1.03**"],
    ], widths=[1.3, 1.6, 1.6, 1.5], size=11.5, row_h=0.42)
    label(s, M, y + 2.0, 7.0, "measured over 4,000 random vector pairs — the scale factor "
                              "holds the spread at ~1 no matter the dimension", 10.5, GRAY)

    x2 = M + 7.4
    w2 = CW - 7.4
    heading(s, x2, y, w2, "What saturation looks like")
    code(s, x2, y + 0.32, w2, 1.9, [
        "scores  [3.0, 1.0, 0.5, 0.2]",
        "",
        "unscaled  -> [1.00, 0.00, 0.00, 0.00]",
        "scaled    -> [0.78, 0.11, 0.06, 0.05]",
    ], size=11)
    para(s, x2, y + 2.35, w2, 1.0,
         "Unscaled, the model attends 100% to one token and **learns nothing about the others** — "
         "their gradient is zero.", 12)

    y = BODY_TOP + 3.35
    bullets(s, M, y, CW, 1.6, [
        "This is a genuinely great exam question, and the answer is one sentence: "
        "**√d keeps the variance of the scores at ~1 so softmax stays soft and gradients keep flowing.**",
        "It is also why `head_size` is usually kept at 64 in real models even as `n_embd` grows to "
        "thousands — you add **more heads**, not fatter ones.",
    ], size=13.5, gap=11)

    # ---------------------------------------------------------------- 49
    s = slide(prs, "The causal mask", "The single line that makes this a GPT")
    code(s, M, BODY_TOP, 6.5, 1.25, [
        "self.register_buffer(\"mask\",",
        "    torch.tril(torch.ones(cfg.block_size, cfg.block_size)))",
    ], size=11.5)

    y = BODY_TOP + 1.35
    heading(s, M, y, 6.5, "torch.tril — a lower triangle of 1s.  1 = may look, 0 = blocked")
    cell = 0.5
    n = 6
    rows = [[1 if c <= r else 0 for c in range(n)] for r in range(n)]
    fills = [[TINT2 if c <= r else INK for c in range(n)] for r in range(n)]
    texts = [[str(v) for v in row] for row in rows]
    grid(s, M + 1.15, y + 0.68, cell, rows, fills=fills, texts=texts, size=10,
         head_cols=[f"tok{j}" for j in range(n)],
         head_rows=[f"tok {i}" for i in range(n)])
    label(s, M + 1.15, y + 0.68 + n * cell + 0.15, n * cell,
          "a triangle", 11, ORANGE_DK)

    x2 = M + 6.9
    w2 = CW - 6.9
    bullets(s, x2, BODY_TOP, w2, 2.6, [
        "`register_buffer` = saved with the model, moved to the GPU with it, but **never trained**. "
        "It is a rule, not a parameter.",
        "Token 0 sees only itself. Token 7 sees everyone before it. The zeros in the top-right "
        "corner are **the future**.",
        "`masked_fill(mask == 0, -inf)` — and `e^(−inf) = 0`, so after softmax those weights are "
        "exactly zero. Not small. **Zero.**",
    ], size=12.5, gap=10)

    box(s, x2, BODY_TOP + 2.9, w2, 1.8, "Why “causal”?",
        ["Because when we **generate**, the future does not exist yet. Training must match that "
         "exactly: predicting token 5 may only use tokens 1-4. If training let it peek, the model "
         "would learn to rely on information that vanishes the moment you deploy it."])

    para(s, M + 4.6, 6.15, CW - 4.6, 0.6,
         "`model4.py` prints exactly this 6×6 triangle when you run it. **Show it on screen** — it "
         "is the most convincing 60 seconds in the whole file.", 12, ORANGE_DK)

    # ---------------------------------------------------------------- 50
    s = slide(prs, "Benefits of the causal mask", "Four things you get from a triangle of zeros")
    y = BODY_TOP
    items = [
        ("1", "T predictions from ONE forward pass",
         "This is the underrated one. Without the mask you could only train on the last position — "
         "one label per sequence. With it, **every** position is a valid supervised example at "
         "once, because none of them can see their own answer. A 128-token window is "
         "**128 training examples**, computed in parallel. That is a 128× data-efficiency "
         "multiplier for free."),
        ("2", "Train and test conditions match exactly",
         "At generation time there is no future. The mask makes training obey the same rule, so "
         "there is zero distribution shift between how it learned and how it runs. A model trained "
         "without the mask would score beautifully in training and collapse instantly on real "
         "generation."),
        ("3", "It makes the KV cache possible",
         "Because token t's attention **never changes** when you append token t+1, the keys and "
         "values already computed stay valid forever. So generation can cache them and each new "
         "token costs O(T) instead of recomputing O(T²). Every fast inference server on earth "
         "depends on this property."),
        ("4", "It is completely free",
         "No parameters, no extra compute, no memory beyond one boolean triangle that is shared by "
         "every layer. Compare that to almost any other capability in deep learning."),
    ]
    for i, (n, t, d) in enumerate(items):
        yy = y + i * 1.32
        chip(s, M, yy, 0.5, 0.5, n, fill=ORANGE, edge=None, color=WHITE, size=14)
        label(s, M + 0.68, yy + 0.02, 11.4, t, 14, INK, PP_ALIGN.LEFT)
        label(s, M + 0.68, yy + 0.42, 11.4, d, 11.5, GRAY, PP_ALIGN.LEFT)

    # ---------------------------------------------------------------- 51
    s = slide(prs, "What could replace the causal mask?",
              "Every alternative — and exactly why it does not beat it for a GPT")
    table(s, M, BODY_TOP, CW, [
        ["Instead of causal…", "What it does", "Why it does not perform better here"],
        ["**No mask at all**",
         "Every token attends to every token, past and future.",
         "**It cheats.** Position t can read position t+1, which *is* the answer. Train loss "
         "collapses toward 0 and generation produces garbage, because at run time the future it "
         "learned to rely on is empty. This is the most instructive failure to demo."],
        ["**Bidirectional (BERT)**",
         "See the whole sentence; train by masking out ~15% of tokens and filling the blanks.",
         "Excellent for classification, embeddings and search. But you only get a signal on the "
         "~15% that were masked, so it is **~6× less data-efficient per pass**, and there is no "
         "natural left-to-right generation loop. Different tool, different job."],
        ["**Prefix-LM (UL2, T5-style)**",
         "The prompt is fully bidirectional; only the generated part is causal.",
         "Genuinely useful — the prompt gets richer representations. Costs a second attention "
         "pattern, complicates the KV cache, and gives little benefit once models are large. "
         "Mostly survives inside encoder-decoder models."],
        ["**Sliding window / local**",
         "Causal, but only the last W tokens (Mistral: 4,096; gpt-oss: 128).",
         "Not a replacement — a **restriction layered on top of** causal. Buys O(T·W) instead of "
         "O(T²), loses long-range recall, so real models **alternate** windowed and full layers."],
        ["**Sparse / block (BigBird, Longformer)**",
         "Attend to a chosen subset: a few global tokens, some random, a local band.",
         "Makes 100k-token documents affordable. At ordinary lengths it is strictly an "
         "approximation — quality drops and complexity rises for no gain."],
        ["**Diffusion / any-order LMs**",
         "Drop left-to-right entirely; denoise or fill tokens in arbitrary order.",
         "A real research direction with genuine parallel-decoding upside. As of now it is still "
         "**behind autoregressive models on quality per unit of compute**, which is why nothing at "
         "the frontier ships it."],
    ], widths=[2.1, 4.0, 6.1], size=9.8, row_h=0.82, head_h=0.34)

    # ---------------------------------------------------------------- 52
    s = slide(prs, "model4.py  ·  proj and dropout",
              "The two pieces of SelfAttention nobody explains")
    xl, xr, cw = twocol(s, 0.5)
    heading(s, xl, BODY_TOP, cw, "proj  —  nn.Linear(n_embd, n_embd)")
    code(s, xl, BODY_TOP + 0.32, cw, 1.15, [
        "y = y.transpose(1, 2).reshape(B, T, C)",
        "return self.dropout(self.proj(y))",
    ], size=11)
    bullets(s, xl, BODY_TOP + 1.62, cw, 3.1, [
        "After the heads are glued back together, the vector is just **4 independent chunks sitting "
        "next to each other**. Nothing has mixed them.",
        "`proj` is the layer that lets the model **combine what different heads found** — e.g. "
        "“head 2 found the subject and head 3 found the verb, now relate them”.",
        "It also puts the output back on the right scale to be **added to the residual stream**. "
        "Without it, every block would dump raw concatenated head output into `x`.",
        "Delete it and the model still trains — noticeably worse. It is cheap: `1 · C²` of the "
        "`12 · C²` per block.",
    ], size=12, gap=9)

    heading(s, xr, BODY_TOP, cw, "dropout  —  it appears three times")
    table(s, xr, BODY_TOP + 0.32, cw, [
        ["Where", "What it protects against"],
        ["after the **embedding** sum", "over-relying on any one input feature"],
        ["on the **attention weights**", "over-relying on one specific token — forces "
                                         "the head to spread its attention"],
        ["after **proj** and inside the **MLP**", "over-relying on any single neuron in the "
                                                  "residual stream"],
    ], widths=[2.3, 3.6], size=11, row_h=0.62)

    box(s, xr, BODY_TOP + 2.75, cw, 1.95, "The detail that catches people out",
        ["Dropout is **on** in `model.train()` and **off** in `model.eval()`. That is why "
         "`estimate_loss` and `generate` both call `model.eval()` first.",
         "Forget it and your validation loss is measured on a **randomly damaged model** — it will "
         "read higher than the truth and jump around between evals."])

    # ---------------------------------------------------------------- 53
    s = slide(prs, "model4.py  ·  the MLP", "Attention was tokens talking. This is one token thinking.")
    code(s, M, BODY_TOP, 7.0, 2.0, [
        "self.net = nn.Sequential(",
        "    nn.Linear(cfg.n_embd, 4 * cfg.n_embd),",
        "    nn.GELU(),                              # a smooth ReLU",
        "    nn.Linear(4 * cfg.n_embd, cfg.n_embd),",
        "    nn.Dropout(cfg.dropout),",
        ")",
    ], size=11.5)

    y = BODY_TOP + 2.3
    chip(s, M + 0.3, y, 2.0, 0.6, "128", sub="n_embd", size=13)
    arrow(s, M + 2.45, y + 0.19, 0.5, 0.22)
    chip(s, M + 3.15, y, 2.4, 0.6, "512", sub="4 × n_embd", fill=TINT, size=13)
    arrow(s, M + 5.7, y + 0.19, 0.5, 0.22)
    chip(s, M + 6.4, y, 2.0, 0.6, "128", sub="back down", size=13)
    label(s, M + 3.15, y + 0.78, 2.4, "GELU applied here", 10.5, ORANGE_DK)

    x2 = M + 7.4
    w2 = CW - 7.4
    bullets(s, x2, BODY_TOP, w2, 4.7, [
        "**Why widen at all?** The wide layer is where the model has room to compute intermediate "
        "features. Think of it as scratch space that gets thrown away.",
        "**Why 4×?** It is the ratio the original 2017 Transformer paper used and everyone kept. "
        "There is no derivation. People have tried 2× and 8×; 4× is a good default.",
        "**Why a non-linearity?** Without GELU, `Linear → Linear` collapses into a single Linear — "
        "the whole MLP would be mathematically pointless. **The non-linearity is the only reason "
        "depth buys anything.**",
        "**Why GELU and not ReLU?** GELU is smooth around zero, so gradients do not have a hard "
        "kink. Slightly better in practice; GPT-2 used it, so we do.",
        "**Two thirds of the parameters live here** — 8 of the 12 · C² per block. The MLP, not "
        "attention, is where most of a GPT's knowledge is stored.",
    ], size=12, gap=10)

    # ---------------------------------------------------------------- 54
    s = slide(prs, "model4.py  ·  the Block", "Talk, then think — and never overwrite")
    code(s, M, BODY_TOP, 7.2, 1.65, [
        "def forward(self, x):",
        "    x = x + self.attn(self.ln1(x))     # talk to the other tokens",
        "    x = x + self.mlp(self.ln2(x))      # think about what you heard",
        "    return x",
    ], size=12)

    y = BODY_TOP + 2.0
    heading(s, M, y, 7.2, "The residual stream — why  x = x + …  and not  x = …")
    chip(s, M, y + 0.42, 1.4, 0.55, "x", size=13)
    arrow(s, M + 1.5, y + 0.53, 0.4, 0.22)
    chip(s, M + 2.0, y + 0.42, 1.5, 0.55, "ln1", fill=WHITE, size=12)
    arrow(s, M + 3.6, y + 0.53, 0.4, 0.22)
    chip(s, M + 4.1, y + 0.42, 1.6, 0.55, "attn", fill=TINT, size=12)
    arrow(s, M + 5.8, y + 0.53, 0.4, 0.22)
    chip(s, M + 6.3, y + 0.42, 0.9, 0.55, "+", fill=ORANGE, edge=None, color=WHITE, size=16)
    label(s, M, y + 1.1, 7.2, "the original x flows straight through and the block only "
                              "**adds a correction** to it", 11.5, ORANGE_DK)

    x2 = M + 7.6
    w2 = CW - 7.6
    bullets(s, x2, BODY_TOP, w2, 2.6, [
        "Each block **adds a small correction** rather than replacing everything. A block that has "
        "learned nothing yet outputs ~0 and is harmless.",
        "Gradients flow backwards through the `+` **undiminished**. Without residuals, deep networks "
        "simply refuse to train — this is the trick that made “deep” learning deep.",
        "Think of `x` as a **shared notepad** every block reads from and writes to.",
    ], size=12, gap=9)

    box(s, x2, BODY_TOP + 2.9, w2, 1.8, "Pre-norm vs post-norm",
        ["We normalise **before** each sub-layer (`ln1(x)` then attention). The 2017 paper "
         "normalised *after*, which needed a careful learning-rate warmup or it diverged.",
         "Pre-norm keeps the residual path completely clean — nothing rescales it — and that is what "
         "makes deep transformers stable. **Every modern model does pre-norm.**"])

    # ---------------------------------------------------------------- 55
    s = slide(prs, "model4.py  ·  the ARGPT class", "Assembling it, and scoring it")
    code(s, M, BODY_TOP, 7.4, 3.35, [
        "self.tok_emb = nn.Embedding(cfg.vocab_size, cfg.n_embd)",
        "self.pos_emb = nn.Embedding(cfg.block_size, cfg.n_embd)",
        "self.drop    = nn.Dropout(cfg.dropout)",
        "self.blocks  = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layer)])",
        "self.ln_f    = nn.LayerNorm(cfg.n_embd)",
        "self.head    = nn.Linear(cfg.n_embd, cfg.vocab_size, bias=False)",
        "self.head.weight = self.tok_emb.weight        # weight tying",
        "self.apply(self._init_weights)                # N(0, 0.02), GPT-2's value",
        "",
        "loss = F.cross_entropy(logits.view(-1, logits.size(-1)),",
        "                       targets.view(-1))",
    ], size=11)

    x2 = M + 7.75
    w2 = CW - 7.75
    heading(s, x2, BODY_TOP, w2, "The loss, in one question")
    box(s, x2, BODY_TOP + 0.32, w2, 1.0, None,
        ["~~“How surprised was the model by the token that actually came next?”~~"],
        size=13, fill=TINT)
    bullets(s, x2, BODY_TOP + 1.5, w2, 1.9, [
        "`.view(-1, …)` flattens B and T into one long list of predictions — cross-entropy does not "
        "care where a prediction came from.",
        "Measured in **nats**. Lower = less surprised. 0 would be perfect and is impossible; "
        "language is not deterministic.",
    ], size=12, gap=9)

    y = BODY_TOP + 3.6
    table(s, M, y, CW, [
        ["Checkpoint", "Shakespeare, char (vocab 65)", "What it means"],
        ["untrained", "≈ 4.17  =  ln(65)", "guessing uniformly — the free sanity check"],
        ["after ~250 steps", "≈ 2.5", "learned letter frequencies and spacing"],
        ["after ~2,000 steps (TINY)", "≈ 1.7 - 1.8", "word shapes, capital letters, name colons"],
        ["a good SMALL run", "≈ 1.5 - 1.6", "readable Shakespeare-flavoured structure"],
    ], widths=[2.5, 3.2, 6.5], size=11, row_h=0.42)

    # ---------------------------------------------------------------- 56
    s = slide(prs, "model4.py  ·  the honest summary",
              "What this file does and does not know")
    box(s, M, BODY_TOP, CW, 1.0, None,
        ["Nothing in this file knows about English. It only learns which number tends to follow "
         "which other numbers. **Grammar is a side effect of doing that well.**"],
        size=15, fill=TINT)

    y = BODY_TOP + 1.25
    xl, xr, cw = twocol(s, 0.5)
    heading(s, xl, y, cw, "Every class in the file, in one line each")
    table(s, xl, y + 0.32, cw, [
        ["Class", "One sentence"],
        ["`SelfAttention`", "tokens look backward at each other and blend information"],
        ["`MLP`", "each token thinks alone: widen, GELU, narrow"],
        ["`Block`", "attention + MLP, each wrapped in pre-norm and a residual"],
        ["`ARGPT`", "embeddings → N blocks → final norm → vocab scores → loss"],
    ], widths=[1.5, 4.4], size=11, row_h=0.55)

    heading(s, xr, y, cw, "Facts worth repeating at the end of this file")
    bullets(s, xr, y + 0.35, cw, 3.3, [
        "The **mask** is the only thing making this a GPT instead of a BERT.",
        "**Two thirds of the parameters are in the MLPs**, not in attention.",
        "The model has **no memory** beyond `block_size` — no hidden state carries over.",
        "It is ~130 lines. GPT-4's core is the same shape; it is the data, the scale and the "
        "post-training that differ.",
    ], size=12, gap=10)

    # ================================================================ FILE 5
    divider(prs, 5, "train5.py", "Teaching ARGPT to predict the next token",
            ["Five steps, repeated. There is no step six.",
             "This is how every neural network on earth is trained",
             "The same function later runs unchanged on a GPU in file 7"])

    # ---------------------------------------------------------------- 58
    s = slide(prs, "train5.py  ·  the loop", "Five steps, forever")
    code(s, M, BODY_TOP, 7.6, 2.15, [
        "for step in range(1, cfg.max_iters + 1):",
        "    x, y = get_batch(\"train\", ...)      # 1. grab a random batch",
        "    _, loss = model(x, y)               # 2+3. predict, and score how wrong",
        "    opt.zero_grad()                     #     clear last step's gradients",
        "    loss.backward()                     # 4. which way should each weight go?",
        "    clip_grad_norm_(params, 1.0)        #     guardrail: no wild jumps",
        "    opt.step()                          # 5. move every weight a little",
    ], size=11.5)

    x2 = M + 7.95
    w2 = CW - 7.95
    for i, (n, t) in enumerate([("1", "get a batch"), ("2", "predict"), ("3", "measure the error"),
                                ("4", "compute gradients"), ("5", "nudge the weights")]):
        yy = BODY_TOP + i * 0.52
        chip(s, x2, yy, 0.42, 0.42, n, fill=ORANGE, edge=None, color=WHITE, size=12)
        label(s, x2 + 0.58, yy + 0.06, w2 - 0.6, t, 13, INK, PP_ALIGN.LEFT)
    arrow(s, x2 + 0.16, BODY_TOP + 2.62, 0.12, 0.3, right=False)
    label(s, x2, BODY_TOP + 2.95, w2, "repeat 2,000 times", 11.5, ORANGE_DK, PP_ALIGN.LEFT)

    y = BODY_TOP + 2.85
    box(s, M, y, 7.6, 0.95, None,
        ["**There is no step 6.** Every neural network you have ever used was trained by "
         "this loop."], size=14, fill=TINT)

    table(s, M, y + 1.15, CW, [
        ["Line", "What it guards against if you delete it"],
        ["`opt.zero_grad()`", "PyTorch **accumulates** gradients by default. Skip this and step 2's "
                              "gradient is added to step 1's, then step 3's on top — the model "
                              "walks in a direction that is the sum of everything it has ever seen. "
                              "Loss stalls or explodes."],
        ["`clip_grad_norm_(…, 1.0)`", "One unlucky batch produces a huge gradient, the weights jump "
                                      "outside their sane range, and every number afterwards is "
                                      "`nan`. Clipping caps the size of a single step — the seatbelt."],
        ["`torch.manual_seed(1337)`", "Without it your live demo produces different text every run "
                                      "and you cannot reproduce a bug a student reports."],
    ], widths=[2.2, 10.0], size=10.8, row_h=0.72)

    # ---------------------------------------------------------------- 59
    s = slide(prs, "Dry run  ·  one training step", "Following a single weight through the loop")
    y = BODY_TOP
    rows = [
        ("1", "get_batch", "x = (32, 128) token ids     y = the same, shifted by one"),
        ("2", "model(x, y)", "forward pass → logits (32, 128, 65) = 266,240 raw scores"),
        ("3", "cross_entropy", "loss = 4.17    ← the model is as surprised as random guessing"),
        ("4", "loss.backward()", "for each of 818,048 weights, compute ∂loss/∂w"),
        ("", "", "e.g.  w = 0.0213     ∂loss/∂w = +0.85     ← raising w makes it worse"),
        ("5", "opt.step()", "w ← 0.0213 − (lr × adjusted gradient) = 0.0210"),
    ]
    for i, (n, fn, txt) in enumerate(rows):
        yy = y + i * 0.62
        if n:
            chip(s, M, yy, 0.42, 0.42, n, fill=ORANGE, edge=None, color=WHITE, size=12)
            label(s, M + 0.58, yy + 0.06, 2.2, fn, 12.5, INK, PP_ALIGN.LEFT)
        label(s, M + 2.95, yy + 0.07, 9.3, txt, 12, GRAY, PP_ALIGN.LEFT)

    y = BODY_TOP + 3.95
    box(s, M, y, CW, 1.55, "Repeat that 2,000 times",
        ["Every step moves **all 818,048 weights** a tiny amount in the direction that would have "
         "made *that batch* less surprising. No single step matters. The average of thousands of "
         "them is what turns noise into Shakespeare.",
         "TINY sees `2,000 × 32 × 128 = 8,192,000` token-predictions — about **7.3 full passes** "
         "over the 1.1M-token Shakespeare file."])

    # ---------------------------------------------------------------- 60
    s = slide(prs, "train5.py  ·  AdamW and estimate_loss",
              "The optimizer, and how we measure honestly")
    xl, xr, cw = twocol(s, 0.5)
    heading(s, xl, BODY_TOP, cw, "Why AdamW and not plain SGD")
    code(s, xl, BODY_TOP + 0.32, cw, 0.85, [
        "opt = torch.optim.AdamW(model.parameters(),",
        "                        lr=cfg.learning_rate)",
    ], size=10.5)
    bullets(s, xl, BODY_TOP + 1.3, cw, 3.4, [
        "**Momentum** — a weight that keeps being pushed the same way gets a bigger and bigger "
        "shove. It builds speed down a consistent slope.",
        "**Adaptivity** — each weight gets its own step size, scaled down if its gradient has been "
        "noisy. Rare tokens' embeddings still learn.",
        "**Decoupled weight decay** (the “W”) — shrink weights toward zero separately from the "
        "gradient. Cleaner regularisation than L2 inside the loss.",
        "Plain SGD would work here, but needs far more careful tuning. AdamW is what everyone uses "
        "for transformers, and it is one line.",
    ], size=12, gap=9)

    heading(s, xr, BODY_TOP, cw, "estimate_loss — measuring without lying")
    code(s, xr, BODY_TOP + 0.32, cw, 1.55, [
        "@torch.no_grad()",
        "def estimate_loss(...):",
        "    model.eval()             # dropout OFF",
        "    ... average over eval_iters batches ...",
        "    model.train()            # dropout back ON",
    ], size=10.5)
    bullets(s, xr, BODY_TOP + 2.0, cw, 2.7, [
        "`@torch.no_grad()` — we are only measuring, so skip building the backward graph. "
        "Faster and uses far less memory.",
        "`model.eval()` — turns **dropout off**. Measuring a randomly damaged model gives you a "
        "number that is both too high and too jumpy.",
        "**Averaging over 50 batches** — one batch is noise; fifty tell the truth. Without this "
        "your loss curve zig-zags and students cannot see the trend.",
        "It runs for **both** `train` and `val`, which is the whole point.",
    ], size=12, gap=9)

    # ---------------------------------------------------------------- 61
    s = slide(prs, "Reading the loss curve", "The actual deliverable of this session")
    y = BODY_TOP
    xw = (CW - 0.8) / 3
    for i, (t, tr, va, verdict, good) in enumerate([
        ("LEARNING", ["4.17", "2.61", "2.10", "1.88", "1.72"],
         ["4.17", "2.63", "2.14", "1.93", "1.79"],
         "Both falling together. The model is learning the **language**.", True),
        ("MEMORISING", ["4.17", "2.55", "1.80", "1.31", "0.94"],
         ["4.17", "2.60", "2.05", "2.11", "2.28"],
         "Train falls, val **turns around**. It is memorising the file. More dropout, more data, "
         "or fewer parameters.", False),
        ("BROKEN", ["4.17", "8.92", "41.3", "nan", "nan"],
         ["4.17", "9.10", "44.0", "nan", "nan"],
         "Learning rate too high. Restart with a smaller `lr`. This is the #1 live-demo failure.",
         False),
    ]):
        x = M + i * (xw + 0.4)
        chip(s, x, y, xw, 0.52, t, fill=ORANGE if good else WHITE, edge=ORANGE,
             color=WHITE if good else INK, size=13)
        rows = [["step", "train", "val"]] + [
            [str((j + 1) * 500), tr[j], va[j]] for j in range(5)]
        table(s, x, y + 0.68, xw, rows, widths=[1, 1, 1], size=10.5, row_h=0.31,
              head_h=0.31, aligns=["c", "c", "c"])
        label(s, x, y + 2.85, xw, verdict, 11.5, INK, PP_ALIGN.LEFT)

    y = BODY_TOP + 4.05
    box(s, M, y, CW, 1.45, "What to tell the class before you press enter",
        ["**The deliverable of this session is the loss curve, not the prose.** ARGPT-TINY is "
         "0.8M parameters. It produces *structure* — line breaks, capital letters, character names "
         "— not *sense*. A class expecting ChatGPT will read a perfectly working demo as a failure. "
         "Say this in the first five minutes."])

    # ---------------------------------------------------------------- 62
    s = slide(prs, "train5.py  ·  the checkpoint", "Three things go in the file, and all three are needed")
    code(s, M, BODY_TOP, 7.4, 1.9, [
        "torch.save({\"model\":     model.state_dict(),",
        "            \"cfg\":       asdict(cfg),",
        "            \"tokenizer\": tokenizer}, path)",
        "",
        "# out/shakespearetinychar.pt",
    ], size=11.5)

    table(s, M, BODY_TOP + 2.2, 7.4, [
        ["What", "Why you cannot omit it"],
        ["`model`", "the weights — obviously"],
        ["`cfg`", "the **shape**, so the same model can be rebuilt. Without it you cannot even "
                  "load the weights."],
        ["`tokenizer`", "without it the numbers can never become text again. The model is "
                        "**useless** without its tokenizer."],
    ], widths=[1.3, 5.4], size=11, row_h=0.62)

    x2 = M + 7.75
    w2 = CW - 7.75
    bullets(s, x2, BODY_TOP, w2, 2.6, [
        "`asdict(cfg)` stores a **plain dict**, not a pickled Python object. That is what lets "
        "`generate6.py` load with `weights_only=True` — safe against a malicious checkpoint.",
        "The filename is `<dataset><name><tokenizer>.pt`, so `shakespearesmallchar.pt` and "
        "`codingsmallbpe.pt` sit side by side in one folder without colliding.",
    ], size=12, gap=10)

    box(s, x2, BODY_TOP + 2.9, w2, 1.8, "The error this design prevents",
        ["`size mismatch for tok_emb.weight`",
         "The classic: train with `SMALL`, then generate while `config1.py` still says `TINY`. "
         "Because the shape comes from the **checkpoint** and never from the config file, "
         "it cannot happen here."])

    # ---------------------------------------------------------------- 63
    s = slide(prs, "Why PyTorch and not TensorFlow?",
              "An honest answer — it is a tooling choice, not a maths one")
    table(s, M, BODY_TOP, CW, [
        ["", "PyTorch  *(what we use)*", "TensorFlow / Keras", "JAX"],
        ["**Execution model**",
         "**Define-by-run.** The graph is built as Python executes, so `print(x.shape)` inside "
         "`forward` just works and you can set a breakpoint mid-attention.",
         "TF1 was define-then-run, which made debugging genuinely painful. TF2 + Keras is eager by "
         "default now and much better — but the research world had already moved.",
         "Functional + JIT-compiled. Extremely fast, but `jit` makes printing and debugging "
         "indirect."],
        ["**Teaching fit**",
         "`nn.Module` maps 1:1 onto the boxes you draw on the whiteboard. `loss.backward()` and you "
         "can inspect `.grad` yourself.",
         "Keras hides the loop behind `model.fit()`. Excellent for productivity, **wrong for this "
         "session** — the loop *is* the lesson.",
         "Requires understanding pure functions, PRNG keys and `vmap` before you write a "
         "transformer."],
        ["**Ecosystem today**",
         "Nearly every new open model ships PyTorch weights first — Llama, Mistral, Qwen, DeepSeek, "
         "gpt-oss. HuggingFace is PyTorch-first.",
         "Strongest in **production serving**: TF Serving, TFLite, TF.js, and a long history of "
         "mobile/edge deployment.",
         "The frontier choice inside Google/DeepMind — Gemini is trained on JAX + TPU."],
        ["**This project specifically**",
         "The lineage is Karpathy's nanoGPT, which is PyTorch. Modal's GPU images ship torch. "
         "`pip install torch` and you are done.",
         "Would work fine — the maths is identical — but every tutorial the students will read "
         "next is in PyTorch.",
         "TPU-oriented; overkill for one L4 and ~700 teaching lines."],
    ], widths=[1.9, 4.0, 3.6, 2.7], size=10, row_h=1.02, head_h=0.36)

    para(s, M, 6.4, CW, 0.4,
         "**Be fair about this in class:** a transformer is the same maths in all three. "
         "Choose PyTorch here because it is the most *readable* and the most likely to match "
         "whatever the students open next.", 12, GRAY)

    # ================================================================ FILE 6
    divider(prs, 6, "generate6.py", "Making ARGPT write",
            ["Predict one token, append it, repeat — there is no plan and no draft",
             "temperature and top_k are the only two knobs",
             "Why the same prompt gives different text every single run"])

    # ---------------------------------------------------------------- 65
    s = slide(prs, "generate6.py  ·  the loop", "Predict, append, repeat")
    code(s, M, BODY_TOP, 7.3, 2.6, [
        "for _ in range(max_new_tokens):",
        "    window = idx[:, -model.cfg.block_size:]   # keep only the newest tokens",
        "    logits, _ = model(window)",
        "    logits = logits[:, -1, :] / temperature   # only the LAST position matters",
        "    ... top_k filter ...",
        "    probs = F.softmax(logits, dim=-1)",
        "    next_id = torch.multinomial(probs, 1)     # a weighted dice roll",
        "    idx = torch.cat([idx, next_id], dim=1)    # append and go again",
    ], size=11)

    y = BODY_TOP + 2.9
    seq = [("\"ROMEO\"", "\":\""), ("\"ROMEO:\"", "\"\\n\""), ("\"ROMEO:\\n\"", "\"I\""),
           ("\"ROMEO:\\nI\"", "\" \"")]
    for i, (a, b) in enumerate(seq):
        yy = y + i * 0.5
        label(s, M + 0.3, yy, 3.0, a, 12.5, INK, PP_ALIGN.RIGHT)
        arrow(s, M + 3.5, yy + 0.05, 0.5, 0.18)
        label(s, M + 4.2, yy, 1.5, b, 12.5, ORANGE_DK, PP_ALIGN.LEFT)
    label(s, M + 0.3, y + 2.05, 5.4, "…and so on, one token at a time", 11.5, GRAY)

    x2 = M + 7.65
    w2 = CW - 7.65
    bullets(s, x2, BODY_TOP, w2, 2.6, [
        "`logits[:, -1, :]` — the model predicted at **every** position, but only the last one is "
        "about a token that does not exist yet.",
        "`idx[:, -block_size:]` — this slice is the hard memory limit, in one line of code.",
        "`torch.cat` — the model's own output becomes its next input. That is what "
        "*autoregressive* means.",
    ], size=12, gap=10)

    box(s, x2, BODY_TOP + 2.9, w2, 2.6, "The honest description",
        ["There is **no plan, no draft, and no memory** beyond the last `block_size` tokens. "
         "The model is not composing a sentence — it is making one local choice, then forgetting "
         "that it made it and doing it again.",
         "Everything that looks like intent is the accumulated weight of those local choices."])

    # ---------------------------------------------------------------- 66
    s = slide(prs, "Dry run  ·  temperature", "The same four logits, three different personalities")
    code(s, M, BODY_TOP, CW, 0.85, [
        "logits = [2.0, 1.0, 0.5, 0.1]     for tokens:  \"the\"   \"a\"   \"my\"   \"thy\"",
    ], size=12.5, title="ONE POSITION, FOUR CANDIDATE NEXT TOKENS")

    y = BODY_TOP + 1.15
    table(s, M, y, CW, [
        ["temperature", "\"the\"", "\"a\"", "\"my\"", "\"thy\"", "Behaviour"],
        ["**0.2**  safe", "**99.27%**", "0.67%", "0.05%", "0.01%",
         "Almost deterministic. Picks the favourite nearly every time — and therefore **repeats "
         "itself**, often getting stuck in a loop."],
        ["**0.8**  the default", "**65.24%**", "18.69%", "10.00%", "6.07%",
         "The sweet spot. Usually sensible, occasionally surprising. This is what `generate6.py` "
         "ships with."],
        ["**1.0**  raw", "57.45%", "21.14%", "12.82%", "8.59%",
         "The model's honest, unmodified distribution. Nothing is being reshaped."],
        ["**1.5**  chaotic", "46.23%", "23.74%", "17.01%", "13.03%",
         "The distribution is flattened, so unlikely tokens get real chances. Creative, then "
         "quickly incoherent."],
    ], widths=[1.9, 1.15, 1.0, 1.0, 1.0, 6.2], size=10.8, row_h=0.75,
        head_h=0.34, aligns=["l", "c", "c", "c", "c", "l"])

    box(s, M, y + 3.55, CW, 1.2, "What temperature actually is",
        ["`logits / temperature`, **before** softmax. Dividing by a small number spreads the scores "
         "apart, so softmax sharpens. Dividing by a large number squashes them together, so softmax "
         "flattens. That is the entire implementation — one division."])

    # ---------------------------------------------------------------- 67
    s = slide(prs, "Dry run  ·  top-k", "Cutting off the tail before you roll the dice")
    code(s, M, BODY_TOP, CW, 0.95, [
        "kth = torch.topk(logits, min(top_k, logits.size(-1))).values[:, [-1]]",
        "logits[logits < kth] = float(\"-inf\")     # everything outside the top k is out",
    ], size=12)

    y = BODY_TOP + 1.25
    heading(s, M, y, CW, "top_k = 3, on a six-token vocabulary")
    cell = 0.68
    toks = ["the", "a", "my", "thy", "zzq", "◇"]
    lg = ["2.0", "1.0", "0.5", "0.1", "-3.0", "-4.1"]
    after = ["2.0", "1.0", "0.5", "−inf", "−inf", "−inf"]
    probs = ["65%", "24%", "11%", "0", "0", "0"]
    grid(s, M + 1.4, y + 0.4, cell, [toks], texts=[toks], size=11, head_rows=["token"],
         fills=[[WHITE] * 6])
    grid(s, M + 1.4, y + 0.4 + cell, cell, [lg], texts=[lg], size=11, head_rows=["logit"],
         fills=[[WHITE] * 6])
    grid(s, M + 1.4, y + 0.4 + 2 * cell, cell, [after], texts=[after], size=9.5,
         head_rows=["after top-k"],
         fills=[[TINT, TINT, TINT, INK, INK, INK]])
    grid(s, M + 1.4, y + 0.4 + 3 * cell, cell, [probs], texts=[probs], size=11,
         head_rows=["sampled from"], fills=[[TINT2, TINT2, TINT2, INK, INK, INK]])

    x2 = M + 6.3
    w2 = CW - 6.3
    bullets(s, x2, y + 0.4, w2, 3.5, [
        "Without top-k, a token with a **0.01% chance still gets picked once every 10,000 tokens** "
        "— and one absurd token derails the whole paragraph after it.",
        "top-k caps how bad the worst case can be, while leaving temperature free to control "
        "variety among sensible options.",
        "The modern alternative is **top-p / nucleus sampling**: keep the smallest set of tokens "
        "whose probabilities sum to p (say 0.9). It adapts — narrow when the model is confident, "
        "wide when it is not.",
    ], size=12, gap=10)

    # ---------------------------------------------------------------- 68
    s = slide(prs, "generate6.py  ·  load_argpt", "Why the same prompt never gives the same text")
    xl, xr, cw = twocol(s, 0.5)
    code(s, xl, BODY_TOP, cw, 1.9, [
        "ckpt = torch.load(path, map_location=device,",
        "                  weights_only=True)",
        "model = ARGPT(Config(**ckpt[\"cfg\"])).to(device)",
        "model.load_state_dict(ckpt[\"model\"])",
        "model.eval()",
    ], size=10.5)
    bullets(s, xl, BODY_TOP + 2.2, cw, 2.5, [
        "The shape comes from `ckpt[\"cfg\"]` — **never** from `config1.py`. That is what stops "
        "`size mismatch for tok_emb.weight`.",
        "`weights_only=True` refuses to execute arbitrary pickled code. Always use it on a "
        "checkpoint you did not create.",
        "`model.eval()` turns dropout **off**. Generating with dropout on gives you a randomly "
        "damaged model writing your text.",
    ], size=12, gap=9)

    heading(s, xr, BODY_TOP, cw, "Run it twice, get two different plays")
    box(s, xr, BODY_TOP + 0.35, cw, 1.55, None,
        ["The last step is `torch.multinomial(probs, 1)` — a **weighted dice roll**, not "
         "“pick the maximum”. A token with 18% probability is chosen 18% of the time."], fill=TINT)
    bullets(s, xr, BODY_TOP + 2.1, cw, 2.6, [
        "Set `temperature` very low (0.05) to make it nearly deterministic — and watch it "
        "immediately start repeating itself.",
        "`torch.manual_seed(n)` before generating makes it exactly reproducible, which is useful "
        "when a student reports “mine looks different”.",
        "This is also true of ChatGPT. Sampling is why you get a different answer to the same "
        "question — it is a feature, not a bug.",
    ], size=12, gap=9)
