"""Slides 1-38: opening, config1.py, tokenizer2.py, data3.py."""

from pptx.enum.text import PP_ALIGN
from theme import (BODY_TOP, CW, GRAY, GRAY_LT, INK, LINE, M, ORANGE, ORANGE_DK,
                   ORANGE_HI, TINT, TINT2, WHITE, arrow, box, bullets, chip, code,
                   divider, grid, heading, label, para, rule, slide, table,
                   title_slide, twocol)


def build(prs):
    # ================================================================ OPENING
    title_slide(
        prs,
        "Build an LLM\nfrom Scratch — Part 2",
        "From a text file to a trained transformer behind your own URL. "
        "Ten files, ~700 lines of PyTorch, no pretrained weights.",
        "Abdul Rahman Azam", "AI Season",
        meta=["Project: ARGPT", "config1.py  →  modern_upgrades10.py",
              "Live demos on CPU + a rented L4 GPU"])

    # ---------------------------------------------------------------- 02
    s = slide(prs, "Where we are", "Part 1 built the intuition. Part 2 builds the machine.")
    xl, xr, cw = twocol(s)
    box(s, xl, BODY_TOP, cw, 2.25, "Part 1 — you learned",
        ["What a token is, what an embedding is, and what attention is trying to do.",
         "Why an LLM is a next-token predictor and nothing more.",
         "The vocabulary: transformer, context window, parameters, loss."],
        fill=WHITE)
    rule(s, xl + 0.05, BODY_TOP + 0.02, cw - 0.1, ORANGE, 0.03)
    box(s, xr, BODY_TOP, cw, 2.25, "Part 2 — you build",
        ["A working tokenizer (two of them), a real transformer, and a training loop.",
         "You train it, watch the loss fall, and read what it writes.",
         "Then you put it on a GPU and behind an HTTP endpoint your agent calls."])

    heading(s, M, BODY_TOP + 2.6, CW, "By the end of this session you can say, honestly:")
    bullets(s, M, BODY_TOP + 2.95, CW, 2.4, [
        "“I know what every single number in a GPT does, because I chose it.”",
        "“I know why the model can't see the future, and I can point at the line that stops it.”",
        "“I know why my model isn't ChatGPT — and it isn't the architecture.”",
        "“I trained a language model for about ~~13 cents~~ and served it on a URL.”",
    ], size=14.5, gap=11)

    # ---------------------------------------------------------------- 03
    s = slide(prs, "The one idea", "Everything in these ten files serves one sentence")
    box(s, M, BODY_TOP, CW, 0.85, None,
        ["~~Given a sequence of tokens, predict the next token.~~"], size=21, fill=TINT)
    para(s, M, BODY_TOP + 1.02, CW, 0.5,
         "That is the **entire** objective. Grammar, character names, indentation in code, "
         "the back-and-forth of a conversation — all of it is a **side effect** of getting very "
         "good at “what comes next”. The model is never told what English is.", 13)

    y = BODY_TOP + 1.85
    steps = [("raw text", "Shakespeare\n.txt"), ("numbers", "tokenizer2"),
             ("(x, y) pairs", "data3"), ("a guess", "model4"), ("loss", "how wrong?"),
             ("nudge weights", "train5")]
    xw, gapw = 1.72, 0.29
    x = M + 0.15
    for i, (a, b) in enumerate(steps):
        chip(s, x, y, xw, 0.95, a, sub=b, size=12.5,
             fill=TINT if i in (0, 5) else WHITE)
        if i < len(steps) - 1:
            arrow(s, x + xw + 0.045, y + 0.36, gapw - 0.09, 0.22)
        x += xw + gapw

    label(s, M, y + 1.15, CW, "repeat a few thousand times   ·   then run the model forward one "
                              "token at a time, feeding its own output back in", 12, ORANGE_DK)

    box(s, M, y + 1.62, CW, 1.05, "Keep coming back to this",
        ["Almost every “why does it do that?” question a student asks resolves to one answer: "
         "**because it was only ever trained to predict the next token.** "
         "Write that sentence on the board and leave it there for the whole session."], fill=WHITE)

    # ---------------------------------------------------------------- 04
    s = slide(prs, "The map", "Ten files, in the order we teach them")
    table(s, M, BODY_TOP, CW, [
        ["#", "File", "The concept", "The thing you point at on screen"],
        ["1", "config1.py", "The control panel", "Every knob that shapes the model, in one dataclass"],
        ["2", "tokenizer2.py", "Text becomes numbers", "Two algorithms: char in 15 lines, then BPE for real"],
        ["3", "data3.py", "The reusable pipeline", "y is x shifted by one — that shift IS the training signal"],
        ["4", "model4.py", "The transformer", "Q, K, V, the attention formula, the causal mask as a triangle"],
        ["5", "train5.py", "Teaching it", "The five-step loop that trains every neural network alive"],
        ["6", "generate6.py", "Making it write", "Predict → append → repeat. temperature and top-k"],
        ["7", "modal_app7.py", "A real GPU", "The same train() function, on a rented L4, for ~13 cents"],
        ["8", "serve8.py", "You become the API", "@modal.enter() and why loading per request is wrong"],
        ["9", "use_from_agent9.py", "Full circle", "Your LangChain agent calling the model you just trained"],
        ["10", "modern_upgrades10.py", "What changed since 2019", "RMSNorm, RoPE, SwiGLU — and everything after them"],
    ], widths=[0.5, 2.5, 2.6, 6.9], size=11.2, row_h=0.395, head_h=0.36,
        aligns=["c", "l", "l", "l"])

    para(s, M, 6.35, CW, 0.5,
         "Every file **runs on its own** (`python tokenizer2.py` prints a live demo) and every file "
         "is **importable**. The teaching order is baked into the filenames, so imports across files "
         "never need a package or a path hack.", 12, GRAY)

    # ---------------------------------------------------------------- 05
    s = slide(prs, "The whole run", "Six commands, start to finish")
    xl, xr, cw = twocol(s, 0.5)
    code(s, xl, BODY_TOP, cw, 1.75, [
        "python data3.py --dataset shakespeare \\",
        "                --tokenizer char",
        "python train5.py",
        "python generate6.py --prompt \"ROMEO:\"",
    ], size=12, title="ON YOUR LAPTOP  ·  ~4 MINUTES TOTAL")
    code(s, xl, BODY_TOP + 2.05, cw, 1.75, [
        "modal run modal_app7.py",
        "modal volume ls argpt-checkpoints",
        "modal deploy serve8.py",
        "python use_from_agent9.py --url <that url>",
    ], size=12, title="ON A RENTED GPU  ·  ~12 MINUTES  ·  ~13 CENTS")

    heading(s, xr, BODY_TOP, cw, "Do these two ONCE, before class")
    code(s, xr, BODY_TOP + 0.32, cw, 1.05, [
        "python data3.py --dataset shakespeare",
        "modal run modal_app7.py   # builds the image",
    ], size=11.5)
    para(s, xr, BODY_TOP + 1.85, cw, 1.0,
         "That first `modal run` downloads a **2.3 GB PyTorch** into a container. It takes a few "
         "minutes **once**, then Modal caches it. Do not discover this live in front of a class.", 12.5)

    box(s, xr, BODY_TOP + 2.95, cw, 1.75, "The best 90 seconds of the session",
        ["`python train5.py` prints a generated sample every 250 steps. Say nothing and let it "
         "scroll. Step 250 is letter soup. By 1000 you get `OMIO:`. By 2000, real character names "
         "and line breaks. **Nobody needs loss explained after watching that.**"])

    # ================================================================ FILE 1
    divider(prs, 1, "config1.py", "The control panel — every number that shapes ARGPT",
            ["One dataclass, two presets, zero magic numbers anywhere else",
             "This is the only file you edit while experimenting",
             "Change one line here and the other nine files follow"])

    # ---------------------------------------------------------------- 07
    s = slide(prs, "config1.py", "One dataclass. Every knob in the whole project.")
    code(s, M, BODY_TOP, 7.3, 4.5, [
        "@dataclass",
        "class Config:",
        "    name: str = \"tiny\"          # names the checkpoint: out/<name>.pt",
        "",
        "    # ---------- the SHAPE of the model ----------",
        "    block_size: int = 128       # how far back it can look",
        "    n_layer:    int = 4         # how many blocks we stack",
        "    n_head:     int = 4         # attention heads per block",
        "    n_embd:     int = 128       # size of one token's vector",
        "    dropout:    float = 0.1     # fraction of neurons switched off",
        "",
        "    vocab_size: int = 0         # NOT yours. data3.py decides it.",
        "",
        "    # ---------- how we TRAIN it ----------",
        "    batch_size:    int = 32",
        "    max_iters:     int = 2000",
        "    eval_interval: int = 250",
        "    eval_iters:    int = 50",
        "    learning_rate: float = 3e-4",
    ], size=11.5)

    x2 = M + 7.6
    w2 = CW - 7.6
    heading(s, x2, BODY_TOP, w2, "Why a config file at all?")
    bullets(s, x2, BODY_TOP + 0.33, w2, 2.4, [
        "In the next nine files you will **never see a magic number**.",
        "Want a bigger model? Change **one line here**, nothing else.",
        "A `@dataclass` gives you free `__init__`, free `__repr__`, and `asdict()` "
        "so the checkpoint can store the exact shape.",
    ], size=12.5)

    box(s, x2, BODY_TOP + 3.0, w2, 1.5, "The rule that breaks everything if you ignore it",
        ["`n_embd` **must divide evenly by** `n_head`.",
         "128 / 4 = 32 ✓    384 / 6 = 64 ✓    100 / 3 ✗"])

    # ---------------------------------------------------------------- 08
    s = slide(prs, "config1.py  ·  the shape knobs",
              "What happens if you turn each one UP or DOWN")
    table(s, M, BODY_TOP, CW, [
        ["Knob", "What it is", "Turn it UP ↑", "Turn it DOWN ↓"],
        ["block_size",
         "How many tokens the model can look back at. Its memory span.",
         "Longer memory, better long-range structure. **Attention cost grows with T²** — "
         "double it and attention gets ~4× slower and ~4× more memory.",
         "Faster and lighter, but the model physically cannot see far. It will forget who "
         "was speaking two lines ago."],
        ["n_layer",
         "How many transformer blocks are stacked. The model's depth.",
         "More reasoning steps, richer features. Cost grows **linearly**. Too deep on tiny "
         "data = memorising, and harder to train.",
         "Trains fast, but the model can only do shallow pattern-matching."],
        ["n_head",
         "How many parallel attention heads per block. Each learns a different kind of relationship.",
         "More kinds of relationship tracked at once (quotes, subject-verb, brackets). "
         "**Same total parameters** — you are only slicing n_embd differently.",
         "Fewer, wider heads. One head must do every job. Usually slightly worse, "
         "sometimes fine at tiny scale."],
        ["n_embd",
         "Length of the vector representing one token. The model's width.",
         "The single biggest quality lever — but cost grows with **n_embd²**. "
         "Doubling it roughly **4×s** the parameters and the compute.",
         "Much cheaper and faster. The model has less room to represent meaning and "
         "plateaus at a higher loss."],
        ["dropout",
         "Fraction of neurons randomly zeroed during training only.",
         "Stronger anti-memorisation. Too high (>0.3 here) and the model can't learn at "
         "all — train loss stops falling.",
         "Learns the training text faster — including **memorising** it. Watch val loss "
         "rise while train loss falls."],
    ], widths=[1.35, 3.0, 4.0, 3.9], size=10.3, row_h=0.98, head_h=0.34)

    # ---------------------------------------------------------------- 09
    s = slide(prs, "config1.py  ·  width vs depth",
              "Why n_embd is the expensive knob and n_layer is the cheap one")
    xl, xr, cw = twocol(s, 0.5)
    code(s, xl, BODY_TOP, cw, 1.5, [
        "params ≈ n_layer × 12 × n_embd²",
        "                  + embeddings",
    ], size=14, title="THE FORMULA THAT PREDICTS MODEL SIZE")

    para(s, xl, BODY_TOP + 1.7, cw, 0.9,
         "`n_layer` appears **once** — linear. `n_embd` is **squared**. That single exponent is why "
         "width costs so much more than depth.", 13)

    table(s, xl, BODY_TOP + 2.65, cw, [
        ["Change", "Params", "Cost"],
        ["baseline: 4 × 128", "0.82 M", "1×"],
        ["double depth: **8** × 128", "1.6 M", "2×"],
        ["double width: 4 × **256**", "3.2 M", "**4×**"],
        ["double both: 8 × 256", "6.4 M", "8×"],
    ], widths=[2.4, 1.3, 1.1], size=11.5, row_h=0.38)

    heading(s, xr, BODY_TOP, cw, "Where the 12 · n_embd² comes from")
    table(s, xr, BODY_TOP + 0.32, cw, [
        ["Piece of one block", "Size"],
        ["attention `qkv`  (C → 3C)", "3 · C²"],
        ["attention `proj`  (C → C)", "1 · C²"],
        ["MLP up  (C → 4C)", "4 · C²"],
        ["MLP down  (4C → C)", "4 · C²"],
        ["**one block total**", "**≈ 12 · C²**"],
    ], widths=[3.2, 1.5], size=11.5, row_h=0.38)

    box(s, xr, BODY_TOP + 2.85, cw, 1.85, "The intuition to hand the class",
        ["**Depth** = how many times the model gets to think. **Width** = how much it can hold "
         "in its head at each step.",
         "You almost always run out of **data** before you run out of parameters — see the "
         "Chinchilla slides near the end."])

    # ---------------------------------------------------------------- 10
    s = slide(prs, "config1.py  ·  block_size", "The model's memory, drawn to scale")
    para(s, M, BODY_TOP, CW, 0.45,
         "`block_size` is a **hard wall**, not a preference. There is no row in `pos_emb` for "
         "position 129, so the model cannot address it. `generate6.py` literally slices the "
         "history: `idx[:, -block_size:]`.", 13)

    y = BODY_TOP + 0.75
    chip(s, M, y, 9.4, 0.62, "…the whole play so far, thousands of tokens…",
         fill=WHITE, edge=LINE, color=GRAY_LT, size=12, bold=False)
    chip(s, M + 9.5, y, 2.73, 0.62, "last 128 tokens", fill=ORANGE, edge=None,
         color=WHITE, size=12.5)
    label(s, M, y + 0.7, 9.4, "invisible — the model has no way to reach this", 10.5, GRAY_LT)
    label(s, M + 9.5, y + 0.7, 2.73, "all it can see", 10.5, ORANGE_DK)

    y = BODY_TOP + 1.95
    table(s, M, y, CW, [
        ["Preset", "block_size", "In characters (char tokenizer)", "In words (BPE tokenizer)", "Attention cost"],
        ["TINY", "128", "~128 characters ≈ 20-25 words", "~90-100 words", "128² = 16,384 scores per head"],
        ["SMALL", "256", "~256 characters ≈ 45 words", "~190 words", "256² = 65,536 scores  (**4×**)"],
        ["GPT-2 (2019)", "1,024", "~1,024 characters", "~750 words", "1,048,576 scores"],
        ["GPT-5 (2025)", "400,000", "—", "~300,000 words", "impossible without FlashAttention + RoPE"],
    ], widths=[1.5, 1.3, 3.1, 2.6, 3.7], size=11, row_h=0.42)

    box(s, M, y + 2.5, CW, 1.15, "Callback to Session 3",
        ["This is **exactly** the problem RAG chunking solves. The model has a fixed window; you "
         "either shrink what you feed it, or you change the position encoding so the window can "
         "grow. **RoPE** (file 10) is the second answer, and it's why GPT-5 has 400k and we have 128."])

    # ---------------------------------------------------------------- 11
    s = slide(prs, "config1.py  ·  n_head", "One wide vector, sliced into parallel heads")
    para(s, M, BODY_TOP, CW, 0.4,
         "Heads do **not** add parameters. `n_embd` is split across them: "
         "`head_size = n_embd / n_head`. Four heads of 32 or one head of 128 — same numbers, "
         "different grouping.", 13)

    y = BODY_TOP + 0.68
    chip(s, M, y, 3.0, 0.6, "n_embd = 128", fill=TINT, edge=ORANGE, size=13)
    arrow(s, M + 3.15, y + 0.19, 0.5, 0.22)
    cx = M + 3.85
    for i, nm in enumerate(["head 0", "head 1", "head 2", "head 3"]):
        chip(s, cx + i * 2.15, y, 1.95, 0.6, nm, sub="32 numbers", size=11.5)
    label(s, cx, y + 0.72, 8.35, "each head learns its own kind of relationship — "
                                 "one may track quotes, another subject→verb, another indentation",
          11, ORANGE_DK)

    y = BODY_TOP + 1.85
    xl, xr, cw = twocol(s, 0.5)
    box(s, xl, y, cw, 1.5, "If n_head goes UP",
        ["More relationship types tracked in parallel, each with a **narrower** slice to work in. "
         "Too many heads on a small `n_embd` starves each one — 128 / 16 = 8 numbers per head is "
         "too thin to represent much."], fill=WHITE)
    rule(s, xl + 0.05, y + 0.02, cw - 0.1, ORANGE, 0.03)
    box(s, xr, y, cw, 1.5, "If n_head goes DOWN",
        ["Fewer, fatter heads. One head must serve every purpose at once, so it averages "
         "conflicting jobs together. Usually a small quality loss; at our scale you may not "
         "even measure it."])

    code(s, M, y + 1.75, CW, 1.4, [
        "assert cfg.n_embd % cfg.n_head == 0, \"n_embd must divide evenly by n_head\"",
        "",
        "# 128 / 4 = 32  OK        384 / 6 = 64  OK        100 / 3  ->  AssertionError",
    ], size=12.5, title="model4.py LINE 45 — THE ASSERT THAT SAVES YOUR DEMO")

    # ---------------------------------------------------------------- 12
    s = slide(prs, "config1.py  ·  dropout", "Randomly switching neurons off, with a dry run")
    para(s, M, BODY_TOP, CW, 0.4,
         "During **training only**, dropout zeroes a random fraction `p` of the values and scales "
         "the survivors up by `1/(1-p)` so the total stays the same. At eval time it does nothing.", 13)

    y = BODY_TOP + 0.62
    heading(s, M, y, CW, "Dry run: an 8-number vector with p = 0.25")
    cell = 0.62
    vals = [["1", "2", "3", "4", "5", "6", "7", "8"]]
    grid(s, M + 1.35, y + 0.35, cell, vals, size=11,
         head_rows=["input"], texts=vals)
    mask = [["1", "0", "1", "1", "0", "1", "1", "1"]]
    fills = [[WHITE if v == "1" else INK for v in mask[0]]]
    grid(s, M + 1.35, y + 0.35 + cell + 0.14, cell, mask, fills=fills, texts=mask,
         size=11, head_rows=["mask"])
    out = [["1.33", "0", "4.0", "5.33", "0", "8.0", "9.33", "10.67"]]
    ofill = [[TINT if v != "0" else INK for v in out[0]]]
    grid(s, M + 1.35, y + 0.35 + 2 * (cell + 0.14), cell, out, fills=ofill, texts=out,
         size=9, head_rows=["output"])

    label(s, M + 6.6, y + 0.4, 5.6,
          "survivors × 1/(1−0.25) = **× 1.333**", 12, ORANGE_DK, PP_ALIGN.LEFT)
    label(s, M + 6.6, y + 1.15, 5.6,
          "sum in = 36.0        sum out = 38.7", 12, GRAY, PP_ALIGN.LEFT)
    label(s, M + 6.6, y + 1.5, 5.6,
          "over many random masks the **expected** sum is unchanged —\n"
          "which is why eval needs no rescaling at all", 11.5, GRAY, PP_ALIGN.LEFT)

    y = BODY_TOP + 3.35
    xl, xr, cw = twocol(s, 0.5)
    box(s, xl, y, cw, 1.7, "dropout ↑ (say 0.3-0.5)",
        ["The model can never rely on any one neuron, so it is forced to spread the "
         "representation out. Strong anti-memorisation — but past ~0.3 at this size the training "
         "loss simply stops falling. **The model is being lobotomised faster than it can learn.**"],
        fill=WHITE)
    rule(s, xl + 0.05, y + 0.02, cw - 0.1, ORANGE, 0.03)
    box(s, xr, y, cw, 1.7, "dropout ↓ (0.0)",
        ["Training loss drops faster and further — which looks great and is a trap. With 1 MB of "
         "Shakespeare and 0.8M parameters, the model will start **memorising the file**. "
         "You will see it as train loss falling while **val loss flattens or rises**."])

    # ---------------------------------------------------------------- 13
    s = slide(prs, "config1.py  ·  the training knobs",
              "What happens if you turn each one UP or DOWN")
    table(s, M, BODY_TOP, CW, [
        ["Knob", "What it is", "Turn it UP ↑", "Turn it DOWN ↓"],
        ["batch_size",
         "How many random windows of text we learn from at once.",
         "Smoother, less noisy gradients and better GPU utilisation. Costs linear memory — "
         "this is the **first knob to cut** when you hit CUDA out-of-memory.",
         "Noisier gradients (which sometimes helps escape bad minima), lower memory, "
         "but poor GPU utilisation — the card sits idle."],
        ["max_iters",
         "How many training steps we take. Total tokens seen = iters × batch × block.",
         "Lower loss, up to a point. Past that you are just doing more epochs over the "
         "same tiny file and **memorising** it.",
         "Faster demo, higher final loss. Below ~500 on TINY the samples never get past "
         "letter soup and the demo falls flat."],
        ["learning_rate",
         "How big a step the optimizer takes each time.",
         "Learns faster — until it doesn't. Too high and the loss **spikes or goes to** `nan`. "
         "That is the #1 cause of a broken live demo.",
         "Very stable, very slow. The loss curve looks almost flat and students think "
         "nothing is happening."],
        ["eval_interval",
         "How often we stop and measure train/val loss + print a sample.",
         "Less interruption, faster wall-clock training. But you see the model learn in "
         "fewer snapshots — you lose the demo.",
         "More snapshots, prettier curve, slower run. Each eval costs "
         "`2 × eval_iters` extra forward passes."],
        ["eval_iters",
         "How many batches we average to get one loss number.",
         "A more trustworthy number, less jitter between evals.",
         "Noisy loss readings. With 1 batch you cannot tell learning from luck."],
    ], widths=[1.45, 3.0, 4.0, 3.8], size=10.3, row_h=0.94, head_h=0.34)

    # ---------------------------------------------------------------- 14
    s = slide(prs, "config1.py  ·  learning_rate", "The knob that decides whether your demo works")
    y = BODY_TOP
    xw = (CW - 0.8) / 3
    for i, (t, sub, lines, tint) in enumerate([
        ("TOO LOW  ·  1e-6", "loss barely moves",
         ["4.17 → 4.16 → 4.15 → 4.15", "→ 4.14 → 4.14 …", "", "“is it even running?”"], WHITE),
        ("JUST RIGHT  ·  3e-4", "loss falls and stays down",
         ["4.17 → 2.61 → 2.10 → 1.88", "→ 1.72 → 1.63 …", "", "this is what you want"], TINT),
        ("TOO HIGH  ·  1e-1", "loss explodes",
         ["4.17 → 8.92 → 41.3 → nan", "→ nan → nan …", "", "the run is dead, restart it"], WHITE),
    ]):
        x = M + i * (xw + 0.4)
        chip(s, x, y, xw, 0.52, t, fill=ORANGE if tint == TINT else WHITE,
             edge=ORANGE, color=WHITE if tint == TINT else INK, size=12.5)
        label(s, x, y + 0.62, xw, sub, 11, GRAY)
        code(s, x, y + 0.95, xw, 1.55, lines, size=11.5)

    y = BODY_TOP + 2.75
    bullets(s, M, y, CW, 2.6, [
        "`nan` **loss is almost always the learning rate.** A single bad batch produces a huge "
        "gradient, the weights jump far outside their sane range, and every number after that is "
        "garbage. `TINY` uses `3e-4` for exactly this reason.",
        "`clip_grad_norm_(params, 1.0)` in `train5.py` is the seatbelt — it caps how big a single "
        "step can be, so one bad batch cannot kill the run.",
        "`SMALL` uses `1e-3`, **higher** than TINY. Bigger batches average out more noise, so a "
        "bigger model on a GPU can safely take bigger steps. Learning rate and batch size are tuned "
        "together, never alone.",
        "Real training runs use a **schedule**: warm up from 0 over the first few hundred steps, "
        "then cosine-decay to near zero. We skipped it — it is one of the “did not build” items and "
        "it is worth maybe 5-10% final loss.",
    ], size=13, gap=11)

    # ---------------------------------------------------------------- 15
    s = slide(prs, "config1.py  ·  vocab_size",
              "The one field you must never set by hand")
    code(s, M, BODY_TOP, 6.6, 1.3, [
        "# vocab_size is NOT set by you.",
        "# data3.py decides it and train5.py fills it in.",
        "vocab_size: int = 0",
    ], size=12.5)

    para(s, M, BODY_TOP + 1.55, 6.6, 1.5,
         "The **data** decides the vocabulary. `data3.py` builds the tokenizer, counts what it "
         "found, and writes `tokenizer.json`. `train5.py` reads that file and sets "
         "`cfg.vocab_size = tok.vocab_size` before the model is even constructed.", 13)

    box(s, M, BODY_TOP + 3.15, 6.6, 1.55, "If you hand-edit it anyway",
        ["`IndexError: index out of range in self`",
         "The embedding table has fewer rows than a token id the data actually contains. "
         "Re-run `data3.py`, then `train5.py`. Never patch the number."])

    x2 = M + 6.95
    w2 = CW - 6.95
    heading(s, x2, BODY_TOP, w2, "What decides the number")
    table(s, x2, BODY_TOP + 0.32, w2, [
        ["Tokenizer + data", "vocab_size", "Untrained loss ≈ ln(V)"],
        ["char · Shakespeare", "65", "4.17"],
        ["char · the demo string", "12", "2.49"],
        ["bpe · our default", "1,024", "6.93"],
        ["GPT-2 (2019)", "50,257", "10.82"],
        ["Llama 3 (2024)", "128,000", "11.76"],
    ], widths=[2.6, 1.3, 1.9], size=11.5, row_h=0.42)

    box(s, x2, BODY_TOP + 3.15, w2, 1.55, "Free sanity check for the class",
        ["Before training, the model guesses uniformly, so its loss should sit near "
         "**ln(vocab_size)**. If step 1 of your run prints ≈ 4.17 on Shakespeare, "
         "your model and data agree. If it prints 11, something is wrong."])

    # ---------------------------------------------------------------- 16
    s = slide(prs, "config1.py  ·  TINY vs SMALL",
              "Same code. Two sets of numbers. Real parameter counts.")
    table(s, M, BODY_TOP, CW, [
        ["", "block_size", "n_layer", "n_head", "head_size", "n_embd", "batch", "iters", "lr",
         "Params", "Where", "Time"],
        ["**TINY**", "128", "4", "4", "32", "128", "32", "2,000", "3e-4", "**818,048**",
         "your CPU", "~3 min"],
        ["**SMALL**", "256", "6", "6", "64", "384", "64", "5,000", "1e-3", "**10,770,816**",
         "L4 GPU", "~10 min"],
    ], widths=[1.0, 1.15, 0.9, 0.9, 1.05, 0.95, 0.8, 0.95, 0.85, 1.5, 1.05, 0.85],
        size=11, row_h=0.48, head_h=0.55, aligns=["l"] + ["c"] * 11)

    heading(s, M, BODY_TOP + 1.75, CW, "Dry run: adding up TINY by hand (vocab = 65)")
    xl, xr, cw = twocol(s, 0.5)
    code(s, xl, BODY_TOP + 2.1, cw, 2.6, [
        "per block:",
        "  qkv  128 x 384 = 49,152   + 384 bias",
        "  proj 128 x 128 = 16,384   + 128 bias",
        "  mlp  128 x 512 = 65,536   + 512 bias",
        "  mlp  512 x 128 = 65,536   + 128 bias",
        "  ln1 + ln2      =    512",
        "  ------------------------------------",
        "  one block      = 198,272",
    ], size=11.5)
    code(s, xr, BODY_TOP + 2.1, cw, 2.6, [
        "  198,272 x 4 layers  =   793,088",
        "  tok_emb  65 x 128   =     8,320",
        "  pos_emb 128 x 128   =    16,384",
        "  ln_f                =       256",
        "  head (weight-tied)  =         0",
        "  ----------------------------------",
        "  TOTAL               =   818,048",
        "                        ~0.82M  ✓",
    ], size=11.5)

    # ================================================================ FILE 2
    divider(prs, 2, "tokenizer2.py", "Turning text into numbers — two algorithms, from scratch",
            ["CharTokenizer: one integer per character, about 15 lines",
             "BPETokenizer: byte-pair encoding, the same algorithm GPT-4 uses",
             "Identical interface, so nothing downstream cares which you picked"])

    # ---------------------------------------------------------------- 18
    s = slide(prs, "tokenizer2.py", "Why this file has to exist at all")
    box(s, M, BODY_TOP, CW, 0.72, None,
        ["A neural network cannot read letters. It only multiplies numbers."],
        size=18, fill=TINT)

    y = BODY_TOP + 0.95
    chip(s, M + 0.4, y, 2.6, 0.72, "\"hello\"", size=15, fill=WHITE)
    arrow(s, M + 3.15, y + 0.24, 0.8, 0.24)
    chip(s, M + 4.1, y, 3.4, 0.72, "[46, 43, 50, 50, 53]", size=15, fill=TINT2, edge=ORANGE)
    arrow(s, M + 7.65, y + 0.24, 0.8, 0.24)
    chip(s, M + 8.6, y, 3.2, 0.72, "the model", size=15, fill=WHITE)
    label(s, M + 3.15, y + 0.8, 0.8, "encode", 10.5, ORANGE_DK)
    label(s, M + 7.65, y + 0.8, 0.8, "train / run", 10.5, ORANGE_DK)

    y = BODY_TOP + 2.15
    heading(s, M, y, CW, "Two facts students consistently get wrong")
    bullets(s, M, y + 0.35, CW, 1.4, [
        "The tokenizer is **not part of the neural network.** It is built by **counting**, before "
        "the model exists, and it is frozen. Backprop never touches it.",
        "The tokenizer decides `vocab_size`, which decides the size of the embedding table and the "
        "output layer. It is upstream of the whole model.",
    ], size=13.5, gap=10)

    y = BODY_TOP + 3.35
    code(s, M, y, CW, 1.35, [
        "encode(\"hello\")               ->  [46, 43, 50, 50, 53]",
        "decode([46, 43, 50, 50, 53])  ->  \"hello\"",
    ], size=13.5, title="BOTH TOKENIZERS EXPOSE EXACTLY THIS — SO NOTHING ELSE IN ARGPT CARES")

    # ---------------------------------------------------------------- 19
    s = slide(prs, "Algorithm 1  ·  CharTokenizer", "One integer per character. That is the whole idea.")
    code(s, M, BODY_TOP, 7.0, 3.1, [
        "class CharTokenizer:",
        "    def train(self, text):",
        "        chars = sorted(set(text))              # every unique character",
        "        self.itos = dict(enumerate(chars))     # 0 -> 'a'",
        "        self.stoi = {c: i for i, c in self.itos.items()}",
        "        self.vocab_size = len(chars)",
        "",
        "    def encode(self, text):",
        "        return [self.stoi[c] for c in text]",
        "",
        "    def decode(self, ids):",
        "        return \"\".join(self.itos[i] for i in ids)",
    ], size=11.5)

    x2 = M + 7.35
    w2 = CW - 7.35
    heading(s, x2, BODY_TOP, w2, "Line by line")
    bullets(s, x2, BODY_TOP + 0.32, w2, 3.0, [
        "`set(text)` throws away every duplicate → the unique alphabet.",
        "`sorted(...)` makes it **deterministic**. Without it the ids change every run and your "
        "old checkpoint becomes unreadable.",
        "`stoi` = string→int for encoding. `itos` = int→string for decoding. Two dicts, "
        "inverses of each other.",
        "`vocab_size` falls out as `len(chars)`. Nobody chooses it.",
    ], size=12.5, gap=9)

    box(s, M, BODY_TOP + 3.4, CW, 1.3, "Fifteen lines and it is genuinely complete",
        ["No unknown-token handling, no special tokens, no edge cases. Every character it saw in "
         "training gets an id, and every id maps back. This is why we teach it first — "
         "**you can hold the entire algorithm in your head.**"])

    # ---------------------------------------------------------------- 20
    s = slide(prs, "Dry run  ·  CharTokenizer",
              "Real output from  python tokenizer2.py")
    code(s, M, BODY_TOP, CW, 0.75, [
        "sample = \"the cat sat on the mat. the cat ate the rat. \" * 200",
    ], size=12.5, title="STEP 0 — THE TEXT")

    y = BODY_TOP + 0.9
    heading(s, M, y, CW, "Step 1 — sorted(set(text))  gives 12 unique characters")
    chars = ["␣", ".", "a", "c", "e", "h", "m", "n", "o", "r", "s", "t"]
    ids = [str(i) for i in range(12)]
    cell = 0.58
    grid(s, M + 0.95, y + 0.35, cell, [chars], texts=[chars], size=12,
         head_rows=["char"], fills=[[TINT] * 12])
    grid(s, M + 0.95, y + 0.35 + cell, cell, [ids], texts=[ids], size=12, head_rows=["id"],
         fills=[[WHITE] * 12])
    label(s, M + 8.3, y + 0.45, 3.9, "space sorts first —\nASCII 32 beats every letter",
          10.5, GRAY, PP_ALIGN.LEFT)

    y = BODY_TOP + 2.35
    heading(s, M, y, CW, "Step 2 — encode('the cat'), one dictionary lookup per character")
    letters = ["t", "h", "e", "␣", "c", "a", "t"]
    vals = ["11", "5", "4", "0", "3", "2", "11"]
    grid(s, M + 0.95, y + 0.35, cell, [letters], texts=[letters], size=12, head_rows=["in"],
         fills=[[WHITE] * 7])
    grid(s, M + 0.95, y + 0.35 + cell, cell, [vals], texts=[vals], size=12,
         head_rows=["out"], fills=[[TINT2] * 7])
    label(s, M + 5.4, y + 0.4, 6.8,
          "`vocab size: 12`\n`'the cat' -> [11, 5, 4, 0, 3, 2, 11]`\n"
          "`back again -> 'the cat'`", 12, INK, PP_ALIGN.LEFT)

    box(s, M, y + 1.75, CW, 1.0, "The trade-off in one number",
        ["`\"the cat sat on the mat\"` = **22 tokens**. Every letter and every space costs a "
         "token, so with `block_size=128` the model's entire memory is about 20 words."])

    # ---------------------------------------------------------------- 21
    s = slide(prs, "Algorithm 2  ·  BPE", "Byte Pair Encoding — the algorithm GPT-2, GPT-4 and Llama use")
    box(s, M, BODY_TOP, CW, 0.78, None,
        ["Find the two tokens that sit next to each other most often, "
         "glue them into one new token, and repeat."], size=16, fill=TINT)

    y = BODY_TOP + 1.0
    xl, xr, cw = twocol(s, 0.5)
    heading(s, xl, y, cw, "Why it starts at 256, not at 0")
    bullets(s, xl, y + 0.33, cw, 2.2, [
        "Ids 0-255 are **the 256 possible byte values**. Every file on earth is bytes, so every "
        "possible input already has an encoding.",
        "**Nothing is ever out-of-vocabulary** — emoji, Urdu, Chinese, source code, a corrupted "
        "file. Worst case it falls back to raw bytes.",
        "New merged tokens start at id 256 and count up to `vocab_size`.",
    ], size=12.5, gap=9)

    code(s, xr, y, cw, 2.5, [
        "self.vocab = {i: bytes([i]) for i in range(256)}",
        "self.merges = {}          # (a, b) -> new_id",
        "",
        "for new_id in range(256, vocab_size):",
        "    pairs = Counter()",
        "    for chunk in chunks:",
        "        pairs.update(zip(chunk, chunk[1:]))",
        "    best, count = pairs.most_common(1)[0]",
        "    chunks = [_merge(c, best, new_id) for c in chunks]",
    ], size=11, title="tokenizer2.py  ·  BPETokenizer.train")

    y = BODY_TOP + 3.6
    bullets(s, M, y, CW, 1.2, [
        "`zip(chunk, chunk[1:])` is the whole “find adjacent pairs” trick — a list zipped against "
        "itself shifted by one. Same shape idea as the `x`/`y` shift in `data3.py`.",
        "`Counter.most_common(1)` picks the winner. Ties are broken by insertion order, which is "
        "why the merges are reproducible.",
    ], size=13, gap=10)

    # ---------------------------------------------------------------- 22
    s = slide(prs, "Dry run  ·  BPE training", "Watch it invent words — real output, merge by merge")
    code(s, M, BODY_TOP, 7.5, 3.55, [
        "merge 256: 'a' + 't'    -> 'at'     (1,200 times)",
        "merge 257: 't' + 'h'    -> 'th'     (800 times)",
        "merge 258: 'th' + 'e'   -> 'the'    (800 times)",
        "merge 259: ' ' + 'the'  -> ' the'   (799 times)",
        "merge 260: ' ' + 'c'    -> ' c'     (400 times)",
        "merge 261: ' c' + 'at'  -> ' cat'   (400 times)",
        "merge 262: ' ' + 's'    -> ' s'     (200 times)",
        "merge 263: ' s' + 'at'  -> ' sat'   (200 times)",
        "merge 264: ' ' + 'o'    -> ' o'     (200 times)",
        "merge 265: ' o' + 'n'   -> ' on'    (200 times)",
    ], size=12, title="python tokenizer2.py  ·  vocab_size=290, verbose=True")

    x2 = M + 7.85
    w2 = CW - 7.85
    heading(s, x2, BODY_TOP, w2, "Read it out loud to the class")
    bullets(s, x2, BODY_TOP + 0.32, w2, 3.4, [
        "**256** — it discovers `at` first, because `cat / sat / mat / rat` all end in it.",
        "**258** — it builds `the` **out of** `th`, a token it invented one step earlier. "
        "Merges compound.",
        "**259** — the leading space joins in. In BPE, `\" the\"` and `\"the\"` are **different "
        "tokens.** That is why prompt spacing changes real model output.",
        "**261** — `\" cat\"` is now a single token, assembled from `\" c\"` + `\"at\"`. "
        "The tokenizer just learned a word nobody told it about.",
    ], size=12, gap=9)

    box(s, M, BODY_TOP + 3.8, CW, 0.9, "The whole point, in one line",
        ["Common words collapse to **one** token; rare words stay in pieces. That is exactly why "
         "`\"the\"` costs 1 token and a rare name costs 4."])

    # ---------------------------------------------------------------- 23
    s = slide(prs, "Dry run  ·  BPE encoding", "Applying learned merges to new text")
    para(s, M, BODY_TOP, CW, 0.4,
         "Encoding is the same merges replayed **in the order they were learned** — lowest id "
         "first — until none apply.", 13)

    y = BODY_TOP + 0.6
    steps = [
        ("start: raw bytes", "t  h  e  ␣  c  a  t  ␣  s  a  t", "116 104 101 32 99 97 116 32 115 97 116"),
        ("apply 256 (a+t → at)", "t  h  e  ␣  c  at  ␣  s  at", "116 104 101 32 99 256 32 115 256"),
        ("apply 257 (t+h → th)", "th  e  ␣  c  at  ␣  s  at", "257 101 32 99 256 32 115 256"),
        ("apply 258 (th+e → the)", "the  ␣  c  at  ␣  s  at", "258 32 99 256 32 115 256"),
        ("apply 260, 261 (→ ' cat')", "the   cat  ␣  s  at", "258 261 32 115 256"),
        ("apply 262, 263 (→ ' sat')", "the   cat   sat", "258 261 263"),
    ]
    for i, (a, b, c) in enumerate(steps):
        yy = y + i * 0.63
        f = TINT if i == len(steps) - 1 else WHITE
        chip(s, M, yy, 3.1, 0.52, a, fill=f, edge=ORANGE if i == len(steps) - 1 else LINE,
             size=11.5, bold=(i == len(steps) - 1))
        label(s, M + 3.3, yy + 0.12, 4.6, b, 12.5, INK, PP_ALIGN.LEFT)
        label(s, M + 8.1, yy + 0.13, 4.2, c, 11.5, GRAY, PP_ALIGN.LEFT)

    box(s, M, y + 4.0, CW, 0.85, None,
        ["`'the cat sat' -> [258, 261, 263]`   →   `['the', ' cat', ' sat']`   →   "
         "**3 tokens instead of 11.** Char would have used 11; BPE uses 3."], fill=TINT)

    # ---------------------------------------------------------------- 24
    s = slide(prs, "tokenizer2.py  ·  the three details that matter",
              "SPLIT, the cache, and why decode can produce a ?")
    y = BODY_TOP
    code(s, M, y, CW, 0.95, [
        "SPLIT = re.compile(r\"\\s*\\w+|\\s*[^\\s\\w]+|\\s+\")",
    ], size=13, title="1 — THE SPLIT REGEX, RUN BEFORE ANY MERGING")
    para(s, M, y + 1.05, CW, 0.75,
         "Text is chopped into word-ish chunks **first**, so a merge can never glue the end of one "
         "word onto the start of the next. Without it, `\"cat dog\"` could become a token `\"t d\"`, "
         "and the tokenizer would waste ids on nonsense that never generalises. **GPT-2 does exactly "
         "this too.**", 12.5)

    y = BODY_TOP + 1.95
    xl, xr, cw = twocol(s, 0.5)
    code(s, xl, y, cw, 1.35, [
        "if chunk not in self._cache:",
        "    self._cache[chunk] = self._encode_chunk(chunk)",
    ], size=11, title="2 — THE _cache")
    para(s, xl, y + 1.45, cw, 1.3,
         "`_encode_chunk` is a loop over merges — slow in pure Python. Real text repeats the same "
         "words constantly, so memoising each chunk makes encoding a 1 MB file take seconds instead "
         "of minutes.", 12)

    code(s, xr, y, cw, 1.35, [
        "raw = b\"\".join(self.vocab[i] for i in ids)",
        "return raw.decode(\"utf-8\", errors=\"replace\")",
    ], size=11, title="3 — DECODE, AND THE ? CHARACTER")
    para(s, xr, y + 1.45, cw, 1.3,
         "A token can hold **half** of a multi-byte character. If a model stops generating "
         "mid-emoji, those bytes are not valid UTF-8. `errors=\"replace\"` turns them into `?` "
         "instead of crashing your live demo.", 12)

    box(s, M, y + 2.9, CW, 0.95, "Where the tokenizer is stored",
        ["`to_dict` / `from_dict` serialise it to JSON. The **checkpoint stores the tokenizer**, "
         "because the numbers are meaningless without the mapping back to text. Lose the tokenizer "
         "and your trained model is a pile of integers."])

    # ---------------------------------------------------------------- 25
    s = slide(prs, "Char vs BPE", "The scoreboard, with real numbers from this project")
    table(s, M, BODY_TOP, CW, [
        ["", "CharTokenizer", "BPETokenizer"],
        ["Vocabulary size", "**Tiny** — 65 for Shakespeare", "**Bigger** — 1,024 here; real models use 32k-128k"],
        ["Sequence length", "**Long.** \"the cat sat on the mat\" = 22 tokens",
         "**~2.5× shorter.** Same sentence = 6 tokens"],
        ["Full Shakespeare", "1,115,394 tokens", "**453,113 tokens** — the same text in 41% of the space"],
        ["What the model must learn",
         "**Spelling from scratch.** It burns capacity learning that t-h-e is a thing.",
         "Words arrive **pre-chunked.** Capacity goes to meaning, not spelling."],
        ["Effective memory (block 128)", "~20-25 words of history", "~90-100 words of history"],
        ["Out-of-vocabulary", "A never-before-seen character breaks it", "**Impossible** — it falls back to raw bytes"],
        ["Build time", "Instant", "~90 seconds on full Shakespeare (pure Python)"],
        ["Embedding table cost", "65 × n_embd — negligible", "1,024 × n_embd — noticeable at small n_embd"],
        ["Best for", "Teaching, tiny models, small alphabets", "**Everything real.** This is what production uses."],
    ], widths=[2.5, 4.4, 5.3], size=10.8, row_h=0.475, head_h=0.34)

    para(s, M, 6.42, CW, 0.4,
         "**The interface is identical**, so switching is one CLI word: "
         "`--tokenizer char` vs `--tokenizer bpe`. Nothing in the model, training or generation "
         "code changes. (Callback to Session 4's pluggable LLM interface.)", 12, GRAY)

    # ---------------------------------------------------------------- 26
    s = slide(prs, "Beyond our two", "The other tokenizer algorithms, and who uses them")
    table(s, M, BODY_TOP, CW, [
        ["Algorithm", "How it decides what to merge / split", "Trade-off vs our BPE", "Used by"],
        ["**Byte-level BPE** *(ours)*",
         "Greedily merge the most **frequent** adjacent pair. Start from 256 bytes.",
         "Simple, fast at inference, never OOV. Purely frequency-driven — no notion of "
         "whether a merge is *linguistically* sensible.",
         "GPT-2, GPT-3, GPT-4, Llama, Mistral"],
        ["**WordPiece**",
         "Merge the pair that most increases the **likelihood** of the corpus, not the raw count "
         "— roughly `count(ab) / (count(a)·count(b))`.",
         "Prefers merges that are genuinely informative over merely common. Slightly better "
         "subwords, slower to train, marks continuations with `##`.",
         "BERT, DistilBERT, Electra"],
        ["**Unigram LM**",
         "Start with a **huge** candidate vocabulary and iteratively **delete** the tokens whose "
         "removal hurts corpus likelihood least. Top-down, not bottom-up.",
         "Can give several valid segmentations of a word with probabilities, which enables "
         "**subword regularisation** (train-time augmentation). Slower to build.",
         "T5, ALBERT, XLNet, mBART"],
        ["**SentencePiece**",
         "Not an algorithm — a **library** that runs BPE or Unigram directly on raw text, treating "
         "space as a normal character (`▁`).",
         "Language-agnostic: works on Japanese/Thai with no whitespace. Fully reversible. "
         "The usual packaging for Unigram.",
         "T5, Llama 1/2, Gemma, most multilingual models"],
        ["**tiktoken-style regex BPE**",
         "Byte-level BPE plus a much more careful pre-split regex (digits grouped, contractions, "
         "leading spaces handled explicitly).",
         "Better handling of numbers and code. Our `SPLIT` regex is the simple ancestor of this.",
         "GPT-3.5, GPT-4, gpt-oss"],
        ["**Tokenizer-free / byte-latent**",
         "Delete the tokenizer entirely. Feed raw bytes and let a small learned network group them "
         "into dynamic patches.",
         "No vocabulary, no OOV, no tokenizer bugs, fair across languages. Costs more compute per "
         "character. Active research, not yet standard.",
         "ByT5, MegaByte, BLT"],
    ], widths=[2.0, 3.9, 4.1, 2.2], size=9.7, row_h=0.83, head_h=0.34)

    # ================================================================ FILE 3
    divider(prs, 3, "data3.py", "The reusable one — text in, train.bin and val.bin out",
            ["It imports nothing from this project except the two tokenizers",
             "y is x shifted one place left — and that shift is the entire training signal",
             "Why raw binary, and not JSON, not CSV, not a vector database"])

    # ---------------------------------------------------------------- 28
    s = slide(prs, "data3.py", "Three jobs, and one rule it obeys")
    y = BODY_TOP
    jobs = [("download(name)", "fetch the raw .txt once and cache it on disk",
             ["shakespeare  1.1 MB", "tinystories  19 MB", "coding       11.6 MB", "custom       your file"]),
            ("prepare(...)", "build the tokenizer, encode everything, split 90/10",
             ["-> tokenizer.json", "-> train.bin", "-> val.bin"]),
            ("get_batch(...)", "hand back random windows of tokens during training",
             ["x = tokens i .. i+127", "y = tokens i+1 .. i+128", "called ~2,000 times"])]
    xw = (CW - 0.8) / 3
    for i, (t, sub, lines) in enumerate(jobs):
        x = M + i * (xw + 0.4)
        chip(s, x, y, xw, 0.55, t, fill=ORANGE, edge=None, color=WHITE, size=13)
        label(s, x + 0.1, y + 0.68, xw - 0.2, sub, 11.5, GRAY)
        code(s, x, y + 1.22, xw, 1.5, lines, size=11)

    y = BODY_TOP + 3.0
    box(s, M, y, CW, 1.05, "The rule this file obeys",
        ["It imports **nothing** else from this project — no config, no model. Every function takes "
         "plain numbers and strings. **That is the only reason you can copy it into your next "
         "project unchanged.** Any model that reads `train.bin` works with this file."])

    para(s, M, y + 1.25, CW, 0.6,
         "For a pretraining LLM the dataset is just **one big pile of text**. No labels, no "
         "question/answer pairs. This is **self-supervised** learning: the text *is* its own answer "
         "key, because the correct next token is simply the token that actually came next.", 13)

    # ---------------------------------------------------------------- 29
    s = slide(prs, "data3.py  ·  the shift",
              "The aha moment of the whole session")
    code(s, M, BODY_TOP, CW, 1.2, [
        "x = data[i     : i + block_size]      # \"the cat sat on the ma\"",
        "y = data[i + 1 : i + 1 + block_size]  # \"he cat sat on the mat\"",
    ], size=13.5, title="get_batch, THE TWO LINES THAT ARE THE ENTIRE TRAINING SIGNAL")

    y = BODY_TOP + 1.4
    heading(s, M, y, CW, "Dry run — one window, char tokenizer, block_size = 8")
    cell = 0.66
    xg = M + 1.0
    xs = ["t", "h", "e", "␣", "c", "a", "t", "␣"]
    ys = ["h", "e", "␣", "c", "a", "t", "␣", "s"]
    grid(s, xg, y + 0.38, cell, [xs], texts=[xs], size=13, head_rows=["x"],
         fills=[[WHITE] * 8])
    grid(s, xg + cell / 2, y + 0.38 + cell + 0.22, cell, [ys], texts=[ys], size=13,
         head_rows=["y"], fills=[[TINT] * 8])
    label(s, xg + 5.9, y + 0.42, 6.0,
          "**y is x, moved one place left.**\nNothing else happened.", 13, INK, PP_ALIGN.LEFT)
    label(s, xg + 5.9, y + 1.15, 6.0,
          "At position 0 the model sees “t” and must predict “h”.\n"
          "At position 6 it sees “the cat ” and must predict “s”.",
          12, GRAY, PP_ALIGN.LEFT)

    y = BODY_TOP + 3.65
    box(s, M, y, CW, 1.45, "Why this is such a big deal",
        ["There is **no separate answers file.** The shift manufactures `block_size` supervised "
         "prediction problems out of every single window of text, for free. One sequence of 128 "
         "tokens is **128 training examples**, not one.",
         "That is where the “self” in self-supervised comes from — and it is why the causal mask "
         "(file 4) matters so much: the mask is what lets all 128 be learned in **one** forward pass."])

    # ---------------------------------------------------------------- 30
    s = slide(prs, "data3.py  ·  why .bin",
              "Raw uint16 numbers on disk. No format, no library, no parsing.")
    code(s, M, BODY_TOP, CW, 1.35, [
        "assert tok.vocab_size < 65536, \"vocab too big for uint16 - use uint32\"",
        "ids = np.array(tok.encode(text), dtype=np.uint16)",
        "n = int(0.9 * len(ids))",
        "ids[:n].tofile(\".../train.bin\");   ids[n:].tofile(\".../val.bin\")",
    ], size=12, title="prepare(), THE FOUR LINES THAT WRITE THE DATASET")

    y = BODY_TOP + 1.55
    heading(s, M, y, CW, "What is actually on disk — every token is exactly 2 bytes")
    cell = 0.72
    ids6 = ["46", "43", "50", "50", "53", "1"]
    bytes6 = ["2E 00", "2B 00", "32 00", "32 00", "35 00", "01 00"]
    grid(s, M + 1.15, y + 0.38, cell, [ids6], texts=[ids6], size=12, head_rows=["token id"],
         fills=[[TINT] * 6])
    grid(s, M + 1.15, y + 0.38 + cell, cell, [bytes6], texts=[bytes6], size=9,
         head_rows=["on disk"], fills=[[WHITE] * 6])
    label(s, M + 6.1, y + 0.42, 6.2,
          "token #500,000 lives at byte offset **1,000,000**.\n"
          "Exactly. Always. No searching, no parsing.", 12.5, INK, PP_ALIGN.LEFT)
    label(s, M + 6.1, y + 1.15, 6.2,
          "`np.fromfile(path, dtype=np.uint16)` hands you a\nnumpy array in one call — already in the "
          "exact\nmemory layout a tensor wants.", 11.5, GRAY, PP_ALIGN.LEFT)

    y = BODY_TOP + 3.5
    bullets(s, M, y, CW, 1.3, [
        "**Fixed width buys random access.** `get_batch` needs `data[i : i+128]` for a *random* i, "
        "thousands of times. Fixed-width means that is a pointer arithmetic — O(1).",
        "**uint16 holds 0-65,535**, which covers char (65) and our BPE (1,024) with room to spare. "
        "A Llama-style 128k vocab would need `uint32` — the assert catches this for you.",
    ], size=13, gap=10)

    # ---------------------------------------------------------------- 31
    s = slide(prs, "Why not JSON?  Why not CSV or Parquet?",
              "The same 1,115,394 Shakespeare tokens, four ways")
    table(s, M, BODY_TOP, CW, [
        ["Format", "Size on disk", "To read token #500,000 you must…", "Verdict"],
        ["**train.bin** (uint16)", "**2.23 MB**",
         "seek to byte 1,000,000 and read 2 bytes. **O(1).**",
         "**What we use.** Zero parsing, random access, memory-mappable if the file exceeds RAM."],
        ["JSON `[46, 43, 50, …]`", "~4.46 MB",
         "parse the **entire file** from the beginning — numbers are variable-width, so byte "
         "offset tells you nothing.",
         "2× the size, and `json.loads` builds a Python list of **1.1M int objects ≈ 40 MB of "
         "RAM** with pointer chasing on every access."],
        ["CSV", "~4.5 MB",
         "same problem — parse from the start, split on commas.",
         "All of JSON's costs plus a text encoder/decoder. Built for spreadsheets, not tensors."],
        ["Parquet / Arrow", "~1.5 MB (compressed)",
         "decompress the row group containing it, then index.",
         "Genuinely good for **large, columnar, typed** datasets and it is what HuggingFace uses at "
         "scale. Overkill here: a library dependency and a decode step to save 0.7 MB."],
    ], widths=[2.1, 1.5, 4.0, 4.6], size=10.4, row_h=1.0, head_h=0.34)

    box(s, M, BODY_TOP + 4.5, CW, 1.0, "The honest summary for the class",
        ["We are not storing a *dataset* in the database sense. We are storing **one enormous "
         "array of small integers** that we slice at random offsets a few thousand times a minute. "
         "For that job, the fastest format is the one with **no format at all.**"])

    # ---------------------------------------------------------------- 32
    s = slide(prs, "Why not a vector database?",
              "The question every student asks after Session 3 — and it's a good one")
    y = BODY_TOP
    xl, xr, cw = twocol(s, 0.5)
    box(s, xl, y, cw, 2.5, "What a vector DB is built to do",
        ["Store **embeddings** and answer one question: *“which stored items are most similar to "
         "this one?”* — via approximate nearest-neighbour search.",
         "It is an **unordered set** with a similarity index. There is no such thing as "
         "“the next row”.",
         "That is exactly right for **RAG at inference time**, which is what Session 3 built."],
        fill=WHITE)
    rule(s, xl + 0.05, y + 0.02, cw - 0.1, ORANGE, 0.03)
    box(s, xr, y, cw, 2.5, "What pretraining actually needs",
        ["**Exact, contiguous order.** Token 5 must be followed by token 6 — the entire training "
         "signal is “what came next”. Order *is* the label.",
         "A slice of 128 consecutive tokens, a few thousand times, as fast as memory allows.",
         "Nothing is ever searched. Nothing is ever compared for similarity."])

    y = BODY_TOP + 2.75
    bullets(s, M, y, CW, 2.3, [
        "**The embeddings don't exist yet.** `tok_emb` is *learned by training*. Vectors are an "
        "**output** of this process, not an input to it. Putting them in a DB beforehand is backwards.",
        "**Speed.** An ANN lookup is milliseconds; a numpy slice is nanoseconds. At 2,000 steps × 32 "
        "sequences you would add hours of latency to a three-minute job — to answer a question we "
        "never ask.",
        "**Right tool, wrong stage.** Vector DBs are for *retrieval at inference*: give the model "
        "facts it was never trained on. Pretraining is *compression into weights*. Different job, "
        "different data structure.",
    ], size=13.5, gap=13)

    # ---------------------------------------------------------------- 33
    s = slide(prs, "data3.py  ·  get_batch and the honesty check",
              "How one batch is assembled, and what val.bin is really for")
    code(s, M, BODY_TOP, 7.4, 2.3, [
        "starts = torch.randint(len(data) - block_size - 1, (batch_size,))",
        "x = torch.stack([torch.from_numpy(data[i : i+block_size]...)",
        "                 for i in starts])",
        "y = torch.stack([torch.from_numpy(data[i+1 : i+1+block_size]...)",
        "                 for i in starts])",
        "return x.to(device), y.to(device)",
    ], size=11, title="32 RANDOM START POINTS, 32 WINDOWS, ONE TENSOR")

    x2 = M + 7.75
    w2 = CW - 7.75
    bullets(s, x2, BODY_TOP, w2, 2.4, [
        "`randint` picks **random** start points every step — the model never sees the file in "
        "order, so it can't learn position-in-file as a shortcut.",
        "`- block_size - 1` keeps the `y` slice inside the array.",
        "Output shapes: `x` and `y` are both **(32, 128)**.",
    ], size=12, gap=9)

    y = BODY_TOP + 2.6
    xl, xr, cw = twocol(s, 0.5)
    box(s, xl, y, cw, 1.05, "The _loaded cache",
        ["Each `.bin` is read into memory **once** and kept in a module-level dict. Shakespeare is "
         "2 MB — this costs nothing and beats re-reading disk 2,000 times."], fill=WHITE)
    rule(s, xl + 0.05, y + 0.02, cw - 0.1, ORANGE, 0.03)
    box(s, xr, y, cw, 1.05, "The 90 / 10 split",
        ["The last 10% becomes `val.bin` — text the model **never trains on**. It is the "
         "experiment's control group."])

    box(s, M, y + 1.3, CW, 1.4, "The lie detector",
        ["**Both losses falling** → the model is learning the *language*.",
         "**Train falls, val rises or flattens** → the model is **memorising the training text**. "
         "With 1 MB of data and 0.8M parameters this is a real risk, and watching two numbers "
         "instead of one is how you catch it live, on screen, in front of the class."])
