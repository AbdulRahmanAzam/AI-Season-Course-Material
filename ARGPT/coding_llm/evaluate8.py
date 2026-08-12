"""
FILE 8: Does it ACTUALLY work? Run the code it writes.
=======================================================
Everybody demos a language model by reading its output and nodding. That is
not a measurement, it is a vibe.

Code is the one domain where you do not have to settle for that. The model
writes a function; we can just run it.

So this file, for all 92 tasks:

    1. asks the question using a phrasing the model has NEVER seen
    2. pulls the ```python block out of the reply
    3. exec()s it
    4. runs the task's assert from tasks.py

and prints one honest number: how many of them actually work.

WHY THE HELD-OUT PHRASING MATTERS
    build_data2.py kept five sentence frames out of training entirely. This
    file asks with those. If the model scores well here it did not memorise
    sentences - it learned what people MEAN. That is the difference between
    a lookup table and a language model, and it is measurable in about
    thirty seconds.

Run me:  python evaluate8.py
         python evaluate8.py --ckpt out/coder-big.pt --verbose
"""

import argparse
import random
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as Timeout

import torch

from build_data2 import OPENERS, val_half, WRITE_TEMPLATES
from chat7 import answer, load_model
from tasks import ALL_CONCEPTS, ALL_TASKS

CODE_BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)


def extract_code(reply):
    """Pull the first fenced python block out of the model's reply."""
    found = CODE_BLOCK.search(reply)
    return found.group(1) if found else None


def run_test(code, test):
    """
    exec the generated code, then its assert. Returns None if it passed, or
    a short description of what went wrong.

    We run it on a worker thread with a timeout, because a model that gets
    a loop condition wrong will happily hand you `while True:` and we would
    rather score that as a failure than hang the demo.
    """
    def attempt():
        scope = {}
        exec(code, scope)
        exec(test, scope)

    with ThreadPoolExecutor(max_workers=1) as pool:
        try:
            pool.submit(attempt).result(timeout=5)
            return None
        except Timeout:
            return "timed out (probably an endless loop)"
        except AssertionError:
            return "runs, but gives the wrong answer"
        except Exception as error:
            return f"{type(error).__name__}: {error}"


def evaluate_tasks(model, tok, device, temperature, seed=0, verbose=False):
    """Ask for every task with an unseen phrasing, and run what comes back."""
    rng = random.Random(seed)
    unseen = val_half(WRITE_TEMPLATES)

    passed, failures = 0, []
    for n, task in enumerate(ALL_TASKS, 1):
        print(f"\r  asking... {n}/{len(ALL_TASKS)}", end="", flush=True)
        ask = rng.choice(task["asks"])
        question = rng.choice(unseen).replace("{ask}", ask)
        reply = answer(model, tok, question, temperature=temperature,
                       device=device, max_tokens=320)

        code = extract_code(reply)
        if code is None:
            problem = "no ```python block in the reply"
        else:
            problem = run_test(code, task["test"])

        if problem is None:
            passed += 1
        else:
            failures.append((task["name"], question, problem, code))
            if verbose:
                print(f"\n  FAILED {task['name']}: {problem}")
                print(f"    asked: {question}")
                print("    got:\n" + "\n".join("      " + l
                                               for l in (code or reply).split("\n")[:12]))
    print("\r" + " " * 30 + "\r", end="")
    return passed, failures


def evaluate_routing(model, tok, device, temperature):
    """
    Does it answer the RIGHT KIND of question? Concept questions should get
    prose, not a function.

    We report this in two halves, because they measure different things:

        SEEN     descriptions of the concept the model trained on, but with
                 no sentence frame and no punctuation at all. Tests whether
                 it keyed off surface features.
        UNSEEN   the one description of each concept held out entirely.
                 Tests whether it understood the topic rather than the
                 wording. This is the harder number and the honest one.
    """
    # the exact sentences build_data2.py uses to open a CODE answer. If a
    # concept question comes back starting with one of these, the model
    # heard "write me a function" when the user asked "what is a class".
    code_openers = tuple(opener.split("{ask}")[0] for opener in OPENERS)

    def check(questions):
        good = []
        for question in questions:
            reply = answer(model, tok, question, temperature=temperature,
                           device=device, max_tokens=260)
            good.append(not reply.strip().startswith(code_openers))
        return good

    seen, unseen = [], []
    for n, concept in enumerate(ALL_CONCEPTS, 1):
        print(f"\r  asking... {n}/{len(ALL_CONCEPTS)}", end="", flush=True)
        # build_data2.py trains on asks[:-1] and holds out asks[-1]
        seen.extend(check(concept["asks"][:-1]))
        unseen.extend(check(concept["asks"][-1:]))
    print("\r" + " " * 30 + "\r", end="")
    return seen, unseen


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", default="out/coder-big.pt")
    p.add_argument("--temperature", type=float, default=0.0,
                   help="0 = always take the most likely token")
    p.add_argument("--verbose", action="store_true", help="print every failure")
    p.add_argument("--cpu", action="store_true")
    args = p.parse_args()

    device = "cpu" if args.cpu or not torch.cuda.is_available() else "cuda"
    model, tok = load_model(args.ckpt, device)

    print("=" * 62)
    print("EXECUTING THE CODE THE MODEL WRITES")
    print(f"{len(ALL_TASKS)} tasks, each asked with a phrasing it has never seen")
    print("=" * 62)

    passed, failures = evaluate_tasks(model, tok, device, args.temperature,
                                      verbose=args.verbose)
    total = len(ALL_TASKS)

    print(f"\n  {passed} / {total} generated functions ran and passed their "
          f"assert   ({passed/total:.0%})")

    if failures and not args.verbose:
        print(f"\n  the {len(failures)} that did not:")
        for name, question, problem, _ in failures[:12]:
            print(f"    {name:24s} {problem}")
        if len(failures) > 12:
            print(f"    ... and {len(failures)-12} more (use --verbose)")

    # ---------- did it at least understand the KIND of question? ----------
    print("\n" + "=" * 62)
    print("ROUTING - concept questions should get prose, not a function")
    print("=" * 62)
    seen, unseen = evaluate_routing(model, tok, device, args.temperature)
    print(f"  wordings it trained on : {sum(seen):3d} / {len(seen):3d} "
          f"({sum(seen)/len(seen):.0%})")
    print(f"  wordings held out      : {sum(unseen):3d} / {len(unseen):3d} "
          f"({sum(unseen)/len(unseen):.0%})   <- the honest one")
    print("\n  The gap between those two lines is the gap between learning a")
    print("  sentence and learning a topic. Each concept was described only")
    print("  two or three ways in training, so there is not much to")
    print("  generalise from - and this is exactly why real instruction sets")
    print("  have thousands of paraphrases per intent, not two.")

    print("\n" + "=" * 62)
    print("This number is the deliverable of the session. Not the demo.")
    print("=" * 62)

# NOTE:
# - Run this with --temperature 0 for the honest score and 1.0 to watch it
#   collapse. Sampling is a choice, and the cost of that choice is now a
#   number instead of an opinion.
# - Failures are worth reading out loud. The usual ones are a correct
#   function under a slightly wrong name, or the right idea with one
#   operator flipped - which tells you exactly how much of "understanding"
#   is really pattern completion.
# - This is a small, honest version of what HumanEval does for the real
#   models. Same idea: generate code, run tests, count.
