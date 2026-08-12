"""
FILE 1: The chat format - why your Shakespeare model cannot answer you
======================================================================
Run train5.py, then ask the model "how do I reverse a string?" and it
replies with more Shakespeare. Everybody's first reaction is that the model
is broken. It is not. It is doing its job perfectly.

Here is the whole problem in one line:

    PRETRAINING teaches:   what text usually comes next
    it does NOT teach:     that a question should be followed by an answer

The Shakespeare model read a million characters of dialogue and never once
saw a question followed by a helpful reply. So it has no reason to produce
one. Asking it to is like handing a novel to someone and expecting a
receipt.

ChatGPT is not one model. It is a base model plus a SECOND training stage
on examples that look like conversations. That stage is called instruction
tuning, and it is what this folder builds.

To do it we need a format, so the model can tell who is speaking:

    <|user|>
    write a function to reverse a string
    <|assistant|>
    def reverse_string(s):
        return s[::-1]
    <|end|>

Those angle-bracket things are SPECIAL TOKENS. They are single tokens, not
punctuation. The tokenizer must never split them, because they are the only
signposts the model has.

Run me:  python chat_format1.py
"""

# ============================================================
# The four special tokens
# ============================================================
# We keep them ugly on purpose. <|user|> will never appear by accident in
# real Python code or in an English sentence, so it can only ever mean the
# one thing we want it to mean.

PAD = "<|pad|>"          # filler, so every training row is the same length
USER = "<|user|>"        # everything after this was typed by a human
ASSISTANT = "<|assistant|>"  # everything after this is the model's job
END = "<|end|>"          # the answer is finished - STOP GENERATING

# The order matters: whatever position a token has in this list becomes its
# id, and the checkpoint depends on that. Never reorder it after training.
SPECIALS = [PAD, USER, ASSISTANT, END]


# ============================================================
# Turning a conversation into one string
# ============================================================

def segments(turns):
    """
    A conversation in, a list of (text, learn) pieces out.

    `turns` is a list of (question, answer) pairs. Pass answer=None for the
    last turn when you are asking the model to fill it in.

    The `learn` flag is the important half of this file, and file 4 (pack4.py)
    is where it pays off:

        learn=False   the question. The model READS it but is never scored
                      on predicting it.
        learn=True    the answer. This is the only part we train on.

    Why not train on everything? Because the model would spend half its
    capacity learning to write plausible QUESTIONS, which is not the job.
    Every serious instruction-tuning setup masks the prompt out like this.
    """
    pieces = []
    for i, (question, answer) in enumerate(turns):
        gap = "\n" if i > 0 else ""
        pieces.append((f"{gap}{USER}\n{question}\n{ASSISTANT}\n", False))
        if answer is not None:
            pieces.append((f"{answer}\n{END}", True))
    return pieces


def render(turns):
    """The same conversation as one plain string, for printing and for BPE."""
    return "".join(text for text, _ in segments(turns))


def prompt_for(question, history=()):
    """
    What we actually feed the model at chat time.

    It ends with `<|assistant|>\\n` and nothing else. The model is now sitting
    exactly where an answer is supposed to start, so the only sensible next
    token is the first token of a reply. That is the entire trick.
    """
    turns = list(history) + [(question, None)]
    return render(turns)


if __name__ == "__main__":
    # ---------- DEMO 1: a complete training example ----------
    print("=" * 62)
    print("ONE TRAINING EXAMPLE, EXACTLY AS THE MODEL WILL SEE IT")
    print("=" * 62)
    example = [("write a function to reverse a string",
                "Here is a Python function that reverses a string:\n\n"
                "```python\ndef reverse_string(s):\n    return s[::-1]\n```\n\n"
                "Slicing with a step of -1 walks the string backwards.")]
    print(render(example))

    # ---------- DEMO 2: which parts do we train on? ----------
    print("\n" + "=" * 62)
    print("THE LOSS MASK - we only train on the parts marked LEARN")
    print("=" * 62)
    for text, learn in segments(example):
        tag = "LEARN " if learn else "ignore"
        for line in text.split("\n"):
            print(f"  {tag} | {line}")

    print("\nThe question is context, not homework. The model reads it and is")
    print("scored on nothing. Every token of the ANSWER is scored.")

    # ---------- DEMO 3: what we send at chat time ----------
    print("\n" + "=" * 62)
    print("AT CHAT TIME WE SEND ONLY THIS, AND LET IT CONTINUE")
    print("=" * 62)
    print(repr(prompt_for("how do i check if a number is prime")))
    print("\nNotice it ENDS mid-conversation, right after <|assistant|>.")
    print("The model is not being asked a question. It is being asked to")
    print("continue a document - which is the only thing it can do. We just")
    print("built a document where continuing it means answering.")

    # ---------- DEMO 4: multi turn ----------
    print("\n" + "=" * 62)
    print("A FOLLOW UP QUESTION IS JUST A LONGER DOCUMENT")
    print("=" * 62)
    print(prompt_for("explain that",
                     history=[("write a function to reverse a string",
                               "def reverse_string(s):\n    return s[::-1]")]))

# NOTE:
# - This file has no PyTorch in it. The chat format is not a model feature,
#   it is a text convention we invented and then trained the model to obey.
# - Every provider picks their own tokens. Llama 3 uses <|start_header_id|>,
#   ChatML uses <|im_start|>. The idea is identical.
# - <|end|> is what stops generation. Without it the model answers, then
#   cheerfully invents your next question and answers that too. You will see
#   exactly that happen if you set the stop token wrong in chat7.py.
