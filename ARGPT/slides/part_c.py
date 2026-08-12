"""Slides 77-end: files 7-9, modern_upgrades10.py, scaling, FAQ, closing."""

from pptx.enum.text import PP_ALIGN
from theme import (BODY_TOP, CW, GRAY, GRAY_LT, INK, LINE, M, ORANGE, ORANGE_DK,
                   TINT, TINT2, WHITE, arrow, box, bullets, chip, code, divider,
                   grid, heading, label, para, rule, slide, table, twocol)


def build(prs):
    # ============================================================= FILES 7-9
    divider(prs, 7, "modal_app7.py", "The same code, on a real GPU",
            ["train5.py's train() is imported and called exactly as on your laptop",
             "Only WHERE it runs changes — .remote() is the entire difference",
             "An L4 costs $0.80/hour, billed by the second. A full run is ~13 cents."])

    # ---------------------------------------------------------------- 78
    s = slide(prs, "modal_app7.py", "Count how many lines of this file are about machine learning")
    code(s, M, BODY_TOP, 7.4, 2.85, [
        "@app.function(image=image, gpu=\"L4\", volumes={\"/ckpt\": vol},",
        "              timeout=60 * 60)",
        "def train_on_gpu(dataset=\"shakespeare\", ...):",
        "    from config1 import SMALL",
        "    from data3 import prepare",
        "    from train5 import train",
        "",
        "    cfg = replace(SMALL, dataset=dataset, data_dir=\"/ckpt/data\", ...)",
        "    prepare(dataset, tokenizer, data_dir=\"/ckpt/data\")",
        "    train(cfg)          # <- the exact same function, not a copy",
        "    vol.commit()        # <- WITHOUT THIS THE CHECKPOINT IS LOST",
    ], size=11)

    x2 = M + 7.75
    w2 = CW - 7.75
    heading(s, x2, BODY_TOP, w2, "The answer: one")
    para(s, x2, BODY_TOP + 0.32, w2, 1.0,
         "`train(cfg)`. Everything else is infrastructure. **Nothing about ARGPT changes to run on "
         "a GPU** — that is the lesson of this file.", 12.5)

    table(s, x2, BODY_TOP + 1.5, w2, [
        ["Piece", "What it is"],
        ["`image`", "the recipe for the machine — Debian + Python 3.11 + torch. Built **once** and "
                    "cached."],
        ["`vol`", "a disk that **survives** after the container is destroyed."],
        ["`.remote()`", "runs on Modal's GPU. `.local()` would run right here. Same function."],
        ["`timeout=3600`", "Modal's default is 300 s. A training run is longer."],
    ], widths=[1.3, 3.4], size=10.5, row_h=0.62)

    y = BODY_TOP + 3.15
    box(s, M, y, 7.4, 1.55, "vol.commit() is not optional",
        ["A Modal container is destroyed when the function returns. Anything written to its local "
         "filesystem **dies with it**. `vol.commit()` flushes the checkpoint to the persistent "
         "Volume. Forget it and your ten-minute GPU run produces nothing — and the error message "
         "is silence."])

    # ---------------------------------------------------------------- 79
    s = slide(prs, "modal_app7.py  ·  the practical bits",
              "Cost, the image build, and the trap that bites everyone once")
    y = BODY_TOP
    xw = (CW - 0.8) / 3
    for i, (t, big, sub) in enumerate([
        ("L4 GPU", "$0.80 / hr", "billed **by the second**, not by the month"),
        ("A 10-minute run", "≈ 13 cents", "the whole class fits in the free tier"),
        ("Modal free tier", "$30 / month", "≈ **37 hours** of L4 time"),
    ]):
        x = M + i * (xw + 0.4)
        chip(s, x, y, xw, 0.5, t, fill=ORANGE, edge=None, color=WHITE, size=12.5)
        label(s, x, y + 0.65, xw, big, 26, INK)
        label(s, x, y + 1.35, xw, sub, 11.5, GRAY)

    y = BODY_TOP + 2.05
    box(s, M, y, CW, 1.7, "Never name a file modal.py — teach this deliberately",
        ["A file called `modal.py` in your folder **shadows the** `modal` **package.** Python checks "
         "the current directory before site-packages, so `import modal` imports *the student's own "
         "file*, and the very first line fails with:",
         "`AttributeError: module 'modal' has no attribute 'App'`",
         "It is baffling if you have never seen it, and it is a genuine lesson about Python's "
         "import order. That is why this file is `modal_app7.py`."])

    y = BODY_TOP + 3.95
    bullets(s, M, y, CW, 1.5, [
        "The first `modal run` downloads **~2.3 GB of PyTorch** into the image. Minutes, **once**. "
        "Run it before class, never live.",
        "Check the checkpoint survived: `modal volume ls argpt-checkpoints`. "
        "Pull it down: `modal volume get argpt-checkpoints codingsmallbpe.pt out/`",
    ], size=13, gap=10)

    # ---------------------------------------------------------------- 80
    divider(prs, 8, "serve8.py", "You become the API",
            ["Sessions 1-6 you called somebody else's API. Now you are the API.",
             "@modal.enter() runs once per container, not once per request",
             "An idle model costs nothing, because the container scales to zero"])

    # ---------------------------------------------------------------- 81
    s = slide(prs, "serve8.py  ·  @modal.enter()", "The one idea that matters in this file")
    code(s, M, BODY_TOP, 6.9, 2.7, [
        "@app.cls(image=image, gpu=\"L4\", volumes={\"/ckpt\": vol},",
        "         scaledown_window=300)",
        "class ARGPTServer:",
        "",
        "    @modal.enter()                     # ONCE per container",
        "    def load(self):",
        "        self.model, self.tok = load_argpt(CKPT, device=\"cuda\")",
        "",
        "    @modal.fastapi_endpoint(method=\"POST\")",
        "    def chat(self, item: dict):        # once per REQUEST",
        "        text = generate(self.model, self.tok, ...)",
    ], size=11)

    x2 = M + 7.25
    w2 = CW - 7.25
    heading(s, x2, BODY_TOP, w2, "With @modal.enter()")
    y = BODY_TOP + 0.35
    for i, (lbl, w, f) in enumerate([("load weights", 2.2, ORANGE), ("req 1", 0.5, TINT2),
                                     ("req 2", 0.5, TINT2), ("req 3", 0.5, TINT2)]):
        pass
    xx = x2
    chip(s, xx, y, 2.1, 0.45, "load weights  4s", fill=ORANGE, edge=None, color=WHITE, size=10.5)
    xx += 2.2
    for i in range(4):
        chip(s, xx, y, 0.62, 0.45, "0.3s", fill=TINT2, edge=ORANGE, size=10)
        xx += 0.68

    heading(s, x2, y + 0.75, w2, "Without it — load inside chat()")
    yy = y + 1.1
    xx = x2
    for i in range(3):
        chip(s, xx, yy, 1.55, 0.45, "load + 0.3s", fill=WHITE, edge=ORANGE, size=10)
        xx += 1.62
    label(s, x2, yy + 0.55, w2, "every single request pays the 4-second load again",
          11, ORANGE_DK, PP_ALIGN.LEFT)

    box(s, x2, BODY_TOP + 2.35, w2, 2.35, "The exercise worth setting",
        ["Delete `@modal.enter()`, move the load into `chat()`, and time both. That comparison "
         "teaches more about server design than any explanation you could give — and it "
         "generalises to every model server the students will ever write."])

    y = BODY_TOP + 3.05
    code(s, M, y, 6.9, 1.35, [
        "curl -X POST <your-url> \\",
        "  -H \"Content-Type: application/json\" \\",
        "  -d '{\"prompt\": \"ROMEO:\", \"max_tokens\": 200}'",
    ], size=11.5, title="TESTING IT")

    # ---------------------------------------------------------------- 82
    s = slide(prs, "serve8.py  ·  scaling to zero", "Why an idle model is free, and what it costs you")
    y = BODY_TOP
    stages = [("request arrives", "container starts"), ("cold start", "~10-20s, weights load"),
              ("serving", "0.3s per request"), ("5 min idle", "container stops"),
              ("billing stops", "$0.00")]
    xw = 2.1
    x = M + 0.3
    for i, (a, b) in enumerate(stages):
        chip(s, x, y, xw, 0.72, a, sub=b, size=11.5,
             fill=TINT if i in (0, 4) else WHITE)
        if i < len(stages) - 1:
            arrow(s, x + xw + 0.03, y + 0.26, 0.22, 0.2)
        x += xw + 0.28

    y = BODY_TOP + 1.3
    xl, xr, cw = twocol(s, 0.5)
    box(s, xl, y, cw, 1.65, "scaledown_window=300",
        ["Stay warm for 5 minutes after the last request, then stop. **Billing stops with it.** "
         "The trade you accept: the first request after an idle period pays a cold start."],
        fill=WHITE)
    rule(s, xl + 0.05, y + 0.02, cw - 0.1, ORANGE, 0.03)
    box(s, xr, y, cw, 1.65, "One deploy serves ONE checkpoint",
        ["`CKPT = \"/ckpt/shakespearesmallchar.pt\"` is a constant. Change it and re-run "
         "`modal deploy serve8.py` to put a different model behind the URL."])

    y = BODY_TOP + 3.2
    table(s, M, y, CW, [
        ["Command", "What you get", "When to use it"],
        ["`modal serve serve8.py`", "a **temporary** URL that hot-reloads as you edit the file",
         "while you are building — you will use this most"],
        ["`modal deploy serve8.py`", "a **permanent** URL that survives your laptop closing",
         "when you are done and want the agent in file 9 to call it"],
    ], widths=[2.8, 5.0, 4.4], size=11, row_h=0.55)

    para(s, M, y + 1.9, CW, 0.5,
         "The URL looks like `https://<your-workspace>--argpt-serve-argptserver-chat.modal.run` "
         "and is printed when you deploy.", 12, GRAY)

    # ---------------------------------------------------------------- 83
    divider(prs, 9, "use_from_agent9.py", "Full circle — your agent calls your model",
            ["ARGPT is behind a URL now, exactly like Groq was in Session 6",
             "So it drops into exactly the same LangChain slot",
             "And then the honest conversation about what it cannot do"])

    # ---------------------------------------------------------------- 84
    s = slide(prs, "use_from_agent9.py", "The same slot Groq's Llama sat in")
    code(s, M, BODY_TOP, 7.2, 2.9, [
        "class ARGPT(LLM):",
        "    url: str",
        "    temperature: float = 0.8",
        "",
        "    def _call(self, prompt, stop=None, run_manager=None, **kwargs):",
        "        return ask_argpt(self.url, prompt, self.max_tokens, self.temperature)",
        "",
        "chain = (PromptTemplate.from_template(\"{character}:\")",
        "         | build_langchain_llm(url)",
        "         | StrOutputParser())",
        "chain.invoke({\"character\": \"JULIET\"})",
    ], size=10.5)

    x2 = M + 7.55
    w2 = CW - 7.55
    y = BODY_TOP
    chip(s, x2, y, w2, 0.5, "PromptTemplate", size=12)
    arrow(s, x2 + w2 / 2 - 0.09, y + 0.56, 0.18, 0.22, right=False)
    chip(s, x2, y + 0.86, w2, 0.5, "your ARGPT, on Modal", fill=ORANGE, edge=None,
         color=WHITE, size=12)
    arrow(s, x2 + w2 / 2 - 0.09, y + 1.42, 0.18, 0.22, right=False)
    chip(s, x2, y + 1.72, w2, 0.5, "StrOutputParser", size=12)
    label(s, x2, y + 2.35, w2, "LangChain neither knows nor cares that this model\n"
                               "is 10M parameters and was trained an hour ago", 11.5, GRAY)

    y = BODY_TOP + 3.2
    box(s, M, y, CW, 1.5, "Why this slide is the point of the whole session",
        ["In Session 6 the LLM in that slot was somebody else's, behind somebody else's API key, "
         "priced by somebody else. It is now **yours** — trained by you, on data you chose, "
         "deployed on a URL you own. The interface did not change. **That is what an interface is "
         "for.**"])

    # ---------------------------------------------------------------- 85
    s = slide(prs, "The honest boundary", "What we built, and what we deliberately did not")
    xl, xr, cw = twocol(s, 0.5)
    box(s, xl, BODY_TOP, cw, 2.05, "What ARGPT can do",
        ["**Continue text** in the style it was trained on. Feed it `\"ROMEO:\"` and it produces "
         "Shakespeare-shaped output. Feed the coding model `def quicksort(` and it produces "
         "Python-shaped output.",
         "That is pretraining, and it works."], fill=WHITE)
    rule(s, xl + 0.05, BODY_TOP + 0.02, cw - 0.1, ORANGE, 0.03)
    box(s, xr, BODY_TOP, cw, 2.05, "What it cannot do",
        ["**Follow instructions.** Ask it “what is 2+2?” and it will continue the *sentence*, not "
         "answer the *question*. It cannot use tools, hold a conversation, or refuse anything.",
         "Feed it a **seed**, not a **question**."])

    y = BODY_TOP + 2.35
    heading(s, M, y, CW, "The four things standing between ARGPT and ChatGPT")
    table(s, M, y + 0.35, CW, [
        ["Layer", "What it is", "Did we build it?"],
        ["0 — **Pretraining**", "next-token prediction on raw text. The engine.", "**Yes** — that is this session"],
        ["1 — **Scale**", "~10⁵-10⁶× more parameters, ~10⁶× more and better data", "No"],
        ["2 — **Instruction tuning (SFT)**", "fine-tune on instruction→response pairs. **This is "
                                             "the step that turns “continues text” into “follows "
                                             "commands”.**", "No — but see `coding_llm/`"],
        ["3 — **Preference alignment**", "RLHF or DPO: make answers match what humans prefer",
         "No"],
        ["4 — **Reasoning RL**", "train it to think in steps before answering. The biggest jump of "
                                 "2024-25, and it is **not architecture**.", "No"],
    ], widths=[2.6, 6.6, 3.0], size=10.8, row_h=0.6)

    box(s, M, y + 3.9, CW, 0.95, None,
        ["**You built layer 0 — the foundation everything else is bolted onto.** "
         "That gap between “predicts text” and “follows instructions” is exactly what the agent "
         "sessions were working around. Now you know what was underneath."], fill=TINT)

    # ============================================================== FILE 10
    divider(prs, 10, "modern_upgrades10.py", "What Llama 3, GPT-4 and GPT-5 changed",
            ["model4.py is a GPT-2 — 2019 architecture, and the right thing to learn first",
             "Modern models kept the exact same skeleton and swapped three parts",
             "Then added a second layer of tricks the file does not cover — we will"])

    # ---------------------------------------------------------------- 87
    s = slide(prs, "The three swaps", "Same skeleton. Three components replaced.")
    table(s, M, BODY_TOP, CW, [
        ["We used  *(2019)*", "Modern swap", "What actually changed", "Worth"],
        ["`nn.LayerNorm`", "**RMSNorm**",
         "Drop the mean-centring step. Somebody tried removing it, nothing got worse, and it ran "
         "faster. Half the parameters, one less pass over the data.",
         "speed"],
        ["learned `pos_emb`", "**RoPE**",
         "Instead of looking up a position vector, **rotate** each token's q and k by an angle "
         "based on its position. Stores **zero** parameters and generalises past the trained length.",
         "long context"],
        ["GELU MLP", "**SwiGLU**",
         "Add a second parallel path that acts as a **gate** — one path decides the content, the "
         "other decides how much of it gets through, per neuron.",
         "quality"],
    ], widths=[2.0, 1.8, 7.4, 1.0], size=11, row_h=0.95, head_h=0.36)

    y = BODY_TOP + 3.5
    box(s, M, y, CW, 1.3, "The reassurance students need at this point",
        ["Notice what did **not** change: attention, the residual stream, the causal mask, the "
         "training loop, the next-token objective. **The core you learned in model4.py is still "
         "the core of every frontier model in 2025.** These are component swaps, not a new idea.",
         "On a model this small you will barely measure a difference. They matter at billions of "
         "parameters and 100k-token contexts."])

    # ---------------------------------------------------------------- 88
    s = slide(prs, "Upgrade 1  ·  RMSNorm", "LayerNorm minus the centring step")
    code(s, M, BODY_TOP, CW, 1.2, [
        "LayerNorm:  (x - mean) / std * weight + bias",
        "RMSNorm:    x / sqrt(mean(x^2)) * weight",
    ], size=13.5)

    y = BODY_TOP + 1.4
    heading(s, M, y, CW, "Dry run on x = [3, −1, 4, 2]")
    cell = 0.66
    xg = M + 1.6
    rows = [["3", "-1", "4", "2"]]
    grid(s, xg, y + 0.38, cell, rows, texts=rows, size=13, head_rows=["x"], fills=[[WHITE] * 4])
    ln = [["0.535", "-1.604", "1.069", "0.000"]]
    grid(s, xg, y + 0.38 + cell, cell, ln, texts=ln, size=9, head_rows=["LayerNorm"],
         fills=[[WHITE] * 4])
    rn = [["1.095", "-0.365", "1.461", "0.730"]]
    grid(s, xg, y + 0.38 + 2 * cell, cell, rn, texts=rn, size=9, head_rows=["RMSNorm"],
         fills=[[TINT] * 4])

    label(s, xg + 3.1, y + 0.42, 7.0,
          "mean = 2.0    std = 1.871    **rms = 2.739**", 12.5, INK, PP_ALIGN.LEFT)
    label(s, xg + 3.1, y + 0.9, 7.0,
          "LayerNorm re-centres on zero (note the 2 → 0.000).\n"
          "RMSNorm only rescales — it keeps the sign structure and never computes a mean at all.",
          12, GRAY, PP_ALIGN.LEFT)
    label(s, xg + 3.1, y + 1.72, 7.0,
          "Parameters for dim = 128:  LayerNorm **256** (weight + bias) vs RMSNorm **128** "
          "(weight only).", 12, ORANGE_DK, PP_ALIGN.LEFT)

    y = BODY_TOP + 3.6
    bullets(s, M, y, CW, 1.3, [
        "It is a **drop-in swap** in `model4.py` — replace `nn.LayerNorm` with `RMSNorm` and "
        "nothing else changes.",
        "Why it matters at scale: normalisation runs `2 × n_layer` times per forward pass. On a "
        "100-layer model, halving its cost and removing a full reduction pass over the data is "
        "real money.",
    ], size=13, gap=10)

    # ---------------------------------------------------------------- 89
    s = slide(prs, "Upgrade 2  ·  RoPE", "Rotate the vector instead of looking up a position")
    para(s, M, BODY_TOP, CW, 0.45,
         "`model4.py` says *“position 5 gets vector #5”*, learned from scratch. RoPE instead "
         "**rotates** each token's q and k by an angle proportional to its position. "
         "Nothing is learned and nothing is stored.", 13)

    y = BODY_TOP + 0.8
    heading(s, M, y, 7.0, "The same vector [1, 0], rotated by position")
    cell = 0.95
    poss = [["pos 0", "pos 1", "pos 2", "pos 3"]]
    vecs = [["[1.00,\n0.00]", "[0.54,\n0.84]", "[-0.42,\n0.91]", "[-0.99,\n0.14]"]]
    grid(s, M + 1.2, y + 0.42, cell, poss, texts=poss, size=10, fills=[[WHITE] * 4])
    grid(s, M + 1.2, y + 0.42 + cell, cell, vecs, texts=vecs, size=8.5, fills=[[TINT] * 4])
    label(s, M + 1.2, y + 2.4, 3.8, "one radian per position, for this frequency", 10.5, GRAY)

    code(s, M, y + 2.85, 7.0, 1.4, [
        "freqs  = 1.0 / (10000 ** (arange(0, hs, 2) / hs))",
        "angles = outer(arange(max_len), freqs)",
        "cos, sin = angles.cos(), angles.sin()",
    ], size=11, title="rope_tables — PRECOMPUTED ONCE, REUSED FOREVER")

    x2 = M + 7.4
    w2 = CW - 7.4
    bullets(s, x2, y, w2, 4.3, [
        "Each **pair** of numbers in the vector is treated as a point on a circle and rotated: "
        "`(x₁cosθ − x₂sinθ, x₁sinθ + x₂cosθ)`.",
        "**Low dimensions rotate fast, high dimensions rotate slowly** — so the full pattern of "
        "angles is unique for every position, like the hands of a clock.",
        "Zero trainable parameters. For `block_size=512, n_embd=128`, learned position embeddings "
        "cost **65,536 parameters**. RoPE costs **0**.",
        "It applies to `q` and `k` **inside** attention, not to `x` at the input — which is why it "
        "needs edits inside `SelfAttention` rather than a one-line swap.",
    ], size=12, gap=10)

    # ---------------------------------------------------------------- 90
    s = slide(prs, "Why RoPE gives long context", "The proof, in five lines of arithmetic")
    para(s, M, BODY_TOP, CW, 0.45,
         "When a query at position **m** meets a key at position **n**, the two rotations partly "
         "cancel. What survives depends only on the **gap (m − n)** — never on the absolute "
         "positions.", 13)

    y = BODY_TOP + 0.75
    table(s, M, y, 8.6, [
        ["query at", "key at", "gap", "attention score"],
        ["position 5", "position 3", "2", "**−0.4161**"],
        ["position 30", "position 28", "2", "**−0.4161**"],
        ["position 3,005", "position 3,003", "2", "**−0.4161**"],
        ["position 5", "position 4", "1", "+0.5403"],
        ["position 5", "position 0", "5", "+0.2837"],
    ], widths=[2.2, 2.2, 1.0, 2.2], size=11.5, row_h=0.4,
        aligns=["l", "l", "c", "c"])

    box(s, M + 8.95, y, CW - 8.95, 2.75, "Identical. Exactly.",
        ["A gap of 2 means the same thing at position 3 as at position 3,000.",
         "The model learns about **distance**, which transfers to lengths it has never seen."])

    y = BODY_TOP + 3.3
    xl, xr, cw = twocol(s, 0.5)
    box(s, xl, y, cw, 1.9, "Why OUR model cannot go past block_size",
        ["`pos_emb = nn.Embedding(block_size, n_embd)` has exactly `block_size` **rows**. "
         "There is no row 129. It is not that quality degrades — the lookup is physically "
         "impossible, and the assert in `forward` stops you."], fill=WHITE)
    rule(s, xl + 0.05, y + 0.02, cw - 0.1, ORANGE, 0.03)
    box(s, xr, y, cw, 1.9, "Why a modern model can",
        ["RoPE is a **function**, not a table — there is an angle for every position, forever. "
         "Combine it with **YaRN** or position interpolation (stretch the frequencies) and a model "
         "trained at 4k runs at 128k. That is the whole trick behind long context."])

    # ---------------------------------------------------------------- 91
    s = slide(prs, "Upgrade 3  ·  SwiGLU", "Adding a gate: one path for content, one for volume")
    code(s, M, BODY_TOP, CW, 0.95, [
        "ours:    W2( gelu(W1 x) )                  # 2 matrices",
        "swiglu:  W2( silu(W1 x) * W3 x )           # 3 matrices, the extra one is a GATE",
    ], size=13)

    y = BODY_TOP + 1.1
    heading(s, M, y, CW, "Dry run — three neurons")
    cell = 0.6
    xg = M + 1.6
    for i, (nm, vals, f) in enumerate([
        ("gate  W1x", ["2.0", "-1.0", "0.5"], WHITE),
        ("up  W3x", ["1.0", "3.0", "-2.0"], WHITE),
        ("silu(gate)", ["1.762", "-0.269", "0.311"], WHITE),
        ("silu × up", ["1.762", "-0.807", "-0.622"], TINT),
    ]):
        grid(s, xg, y + 0.38 + i * cell, cell, [vals], texts=[vals], size=10,
             head_rows=[nm], fills=[[f] * 3])

    label(s, xg + 2.3, y + 0.4, 7.6,
          "Look at neuron 3.", 13, INK, PP_ALIGN.LEFT)
    label(s, xg + 2.3, y + 0.85, 7.6,
          "Its content is a mild **+0.311**. But the gate path says **−2.0**,\nso the output flips to "
          "**−0.622**.", 12, GRAY, PP_ALIGN.LEFT)
    label(s, xg + 2.3, y + 1.6, 7.6,
          "In our GELU MLP one matrix decides **both** what the feature is\nand how strongly it "
          "fires. SwiGLU splits those two decisions apart\n— and a network that can multiply two "
          "learned quantities can\nrepresent things an additive one cannot.",
          12, GRAY, PP_ALIGN.LEFT)

    y = BODY_TOP + 4.1
    box(s, M, y, CW, 1.35, "It is not free — and it is kept fair",
        ["A third matrix would grow the MLP by 50%, so the hidden size is shrunk to about **8/3 × "
         "n_embd** instead of 4×. Measured at n_embd=128: our GELU MLP is **131,712** parameters, "
         "SwiGLU is **130,944**. Same budget, slightly better results — which is why "
         "**everyone switched**."])

    # ---------------------------------------------------------------- 92
    s = slide(prs, "Beyond file 10  ·  attention efficiency",
              "Three upgrades that made long context affordable")
    y = BODY_TOP
    box(s, M, y, CW, 1.35, "1 — KV cache  (inference)",
        ["Because of the causal mask, token *t*'s keys and values **never change** when you append "
         "token *t+1*. So cache them. Generating the 1,000th token then costs one new row of "
         "attention instead of recomputing all 1,000. **O(T) per token instead of O(T²).** "
         "This is why the first token of a ChatGPT reply is slow and the rest stream fast."])

    y += 1.55
    box(s, M, y, CW, 1.35, "2 — FlashAttention  (training and inference)",
        ["**Identical maths, different memory access.** The T×T attention matrix is never written "
         "to GPU main memory at all — it is computed in tiles inside fast on-chip SRAM. "
         "Memory goes from O(T²) to O(T), and it runs 2-4× faster. `F.scaled_dot_product_attention` "
         "calls it for you. This single engineering change is a large part of why 100k context "
         "became possible."], fill=WHITE)
    rule(s, M + 0.05, y + 0.02, CW - 0.1, ORANGE, 0.03)

    y += 1.55
    box(s, M, y, CW, 1.75, "3 — GQA: Grouped-Query Attention",
        ["The KV cache, not the compute, is what runs out of memory at long context. GQA keeps all "
         "`n_head` **query** heads but shares a smaller number of **key/value** heads between them.",
         "Llama 3: 32 query heads → 8 KV heads = **4× smaller cache**. gpt-oss-120b: 64 query heads "
         "→ 8 KV heads = **8× smaller**. MQA is the extreme case of one KV head. Quality cost is "
         "close to zero; the memory saving is enormous."])

    # ---------------------------------------------------------------- 93
    s = slide(prs, "Beyond file 10  ·  GQA drawn out",
              "Where the memory actually goes")
    y = BODY_TOP + 0.1
    heading(s, M, y, 5.6, "MHA — what model4.py does")
    for i in range(4):
        chip(s, M + 0.3 + i * 1.3, y + 0.4, 1.15, 0.45, f"Q{i}", size=11)
        chip(s, M + 0.3 + i * 1.3, y + 0.95, 1.15, 0.45, f"K{i}V{i}", fill=TINT2,
             edge=ORANGE, size=11)
    label(s, M, y + 1.55, 5.6, "4 queries, **4 KV pairs** to cache", 11.5, GRAY)

    heading(s, M + 6.3, y, 5.9, "GQA — what Llama 3 and gpt-oss do")
    for i in range(4):
        chip(s, M + 6.6 + i * 1.3, y + 0.4, 1.15, 0.45, f"Q{i}", size=11)
    chip(s, M + 6.6, y + 0.95, 2.45, 0.45, "K0 V0", fill=TINT2, edge=ORANGE, size=11)
    chip(s, M + 9.2, y + 0.95, 2.45, 0.45, "K1 V1", fill=TINT2, edge=ORANGE, size=11)
    label(s, M + 6.3, y + 1.55, 5.9, "4 queries, **2 KV pairs** shared → half the cache",
          11.5, ORANGE_DK)

    y = BODY_TOP + 1.9
    table(s, M, y, CW, [
        ["Model", "Query heads", "KV heads", "Cache saving", "Context"],
        ["GPT-2 (2019) / our ARGPT", "12 / 4", "12 / 4  (MHA)", "1× (baseline)", "1,024 / 128"],
        ["Llama 2-70B, Llama 3", "64", "8", "**8×**", "4k → 128k"],
        ["Mistral 7B", "32", "8", "4×", "32k (sliding window)"],
        ["gpt-oss-120b (2025)", "64", "8", "**8×**", "131,072 (RoPE + YaRN)"],
        ["DeepSeek-V3", "MLA — a low-rank latent", "instead of dropping heads", "**~10×+**", "128k"],
    ], widths=[3.0, 2.4, 2.6, 1.8, 2.4], size=10.8, row_h=0.44)

    box(s, M, y + 2.7, CW, 0.9, "The point to make",
        ["These all leave the **attention formula unchanged** — they only change how many copies "
         "of K and V you keep. **Engineering around the same maths.**"])

    # ---------------------------------------------------------------- 94
    s = slide(prs, "Beyond file 10  ·  Mixture of Experts",
              "How a 117-billion-parameter model runs like a 5-billion one")
    y = BODY_TOP
    chip(s, M + 0.4, y + 0.6, 1.9, 0.55, "token", size=12.5)
    arrow(s, M + 2.4, y + 0.71, 0.45, 0.22)
    chip(s, M + 2.95, y + 0.6, 1.5, 0.55, "router", fill=ORANGE, edge=None, color=WHITE, size=12.5)
    for i in range(4):
        yy = y + i * 0.55
        f, e = (TINT2, ORANGE) if i in (1, 2) else (WHITE, LINE)
        chip(s, M + 4.95, yy, 2.6, 0.45, f"expert {i+1}  (an MLP)", fill=f, edge=e, size=11)
    label(s, M + 4.95, y + 2.35, 2.6, "…128 of them in gpt-oss-120b", 10.5, GRAY)
    arrow(s, M + 7.7, y + 0.71, 0.45, 0.22)
    chip(s, M + 8.25, y + 0.6, 2.4, 0.55, "weighted sum", fill=TINT, size=12)
    label(s, M + 4.95, y + 2.75, 5.7, "only the **top 4** run for any given token", 11.5, ORANGE_DK)

    y = BODY_TOP + 3.3
    bullets(s, M, y, CW, 2.2, [
        "**Replace the single MLP in each block with N MLPs plus a small router.** The router "
        "scores the experts for this token, and only the top-k actually run.",
        "**Total parameters** grow enormously — that is where knowledge is stored. "
        "**Active parameters per token** stay small — that is what you pay for at inference. "
        "gpt-oss-120b: **117B total, 5.1B active.** DeepSeek-V3: **671B total, 37B active.**",
        "The cost is memory: every expert must be resident in VRAM even though most are idle. "
        "That is why MoE models are big to host but cheap to run.",
        "Recall that **two thirds of a dense GPT's parameters are in the MLPs.** MoE is a "
        "direct answer to exactly that observation.",
    ], size=13, gap=11)

    # ---------------------------------------------------------------- 95
    s = slide(prs, "Beyond file 10  ·  the rest of the 2025 toolkit",
              "Everything else a frontier model adds on top of what you built")
    table(s, M, BODY_TOP, CW, [
        ["Technique", "What it does", "Why it helps"],
        ["**Sliding-window attention**", "Most layers attend only to the last W tokens "
                                         "(gpt-oss: 128), with full attention every other layer.",
         "Bounds cost at long context while a few dense layers still carry global information."],
        ["**Attention sinks**", "A learned bias in the softmax denominator, letting a head attend "
                                "to *nothing*.",
         "Without it a head is forced to distribute 100% somewhere. Fixes the quality collapse "
         "that streaming long contexts used to cause."],
        ["**YaRN / position interpolation**", "Rescale RoPE's frequencies after training.",
         "Takes a model trained at 4k and runs it at 128k+ with a short fine-tune instead of a "
         "full retrain."],
        ["**QK-Norm**", "Normalise q and k before the dot product.",
         "Stops attention logits blowing up in very large runs. Cheap stability insurance."],
        ["**bf16 / fp8 / MXFP4**", "Train and serve in fewer bits per number.",
         "2-4× throughput and memory. gpt-oss ships its experts in **MXFP4**, which is how 117B "
         "parameters fit on one 80 GB card."],
        ["**LR warmup + cosine decay, weight decay**", "A schedule instead of a constant "
                                                       "learning rate.",
         "Worth several percent of final loss for free. One of our “did not build” items."],
        ["**Speculative decoding**", "A small draft model proposes several tokens; the big model "
                                     "verifies them in one pass.",
         "2-3× faster generation with **identical** output distribution."],
        ["**Post-training: SFT → RLHF/DPO → reasoning RL**", "Not architecture at all.",
         "**Arguably the biggest quality jump of 2024-25.** It is what makes a model *useful* "
         "rather than merely fluent."],
    ], widths=[3.1, 4.6, 4.5], size=10, row_h=0.62, head_h=0.34)

    # ---------------------------------------------------------------- 96
    s = slide(prs, "So which of these does GPT-5 use?",
              "The honest answer, which is a better lesson than a confident guess")
    box(s, M, BODY_TOP, CW, 1.15, "What OpenAI has actually published",
        ["**GPT-5's architecture is not disclosed.** There is no paper, no parameter count, no "
         "layer configuration. Anyone quoting exact numbers is guessing. The system card describes "
         "the *product*, not the internals — and says so."])

    y = BODY_TOP + 1.35
    xl, xr, cw = twocol(s, 0.5)
    box(s, xl, y, cw, 2.1, "What IS public about GPT-5", [
        "It is a **routed system**, not one model: a fast main model, a deeper “thinking” model, "
        "and a real-time router that picks between them per message.",
        "**400,000-token context**, up to 128,000 output tokens.",
        "Heavy reinforcement learning for reasoning. OpenAI explicitly did not publish the router's "
        "architecture, thresholds, or training data.",
    ], fill=WHITE)
    rule(s, xl + 0.05, y + 0.02, cw - 0.1, ORANGE, 0.03)

    box(s, xr, y, cw, 2.1, "What we can say with confidence", [
        "OpenAI **did** publish full architecture details for **gpt-oss-120b / 20b** (August 2025) "
        "— their open-weight models.",
        "That is the closest public evidence of OpenAI's current design language, and it uses "
        "**every technique on the previous four slides**.",
        "It is fair to teach: *“this is the shape of a 2025 frontier model.”* It is not fair to "
        "teach: *“this is GPT-5.”*",
    ])

    y = BODY_TOP + 3.75
    box(s, M, y, CW, 1.35, "The teaching answer to give when a student asks",
        ["*“Take the three swaps in file 10 — RMSNorm, RoPE, SwiGLU — then add GQA, MoE, "
         "FlashAttention, sliding-window attention and long-context RoPE scaling. That is the "
         "shape of every 2025 frontier model, GPT-5 almost certainly included. The exact numbers "
         "are a trade secret, and it is worth knowing the difference between what we know and what "
         "we assume.”*"])

    # ---------------------------------------------------------------- 97
    s = slide(prs, "gpt-oss-120b", "OpenAI's own open model, component by component")
    table(s, M, BODY_TOP, CW, [
        ["Component", "gpt-oss-120b (published, Aug 2025)", "What we built in model4.py"],
        ["Objective", "next-token prediction", "**identical**"],
        ["Block structure", "attention → MLP, pre-norm, residual", "**identical**"],
        ["Mask", "causal", "**identical**"],
        ["Normalisation", "**RMSNorm** before each attention and MoE block", "LayerNorm, pre-norm"],
        ["Positions", "**RoPE**, extended to **131,072** tokens with **YaRN**", "learned pos_emb, 128"],
        ["Feed-forward", "**MoE**: 128 experts, **top-4** routed, gated **SwiGLU**",
         "one dense GELU MLP"],
        ["Attention heads", "64 query heads (dim 64), **GQA with 8 KV heads**", "4 heads, MHA"],
        ["Attention pattern", "alternating **dense** and **banded sliding-window (128)** layers, "
                              "with learned **attention sinks**", "dense everywhere"],
        ["Size", "**117B total / 5.1B active** per token", "0.82M / 10.8M, all active"],
        ["Precision", "**MXFP4** quantised experts — fits on one 80 GB GPU", "fp32"],
    ], widths=[2.4, 6.4, 3.4], size=10.3, row_h=0.415, head_h=0.36)

    box(s, M, 6.15, CW, 0.75, None,
        ["Every single row is either **identical to what you built**, or one of the swaps in "
         "file 10 and the four slides after it. **There is nothing in that column you have not "
         "now seen.**"], fill=TINT)

    # ---------------------------------------------------------------- 98
    s = slide(prs, "2019 vs 2025", "How is the modern architecture actually better?")
    table(s, M, BODY_TOP, CW, [
        ["Dimension", "GPT-2, 2019  =  our model4.py", "Frontier, 2025", "The win"],
        ["Context length", "1,024 tokens, hard ceiling from a learned table",
         "128k - 1M+ via RoPE + YaRN", "**~1,000×**"],
        ["Attention memory", "O(T²) matrix written to GPU memory", "FlashAttention: never "
                                                                   "materialised, O(T)", "makes long context possible at all"],
        ["KV cache", "full — one K and V per head", "GQA / MLA — 4-10× smaller", "**longer contexts fit**"],
        ["Normalisation", "LayerNorm, 2 params per dim", "RMSNorm + QK-norm, 1 param per dim",
         "speed + stability"],
        ["Feed-forward", "dense GELU, every parameter active", "SwiGLU + MoE, ~4% active",
         "**~20× params at the same cost**"],
        ["Precision", "fp32", "bf16 / fp8 / MXFP4", "2-4× throughput"],
        ["Training data", "~40 GB WebText, ~10B tokens", "10-20+ **trillion** curated tokens",
         "**~1,000×**"],
        ["Training recipe", "constant LR, pretraining only", "warmup + cosine, then SFT → "
                                                             "RLHF/DPO → reasoning RL", "the qualitative jump"],
        ["Serving", "recompute everything, one request at a time", "KV cache, paged attention, "
                                                                   "continuous batching, speculative decoding", "orders of magnitude cheaper"],
        ["What it can do", "continue text plausibly", "follow instructions, use tools, reason, "
                                                      "see images, write code that runs", "—"],
    ], widths=[2.0, 3.6, 4.0, 2.6], size=9.8, row_h=0.415, head_h=0.36)

    # ---------------------------------------------------------------- 99
    s = slide(prs, "But be honest about where the gains came from",
              "The architecture is the smallest part of the story")
    y = BODY_TOP
    xw = (CW - 0.8) / 3
    for i, (pct, t, d) in enumerate([
        ("Efficiency", "RMSNorm, RoPE, SwiGLU,\nGQA, FlashAttention, MoE",
         "These mostly did not make models **smarter** directly. They made it **affordable to "
         "train and serve a much bigger model on much more data.** Their real contribution is "
         "removing the ceiling."),
        ("Scale", "1,000× more data,\n100,000× more compute",
         "This is where most of the raw capability came from. SmolLM2-135M is only ~13× bigger "
         "than ARGPT-SMALL but saw **~2,000,000× more tokens.**"),
        ("Post-training", "SFT → RLHF/DPO →\nreasoning RL",
         "**Not architecture at all.** This is what turns a fluent text-continuer into something "
         "that answers your question, uses a tool, and thinks before replying. Arguably the "
         "biggest single jump of 2024-25."),
    ]):
        x = M + i * (xw + 0.4)
        chip(s, x, y, xw, 0.55, pct, fill=ORANGE, edge=None, color=WHITE, size=14)
        label(s, x, y + 0.7, xw, t, 12, ORANGE_DK)
        label(s, x + 0.1, y + 1.5, xw - 0.2, d, 11.5, GRAY, PP_ALIGN.LEFT)

    y = BODY_TOP + 3.6
    box(s, M, y, CW, 1.6, "The conclusion to leave them with",
        ["If you dropped GPT-2's exact 2019 architecture into 2025 — same LayerNorm, same learned "
         "positions, same dense GELU MLP — but gave it modern data, modern compute and modern "
         "post-training, **you would get something startlingly good.** Slower and more expensive "
         "than the real thing, and capped at short context, but good.",
         "**The core did not change. What changed was everything around it.** That is exactly why "
         "learning the 2019 core first is the right call."])

    # ============================================================== SCALING
    s = slide(prs, "How much data does a model need?",
              "The Chinchilla rule, and why our models are deliberately starved")
    box(s, M, BODY_TOP, CW, 0.8, None,
        ["Chinchilla (DeepMind, 2022): for compute-optimal training, use about "
         "~~20 tokens of data per parameter~~."], size=15, fill=TINT)

    y = BODY_TOP + 1.05
    xl, xr, cw = twocol(s, 0.5)
    table(s, xl, y, cw, [
        ["Model", "Params", "Wants (~20×)"],
        ["ARGPT TINY", "0.8 M", "~16 M tokens"],
        ["ARGPT SMALL", "10.8 M", "~200 M tokens"],
        ["SmolLM2-135M", "135 M", "~2.7 B tokens"],
        ["GPT-3", "175 B", "~3.5 T tokens"],
    ], widths=[2.2, 1.2, 1.8], size=11.5, row_h=0.4)

    table(s, xr, y, cw, [
        ["Our actual run", "Have", "Verdict"],
        ["TINY on Shakespeare", "1.1 M", "**15× short**"],
        ["SMALL on coding (BPE)", "4.6 M", "**43× short**"],
        ["SMALL on knowledge (char)", "10.7 M", "**19× short**"],
    ], widths=[2.6, 1.1, 1.5], size=11.5, row_h=0.4)

    y = BODY_TOP + 3.05
    bullets(s, M, y, CW, 2.0, [
        "**Every model in this project is data-limited, not parameter-limited.** We compensate by "
        "doing multiple epochs — TINY passes over Shakespeare about **7.3 times**.",
        "That is fine for a demo, and it is exactly *why* val loss matters: with this little data a "
        "model starts memorising rather than generalising, and the val curve is how you catch it.",
        "So the **#1 lever to make ARGPT better is more and better-matched data**, not more layers. "
        "If a student asks “should I add layers?”, the answer is almost always no.",
    ], size=13.5, gap=12)

    # ---------------------------------------------------------------- 101
    s = slide(prs, "The number that answers “why isn't mine ChatGPT?”",
              "Modern small models deliberately break the Chinchilla rule")
    table(s, M, BODY_TOP, CW, [
        ["Model", "Parameters", "Tokens trained on", "Tokens per parameter"],
        ["Chinchilla-optimal", "N", "20 · N", "20"],
        ["**ARGPT SMALL** *(ours)*", "**10.8 M**", "**~4.6 M unique**", "**~0.4**"],
        ["SmolLM2-135M", "135 M", "**2 trillion**", "~14,800"],
        ["SmolLM2-360M", "360 M", "4 trillion", "~11,000"],
        ["SmolLM2-1.7B", "1.7 B", "11 trillion", "~6,500"],
    ], widths=[3.0, 2.0, 2.6, 2.6], size=11.5, row_h=0.45, head_h=0.36,
        aligns=["l", "c", "c", "c"])

    y = BODY_TOP + 2.85
    box(s, M, y, CW, 1.3, "Let this land",
        ["**SmolLM2-135M is only ~13× more parameters than ARGPT-SMALL, but it was trained on "
         "roughly 2,000,000× more tokens.** The parameters are the easy part. The data and the "
         "compute are the mountain."])

    y += 1.55
    bullets(s, M, y, CW, 1.4, [
        "**Why over-train past 20×?** Chinchilla is optimal for *training cost*. But you train once "
        "and serve forever — so it is often worth a smaller model trained far longer, because it is "
        "cheaper to run for the rest of its life.",
        "**Matching data complexity to model capacity matters more than raw token count.** "
        "TinyStories — simple stories written for four-year-olds — produces genuinely readable "
        "English at 10M parameters, where general web text produces mush.",
    ], size=13, gap=10)

    # ---------------------------------------------------------------- 102
    s = slide(prs, "The ladder", "How to get from ARGPT to something genuinely useful, in order of impact")
    y = BODY_TOP
    rungs = [
        ("1", "More, and better-matched, data",
         "The biggest lever by a distance. Feed parameters ~20×+ their count in tokens, and pick "
         "data a model this size can actually model."),
        ("2", "More parameters — but only alongside more data",
         "n_layer and n_embd. Raise them without raising data and you simply memorise faster."),
        ("3", "Longer context: block_size + RoPE",
         "So the model can use long histories, and generalise past the length it trained on."),
        ("4", "The modern architecture swaps",
         "RMSNorm, SwiGLU, GQA, FlashAttention. Marginal at our scale, decisive at billions."),
        ("5", "Efficiency, so you can afford steps 1-4",
         "bf16 mixed precision, torch.compile, gradient accumulation, LR warmup + cosine decay."),
        ("6", "Instruction tuning (SFT)",
         "Fine-tune on many instruction→response pairs. **The step that turns “continues text” "
         "into “follows commands”.**"),
        ("7", "Preference alignment (RLHF or DPO), then reasoning RL",
         "The final polish: match human preference, then learn to think in steps before answering."),
    ]
    for i, (n, t, d) in enumerate(rungs):
        yy = y + i * 0.76
        chip(s, M, yy, 0.44, 0.44, n, fill=ORANGE, edge=None, color=WHITE, size=12.5)
        label(s, M + 0.6, yy - 0.01, 11.5, t, 13.5, INK, PP_ALIGN.LEFT)
        label(s, M + 0.6, yy + 0.36, 11.5, d, 11.5, GRAY, PP_ALIGN.LEFT)

    # ---------------------------------------------------------------- 103
    s = slide(prs, "The FAQ  ·  1 of 2", "Hard questions students will ask")
    qa = [
        ("Why can't it answer my question or do maths?",
         "Because we only did **pretraining**. It continues text; it does not respond to requests. "
         "Feed it a seed, not a question."),
        ("Where is the “intelligence” stored? What did it actually learn?",
         "In the 818,048 weights — the embedding tables, the q/k/v/proj matrices and the MLPs. "
         "Concretely: a giant statistical model of which token follows which."),
        ("What makes this a GPT and not a BERT?",
         "The mask. GPT is causal, left-to-right, predict-the-next. BERT is bidirectional and fills "
         "in blanks. **Same attention maths, different mask, different objective.**"),
        ("Why does the same prompt give different text every time?",
         "The last step is `torch.multinomial` — a weighted dice roll over the top-k tokens, not "
         "“pick the maximum”. Lower the temperature to make it near-deterministic."),
        ("Why can't it remember earlier in a long conversation?",
         "It physically cannot see past `block_size`. `generate6.py` literally slices "
         "`idx[:, -block_size:]`. Same constraint as Session 3's RAG chunking."),
        ("If I make n_layer and n_embd huge, will it get smart?",
         "No — you will memorise the tiny dataset. Train loss drops, val loss rises. "
         "Model size must grow **with** data."),
    ]
    for i, (q, a) in enumerate(qa):
        yy = BODY_TOP + i * 0.88
        label(s, M, yy, CW, "Q   " + q, 13.5, ORANGE, PP_ALIGN.LEFT)
        label(s, M + 0.45, yy + 0.34, CW - 0.45, a, 12, INK, PP_ALIGN.LEFT)

    # ---------------------------------------------------------------- 104
    s = slide(prs, "The FAQ  ·  2 of 2", "Hard questions students will ask")
    qa = [
        ("What are the units of loss, and what is a good number?",
         "Cross-entropy in **nats**. Untrained ≈ ln(vocab_size): 4.17 for char-65, 6.93 for "
         "BPE-1024. On Shakespeare-char, ~1.6 is decent. `perplexity = exp(loss)` if that lands better."),
        ("Is the tokenizer trained by backpropagation?",
         "**No.** It is built by counting — BPE merges or the character set — before the model "
         "exists, and then frozen. The network never changes it."),
        ("Char or BPE — which is better?",
         "Neither universally. Char: tiny vocab, long sequences, learns spelling, instant to build. "
         "BPE: bigger vocab, ~2.5× shorter sequences, longer effective memory. Same interface, "
         "so it is one CLI flag."),
        ("Why 90/10 train/val — what does val actually catch?",
         "Val is text the model never trains on. Comparing the two curves is the only way to tell "
         "*learning the language* from *memorising the file*. It is the control group."),
        ("Can I train it on my own writing, or another language, or emoji?",
         "Yes. Drop any `.txt` at `data/custom/input.txt` and run `python data3.py --dataset custom`. "
         "BPE starts from raw bytes, so nothing is ever out-of-vocabulary."),
        ("How much would it cost to make it actually good?",
         "SmolLM2-135M is ~13× our SMALL model but saw **2 trillion** tokens — millions of "
         "GPU-hours of data throughput. **The architecture is a weekend. The data and compute "
         "are the real cost.**"),
    ]
    for i, (q, a) in enumerate(qa):
        yy = BODY_TOP + i * 0.88
        label(s, M, yy, CW, "Q   " + q, 13.5, ORANGE, PP_ALIGN.LEFT)
        label(s, M + 0.45, yy + 0.34, CW - 0.45, a, 12, INK, PP_ALIGN.LEFT)

    # ---------------------------------------------------------------- 105
    s = slide(prs, "Numbers to have memorised", "The cheat sheet — keep this one open while teaching")
    xl, xr, cw = twocol(s, 0.5)
    table(s, xl, BODY_TOP, cw, [
        ["Thing", "Value"],
        ["TINY", "4 layers, 4 heads, n_embd 128, block 128"],
        ["TINY parameters", "**818,048**  (~0.82M), ~3 min on CPU"],
        ["SMALL", "6 layers, 6 heads, n_embd 384, block 256"],
        ["SMALL parameters", "**10,770,816**  (~10.8M), ~10 min on L4"],
        ["head_size", "n_embd / n_head — TINY 32, SMALL 64"],
        ["Parameter formula", "≈ n_layer × 12 × n_embd² + embeddings"],
        ["Shakespeare", "1.1 MB, char vocab **65**, 1,115,394 tokens"],
        ["char → BPE compression", "**~2.5×** fewer tokens (1.12M → 453k)"],
        ["Coding dataset", "11.6 MB → ~4.6M BPE tokens"],
    ], widths=[2.3, 3.6], size=11, row_h=0.36, head_h=0.34)

    table(s, xr, BODY_TOP, cw, [
        ["Thing", "Value"],
        ["Untrained loss", "≈ ln(vocab): **4.17** char-65, **6.93** BPE-1024"],
        ["Good Shakespeare-char loss", "**~1.6**"],
        ["TINY token-predictions", "2000 × 32 × 128 = **8,192,000**  (~7.3 epochs)"],
        ["SMALL token-predictions", "5000 × 64 × 256 = **81,920,000**"],
        ["Chinchilla rule", "**~20 tokens per parameter**"],
        ["SmolLM2 training", "135M→**2T**, 360M→**4T**, 1.7B→**11T** tokens"],
        ["L4 GPU cost", "$0.80/hr by the second ≈ **13¢** per 10-min run"],
        ["Modal free tier", "$30/month ≈ **37 GPU-hours**"],
        ["GPT-5 context", "400,000 tokens (architecture undisclosed)"],
    ], widths=[2.5, 3.6], size=11, row_h=0.36, head_h=0.34)

    y = BODY_TOP + 3.72
    table(s, M, y, CW, [
        ["When you see this", "What happened"],
        ["`AttributeError: module 'modal' has no attribute 'App'`", "A file named `modal.py` is "
                                                                    "shadowing the package. Rename it."],
        ["`IndexError: index out of range in self`", "vocab_size disagrees with the data. Re-run "
                                                     "`data3.py`, then `train5.py`."],
        ["`FileNotFoundError: .../train.bin`", "Run `data3.py` before `train5.py`."],
        ["Loss goes to `nan`", "Learning rate too high. TINY uses 3e-4 for a reason."],
    ], widths=[4.6, 7.6], size=10.5, row_h=0.34, head_h=0.34)

    # ---------------------------------------------------------------- 106
    s = slide(prs, "Glossary", "Every term used in this session, in one place")
    xl, xr, cw = twocol(s, 0.5)
    left = [
        ("Token", "the atomic unit of text the model reads"),
        ("vocab_size", "how many distinct tokens exist. **Set by the data.**"),
        ("n_embd (C)", "the length of one token's vector. The model's width."),
        ("n_layer", "how many blocks are stacked. The model's depth."),
        ("n_head", "parallel attention heads per block"),
        ("block_size (T)", "max tokens it can look back at. Its memory span."),
        ("Parameter", "one learned number. 10M parameters = 10M knobs."),
        ("Embedding", "a lookup table: id → a learned vector"),
        ("Attention", "how tokens exchange information, via q / k / v"),
        ("Causal mask", "the rule that a token may only see earlier tokens"),
        ("Residual", "`x = x + sublayer(x)` — adds a correction, enables depth"),
        ("Logits", "raw pre-softmax scores, one per vocab token"),
    ]
    right = [
        ("Cross-entropy", "“how surprised was the model”, measured in nats"),
        ("Perplexity", "`exp(loss)` — how many tokens it is choosing between"),
        ("Epoch", "one full pass over the training data"),
        ("Temperature", "generation boldness; divides logits before softmax"),
        ("top-k / top-p", "restrict sampling to the k best, or to a probability mass"),
        ("Pretraining", "training on raw text with the next-token objective"),
        ("SFT", "instruction tuning — fine-tuning on instruction→response pairs"),
        ("RLHF / DPO", "aligning outputs to human preference, after SFT"),
        ("Chinchilla", "the ~20-tokens-per-parameter compute-optimal rule"),
        ("BPE", "byte-pair encoding — merge the most frequent adjacent pair"),
        ("RoPE", "rotary positions; makes attention depend on the **gap**"),
        ("GQA / MoE", "share KV heads / route to a few expert MLPs per token"),
    ]
    for col, x in ((left, xl), (right, xr)):
        for i, (t, d) in enumerate(col):
            yy = BODY_TOP + i * 0.44
            label(s, x, yy, 2.0, t, 11.5, ORANGE, PP_ALIGN.LEFT)
            label(s, x + 2.05, yy, cw - 2.05, d, 11, GRAY, PP_ALIGN.LEFT)

    # ---------------------------------------------------------------- 107
    s = slide(prs, "One last thing", "What to say as you close the laptop")
    box(s, M, BODY_TOP + 0.3, CW, 2.1, None,
        ["Everything in this project — the whole pipeline from a raw text file to a deployed URL "
         "your agent can call — is built on one sentence: ~~predict the next token~~.",
         "GPT-4, GPT-5 and SmolVLM are the same sentence, with more data, more compute, and a few "
         "bolt-ons. **You did not build a toy. You built the foundation, and now you can see "
         "exactly what everything else is standing on.**"], size=16, fill=TINT)

    y = BODY_TOP + 2.8
    xw = (CW - 0.8) / 3
    for i, (t, d) in enumerate([
        ("Run it again tonight", "Change one number in `config1.py` and watch what it does to the "
                                 "loss curve. That is the whole experiment."),
        ("Then go read coding_llm/", "The same model plus a chat format, an instruction dataset "
                                     "and loss masking — the SFT step we skipped."),
        ("Then swap in file 10", "`nn.LayerNorm` → `RMSNorm` and the MLP → `SwiGLU` are both "
                                 "drop-in. RoPE needs edits inside `SelfAttention`."),
    ]):
        x = M + i * (xw + 0.4)
        chip(s, x, y, xw, 0.55, t, fill=ORANGE, edge=None, color=WHITE, size=13)
        label(s, x + 0.1, y + 0.75, xw - 0.2, d, 12, GRAY, PP_ALIGN.LEFT)

    label(s, M, y + 2.1, CW, "AI Season   ·   Build an LLM from Scratch, Part 2   ·   "
                             "Abdul Rahman Azam", 13, ORANGE_DK)
