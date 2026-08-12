"""
FILE 2: Building the instruction dataset
=========================================
This is the file that decides whether your model works. Not the
architecture. Not the learning rate. This one.

A base model learns the SHAPE of language from raw text. An instruction
model learns the JOB from examples of the job being done. So we have to
write those examples. All of them.

We take 92 hand-written coding tasks from tasks.py and multiply them out
along four independent axes:

    1. how the question is phrased    "write a function to X"
                                      "how do i X in python"
                                      "im stuck, how do i X"
    2. how the task is described      "reverse a string"
                                      "flip a string backwards"
    3. what the parameter is called   def reverse_string(s)
                                      def reverse_string(text)
    4. what KIND of question it is    write it / explain it / fix it /
                                      answer a follow-up

92 tasks becomes about ten thousand examples. That multiplication is why
the model learns the IDEA instead of memorising one exact sentence.

THE HELD-OUT PHRASINGS
    The last few question templates in each list are never used for
    training. They only appear in val.jsonl. So when we measure val loss we
    are asking a real question: did it learn what the user MEANT, or did it
    just memorise the words they used? That is the honest test, and it is
    the one that matters for a chat model.

WE TEST THE DATA BEFORE WE TRAIN ON IT
    Every single code sample is executed and its assert is run, first, here.
    A model trained on broken code learns to write broken code, and no
    amount of GPU fixes that. Garbage in, garbage out is not a slogan, it is
    a measurement.

Run me:  python build_data2.py
         python build_data2.py --per-task 100     # a bigger dataset
"""

import argparse
import json
import os
import random
import textwrap

from chat_format1 import render
from tasks import ALL_CONCEPTS, ALL_TASKS, BUGS

random.seed(1337)          # same dataset every time, so results are comparable


# ============================================================
# 1. QUESTION TEMPLATES  -  how a human might ask
# ============================================================
# The last HELD_OUT of each list is for validation only. The model never
# trains on those sentences.

HELD_OUT = 5

WRITE_TEMPLATES = [
    "write a python function to {ask}",
    "write a function to {ask}",
    "how do i {ask} in python",
    "how do i {ask}",
    "can you {ask}",
    "can you write code to {ask}",
    "give me python code to {ask}",
    "i need a function that will {ask}",
    "show me how to {ask}",
    "what is the best way to {ask}",
    "python function to {ask}",
    "code to {ask}",
    "please write a function to {ask}",
    "i want to {ask}",
    "could you {ask} for me",
    "help me {ask}",
    "write me a script to {ask}",
    "whats the python way to {ask}",
    "make a function to {ask}",
    "create a python function that will {ask}",
    "{ask}",
    "python: {ask}",
    # Question marks on the CODE side too. Without these, every "?" in the
    # dataset belonged to a concept question, and the model learned that
    # punctuation mark as the signal instead of the words. See the README -
    # this was a real bug and it took an evaluation to catch it.
    "how do i {ask}?",
    "can you {ask}?",
    "how would i {ask}?",
    "whats the easiest way to {ask}?",
    # Apologetic lead-ins on the CODE side too, for the same reason. The
    # concept templates below all start with things like "im new to python"
    # and "sorry if this is basic", so without these the model reads any
    # hesitant opening as "this person wants an explanation, not a function".
    "im new to python, how do i {ask}",
    "sorry if this is basic, how do i {ask}",
    "i cant work this out. how do i {ask}?",
    "quick question - how do i {ask}?",
    # ---- held out, validation only ----
    "any idea how to {ask}",
    "im stuck, how do i {ask}",
    "is there a simple way to {ask}",
    "how would you {ask} in python",
    "do you know how to {ask}",
]

EXPLAIN_TEMPLATES = [
    "what does this code do?\n\n```python\n{code}\n```",
    "explain this code\n\n```python\n{code}\n```",
    "can you explain what this does\n\n```python\n{code}\n```",
    "explain this to me\n\n```python\n{code}\n```",
    "what is this function doing\n\n```python\n{code}\n```",
    "walk me through this code\n\n```python\n{code}\n```",
    "i dont understand this code\n\n```python\n{code}\n```",
    # ---- held out, validation only ----
    "what is going on here\n\n```python\n{code}\n```",
    "could you explain this one\n\n```python\n{code}\n```",
    "whats this code for\n\n```python\n{code}\n```",
    "tell me what this does\n\n```python\n{code}\n```",
    "explain please\n\n```python\n{code}\n```",
]

