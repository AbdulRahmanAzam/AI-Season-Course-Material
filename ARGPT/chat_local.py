"""
Interactive local chat with YOUR trained ARGPT.
=================================================
Loads the checkpoint ONCE, then loops: you type a seed line, the model
continues it. This is the closest thing to "using it like an LLM" without
deploying anything.

HONEST EXPECTATION:
    This is a PRETRAINED text-continuation model, not an instruction model.
    It continues your text in the style it was trained on (Shakespeare).
    It cannot answer questions or follow commands -- that would need
    instruction tuning + RLHF, which we did not do. Feed it a SEED, not a
    question:   good ->  "ROMEO:"      bad -> "what is 2+2?"

Run me:  python chat_local.py                                  # loads out/shakespearetinychar.pt
         python chat_local.py --ckpt out/codingtinybpe.pt       # test a different dataset/size/tokenizer

Commands while chatting:
    /temp 0.8     change temperature (0.2 safe .. 1.5 chaotic)
    /tokens 200   change how many tokens to generate
    /quit         exit
"""

import argparse

import torch

from generate6 import generate, load_argpt

p = argparse.ArgumentParser()
p.add_argument("--ckpt", default="out/shakespearetinychar.pt")
args = p.parse_args()

device = "cuda" if torch.cuda.is_available() else "cpu"
model, tok = load_argpt(args.ckpt, device)

temperature = 0.8
max_tokens = 200

print(f"ARGPT loaded on {device}.")
print("Type a seed line and it will continue it. /quit to exit.\n")

while True:
    try:
        prompt = input("you> ")
    except (EOFError, KeyboardInterrupt):
        print()
        break

    if not prompt.strip():
        continue
    if prompt.startswith("/quit"):
        break
    if prompt.startswith("/temp"):
        temperature = float(prompt.split()[1])
        print(f"  temperature -> {temperature}")
        continue
    if prompt.startswith("/tokens"):
        max_tokens = int(prompt.split()[1])
        print(f"  tokens -> {max_tokens}")
        continue

    print("argpt>", end=" ", flush=True)
    generate(model, tok, prompt, max_tokens, temperature,
             device=device, stream=True)
    print("\n")
