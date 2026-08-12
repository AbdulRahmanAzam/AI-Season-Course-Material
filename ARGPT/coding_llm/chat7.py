"""
FILE 7: Chatting with it
=========================
The model still only does one thing: predict the next token. Nothing in
here changes that. What changed is the document we hand it.

    we send:  <|user|>
              how do i reverse a string
              <|assistant|>
              <- and stop, right here

The most likely continuation of THAT document is an answer, because every
example it trained on continued exactly this way. So it answers. That is
the whole trick, and it is worth saying out loud to a class: we did not
teach the model to obey. We built a document where obeying is the most
likely thing to write next.

THE STOP TOKEN
    We generate until the model emits <|end|>, then stop and throw that
    token away. Get this wrong and the model answers your question, then
    invents your NEXT question and answers that too, forever. Run
    /noend in the chat below to watch it happen. It is the single most
    convincing demo in this file.

Run me:  python chat7.py
         python chat7.py --ckpt out/coder-big.pt
         python chat7.py --ask "write a function to check if a number is prime"
"""

import argparse
import os

import torch
from torch.nn import functional as F

from chat_format1 import END, prompt_for
from model5 import ARGPTCoder, Config
from tokenizer3 import ChatTokenizer


def load_model(path, device="cpu"):
    """
    Rebuild the model AND its tokenizer from one file.

    The shape comes out of the checkpoint, never out of model5.py. That is
    what stops the classic "size mismatch for tok_emb.weight" when you
    train with one preset and chat with another.
    """
    if not os.path.exists(path):
        raise SystemExit(f"No checkpoint at {path}\nTrain one first: python train6.py")
    ckpt = torch.load(path, map_location=device, weights_only=True)
    model = ARGPTCoder(Config(**ckpt["cfg"])).to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()
    tok = ChatTokenizer().load_dict(ckpt["tokenizer"])
    return model, tok


@torch.no_grad()
def answer(model, tok, question, history=(), max_tokens=320,
           temperature=0.2, top_k=20, device="cpu", stream=False,
           stop_at_end=True):
    """
    Ask a question, get the reply.

    temperature - how bold it is.
        0.0 always takes the single most likely token. Best for code.
        0.2 is our default: almost deterministic, a little life.
        1.0 raw. Try it and watch the code stop compiling.
    top_k - never consider anything outside the k most likely tokens.
    """
    # Dropout must be OFF while generating, or the model randomly switches
    # off a twentieth of its own neurons at every token. train6.py samples
    # mid-training, so this matters more than it looks.
    was_training = model.training
    model.eval()

    end_id = tok.special_to_id[END]
    ids = tok.encode(prompt_for(question, history))
    idx = torch.tensor([ids], dtype=torch.long, device=device)

    produced = []
    printed = 0

    for _ in range(max_tokens):
        window = idx[:, -model.cfg.block_size:]
        logits, _ = model(window)                 # (B, 1, vocab)
        logits = logits[:, -1, :]

        if temperature <= 0:
            next_id = logits.argmax(dim=-1, keepdim=True)
        else:
            logits = logits / temperature
            if top_k:
                kth = torch.topk(logits, min(top_k, logits.size(-1))).values[:, [-1]]
                logits[logits < kth] = float("-inf")
            probs = F.softmax(logits, dim=-1)
            next_id = torch.multinomial(probs, num_samples=1)

        token = int(next_id)
        if token == end_id and stop_at_end:
            break                                  # the model said it is done

        produced.append(token)
        idx = torch.cat([idx, next_id], dim=1)

        if stream:
            # decode the whole answer each time and print only what is new.
            # A single BPE token can be half a character, so decoding one at
            # a time would print broken text.
            text = tok.decode(produced)
            print(text[printed:], end="", flush=True)
            printed = len(text)

    model.train(was_training)
    return tok.decode(produced)


# ============================================================
# The interactive loop
# ============================================================

BANNER = """
  /topics        what this model was actually taught
  /temp 0.8      change temperature (0 = always the safest token)
  /new           forget the conversation so far
  /noend         DEMO: ignore the stop token and see what happens
  /raw           DEMO: show the exact text being fed to the model
  /quit          exit
"""


def repl(model, tok, device):
    history = []
    temperature = 0.2
    show_raw = False
    respect_end = True

    print(f"\nARGPT-Coder on {device}. Ask me for a Python function.")
    print(BANNER)

    while True:
        try:
            question = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if not question:
            continue
        if question in ("/quit", "/exit", "/q"):
            return
        if question == "/new":
            history = []
            print("  (conversation cleared)\n")
            continue
        if question == "/raw":
            show_raw = not show_raw
            print(f"  raw prompt display: {'on' if show_raw else 'off'}\n")
            continue
        if question == "/noend":
            respect_end = not respect_end
            print(f"  stop token: {'respected' if respect_end else 'IGNORED'}"
                  f" - ask something and watch\n")
            continue
        if question.startswith("/temp"):
            try:
                temperature = float(question.split()[1])
                print(f"  temperature -> {temperature}\n")
            except (IndexError, ValueError):
                print("  usage: /temp 0.8\n")
            continue
        if question == "/topics":
            from tasks import ALL_CONCEPTS, ALL_TASKS
            print("\n  It was trained on these, and nothing else:\n")
            asks = sorted(t["asks"][0] for t in ALL_TASKS)
            half = (len(asks) + 1) // 2
            for left, right in zip(asks[:half], asks[half:] + [""]):
                print(f"   - {left:<44s}{'   - ' + right if right else ''}")
            print(f"\n  plus {len(ALL_CONCEPTS)} concept questions "
                  f"(what is a dictionary, what is recursion, ...)")
            print("  Ask any of these however you like. Ask something else and")
            print("  it will confidently make something up.\n")
            continue

        if show_raw:
            print("-" * 62)
            print(repr(prompt_for(question, history)))
            print("-" * 62)

        print("\nargpt> ", end="", flush=True)
        reply = answer(model, tok, question, history,
                       temperature=temperature, device=device, stream=True,
                       stop_at_end=respect_end)
        print("\n")
        history.append([question, reply])
        # One previous turn is all it was ever trained on. Feed it three and
        # you are asking for behaviour that appears nowhere in the data.
        history = history[-1:]


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", default="out/coder-laptop.pt")
    p.add_argument("--ask", default=None, help="ask one question and exit")
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--cpu", action="store_true", help="force CPU even if a GPU exists")
    args = p.parse_args()

    device = "cpu" if args.cpu or not torch.cuda.is_available() else "cuda"
    model, tok = load_model(args.ckpt, device)
    print(f"loaded {args.ckpt}  ({model.num_params()/1e6:.1f}M parameters, "
          f"vocab {model.cfg.vocab_size})")

    if args.ask:
        print("=" * 62)
        print(f"you> {args.ask}")
        print("=" * 62)
        print("argpt> ", end="", flush=True)
        answer(model, tok, args.ask, temperature=args.temperature,
               device=device, stream=True)
        print()
    else:
        repl(model, tok, device)

# NOTE:
# - Every token costs a full forward pass over the whole conversation so
#   far, because we keep nothing between steps. Real servers cache the keys
#   and values of the tokens they have already seen (a "KV cache") and get
#   10x faster. We left it out because it is an optimisation, not an idea.
# - Ask it something outside /topics and it will answer with total
#   confidence and be wrong. That is not a bug in the code, it is what a
#   25M parameter model IS. Show the class deliberately.
# - /temp 1.5 is worth doing live. The structure survives and the details
#   fall apart - you can watch exactly which parts of the answer the model
#   is sure about.