FIX_TEMPLATES = [
    "fix this code\n\n```python\n{code}\n```",
    "whats wrong with this code?\n\n```python\n{code}\n```",
    "this code is not working, can you fix it\n\n```python\n{code}\n```",
    "why does this not work?\n\n```python\n{code}\n```",
    "debug this for me\n\n```python\n{code}\n```",
    "there is a bug in here somewhere\n\n```python\n{code}\n```",
    "this is broken, help\n\n```python\n{code}\n```",
    # ---- held out, validation only ----
    "can you spot the mistake\n\n```python\n{code}\n```",
    "my code gives the wrong answer\n\n```python\n{code}\n```",
    "what did i do wrong\n\n```python\n{code}\n```",
    "please fix\n\n```python\n{code}\n```",
    "something is off with this\n\n```python\n{code}\n```",
]

FOLLOW_UPS = [
    "explain that",
    "how does it work",
    "why does that work",
    "can you explain it",
    "explain the code",
    "i dont understand, explain please",
    "what is it actually doing",
    # ---- held out, validation only ----
    "break that down for me",
    "how come that works",
    "explain it simply",
    "say more about that",
    "why though",
]

CONCEPT_TEMPLATES = [
    "{ask}",
    "hey, {ask}",
    "can you explain, {ask}",
    "i have a question - {ask}",
    "quick question. {ask}",
    "please explain: {ask}",
    "sorry if this is basic, but {ask}",
    "im new to python. {ask}",
    "tell me, {ask}",
    "in simple terms, {ask}",
    "explain like im five: {ask}",
    "one more thing - {ask}",
    "i keep hearing about this. {ask}",
    # ---- held out, validation only ----
    "so {ask}",
    "just wondering, {ask}",
    "could someone explain, {ask}",
    "help me understand: {ask}",
    "genuinely no idea - {ask}",
]

# Tacked onto the end of a concept question when it does not already end in
# punctuation. Cheap variety: 18 frames x 2 descriptions x 6 endings is over
# 200 distinct ways to ask the same thing, which is what stops the model
# keying off one exact sentence.
#
# The two empty strings are not padding. Without them EVERY concept question
# ended in punctuation and every code question did not, so the model learned
# the punctuation and ignored the words.
CONCEPT_ENDINGS = ["", "", "?", "?", ".", " please?", " thanks"]

OPENERS = [
    "Here is a Python function that will {ask}:",
    "Sure. This function will {ask}:",
    "You can {ask} like this:",
    "Here is one way to {ask}:",
]


def train_half(templates):
    return templates[:-HELD_OUT]


def val_half(templates):
    return templates[-HELD_OUT:]


# ============================================================
# 2. SMALL TALK  -  so it does not answer "hi" with a for loop
# ============================================================
# Ten lines of data that make the model feel like an assistant instead of
# a code vending machine. Cheap, and the first thing anyone types.

SMALL_TALK = [
    (["hi", "hello", "hey", "hey there", "yo", "hi there", "good morning"],
     "Hi! Ask me for a Python function and I will write it and explain "
     "how it works."),
    (["who are you", "what are you", "whats your name", "introduce yourself"],
     "I am ARGPT-Coder, a small language model built from scratch and "
     "trained on Python coding questions. Ask me to write a function, "
     "explain some code, or fix a bug."),
    (["what can you do", "what can you help with", "how can you help me",
      "what do you know"],
     "I can write small Python functions, explain what a piece of code "
     "does, fix simple bugs, and answer questions about Python ideas like "
     "list comprehensions or classes."),
    (["thanks", "thank you", "thanks a lot", "cheers", "nice, thanks"],
     "You are welcome. Ask me anything else about Python."),
    (["are you chatgpt", "are you gpt4", "how big are you"],
     "No. I am a very small model that was trained from scratch on a "
     "narrow set of Python coding examples. I am good inside that set and "
     "I make things up outside it."),
    (["bye", "goodbye", "see you", "thats all"],
     "Bye! Come back when you have another Python question."),
]


