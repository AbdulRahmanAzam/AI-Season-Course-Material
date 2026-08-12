# ARGPT-Coder — teaching a model you built to actually answer you

The main session built a language model from scratch and trained it on
Shakespeare. Then everybody asked it a question and it replied with more
Shakespeare, and the room went quiet.

**That model is not broken.** This folder is about why, and about the second
training stage that fixes it.

```
PRETRAINING teaches   : what text usually comes next
it does NOT teach     : that a question should be followed by an answer
```

The Shakespeare model read a million characters and never once saw a question
followed by a helpful reply. So it has no reason to produce one. ChatGPT is not
one model — it is a base model plus a second stage trained on examples of
conversations. That stage is called **instruction tuning**, and it is nine files
and about twenty minutes of GPU time away.

At the end of this you have a model that does this:

```
you>   how do i check if a number is prime
argpt> Here is a Python function that will check if a number is prime:

       ```python
       def is_prime(n):
           if n < 2:
               return False
           for i in range(2, int(n ** 0.5) + 1):
               if n % i == 0:
                   return False
           return True
       ```

       A prime has no divisors other than 1 and itself. We only need to test
       up to the square root, because any factor larger than that must pair
       with one smaller than it, which we would already have found.
```

and a script that **executes every function it writes and counts how many
actually pass their tests**, so the deliverable is a number, not a vibe.

## Measured, on a laptop RTX 3050

Everything below was run, not estimated — the default `laptop` preset, 11.4M
parameters, **6 minutes** of training on a mid-range laptop GPU:

| what | result |
|---|---|
| token accuracy on held-out phrasings | **99.0%** |
| generated functions that run and pass their assert | **91 / 92 (99%)** |
| concept questions routed to prose, trained wordings | **61 / 62 (98%)** |
| concept questions routed to prose, *held-out* wordings | **20 / 31 (65%)** |

Every one of those 92 questions was asked using a sentence frame that appears
nowhere in the training data, and every generated function was executed by a real
Python interpreter against the assert from `tasks.py`.

