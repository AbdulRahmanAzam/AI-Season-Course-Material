"""
FILE 6: Generate — making ARGPT write
======================================
The model only ever answers one question: "what token comes next?"

To get a paragraph we ask it that question over and over, each time
feeding back what it just said:

    "ROMEO"  ->  ":"
    "ROMEO:" ->  "\n"
    "ROMEO:\n" -> "I"     ... and so on

That is all "generation" means. There is no plan, no draft, no memory
beyond the last block_size tokens.

Run me:  python generate6.py --prompt "ROMEO:"
"""

import argparse

import torch
from torch.nn import functional as F

from config1 import Config
from model4 import ARGPT
from tokenizer2 import tokenizer_from_dict


def load_argpt(path="out/shakespearetinychar.pt", device="cpu"):
    """
    Rebuild the model and its tokenizer from one checkpoint file.

    The shape comes from the checkpoint, never from config1.py. That is what
    stops the classic "size mismatch for tok_emb.weight" error when you train
    with one preset and try to generate with another.
    """
    ckpt = torch.load(path, map_location=device, weights_only=True)
    model = ARGPT(Config(**ckpt["cfg"])).to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()
    return model, tokenizer_from_dict(ckpt["tokenizer"])


@torch.no_grad()
def generate(model, tok, prompt="\n", max_new_tokens=300,
             temperature=0.8, top_k=50, device="cpu", stream=False):
    """
    temperature — how bold the model is.
        0.2 = safe and repetitive.  1.0 = raw.  1.5 = chaotic.
    top_k — only ever consider the k most likely tokens.
        Stops the model picking something absurd just because it can.
    """
    idx = torch.tensor([tok.encode(prompt)], dtype=torch.long, device=device)

    for _ in range(max_new_tokens):
        # the model can only see block_size tokens, so keep the newest ones
        window = idx[:, -model.cfg.block_size:]
        logits, _ = model(window)

        # we only care about the prediction at the LAST position
        logits = logits[:, -1, :] / temperature

        if top_k:
            kth = torch.topk(logits, min(top_k, logits.size(-1))).values[:, [-1]]
            logits[logits < kth] = float("-inf")       # everything else is out

        probs = F.softmax(logits, dim=-1)
        next_id = torch.multinomial(probs, num_samples=1)   # roll a weighted dice
        idx = torch.cat([idx, next_id], dim=1)

        if stream:
            print(tok.decode([next_id.item()]), end="", flush=True)

    return tok.decode(idx[0].tolist())


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", default="\n")
    p.add_argument("--tokens", type=int, default=300)
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--ckpt", default="out/shakespearetinychar.pt")
    args = p.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, tok = load_argpt(args.ckpt, device)

    # ---------- DEMO: watch it write, one token at a time ----------
    print("=" * 55)
    print(f"prompt: {args.prompt!r}   temperature: {args.temperature}")
    print("=" * 55)
    print(args.prompt, end="")
    generate(model, tok, args.prompt, args.tokens,
             args.temperature, device=device, stream=True)
    print("\n" + "=" * 55)

# NOTE:
# - Run it twice with the same prompt. You get different text, because of the
#   dice roll. Set temperature very low to make it nearly deterministic.
# - After the TINY laptop run this will look like nonsense with the right
#   SHAPE -- line breaks, capital letters, name colons. That shape is the proof
#   it learned something. The GPU run in modal_app7.py is what makes it readable.