# ============================================================
# 3. BUGS  -  break working code in realistic ways
# ============================================================
# Each function takes correct code and returns a broken version, or None if
# that particular mistake does not apply to that particular function. That
# `or None` is why we never produce a nonsense "fix this" example.

def bug_missing_return(code):
    """Delete the word `return`. The function now silently gives back None."""
    lines = code.split("\n")
    for i in range(len(lines) - 1, -1, -1):
        body = lines[i].lstrip()
        if body.startswith("return ") and lines[i].startswith("    "):
            indent = lines[i][: len(lines[i]) - len(body)]
            lines[i] = indent + body[len("return "):]
            return "\n".join(lines)
    return None


def bug_assignment_in_condition(code):
    """Turn == into = inside an if. Python refuses to even parse it."""
    lines = code.split("\n")
    for i, line in enumerate(lines):
        body = line.lstrip()
        if (body.startswith("if ") or body.startswith("elif ")) and " == " in line:
            lines[i] = line.replace(" == ", " = ", 1)
            return "\n".join(lines)
    return None


def bug_off_by_one(code):
    """Drop the + 1 from a range, so the loop stops one short."""
    if "+ 1):" in code:
        return code.replace("+ 1):", "):", 1)
    return None


def bug_wrong_indent(code):
    """Pull the final return inside the loop, so it exits on the first pass."""
    lines = code.split("\n")
    last = len(lines) - 1
    if lines[last].startswith("    return ") and len(lines) >= 3:
        if any(l.startswith("        ") and l.strip() for l in lines[:last]):
            lines[last] = "    " + lines[last]
            return "\n".join(lines)
    return None


BUG_MAKERS = {
    "missing_return": bug_missing_return,
    "assignment_in_condition": bug_assignment_in_condition,
    "off_by_one": bug_off_by_one,
    "wrong_indent": bug_wrong_indent,
}
BUG_WHY = dict(BUGS)


# ============================================================
# 4. TESTING THE CURRICULUM BEFORE WE TRAIN ON IT
# ============================================================

def verify(tasks):
    """
    Execute every task's code, for every parameter name, and run its assert.

    This takes about a second and it is the highest-value second in the
    whole session. If it fails you have found a bug in your DATA, which is
    the one kind of bug training will never fix - it will faithfully learn
    the broken version instead.
    """
    checked = 0
    for task in tasks:
        for var in task["vars"]:
            code = task["code"].replace("{v}", var)
            scope = {}
            try:
                exec(code, scope)
                exec(task["test"], scope)
            except Exception as error:
                raise SystemExit(
                    f"\nBROKEN TASK in tasks.py: {task['name']} (with {var!r})\n"
                    f"{type(error).__name__}: {error}\n\n{code}\n"
                )
            checked += 1
    return checked


# ============================================================
# 5. TURNING TASKS INTO CONVERSATIONS
# ============================================================

def wrap(text, width=74):
    """Keep explanations to a sane line width so the output looks tidy."""
    return textwrap.fill(text, width=width)


def code_answer(task, var, ask, rng):
    """The full assistant reply for a "write me this" question."""
    # The opener echoes the user's own wording back at them. Small touch,
    # but it is a big part of why a reply feels like it was read rather
    # than looked up.
    opener = rng.choice(OPENERS).replace("{ask}", ask)
    code = task["code"].replace("{v}", var)
    return f"{opener}\n\n```python\n{code}\n```\n\n{wrap(task['why'])}"


def explain_answer(task):
    """The reply for "what does this code do". One line of what, then why."""
    return f"This code will {task['asks'][0]}.\n\n{wrap(task['why'])}"


