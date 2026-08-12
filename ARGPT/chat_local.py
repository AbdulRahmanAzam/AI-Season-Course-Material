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

    ...unless the text it pretrained on was ALREADY shaped like a conversation.
    That is what data/knowledge/ is: 10 MB of "User: ... / Buddy: ..." exchanges.
    Train on that and --wrap makes the same model look like a chatbot, with no
    instruction tuning anywhere. Nothing about the model changed. Only the text.

Run me:  python chat_local.py                                  # loads out/shakespearetinychar.pt
         python chat_local.py --ckpt out/codingtinybpe.pt       # test a different dataset/size/tokenizer
         python chat_local.py --ckpt out/knowledgetinychar.pt --wrap

Commands while chatting:
    /temp 0.8     change temperature (0.2 safe .. 1.5 chaotic)
    /tokens 200   change how many tokens to generate
    /wrap         toggle the User:/Buddy: template on and off -- the single
                  best demo in this file. Same weights, same question, and it
                  only answers you with the template on.
    /quit         exit
"""

import argparse

import torch

from generate6 import generate, load_argpt

p = argparse.ArgumentParser()
p.add_argument("--ckpt", default="out/shakespearetinychar.pt")
p.add_argument("--wrap", action="store_true",
               help="wrap what you type as 'User: ...\\nBuddy:' (knowledge model)")
args = p.parse_args()

device = "cuda" if torch.cuda.is_available() else "cpu"
model, tok = load_argpt(args.ckpt, device)

temperature = 0.8
max_tokens = 200
wrap = args.wrap

print(f"ARGPT loaded on {device}.")
if wrap:
    print("wrap ON  -- what you type becomes 'User: <you>\\nBuddy:'")
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
    if prompt.startswith("/wrap"):
        wrap = not wrap
        print(f"  wrap -> {'ON' if wrap else 'OFF'}")
        continue

    # THE WHOLE TRICK. Six characters of punctuation are the difference between
    # a model that rambles and a model that answers you. We are not asking it to
    # obey -- we are writing the start of a document where the most likely
    # continuation happens to be an answer.
    seed = f"User: {prompt}\nBuddy:" if wrap else prompt

    print("argpt>", end=" ", flush=True)
    generate(model, tok, seed, max_tokens, temperature,
             device=device, stream=True)
    print("\n")

# NOTE:
# - With --wrap on the knowledge model, watch it run straight past its answer
#   into a brand new "User:" turn it made up. It has no idea when to stop,
#   because plain text has no "I am done" marker. That missing marker is
#   exactly the <|end|> token in coding_llm/chat_format1.py.
