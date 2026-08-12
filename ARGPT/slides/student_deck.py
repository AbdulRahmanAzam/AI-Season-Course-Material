"""
The STUDENT deck — 29 slides, diagram-led, minimal text.

This is the one you project and send to the class. The 94-slide instructor deck
(Build-an-LLM-from-Scratch-Part-2.pptx) is the one you read from.

    python student_deck.py
"""

import os
import sys

from pptx import Presentation
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import theme
from theme import (BODY_TOP, CW, GRAY, GRAY_LT, INK, LINE, M, ORANGE, ORANGE_DK,
                   ORANGE_HI,
                   TINT, TINT2, WHITE, arrow, box, bullets, chip, code, grid,
                   heading, label, para, rule, slide, table, title_slide, twocol)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "Build-an-LLM-from-Scratch-Part-2-STUDENTS.pptx")


def big(s, x, y, w, text, size=17, color=INK, align=PP_ALIGN.CENTER):
    """One short line of student-facing text."""
    return label(s, x, y, w, text, size, color, align)


def step(prs, n, title, sub=""):
    """A content slide whose kicker is STEP n."""
    return slide(prs, f"Step {n}" + (f"   ·   {sub}" if sub else ""), title)


def build(prs):
    # ------------------------------------------------------------------ 1
    title_slide(
        prs,
        "Build an LLM\nfrom Scratch — Part 2",
        "How a language model actually works — from a text file to a model "
        "you can talk to.",
        "Abdul Rahman Azam", "AI Season",
        meta=["Project: ARGPT", "~700 lines of PyTorch",
              "No pretrained weights. We build all of it."])

    # ------------------------------------------------------------------ 2
    s = slide(prs, "Today", "We are building this")
    y = BODY_TOP + 0.35
    steps = [("A text file", "Shakespeare\n1.1 MB"),
             ("A tokenizer", "text → numbers"),
             ("A transformer", "0.8M numbers\nto learn"),
             ("Training", "watch it\nget better"),
             ("Your own model", "on a URL\nyou own")]
    xw, gap = 2.2, 0.34
    x = M + 0.35
    for i, (a, b) in enumerate(steps):
        chip(s, x, y, xw, 1.15, a, sub=b, size=14,
             fill=TINT if i in (0, 4) else WHITE)
        if i < 4:
            arrow(s, x + xw + 0.04, y + 0.46, gap - 0.08, 0.24)
        x += xw + gap

    big(s, M, y + 1.75, CW, "By the end of today you will have trained a "
                            "language model **yourself**.", 17)
    big(s, M, y + 2.45, CW, "Not called an API. Not downloaded. Trained.", 15, ORANGE_DK)

    box(s, M, y + 3.15, CW, 0.95, None,
        ["It will be small, and it will write nonsense. **That is the point** — "
         "you will be able to see exactly why."], size=14, fill=TINT)

    # ------------------------------------------------------------------ 3
    s = slide(prs, "The one idea", "Everything today is one sentence")
    box(s, M, BODY_TOP + 0.5, CW, 1.15, None,
        ["~~Given some tokens, predict the next token.~~"], size=26, fill=TINT)

    y = BODY_TOP + 2.15
    cell = 0.9
    given = ["The", "cat", "sat", "on", "the", "?"]
    fills = [[WHITE] * 5 + [ORANGE_HI]]
    grid(s, M + 2.35, y, cell, [given], texts=[given], size=15, fills=fills)
    label(s, M + 2.35, y + cell + 0.25, cell * 5, "what the model can see", 12, GRAY)
    label(s, M + 2.35 + cell * 5, y + cell + 0.25, cell, "predict this", 12, ORANGE_DK)

    big(s, M, y + 1.85, CW, "That is it. Grammar, names, punctuation, code — all of it "
                            "comes out of doing **this one thing** very well.", 16)

    # ------------------------------------------------------------------ 4
    s = slide(prs, "The pipeline", "Five things, in order")
    y = BODY_TOP + 0.55
    rows = [("1", "Tokenizer", "turn text into numbers", "tokenizer2.py"),
            ("2", "Data", "make training examples", "data3.py"),
            ("3", "Model", "the transformer itself", "model4.py"),
            ("4", "Training", "make it less wrong, 2000 times", "train5.py"),
            ("5", "Generate", "make it write", "generate6.py")]
    for i, (n, t, d, f) in enumerate(rows):
        yy = y + i * 0.86
        chip(s, M + 0.6, yy, 0.55, 0.55, n, fill=ORANGE_HI, edge=None, color=INK, size=16)
        label(s, M + 1.5, yy + 0.02, 3.0, t, 17, INK, PP_ALIGN.LEFT)
        label(s, M + 4.7, yy + 0.08, 5.0, d, 14, GRAY, PP_ALIGN.LEFT)
        label(s, M + 9.9, yy + 0.1, 2.4, f, 13, ORANGE_DK, PP_ALIGN.LEFT)
        if i < 4:
            arrow(s, M + 0.79, yy + 0.6, 0.18, 0.2, right=False)

    # ================================================================ TOKENIZER
    # ------------------------------------------------------------------ 5
    s = step(prs, 1, "A neural network cannot read letters", "the tokenizer")
    big(s, M, BODY_TOP + 0.15, CW, "It only multiplies numbers. So first, text has to "
                                   "become numbers.", 17)

    y = BODY_TOP + 1.1
    chip(s, M + 0.8, y, 2.8, 0.9, "\"hello\"", size=20, fill=WHITE)
    arrow(s, M + 3.75, y + 0.33, 0.85, 0.26)
    chip(s, M + 4.75, y, 3.9, 0.9, "[46, 43, 50, 50, 53]", size=19, fill=TINT2, edge=ORANGE)
    arrow(s, M + 8.8, y + 0.33, 0.85, 0.26)
    chip(s, M + 9.8, y, 2.4, 0.9, "the model", size=18, fill=WHITE)
    label(s, M + 3.75, y + 1.0, 0.85, "encode", 12, ORANGE_DK)
    label(s, M + 8.8, y + 1.0, 0.85, "learns", 12, ORANGE_DK)

    y = BODY_TOP + 2.9
    xl, xr, cw = twocol(s, 0.5)
    box(s, xl, y, cw, 1.7, "Way 1 — one number per letter",
        ["Simple. Small vocabulary.",
         "But every single letter costs a token, so sentences get **long**."], size=14, fill=WHITE)
    rule(s, xl + 0.05, y + 0.02, cw - 0.1, ORANGE, 0.03)
    box(s, xr, y, cw, 1.7, "Way 2 — one number per word-piece",
        ["Harder to build. Bigger vocabulary.",
         "But common words become **one** token. This is what GPT-4 uses."], size=14)

    # ------------------------------------------------------------------ 6
    s = slide(prs, "Way 1  ·  characters", "Give every letter a number")
    heading(s, M, BODY_TOP + 0.1, CW, "The text:  \"the cat sat on the mat…\"")

    y = BODY_TOP + 0.6
    chars = ["␣", ".", "a", "c", "e", "h", "m", "n", "o", "r", "s", "t"]
    ids = [str(i) for i in range(12)]
    cell = 0.72
    xg = M + 1.5
    grid(s, xg, y, cell, [chars], texts=[chars], size=15, head_rows=["letter"],
         fills=[[TINT] * 12])
    grid(s, xg, y + cell, cell, [ids], texts=[ids], size=15, head_rows=["number"],
         fills=[[WHITE] * 12])
    label(s, xg, y + 2 * cell + 0.18, cell * 12, "12 different characters  →  vocabulary = 12",
          13, GRAY)

    y = BODY_TOP + 2.75
    heading(s, M, y, CW, "Now encode  \"the cat\"")
    letters = ["t", "h", "e", "␣", "c", "a", "t"]
    vals = ["11", "5", "4", "0", "3", "2", "11"]
    xg2 = M + 3.0
    grid(s, xg2, y + 0.4, cell, [letters], texts=[letters], size=15, fills=[[WHITE] * 7])
    grid(s, xg2, y + 0.4 + cell, cell, [vals], texts=[vals], size=15, fills=[[TINT2] * 7])
    label(s, M, y + 0.4 + cell * 0.35, 2.8, "in →", 15, INK, PP_ALIGN.RIGHT)
    label(s, M, y + 0.4 + cell * 1.35, 2.8, "out →", 15, INK, PP_ALIGN.RIGHT)

    big(s, M, y + 2.1, CW, "7 letters  →  **7 numbers.** Simple, but long.", 16)

    # ------------------------------------------------------------------ 7
    s = slide(prs, "Way 2  ·  BPE", "Watch it invent words by itself")
    box(s, M, BODY_TOP + 0.05, CW, 0.8, None,
        ["Find the two pieces that appear together most often. Glue them. Repeat."],
        size=17, fill=TINT)

    y = BODY_TOP + 1.15
    merges = [("round 1", "'a' + 't'", "'at'", "1,200 times"),
              ("round 2", "'t' + 'h'", "'th'", "800 times"),
              ("round 3", "'th' + 'e'", "'the'", "800 times"),
              ("round 6", "' c' + 'at'", "' cat'", "400 times"),
              ("round 8", "' s' + 'at'", "' sat'", "200 times")]
    for i, (r, a, b, c) in enumerate(merges):
        yy = y + i * 0.72
        f = TINT if i >= 3 else WHITE
        label(s, M + 0.7, yy + 0.1, 1.6, r, 13, GRAY, PP_ALIGN.LEFT)
        chip(s, M + 2.5, yy, 2.5, 0.55, a, size=14, fill=WHITE)
        arrow(s, M + 5.15, yy + 0.17, 0.55, 0.22)
        chip(s, M + 5.9, yy, 2.2, 0.55, b, size=14, fill=f, edge=ORANGE)
        label(s, M + 8.4, yy + 0.12, 3.0, c, 13, GRAY_LT, PP_ALIGN.LEFT)

    big(s, M, y + 3.85, CW, "Nobody told it the word “cat”. It **counted**, and found it.",
        16, ORANGE_DK)

    # ------------------------------------------------------------------ 8
    s = slide(prs, "Which one wins?", "Same sentence, two tokenizers")
    y = BODY_TOP + 0.3
    heading(s, M, y, CW, "\"the cat sat\"  —  by character")
    cell = 0.72
    a = ["t", "h", "e", "␣", "c", "a", "t", "␣", "s", "a", "t"]
    grid(s, M + 1.2, y + 0.4, cell, [a], texts=[a], size=14, fills=[[WHITE] * 11])
    label(s, M + 9.6, y + 0.55, 2.7, "**11 tokens**", 18, INK, PP_ALIGN.LEFT)

    y = BODY_TOP + 2.0
    heading(s, M, y, CW, "\"the cat sat\"  —  by BPE")
    b = ["the", " cat", " sat"]
    grid(s, M + 1.2, y + 0.4, 2.4, [b], texts=[b], size=16, fills=[[TINT2] * 3])
    label(s, M + 9.6, y + 0.6, 2.7, "**3 tokens**", 18, ORANGE, PP_ALIGN.LEFT)

    box(s, M, BODY_TOP + 3.5, CW, 1.3, None,
        ["The model can only hold a fixed number of tokens in its head. Fewer tokens for the "
         "same text means it **remembers more of the story.** That is why real models use BPE."],
        size=15, fill=TINT)

    # ================================================================ DATA
    # ------------------------------------------------------------------ 9
    s = step(prs, 2, "Where do the training examples come from?", "the data")
    big(s, M, BODY_TOP + 0.1, CW, "Nobody labels anything. The text labels itself.", 17)

    y = BODY_TOP + 0.95
    cell = 0.78
    xs = ["t", "h", "e", "␣", "c", "a", "t", "␣"]
    ys = ["h", "e", "␣", "c", "a", "t", "␣", "s"]
    xg = M + 2.6
    grid(s, xg, y, cell, [xs], texts=[xs], size=16, head_rows=["input"],
         fills=[[WHITE] * 8])
    grid(s, xg + cell / 2, y + cell + 0.35, cell, [ys], texts=[ys], size=16,
         head_rows=["answer"], fills=[[TINT2] * 8])

    label(s, M - 0.1, y + 1.05, 1.85, "shifted\nby one →", 14, ORANGE_DK, PP_ALIGN.RIGHT)

    y = BODY_TOP + 3.05
    big(s, M, y, CW, "The answer is just the input, **moved one place left.**", 18)
    box(s, M, y + 0.75, CW, 1.4, None,
        ["See “t” → say “h”.      See “the c” → say “a”.      See “the cat ” → say “s”.",
         "One line of 8 letters is **8 practice questions.** A line of 128 is 128."],
        size=15, fill=TINT)

    # ------------------------------------------------------------------ 10
    s = slide(prs, "Two files", "One to learn from, one to check honesty")
    y = BODY_TOP + 0.5
    chip(s, M + 0.6, y, 7.4, 1.0, "train.bin", sub="90% of the text — the model learns from this",
         fill=TINT, size=20)
    chip(s, M + 8.2, y, 3.4, 1.0, "val.bin", sub="10% — it never sees this",
         fill=WHITE, size=20)

    y = BODY_TOP + 2.1
    xl, xr, cw = twocol(s, 0.5)
    box(s, xl, y, cw, 2.0, "Both numbers going down",
        ["The model is learning **the language**.",
         "This is what you want to see."], size=15, fill=WHITE)
    rule(s, xl + 0.05, y + 0.02, cw - 0.1, ORANGE, 0.03)
    box(s, xr, y, cw, 2.0, "Only the training number going down",
        ["The model is **memorising the file**, not learning.",
         "Like a student who memorised the answer key."], size=15)

    big(s, M, y + 2.4, CW, "That is why we hold 10% back. It is the only way to tell the "
                           "difference.", 15, GRAY)

    # ================================================================ MODEL
    # ------------------------------------------------------------------ 11
    s = step(prs, 3, "The model, all of it", "the transformer")
    y = BODY_TOP + 0.1
    cx = M + 3.9
    bw = 5.5
    stack = [("numbers in", "[11, 5, 4, 0, 3, 2, 11]", WHITE),
             ("turn each into a vector", "what it is  +  where it sits", TINT),
             ("BLOCK 1", "tokens talk, then think", TINT2),
             ("BLOCK 2   ·   BLOCK 3   ·   BLOCK 4", "the same thing, three more times", TINT2),
             ("score every possible next token", "65 scores, one per character", TINT)]
    for i, (t, sub, f) in enumerate(stack):
        yy = y + i * 0.92
        chip(s, cx, yy, bw, 0.66, t, sub=sub, size=14, fill=f,
             edge=ORANGE if f != WHITE else LINE)
        if i < len(stack) - 1:
            arrow(s, cx + bw / 2 - 0.11, yy + 0.70, 0.22, 0.18, right=False)

    arrow(s, cx + bw / 2 - 0.11, y + 4.30, 0.22, 0.18, right=False)
    chip(s, cx, y + 4.58, bw, 0.6, "“the next letter is probably  s ”",
         fill=ORANGE_HI, edge=None, color=INK, size=15)

    label(s, M, y + 1.9, 3.4, "**This is the whole model.**", 16, INK, PP_ALIGN.LEFT)
    label(s, M, y + 2.5, 3.4, "Everything after this slide is just\nzooming into one of "
                              "these boxes.", 14.5, GRAY, PP_ALIGN.LEFT)

    # ------------------------------------------------------------------ 12
    s = slide(prs, "Inside  ·  vectors", "A number becomes a list of numbers")
    big(s, M, BODY_TOP + 0.1, CW, "One token id is not enough to describe a word. "
                                  "So each one gets **128 numbers** instead.", 16)

    y = BODY_TOP + 1.0
    cell = 0.8
    grid(s, M + 1.3, y, cell, [["11"]], texts=[["11"]], size=18, fills=[[WHITE]])
    arrow(s, M + 2.35, y + 0.28, 0.7, 0.24)
    vec = [["0.31", "-1.2", "0.04", "0.88", "…", "0.5"]]
    grid(s, M + 3.3, y, cell, vec, texts=vec, size=12, fills=[[TINT] * 6])
    label(s, M + 3.3, y + cell + 0.2, cell * 6, "128 numbers, learned during training",
          13, ORANGE_DK)
    label(s, M + 8.6, y + 0.15, 3.7, "The model can put “cat” and\n“dog” near each other here.\n"
                                     "Nobody programs that — it\nfalls out of training.",
          14, GRAY, PP_ALIGN.LEFT)

    y = BODY_TOP + 2.6
    heading(s, M, y, CW, "And we add one more thing: WHERE the token sits")
    chip(s, M + 1.4, y + 0.45, 3.2, 0.72, "what it is", sub="\"cat\"", size=15, fill=TINT)
    label(s, M + 4.75, y + 0.62, 0.6, "+", 22, ORANGE)
    chip(s, M + 5.5, y + 0.45, 3.2, 0.72, "where it is", sub="position 4", size=15, fill=TINT)
    label(s, M + 8.85, y + 0.62, 0.6, "=", 22, ORANGE)
    chip(s, M + 9.6, y + 0.45, 2.6, 0.72, "one vector", size=15, fill=TINT2, edge=ORANGE)

    big(s, M, y + 1.5, CW, "Without position, **“dog bites man” and “man bites dog” "
                           "look identical.**", 15, GRAY)

    # ------------------------------------------------------------------ 13
    s = slide(prs, "Inside  ·  attention", "How tokens look at each other")
    big(s, M, BODY_TOP + 0.05, CW, "Every token asks a question, advertises an answer, "
                                   "and carries information.", 16)

    y = BODY_TOP + 0.85
    xw = (CW - 0.9) / 3
    for i, (letter, name, quote) in enumerate([
        ("Q", "query", "“what am I looking for?”"),
        ("K", "key", "“here is what I am about”"),
        ("V", "value", "“here is what I will tell you”"),
    ]):
        x = M + i * (xw + 0.45)
        chip(s, x, y, xw, 0.7, f"{letter}   {name}", fill=ORANGE_HI, edge=None,
             color=INK, size=18)
        label(s, x, y + 0.9, xw, quote, 15, INK)

    y = BODY_TOP + 2.35
    heading(s, M, y, CW, "Example — the word “it” is looking for what it refers to")
    yy = y + 0.5
    words = ["The", "cat", "sat", "because", "it", "was", "tired"]
    ws = [1.15, 1.15, 1.15, 1.9, 0.95, 1.15, 1.35]
    x = M + 0.9
    for i, (w, wd) in enumerate(zip(words, ws)):
        f, e, c = WHITE, LINE, INK
        if i == 4:
            f, e, c = ORANGE_HI, None, INK
        elif i == 1:
            f, e = TINT2, ORANGE
        chip(s, x, yy, wd, 0.62, w, fill=f, edge=e, color=c, size=15)
        x += wd + 0.28
    label(s, M + 0.9, yy + 0.78, 3.0, "strong match ↑", 13, ORANGE_DK)
    label(s, M + 6.4, yy + 0.78, 2.0, "↑ asking", 13, ORANGE_DK)

    big(s, M, y + 2.05, CW, "“it” asks, “cat” matches best, so **“cat” gets copied into “it”.**",
        16)

    # ------------------------------------------------------------------ 14
    s = slide(prs, "Inside  ·  attention", "What that looks like as numbers")
    heading(s, M, BODY_TOP + 0.1, CW, "How much each word listens to each other word")
    y = BODY_TOP + 0.75
    cell = 0.82
    sm = [["100%", "", "", ""],
          ["33%", "67%", "", ""],
          ["25%", "25%", "50%", ""],
          ["54%", "13%", "27%", "6%"]]
    sf = [[TINT2 if c <= r else INK for c in range(4)] for r in range(4)]
    grid(s, M + 2.4, y, cell, sm, texts=sm, size=13, fills=sf,
         head_cols=["The", "cat", "sat", "on"],
         head_rows=["The", "cat", "sat", "on"])

    label(s, M + 6.4, y + 0.15, 5.9, "**Read a row across.**", 16, INK, PP_ALIGN.LEFT)
    label(s, M + 6.4, y + 0.7, 5.9, "Row “sat”: it listens 25% to “The”,\n"
                                    "25% to “cat”, and 50% to itself.", 15, GRAY, PP_ALIGN.LEFT)
    label(s, M + 6.4, y + 1.8, 5.9, "Every row adds up to 100%.", 15, GRAY, PP_ALIGN.LEFT)
    label(s, M + 6.4, y + 2.45, 5.9, "**The black squares are the future.**\nNothing gets "
                                     "through them — see the next slide.", 15, ORANGE_DK,
          PP_ALIGN.LEFT)

    # ------------------------------------------------------------------ 15
    s = slide(prs, "The most important rule", "A token can never see the future")
    y = BODY_TOP + 0.15
    cell = 0.62
    n = 6
    rows = [[1 if c <= r else 0 for c in range(n)] for r in range(n)]
    fills = [[TINT2 if c <= r else INK for c in range(n)] for r in range(n)]
    texts = [["✓" if c <= r else "✕" for c in range(n)] for r in range(n)]
    grid(s, M + 1.6, y + 0.4, cell, rows, fills=fills, texts=texts, size=15,
         head_cols=[f"w{j+1}" for j in range(n)],
         head_rows=[f"word {i+1}" for i in range(n)])
    label(s, M + 1.6, y + 0.4 + n * cell + 0.2, n * cell,
          "✓ = allowed to look   ·   ✕ = blocked", 13, GRAY)

    x2 = M + 6.3
    w2 = CW - 6.3
    big(s, x2, y + 0.5, w2, "Word 1 sees only itself.", 16, INK, PP_ALIGN.LEFT)
    big(s, x2, y + 1.1, w2, "Word 6 sees everything before it.", 16, INK, PP_ALIGN.LEFT)
    big(s, x2, y + 1.7, w2, "Nobody ever sees ahead.", 16, ORANGE, PP_ALIGN.LEFT)

    box(s, x2, y + 2.5, w2, 1.9, "Why?",
        ["When the model is **writing**, the future does not exist yet.",
         "So while it learns, we block the future too — otherwise it would be copying "
         "the answer instead of predicting it."], size=15)

    # ------------------------------------------------------------------ 16
    s = slide(prs, "Inside  ·  a block", "Talk, then think")
    y = BODY_TOP + 0.4
    chip(s, M + 0.8, y, 2.4, 1.0, "a token", size=17, fill=WHITE)
    arrow(s, M + 3.35, y + 0.36, 0.6, 0.28)
    chip(s, M + 4.1, y, 3.3, 1.0, "ATTENTION", sub="look at the other tokens\nand take what you need",
         size=16, fill=TINT2, edge=ORANGE)
    arrow(s, M + 7.55, y + 0.36, 0.6, 0.28)
    chip(s, M + 8.3, y, 3.3, 1.0, "MLP", sub="think alone about\nwhat you just heard",
         size=16, fill=TINT2, edge=ORANGE)

    label(s, M + 4.1, y + 1.15, 3.3, "tokens talking", 14, ORANGE_DK)
    label(s, M + 8.3, y + 1.15, 3.3, "one token thinking", 14, ORANGE_DK)

    y = BODY_TOP + 2.3
    heading(s, M, y, CW, "Then stack that block four times")
    x = M + 1.6
    for i in range(4):
        chip(s, x, y + 0.5, 2.0, 0.7, f"block {i+1}", size=15,
             fill=TINT if i % 2 == 0 else WHITE)
        if i < 3:
            arrow(s, x + 2.05, y + 0.68, 0.35, 0.22)
        x += 2.4

    big(s, M, y + 1.55, CW, "Four rounds of “talk, then think”. **That is the whole "
                            "transformer.**", 17)
    big(s, M, y + 2.2, CW, "GPT-4 does the same thing — just with far more blocks, "
                           "far bigger.", 15, GRAY)

    # ================================================================ TRAINING
    # ------------------------------------------------------------------ 17
    s = step(prs, 4, "How it learns", "training")
    y = BODY_TOP + 0.3
    loop = [("1", "Show it some text"),
            ("2", "Ask it to guess the next letter"),
            ("3", "Measure how wrong it was"),
            ("4", "Work out which way to adjust"),
            ("5", "Adjust everything a tiny bit")]
    for i, (n, t) in enumerate(loop):
        yy = y + i * 0.78
        chip(s, M + 1.6, yy, 0.6, 0.6, n, fill=ORANGE_HI, edge=None, color=INK, size=17)
        label(s, M + 2.5, yy + 0.1, 7.0, t, 18, INK, PP_ALIGN.LEFT)
        if i < 4:
            arrow(s, M + 1.81, yy + 0.64, 0.18, 0.16, right=False)

    label(s, M + 9.3, y + 1.7, 3.0, "then do it again\n**2,000 times**", 17, ORANGE_DK,
          PP_ALIGN.LEFT)

    box(s, M, y + 4.2, CW, 0.9, None,
        ["There is no step 6. **Every** neural network ever built was trained by this loop."],
        size=16, fill=TINT)

    # ------------------------------------------------------------------ 18
    s = slide(prs, "The number that matters", "Loss = how surprised the model was")
    y = BODY_TOP + 0.4
    stages = [("4.17", "at the start", "pure guessing", ORANGE),
              ("2.50", "after 250 steps", "learned which letters are common", WHITE),
              ("1.80", "after 1,000 steps", "learned word shapes", WHITE),
              ("1.60", "after 2,000 steps", "learned names and line breaks", TINT)]
    xw = (CW - 1.2) / 4
    for i, (v, when, what, f) in enumerate(stages):
        x = M + i * (xw + 0.4)
        chip(s, x, y, xw, 0.75, when, fill=f, edge=ORANGE,
             color=INK, size=14)
        label(s, x, y + 0.95, xw, v, 38, INK)
        label(s, x, y + 1.95, xw, what, 13, GRAY)

    y = BODY_TOP + 3.0
    big(s, M, y, CW, "**Lower is better.** It means the model was less surprised by "
                     "what actually came next.", 17)
    box(s, M, y + 0.75, CW, 1.35, None,
        ["Zero would be a model that is never surprised — impossible, because language "
         "is not predictable. **Watching this number fall is the real result of today.**"],
        size=15, fill=TINT)

    # ------------------------------------------------------------------ 19
    s = slide(prs, "Watch it learn", "The same model, writing, as training goes on")
    y = BODY_TOP + 0.15
    samples = [
        ("step 250", ["oTh eaw rn,dtI ohes", "ne tt ahe uor mt sae"], "noise with the right letters"),
        ("step 1,000", ["OMIO:", "And the sear the world", "the sead of hear"],
         "words appear, names almost work"),
        ("step 2,000", ["ROMEO:", "I will be so the world,", "And the state of his death."],
         "names, colons, line breaks, sentence shape"),
    ]
    xw = (CW - 0.9) / 3
    for i, (when, lines, note) in enumerate(samples):
        x = M + i * (xw + 0.45)
        chip(s, x, y, xw, 0.6, when, fill=ORANGE_HI if i == 2 else WHITE, edge=ORANGE,
             color=INK, size=15)
        code(s, x, y + 0.78, xw, 1.85, lines, size=12.5)
        label(s, x + 0.1, y + 2.8, xw - 0.2, note, 13.5, GRAY)

    y = BODY_TOP + 3.6
    box(s, M, y, CW, 1.35, "Be honest about what this is",
        ["It is 0.8 million numbers trained for three minutes on 1 MB of text. It learned the "
         "**shape** of Shakespeare, not the meaning. **That is exactly what should happen** — "
         "and it is the same process that made ChatGPT, at a millionth of the scale."],
        size=14.5)

    # ================================================================ USING IT
    # ------------------------------------------------------------------ 20
    s = step(prs, 5, "How it writes a whole sentence", "generating")
    big(s, M, BODY_TOP + 0.1, CW, "It only ever predicts **one** token. So we just ask it "
                                  "again, and again.", 16)

    y = BODY_TOP + 0.9
    chain = [("\"ROMEO\"", "\":\""), ("\"ROMEO:\"", "new line"), ("\"ROMEO:⏎\"", "\"I\""),
             ("\"ROMEO:⏎I\"", "\" \""), ("\"ROMEO:⏎I \"", "\"w\"")]
    for i, (a, b) in enumerate(chain):
        yy = y + i * 0.66
        label(s, M + 1.0, yy, 4.2, a, 16, INK, PP_ALIGN.RIGHT)
        arrow(s, M + 5.5, yy + 0.08, 0.7, 0.2)
        label(s, M + 6.4, yy, 2.4, b, 16, ORANGE_DK, PP_ALIGN.LEFT)
        if i < 4:
            label(s, M + 8.9, yy, 3.4, "…then feed it back in", 12.5, GRAY_LT, PP_ALIGN.LEFT)

    box(s, M, y + 3.6, CW, 1.2, None,
        ["There is **no plan and no draft.** It makes one small choice, forgets it, and makes "
         "the next one. Everything that looks like intention comes out of that."],
        size=15, fill=TINT)

    # ------------------------------------------------------------------ 21
    s = slide(prs, "One dial you control", "Temperature — how bold the model is")
    y = BODY_TOP + 0.35
    opts = [("0.2", "safe", ["the   99%", "a      1%", "my     0%"],
             "Almost always picks the favourite. Sensible, but repeats itself."),
            ("0.8", "the default", ["the   65%", "a     19%", "my    10%"],
             "Usually sensible, sometimes surprising. This is what we use."),
            ("1.5", "wild", ["the   46%", "a     24%", "my    17%"],
             "Gives odd choices a real chance. Creative, then incoherent.")]
    xw = (CW - 0.9) / 3
    for i, (t, name, lines, note) in enumerate(opts):
        x = M + i * (xw + 0.45)
        chip(s, x, y, xw, 0.68, f"{t}   {name}", fill=ORANGE_HI if i == 1 else WHITE,
             edge=ORANGE, color=INK, size=16)
        code(s, x, y + 0.85, xw, 1.5, lines, size=13)
        label(s, x + 0.1, y + 2.5, xw - 0.2, note, 14, GRAY)

    big(s, M, y + 3.85, CW, "The last step is a **weighted dice roll** — which is why the "
                            "same prompt gives different text every time.", 15)

    # ------------------------------------------------------------------ 22
    s = slide(prs, "From your laptop to a real GPU", "Same code. Different machine.")
    y = BODY_TOP + 0.5
    xl, xr, cw = twocol(s, 0.6)
    box(s, xl, y, cw, 2.3, "Your laptop",
        ["**0.8 million** numbers to learn",
         "About **3 minutes**",
         "Output: Shakespeare-shaped nonsense"], size=15, fill=WHITE)
    rule(s, xl + 0.05, y + 0.02, cw - 0.1, ORANGE, 0.03)
    box(s, xr, y, cw, 2.3, "A rented GPU",
        ["**10.8 million** numbers to learn",
         "About **10 minutes**, costs about **13 cents**",
         "Output: actually readable-ish"], size=15)

    y = BODY_TOP + 3.1
    big(s, M, y, CW, "Not one line of the model changes. Only **where it runs.**", 17)
    y += 0.75
    chips = [("your code", WHITE), ("rented GPU", TINT), ("trained model saved", TINT),
             ("behind a URL", ORANGE_HI)]
    x = M + 1.0
    for i, (t, f) in enumerate(chips):
        chip(s, x, y, 2.4, 0.65, t, fill=f, edge=None if f == ORANGE_HI else ORANGE,
             color=INK, size=14)
        if i < 3:
            arrow(s, x + 2.45, y + 0.22, 0.35, 0.2)
        x += 2.8

    # ------------------------------------------------------------------ 23
    s = slide(prs, "Now you are the API", "Your model, on your own URL")
    y = BODY_TOP + 0.4
    xl, xr, cw = twocol(s, 0.6)
    box(s, xl, y, cw, 2.0, "Sessions 1 – 6",
        ["You sent a request to **somebody else's** model.",
         "Their key. Their price. Their rules."], size=15, fill=WHITE)
    rule(s, xl + 0.05, y + 0.02, cw - 0.1, ORANGE, 0.03)
    box(s, xr, y, cw, 2.0, "Today",
        ["You send a request to **your own** model.",
         "You trained it. You host it. You own it."], size=15)

    y = BODY_TOP + 2.75
    code(s, M, y, CW, 1.5, [
        "curl -X POST  https://<your-url>  \\",
        "     -d '{\"prompt\": \"ROMEO:\", \"max_tokens\": 200}'",
    ], size=13.5, title="AND ANYONE CAN CALL IT")

    big(s, M, y + 1.75, CW, "The same LangChain code from Session 6 works on it, unchanged.",
        15, GRAY)

    # ================================================================ CONTEXT
    # ------------------------------------------------------------------ 24
    s = slide(prs, "So why isn't it ChatGPT?", "You built the bottom layer. There are four more.")
    y = BODY_TOP + 0.25
    layers = [
        ("Layer 0", "Pretraining — predict the next token", "**This is what we built today.**", True),
        ("Layer 1", "Scale — about a million times bigger, on a million times more text", "", False),
        ("Layer 2", "Instruction tuning — teach it to *answer* instead of *continue*", "", False),
        ("Layer 3", "Human feedback — teach it which answers people prefer", "", False),
        ("Layer 4", "Reasoning training — teach it to think in steps first", "", False),
    ]
    for i, (n, t, extra, mine) in enumerate(reversed(layers)):
        yy = y + i * 0.82
        f = ORANGE_HI if mine else WHITE
        chip(s, M + 0.5, yy, 1.5, 0.6, n, fill=f, edge=ORANGE,
             color=INK, size=14)
        label(s, M + 2.3, yy + 0.12, 8.6, t, 15.5, INK if mine else GRAY, PP_ALIGN.LEFT)
        if mine:
            label(s, M + 8.9, yy + 0.13, 3.4, extra, 14, ORANGE, PP_ALIGN.LEFT)

    big(s, M, y + 4.3, CW, "**Layer 0 is the engine. The other four are the driving lessons.**",
        17)
    big(s, M, y + 4.9, CW, "Nobody can build layers 1–4 without layer 0 — and now you know "
                           "exactly what it is.", 14.5, GRAY)

    # ------------------------------------------------------------------ 25
    s = slide(prs, "What changed since 2019?", "Less than you would think")
    table(s, M, BODY_TOP + 0.2, CW, [
        ["What we built  (GPT-2, 2019)", "What GPT-5 and Llama use today"],
        ["attention", "**the same attention**"],
        ["predict the next token", "**the same objective**"],
        ["can't see the future", "**the same rule**"],
        ["stack identical blocks", "**the same structure**"],
        ["remembers 128 tokens", "remembers 400,000 — a smarter way to number positions"],
        ["one thinking layer per block", "hundreds of them, but only a few run per token"],
        ["trained on 1 MB", "trained on **10-20 trillion** words"],
    ], widths=[5.4, 6.8], size=13.5, row_h=0.5, head_h=0.45)

    box(s, M, BODY_TOP + 4.55, CW, 0.95, None,
        ["**The core did not change.** What changed was the amount of data, the amount of "
         "computing, and the training that happens afterwards."], size=15, fill=TINT)

    # ------------------------------------------------------------------ 26
    s = slide(prs, "The honest scale", "Why yours writes nonsense and theirs does not")
    y = BODY_TOP + 0.5
    cols = [("Your model today", "10.8 M", "numbers to learn", "~4.6 M words of training text", WHITE),
            ("The smallest real model", "135 M", "numbers to learn",
             "**2,000,000,000,000** words", TINT),
            ("GPT-4 class", "~1,000,000 M", "roughly", "the readable internet", WHITE)]
    xw = (CW - 0.9) / 3
    for i, (t, big_n, sub, data, f) in enumerate(cols):
        x = M + i * (xw + 0.45)
        chip(s, x, y, xw, 0.62, t, fill=ORANGE_HI if i == 0 else WHITE, edge=ORANGE,
             color=INK, size=14)
        label(s, x, y + 0.85, xw, big_n, 30, INK)
        label(s, x, y + 1.65, xw, sub, 12.5, GRAY_LT)
        label(s, x, y + 2.15, xw, data, 14, ORANGE_DK)

    box(s, M, y + 3.1, CW, 1.4, None,
        ["The smallest serious model is only about **13× bigger** than yours — but it read "
         "about **2,000,000× more text.**",
         "**The design is the easy part. The data and the computing are the mountain.**"],
        size=15, fill=TINT)

    # ------------------------------------------------------------------ 27
    s = slide(prs, "Everything on one page", "The whole session")
    y = BODY_TOP + 0.2
    recap = [
        ("Text becomes numbers", "a tokenizer, built by counting — not by the network"),
        ("The answer is the text itself", "shifted one place left"),
        ("Tokens look backwards at each other", "and never at the future"),
        ("Each token then thinks alone", "attention, then MLP — repeated N times"),
        ("Training is five steps, repeated", "guess, measure, adjust"),
        ("Writing is one token at a time", "predict, append, repeat"),
        ("It is not ChatGPT because of data and tuning", "not because of the design"),
    ]
    for i, (t, d) in enumerate(recap):
        yy = y + i * 0.75
        chip(s, M + 0.4, yy, 0.5, 0.5, str(i + 1), fill=ORANGE_HI, edge=None, color=INK, size=13)
        label(s, M + 1.1, yy - 0.02, 6.6, t, 16, INK, PP_ALIGN.LEFT)
        label(s, M + 7.9, yy + 0.05, 4.4, d, 13.5, GRAY, PP_ALIGN.LEFT)

    # ------------------------------------------------------------------ 28
    s = slide(prs, "Try it yourself", "Six commands. It runs on your laptop.")
    code(s, M, BODY_TOP + 0.3, CW, 2.6, [
        "python data3.py --dataset shakespeare --tokenizer char",
        "python train5.py                    # ~3 minutes, watch the loss fall",
        "python generate6.py --prompt \"ROMEO:\"",
    ], size=14, title="ON YOUR OWN MACHINE")

    y = BODY_TOP + 3.2
    xw = (CW - 0.9) / 3
    for i, (t, d) in enumerate([
        ("Change one number", "Open `config1.py`, change `n_layer` to 6, run it again. "
                              "Watch what happens to the loss."),
        ("Use your own text", "Put any `.txt` at `data/custom/input.txt` and run with "
                              "`--dataset custom`."),
        ("Break it on purpose", "Set `learning_rate` to `0.1` and watch the loss explode. "
                                "Now you know what that looks like."),
    ]):
        x = M + i * (xw + 0.45)
        chip(s, x, y, xw, 0.6, t, fill=ORANGE_HI, edge=None, color=INK, size=14)
        label(s, x + 0.1, y + 0.8, xw - 0.2, d, 14, GRAY, PP_ALIGN.LEFT)

    # ------------------------------------------------------------------ 29
    s = slide(prs, "One last thing", "It really is just one sentence")
    box(s, M, BODY_TOP + 0.7, CW, 1.9, None,
        ["Everything you saw today — a text file turning into a model on a URL — "
         "is built on one sentence:",
         "~~Predict the next token.~~"], size=19, fill=TINT)

    big(s, M, BODY_TOP + 3.1, CW, "GPT-5 is the same sentence, with more data, more "
                                  "computing, and a few extra parts.", 17)
    big(s, M, BODY_TOP + 3.85, CW, "**You did not build a toy. You built the foundation — "
                                   "and now you can see what everything else stands on.**", 17)

    label(s, M, BODY_TOP + 4.9, CW, "AI Season   ·   Abdul Rahman Azam", 15, ORANGE_DK)


def main():
    prs = Presentation()
    prs.slide_width = Inches(theme.W)
    prs.slide_height = Inches(theme.H)
    theme.reset_counter()
    theme.FOOTER = "AI Season   ·   Build an LLM from Scratch, Part 2"
    build(prs)
    prs.save(OUT)
    print(f"{len(prs.slides._sldIdLst)} slides -> {os.path.abspath(OUT)}")


if __name__ == "__main__":
    main()
