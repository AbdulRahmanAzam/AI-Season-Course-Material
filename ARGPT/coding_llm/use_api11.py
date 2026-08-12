"""
FILE 11: Calling your own API, from anywhere
=============================================
serve10.py put your model behind a URL. This file is the other side of that
line: an ordinary client, with no PyTorch, no model, and no GPU. It would
run on a Raspberry Pi.

That is the whole point of deploying. In session 6 you wrote this exact kind
of code against Groq. This is the same code against a model you built.

TWO THINGS PEOPLE MIX UP

    THE URL   https://you--argpt-coder-api-coder-chat.modal.run
              WHERE the model is. Not a secret on its own, but anyone who
              has it can knock on the door.

    THE KEY   argpt_xxxxxxxxxxxxxxxxxxxx
              PERMISSION to come in. This is the secret. Without it the
              endpoint returns 401 and costs you nothing.

    Before we added the key, anyone who found the URL could run your GPU on
    your credits. An open endpoint is not "unauthenticated", it is
    "everybody's".

WHAT YOU ACTUALLY PAY FOR
    Not requests. SECONDS OF CONTAINER LIFE. Every reply below prints three
    numbers so you can watch the bill happen:

        round trip     what you waited
        generating     what the GPU spent making tokens
        the difference network, plus a cold start if the container was asleep

    The first call after two minutes of quiet pays ~12 seconds of cold
    start. The second call pays ~0. That gap is the entire economics of
    serverless GPUs, and you can see it in the numbers.

Setup, once:
    set ARGPT_URL=https://you--argpt-coder-api-coder-chat.modal.run
    set ARGPT_API_KEY=argpt_xxxxxxxxxxxx

Run me:  python use_api11.py                       # interactive
         python use_api11.py "reverse a string"    # one question
         python use_api11.py --cost                # show what a demo costs
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

# Modal's T4, per second, at $0.59/hour. Only used for the cost estimate.
T4_PER_SECOND = 0.59 / 3600


def load_settings():
    """
    URL and key from the environment, falling back to files next to this one.

    Environment variables first is the right order: it is what a real
    deployment does, and it keeps the key out of anything you might commit.
    """
    here = os.path.dirname(os.path.abspath(__file__))

    def from_env_or_file(env_name, filename):
        value = os.environ.get(env_name)
        if value:
            return value.strip()
        path = os.path.join(here, filename)
        if os.path.exists(path):
            return open(path, encoding="utf-8").read().strip()
        return None

    url = from_env_or_file("ARGPT_URL", ".api_url.txt")
    key = from_env_or_file("ARGPT_API_KEY", ".api_key.txt")

    if not url or not key:
        raise SystemExit(
            "Missing the URL or the key.\n\n"
            "  set ARGPT_URL=https://you--argpt-coder-api-coder-chat.modal.run\n"
            "  set ARGPT_API_KEY=argpt_xxxxxxxxxxxx\n\n"
            "or put them in .api_url.txt and .api_key.txt next to this file.\n"
            "Get the URL from:  modal deploy serve10.py")
    return url, key


def ask(question, url, key, history=(), temperature=0.2, timeout=300):
    """
    One question in, one dict out.

    This is the entire client. Everything else in this file is presentation.
    """
    body = json.dumps({"question": question,
                       "api_key": key,
                       "history": list(history),
                       "temperature": temperature}).encode()
    request = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"})

    started = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read())
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")
        if error.code == 401:
            raise SystemExit("401 - the server rejected your api_key.\n"
                             "Check ARGPT_API_KEY matches the Modal secret:\n"
                             "  modal secret list")
        raise SystemExit(f"HTTP {error.code}: {detail}")
    except urllib.error.URLError as error:
        raise SystemExit(f"Could not reach {url}\n{error.reason}\n"
                         "Is the app deployed?  modal app list")

    result["round_trip"] = time.time() - started
    return result


def show(result):
    """Print the answer, then the three numbers that explain the bill."""
    print(result["answer"])

    trip = result["round_trip"]
    generating = result.get("generate_seconds", 0.0)
    overhead = max(0.0, trip - generating)
    print()
    print(f"  round trip   {trip:6.2f}s")
    print(f"  generating   {generating:6.2f}s   <- the GPU actually working")
    print(f"  overhead     {overhead:6.2f}s   ", end="")
    print("<- COLD START, the container was asleep" if overhead > 5
          else "<- warm, this is just the network")


def cost_report():
    """The arithmetic, so nobody has to be nervous about pressing the button."""
    print("=" * 62)
    print("WHAT THIS ACTUALLY COSTS")
    print("=" * 62)
    print(f"  Modal T4: $0.59/hour = ${T4_PER_SECOND:.6f} per second\n")

    print("  You are billed per SECOND THE CONTAINER IS ALIVE, not per")
    print("  request. serve10.py sets scaledown_window, which decides how")
    print("  long it stays alive after your last question.\n")

    rows = [
        ("one question, container asleep", 12 + 3 + 5),
        ("one question, container awake", 3 + 5),
        ("a 20-question class demo, window=5", 20 * (12 + 3 + 5)),
        ("a 20-question class demo, window=120", 12 + 20 * 3 + 120),
    ]
    for label, seconds in rows:
        print(f"  {label:40s} {seconds:5.0f}s  "
              f"${seconds * T4_PER_SECOND:6.4f}")

    print("\n  Look at the last two lines. Keeping the container warm for two")
    print("  minutes costs LESS than paying twenty cold starts, and answers")
    print("  in 1.5 seconds instead of 14. The short window only wins when")
    print("  questions are genuinely rare.")
    print(f"\n  Modal's free tier is $30 a month. That is about "
          f"{30/T4_PER_SECOND/3600:.0f} hours of T4.")
    print("  You cannot meaningfully dent it with a classroom.")
    print("=" * 62)


def repl(url, key):
    history = []
    print(f"\nconnected to {url}")
    print("Ask a Python question. /new clears the conversation, /quit exits.\n")
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

        print("\nargpt> ", end="", flush=True)
        result = ask(question, url, key, history)
        show(result)
        print()
        history = [[question, result["answer"]]]   # one turn, as trained


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("question", nargs="*", help="ask one question and exit")
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--cost", action="store_true", help="show the cost maths and exit")
    args = p.parse_args()

    if args.cost:
        cost_report()
        sys.exit(0)

    url, key = load_settings()

    if args.question:
        question = " ".join(args.question)
        print("=" * 62)
        print(f"you>   {question}")
        print("=" * 62)
        show(ask(question, url, key, temperature=args.temperature))
    else:
        repl(url, key)

# NOTE:
# - There is no PyTorch import in this file. That is the deliverable of
#   deploying: the model became something you call, not something you carry.
# - The key goes in the JSON body here because it keeps the file short. Real
#   APIs put it in an Authorization header - the security is identical, the
#   convention is not. Worth saying out loud rather than teaching the habit
#   silently.
# - Anyone in your class can run this file against your URL from their own
#   laptop, with no GPU and no install. That is a good five minutes: they are
#   all talking to a model you trained this afternoon.
# - To take the endpoint down entirely:  modal app stop argpt-coder-api