That last row is in the table deliberately. It is the honest limit of the thing,
and [the question mark bug](#the-best-story-in-the-folder-the-question-mark-bug)
explains what it took to find it.

### And on a rented GPU

Files 9 and 10 were run for real, not just written. The same `train()` function,
the 26.4M `big` preset, on a Modal L4:

| | laptop RTX 3050 | Modal L4 |
|---|---|---|
| throughput | 18k tokens/sec | **78k tokens/sec** |
| 3500 training steps | 19.3 min | **4.5 min** |
| best val loss | 0.030 | **0.024** |

Cost: about 6 cents. The deployed API answered in **11.6s on the first request and
1.3s on the second** — that gap is the cold start, and it is the single clearest
demonstration of what `@modal.enter()` is for. `use_api11.py` prints those numbers
under every reply.

### One thing to say out loud about the API key

The endpoint now checks a key and returns 401 without it — verified against a
missing key and a wrong key. But **the check runs inside the container**, so a
request with a rubbish key has already woken a GPU and loaded 26M parameters
before it gets rejected.

> The key protects your model. It does not protect your wallet.

Rejecting at Modal's edge instead is one argument —
`@endpoint(method="POST", requires_proxy_auth=True)` — but then callers need
Modal-issued headers and your students cannot curl it from their own laptops.
`serve10.py` keeps the simple version and says why in a comment. That trade-off
is a better security lesson than either option on its own.

---

## Setup

You already have everything from the main session. Nothing new is required:

```bash
pip install torch numpy
```

Modal (files 9 and 10) is optional — the whole thing trains on a laptop.

**Windows + Modal:** run this once per terminal before any `modal` command, or the
CLI crashes on its own tick character *after* your GPU job has already succeeded:

```bash
set PYTHONIOENCODING=utf-8
```

Your API from this session is already live and **key-protected**. The URL and key
are in `.api_url.txt` and `.api_key.txt` (both gitignored):

```bash
python use_api11.py                              # interactive
python use_api11.py "reverse a string"           # one question
python use_api11.py --cost                       # what a demo actually costs
```

It costs nothing while idle. Take it down with `modal app stop argpt-coder-api`.
Rotate the key any time with:

```bash
modal secret create argpt-coder-key ARGPT_API_KEY=your-new-key --force
modal deploy serve10.py
```

**Check your disk before class.** Each checkpoint is 45-105 MB and the build
writes about 25 MB of data. Free space with:

```bash
conda clean --all          # the anaconda3\pkgs cache
pip cache purge
```

`~/.cache` is usually the biggest one (downloaded Hugging Face models live there)
— worth a look, but check what is in it before deleting anything.

---

## The run, start to finish

Five commands. From inside `coding_llm/`:

```bash
python build_data2.py      # ~10s   92 tasks -> 7,800 conversations
python tokenizer3.py       # ~5s    BPE with special tokens
python pack4.py            # ~5s    loss masks + .bin files
python train6.py           # see table below
python chat7.py            # talk to it
```

Then the honest scorecard:

```bash
python evaluate8.py --ckpt out/coder-big.pt
```

### Which preset

All three timings below are measured on a laptop RTX 3050, not estimated.

| preset | size | command | time | best val loss | what you get |
|---|---|---|---|---|---|
| `quick` | 3.6M | `python train6.py --preset quick` | ~2 min | — | answers the common questions, fumbles the rest. **Run this one live.** |
| `laptop` | 11.4M | `python train6.py` | **6.1 min** | **0.027** | the sweet spot. This is the default for a reason. |
| `big` | 26.4M | `python train6.py --preset big` | 19.3 min | 0.030 | three times the compute, no better. Worth showing. |

**`laptop` beat `big`.** That is not a mistake and it is worth a minute of class
time: 92 tasks is a small amount to learn, 11M parameters is already more than
enough to hold it, and the extra 15M just take longer to arrive at the same place.
Scaling laws are about *data*, and we have a fixed, small amount of it. The way to
improve this model is to write more tasks in `tasks.py`, not to add layers.

`big` uses about 3.8 GB of VRAM at `batch_size 32`. On a 4 GB card that is right at
the edge — add `--batch 16` if it runs out. No GPU at all? `--preset quick` on CPU
works, it is just slower.

**Chatting needs no GPU.** Generation is about 0.4 seconds an answer on a CPU for
`quick`, a few seconds for `big`. Students can all run `chat7.py` on their own
laptops from your checkpoint.

---

## The files, in teaching order

| # | file | topic | what students learn |
|---|---|---|---|
| — | `tasks.py` | **the curriculum** | Everything the model will ever know, written by hand. 92 coding tasks and 31 concepts, each with runnable code and an assert. Not a lesson file — it is the content. |
| 1 | `chat_format1.py` | **the chat template** | Why a base model cannot answer. Special tokens. `<\|user\|>` / `<\|assistant\|>` / `<\|end\|>`, and the first sight of the loss mask. No PyTorch in this file at all. |
| 2 | `build_data2.py` | **the dataset** | 92 tasks multiplied along four axes into 7,800 conversations. Held-out phrasings for an honest val set. **Every code sample is executed before training.** |
| 3 | `tokenizer3.py` | **tokenizer, upgraded** | Special tokens that never split, and one idea that makes BPE training **32x faster** — 149 seconds becomes 4.6. |
| 4 | `pack4.py` | **loss masking** | The single most important idea here: score the answer, never the question. Plus dynamic padding, which buys back 36% of the compute. |
| 5 | `model5.py` | **a 2024 transformer** | RMSNorm, RoPE, SwiGLU, flash attention — the four swaps modern models actually made — and the masked loss in `forward()`. |
| 6 | `train6.py` | **training properly** | Warmup + cosine decay, weight decay on the right tensors, bfloat16, and **token accuracy** so the class sees a percentage instead of a number in nats. |
| 7 | `chat7.py` | **using it** | The REPL. Stop tokens, temperature, and `/noend` — a one-command demo of what happens when the stop token is wrong. |
| 8 | `evaluate8.py` | **does it work?** | Ask with unseen phrasings, `exec()` the reply, run the assert. One honest number. |
| 9 | `modal_train9.py` | **a rented GPU** | The identical pipeline on an L4 for about 20 cents. |
| 10 | `serve10.py` | **you become the API** | `@modal.enter()` and why loading weights per request is the wrong answer. An API key from a Modal secret, and where that check has to live. |
| 11 | `use_api11.py` | **calling it back** | A client with no PyTorch in it. URL vs key, and three timing numbers per reply that make the billing visible. |

Every file runs on its own and prints a demo:

```bash
python chat_format1.py
python model5.py
```

---

## Running the session

### The five minutes that matter most

**Open with the failure, not the fix.** Load the Shakespeare model from the main
session and ask it a question in front of everyone. Let it reply with Shakespeare.
*Then* explain that this is correct behaviour and the model was never shown a
single question-and-answer pair. The whole session lands better when the class has
felt the problem first.

**`python chat_format1.py` is the conceptual centre.** It has no PyTorch in it.
The entire idea — that we are not teaching the model to obey, we are building a
document where obeying is the most likely continuation — is a text convention and
nothing more. If the class only remembers one file, this is the one.

**`python build_data2.py` is where the real lesson hides.** Step 1 executes all 205
code samples before anything else happens. Say why: a model trained on broken code
learns to write broken code, and no amount of GPU fixes that. While writing this
folder that check caught a genuine bug in `tasks.py` on the first run.

**`python pack4.py` prints the mask beside the tokens.** Let them read the
`ignore | ... SCORE | ...` column. Nobody needs loss masking explained after
seeing that.

**`python train6.py --preset quick` is the 90-second showpiece.** Around step 250
it is already writing well-formed Python that answers the wrong question. By step
1000 it answers the right one. Say nothing and let the samples scroll.

**`python evaluate8.py` is how you finish.** A number, generated live, from code
the model wrote thirty seconds ago and that a Python interpreter just ran.

### Four questions to demo with, in this order

```
you> how do i check if a number is prime          -> code + explanation
you> what is a dictionary                         -> prose, no code block
you> hi                                           -> it behaves like an assistant
you> explain this code
     ```python
     def mystery(items):
         seen = set()
         result = []
         for item in items:
             if item not in seen:
                 seen.add(item)
                 result.append(item)
         return result
     ```
```

**Save the fourth one for last**, because it is the one that convinces people.
That function is `remove_duplicates` from `tasks.py` with the name changed to
`mystery`. The model has never seen that name. It still answers:

> This code will remove duplicates from a list.
>
> A set remembers what we have already met and checks membership instantly. We
> append to the result only the first time we see each item, which is what
> preserves the original order.

It cannot be reading the name, because the name is gone. It is reading the code.
Anyone in the room who thinks this is a lookup table has just been answered.

Then immediately ask it something outside `/topics` and let it fail, so the demo
ends honest.

### The best story in the folder: the question mark bug

This actually happened while building this folder, twice, and it is worth ten
minutes of class time because it is the whole of "why evaluation matters" in one
concrete example.

An early version scored 97% on writing code but kept answering concept questions
with a function. Testing by hand found this:

```
you> what is a list comprehension?      ->  A list comprehension builds a whole list ...   correct
you> what is a list comprehension       ->  Here is one way to save a list into a tuple:   nonsense
```

A single question mark flipped it. The cause was in the **data**, not the model:
every concept question in `build_data2.py` had punctuation appended, and not one
of the 22 "write me a function" templates contained a `?`. So across the entire
training set, `?` was a *perfect* predictor of "this is a concept question".

The model did exactly what it was asked to do. It found the cheapest reliable
signal and used it. That signal happened to be punctuation instead of meaning.

Then the fixed version failed a second time, the same way:

```
you> im stuck, how do i write a bubble sort
argpt> A large language model is a neural network trained on ...
```

Same cause, different surface feature. Apologetic lead-ins — "im new to python",
"sorry if this is basic" — appeared only on the concept templates, so the model
learned that sounding hesitant meant you wanted an explanation.

Both fixes were data, not architecture:

- `""` added to `CONCEPT_ENDINGS`, so concept questions also appear unpunctuated
- four `?` variants added to `WRITE_TEMPLATES`, so `?` appears on both sides
- four apologetic lead-ins added to `WRITE_TEMPLATES`, for the same reason

**The lesson for the class:** any surface feature that lines up perfectly with the
label *will* be learned instead of the meaning, because it is cheaper. Nobody would
have caught either bug by admiring the demo — the demo looked great, because
everyone types a question mark. It took running an evaluation.

That is the real answer to "why do the big labs spend so much on evals".

### The callbacks that land

- Session 3 chunked documents for RAG. `block_size` is the same constraint.
- Session 4 built a pluggable LLM interface. `serve10.py` puts your own model
  behind the same kind of URL.
- Session 6 wrapped Groq in LangChain. The endpoint from file 10 drops into
  exactly that slot — `use_from_agent9.py` in the parent folder shows how.
- The main session's `modern_upgrades10.py` showed RMSNorm, RoPE and SwiGLU as
  isolated demos. `model5.py` is those three actually wired in and trained.

---

## What it can and cannot do

Say this out loud early, because a class expecting ChatGPT will read a working
demo as a failure.

**It genuinely can:**

- write any of the 92 functions in `tasks.py`, phrased however you like
- explain code from that set, line by line
- fix four kinds of common bug in that code
- answer 31 concept questions ("what is a dictionary", "what is recursion")
- handle a follow-up turn — "explain that" after it writes something
- reply sensibly to "hi", "what can you do", "thanks"

**It absolutely cannot:**

- write anything outside the curriculum. Ask for a Django view and it will
  confidently produce something that looks like Python and is wrong.
- do arithmetic, remember anything past two turns, or use a tool
- know that it does not know. There is no uncertainty in a 26M model.

Type `/topics` inside `chat7.py` to see exactly what it was taught. **Then
deliberately ask it something outside that list**, and let the class watch it
invent an answer with total confidence. That is the most useful ninety seconds of
the whole session — it is what "hallucination" looks like when you can see the
entire training set on one screen.

---

## The honest boundary of the technique

Worth naming, because students will ask:

- **This is instruction tuning, not RLHF.** No preference model, no reward
  learning. Real assistants add a third stage where humans rank pairs of answers.
- **The data is synthetic and templated.** Real instruction datasets (Alpaca,
  Dolly, OpenAssistant) are the same shape — a jsonl of prompts and responses —
  just written by thousands of people instead of generated from 92 templates.
- **We deliberately overfit.** `dropout` is 0.05 and we train for many epochs
  because we *want* this model to memorise its curriculum. That is the right call
  for a narrow assistant and the wrong call for a general one. The val split
  measures the thing that still has to generalise: the phrasing.
- **No KV cache.** Every generated token re-reads the whole conversation. A real
  server caches the keys and values and gets ~10x faster. It is an optimisation,
  not an idea, so it is left out.

---

## Common breakages

| what you see | what happened |
|---|---|
| `'charmap' codec can't encode character '✓'` | **Windows + Modal.** Modal's CLI prints a tick when it finishes and the console code page cannot encode it. Run `set PYTHONIOENCODING=utf-8` first. The GPU work has usually already succeeded — check `modal volume ls argpt-coder`. |
| `Run these first: python build_data2.py` | Files 2, 3, 4 have to run before 6, in that order. |
| `BROKEN TASK in tasks.py: ...` | You added a task whose code does not pass its own assert. It is telling you the exact function and error. This is the check working. |
| `CUDA out of memory` | `--batch 16`, or drop to `--preset laptop`. `big` needs ~3.8 GB. |
| `size mismatch for tok_emb.weight` | Chatting with a checkpoint trained at a different preset. The shape comes from the checkpoint, so pass the matching `--ckpt`. |
| Model answers, then invents your next question | The stop token is not being respected. That is exactly what `/noend` demonstrates on purpose. |
| Answers are fluent but the wrong function | Undertrained. Look at token accuracy — below about 90% it is still guessing which task you meant. |
| `AttributeError: module 'modal' has no attribute 'App'` | A file named `modal.py` is shadowing the package. Rename it. |

---

## Making it yours

The whole workflow for teaching the model something new is one edit:

```python
# in tasks.py
T("count_uppercase",
  ["count the uppercase letters in a string", "count capital letters"],
  """
  def count_uppercase({v}):
      return sum(1 for ch in {v} if ch.isupper())
  """,
  """isupper() is True only for letters that have a case and are currently
     uppercase, so digits and spaces are not counted.""",
  "assert count_uppercase('Hello World') == 2",
  vars=["s", "text"]),
```

Then rerun files 2, 3, 4, 6. That is the same loop the big labs run — they just
have contractors writing the examples instead of you.

**The most interesting homework** is to have students each add five tasks in their
own domain, merge them, and retrain. The model gets measurably better at exactly
the things they wrote down, and nothing else. It is the clearest possible
demonstration that a model is its training data.