def build(per_task=60, explains=16, follows=10, fixes=8, concepts_each=45):
    """Produce (train, val) lists of examples."""
    train, val = [], []
    seen = set()

    def add(bucket, turns, task_name, kind):
        text = render(turns)
        if text in seen:               # never store the exact same string twice
            return
        seen.add(text)
        bucket.append({"turns": turns, "task": task_name, "kind": kind})

    for task in ALL_TASKS:
        rng = random.Random(task["name"])       # stable per task

        # ---------- write me this function ----------
        for bucket, templates, n in ((train, train_half(WRITE_TEMPLATES), per_task),
                                     (val, val_half(WRITE_TEMPLATES), max(2, per_task // 10))):
            for _ in range(n):
                var = rng.choice(task["vars"])
                ask = rng.choice(task["asks"])
                question = rng.choice(templates).replace("{ask}", ask)
                add(bucket, [[question, code_answer(task, var, ask, rng)]],
                    task["name"], "write")

        # ---------- what does this code do ----------
        for bucket, templates, n in ((train, train_half(EXPLAIN_TEMPLATES), explains),
                                     (val, val_half(EXPLAIN_TEMPLATES), max(2, explains // 4))):
            for _ in range(n):
                var = rng.choice(task["vars"])
                code = task["code"].replace("{v}", var)
                question = rng.choice(templates).replace("{code}", code)
                add(bucket, [[question, explain_answer(task)]], task["name"], "explain")

        # ---------- fix this broken code ----------
        for bucket, templates, n in ((train, train_half(FIX_TEMPLATES), fixes),
                                     (val, val_half(FIX_TEMPLATES), max(1, fixes // 4))):
            for _ in range(n):
                var = rng.choice(task["vars"])
                good = task["code"].replace("{v}", var)
                # only the mistakes that CAN be made in this particular
                # function - you cannot forget a `return` that is not there
                possible = [(name, maker(good)) for name, maker in BUG_MAKERS.items()]
                possible = [(name, broken) for name, broken in possible if broken]
                if not possible:
                    break
                kind, broken = rng.choice(possible)
                question = rng.choice(templates).replace("{code}", broken)
                answer = f"{wrap(BUG_WHY[kind])}\n\n```python\n{good}\n```"
                add(bucket, [[question, answer]], task["name"], "fix")

        # ---------- two turns: write it, then "explain that" ----------
        for bucket, templates, follow_pool, n in (
                (train, train_half(WRITE_TEMPLATES), train_half(FOLLOW_UPS), follows),
                (val, val_half(WRITE_TEMPLATES), val_half(FOLLOW_UPS), max(1, follows // 4))):
            for _ in range(n):
                var = rng.choice(task["vars"])
                ask = rng.choice(task["asks"])
                first = rng.choice(templates).replace("{ask}", ask)
                add(bucket,
                    [[first, code_answer(task, var, ask, rng)],
                     [rng.choice(follow_pool), wrap(task["why"])]],
                    task["name"], "followup")

    # ---------- concept questions ----------
    # Held out here is BOTH the last way of describing the concept and the
    # last five sentence frames, so val really is unseen wording.
    for concept in ALL_CONCEPTS:
        rng = random.Random(concept["name"])
        asks = concept["asks"]
        train_asks = asks[:-1] if len(asks) > 1 else asks
        for bucket, pool, templates, n in (
                (train, train_asks, train_half(CONCEPT_TEMPLATES), concepts_each),
                (val, asks[-1:], val_half(CONCEPT_TEMPLATES), max(2, concepts_each // 5))):
            for _ in range(n):
                question = rng.choice(templates).replace("{ask}", rng.choice(pool))
                if question[-1].isalnum():
                    question += rng.choice(CONCEPT_ENDINGS)
                add(bucket, [[question, concept["answer"]]], concept["name"], "concept")

    # ---------- small talk ----------
    for asks, answer in SMALL_TALK:
        for question in asks:
            for suffix in ("", "!", "?"):
                add(train, [[question + suffix, answer]], "smalltalk", "chat")

    random.shuffle(train)
    random.shuffle(val)
    return train, val


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def write_corpus(path):
    """
    Every unique BUILDING BLOCK of the dataset, written down once.

    Not the 7,800 conversations - the ingredients they are made of. Every
    line of code, every explanation, every sentence frame, exactly one copy
    each.

    Why: BPE counts pairs of tokens in pure Python, which is slow. Training
    it on 3.5 MB of highly repetitive text takes minutes and produces
    exactly the same merges as training it on the 130 KB of unique material
    those 3.5 MB are built from. The tokenizer needs to see the vocabulary,
    not ten thousand copies of it.
    """
    pieces = ["```python", "```", "<|user|>", "<|assistant|>", "<|end|>"]

    for task in ALL_TASKS:
        for var in task["vars"]:
            pieces.append(task["code"].replace("{v}", var))
            broken = bug_missing_return(task["code"].replace("{v}", var))
            if broken:
                pieces.append(broken)
        pieces.append(wrap(task["why"]))
        pieces.extend(task["asks"])
        # A sentence frame only needs to appear often enough for BPE to see
        # it as common. Three asks each is plenty; all 92 would triple the
        # file for no extra merges.
        for template in WRITE_TEMPLATES:
            for ask in task["asks"][:1]:
                pieces.append(template.replace("{ask}", ask))
        for opener in OPENERS:
            pieces.append(opener.replace("{ask}", task["asks"][0]))

    for concept in ALL_CONCEPTS:
        pieces.append(concept["answer"])
        for ask in concept["asks"]:
            pieces.append(ask)
        for template in CONCEPT_TEMPLATES:
            pieces.append(template.replace("{ask}", concept["asks"][0]))

    for template in EXPLAIN_TEMPLATES + FIX_TEMPLATES:
        pieces.append(template.replace("{code}", ""))
    pieces.extend(FOLLOW_UPS)
    for asks, answer in SMALL_TALK:
        pieces.extend(asks)
        pieces.append(answer)
    for name, why in BUGS:
        pieces.append(wrap(why))

    unique = sorted(set(pieces))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(unique))
    return len(unique), sum(len(p) + 1 for p in unique)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--per-task", type=int, default=60,
                   help="how many 'write this function' examples per task")
    p.add_argument("--out", default="data")
    args = p.parse_args()

    os.makedirs(args.out, exist_ok=True)

    # ---------- STEP 1: is the curriculum actually correct? ----------
    print("=" * 62)
    print("STEP 1  running every code sample in tasks.py")
    print("=" * 62)
    checked = verify(ALL_TASKS)
    print(f"  {checked} code samples executed, {checked} asserts passed")
    print("  every line the model will learn from is known-good code")

    # ---------- STEP 2: multiply it out ----------
    print("\n" + "=" * 62)
    print("STEP 2  turning 92 tasks into a conversation dataset")
    print("=" * 62)
    train, val = build(per_task=args.per_task)

    kinds = {}
    for row in train:
        kinds[row["kind"]] = kinds.get(row["kind"], 0) + 1
    for kind, count in sorted(kinds.items(), key=lambda kv: -kv[1]):
        print(f"  {kind:10s} {count:6,d}")
    print(f"  {'-' * 17}")
    print(f"  {'train':10s} {len(train):6,d}")
    print(f"  {'val':10s} {len(val):6,d}   <- held-out PHRASINGS, never trained on")

    write_jsonl(os.path.join(args.out, "train.jsonl"), train)
    write_jsonl(os.path.join(args.out, "val.jsonl"), val)
    unique, size = write_corpus(os.path.join(args.out, "corpus.txt"))
    chars = sum(len(render(r["turns"])) for r in train)
    print(f"\n  {chars:,} characters of training text")
    print(f"  {unique:,} unique building blocks ({size/1024:.0f} KB) -> data/corpus.txt")
    print("  that file is what the tokenizer learns from, not the 3.5 MB")

    # ---------- STEP 3: look at what we made ----------
    print("\n" + "=" * 62)
    print("STEP 3  four examples, picked at random")
    print("=" * 62)
    shown = set()
    for row in train:
        if row["kind"] in shown:
            continue
        shown.add(row["kind"])
        print(f"\n--- kind: {row['kind']} | task: {row['task']} ---")
        print(render(row["turns"]))
        if len(shown) == 4:
            break

    print("\n" + "=" * 62)
    print("next:  python tokenizer3.py")

# NOTE:
# - Want the model to know something new? Add a T(...) to tasks.py and rerun
#   this file. That is the entire loop, and it is the same loop OpenAI runs,
#   just with a few thousand contractors writing the examples instead of you.
# - The val set is NOT random rows held back. It is held-back WAYS OF ASKING.
#   Random rows would leak: the same sentence would appear on both sides and
#   val loss would flatter you. This split cannot lie to you.
# - Real instruction datasets (Alpaca, Dolly, OpenAssistant) are exactly this
#   file's output, just written by humans. Go and look at one - it is a jsonl
#   of prompts and responses and nothing more.
