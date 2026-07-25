# ARGPT — build a language model from scratch

Sessions 1 to 6 you called somebody else's LLM. This time you build one, train it
on a rented GPU, and put it behind your own URL.

No `transformers`, no `langchain`, no pretrained weights. Just PyTorch and about
700 lines you can read in one sitting.

---

## Setup (do this ONCE, before class)

```bash
pip install -r requirements.txt

pip install modal
modal setup            # opens a browser, sign in with GitHub
```

Then warm up the two slow things so class time is not spent watching progress bars:

```bash
python data3.py --dataset shakespeare --tokenizer char    # downloads 1 MB
modal run modal_app7.py                                   # builds the GPU image
```

That first `modal run` installs a 2.3 GB PyTorch into a container. It takes a few
minutes **once**. Modal caches it, so every run after that starts in seconds.
Do not discover this live.

> **Note:** there is no `.env` and no API key anywhere in this session.
> Modal authenticates through `modal setup`, and the model is yours.

---

## The files, in teaching order

| # | File | Topic | What students learn |
|---|------|-------|---------------------|
| 1 | `config1.py` | The control panel | Every number that shapes a model, in one place. `TINY` for your laptop, `SMALL` for the GPU — the same code, two sizes. |
| 2 | `tokenizer2.py` | Text becomes numbers | Character-level in 15 lines, then **BPE built from scratch**. Watch it invent `th`, then `the`, then ` cat`. Why "the" costs 1 token and a rare name costs 4. |
| 3 | `data3.py` | The reusable one | Download, tokenize, save as `train.bin` / `val.bin`. See `x` and `y` side by side and realise `y` is just `x` shifted one place — that shift is the entire training signal. |
| 4 | `model4.py` | **The transformer** | Q, K, V. The attention formula written out by hand. The causal mask printed as a literal triangle of zeros. Residuals, LayerNorm, and why `x = x + ...` matters. |
| 5 | `train5.py` | Teaching it | The five-step loop that trains every neural network. Prints a sample every 250 steps, so the class watches noise become letters become words become Shakespeare. |
| 6 | `generate6.py` | Making it write | Predict one token, append, repeat. What temperature and top-k actually do. |
| 7 | `modal_app7.py` | A real GPU | The exact same `train()` function, on an L4. Images, Volumes, `.remote()` vs `.local()`, and why `vol.commit()` is not optional. |
| 8 | `serve8.py` | You become the API | Deploy the model behind a URL. `@modal.enter()` and why loading weights per request is the wrong answer. |
| 9 | `use_from_agent9.py` | Full circle | Your Session 6 LangChain agent, running on the model you just built. |
| 10 | `modern_upgrades10.py` | What changed since GPT-2 | RMSNorm, RoPE, SwiGLU — the three swaps Llama 3 and GPT-4 made, and why the core you learned is still the core. *(bonus, skip if short on time)* |

Every file runs on its own:

```bash
python tokenizer2.py     # each file prints a live demo
python model4.py
```

and every file is importable — the teaching order is baked right into the
filename (`config1.py` → `modern_upgrades10.py`), so imports across files never
need a package or a path hack.

---

## The run, start to finish

```bash
python data3.py --dataset shakespeare --tokenizer char   # 1 MB, a few seconds
python train5.py                                         # laptop CPU, ~3 min
python generate6.py --prompt "ROMEO:"                    # bad, but Shakespeare-shaped

modal run modal_app7.py                                  # L4 GPU, ~10 min, ~$0.13
modal volume ls argpt-checkpoints                       # the checkpoint outlived the container

modal deploy serve8.py                                   # prints your URL
python use_from_agent9.py --url <that url>
```

---

## Tips for the live session

**Set expectations in the first five minutes.** ARGPT is 0.8M parameters on a
laptop, 10M on the GPU. GPT-4 is roughly a million times bigger. This model
produces *structure*, not *sense*. The deliverable is the loss curve, not the
prose. A class expecting ChatGPT will read a working demo as a failure.

**The best 90 seconds of the session** is `python train5.py`. Say nothing and let
the samples scroll. Around step 250 it is letter soup, by step 1000 you get
`OMIO:`, by step 2000 you get real character names and line breaks. Nobody needs
loss explained after watching that.

**Never name a file `modal.py`.** It shadows the `modal` package and `import modal`
then imports the student's own file. The error is `AttributeError: module 'modal'
has no attribute 'App'` and it is baffling if you have not seen it. Teach it
deliberately — it is a real lesson about Python's import order.

**Your laptop is not their laptop.** If you have an NVIDIA GPU, `python train5.py`
finishes in about 70 seconds for you and several minutes for a student on CPU.
Say so, or your demo looks broken on their machine.

**BPE takes about 90 seconds** to train on the full Shakespeare text. Run
`python data3.py --tokenizer bpe` during a break, not in front of the class. The
default `char` path is instant. Payoff worth showing: 1,115,394 characters becomes
1,115,394 char tokens but only 453,113 BPE tokens — the same text in less than
half the space.

**Callbacks that land well:**
- Session 3 chunked documents for RAG. `block_size` is the same problem: the
  model physically cannot see past it.
- Session 4 built a pluggable LLM interface. `CharTokenizer` and `BPETokenizer`
  expose the same `encode`/`decode` — swap one line, everything else works.
- Session 6 wrapped Groq in a LangChain object. File 9 does that to ARGPT.

**Cost, so nobody is afraid to press the button:** L4 is $0.80/hour billed by the
second. A ten minute training run is about **13 cents**. Modal's free tier is $30
a month, which is roughly 37 hours of GPU. The whole class fits inside it.

**If the wifi dies:** put any `.txt` file at `data/custom/input.txt` and run
`python data3.py --dataset custom`. Everything downstream works unchanged.

---

## Common breakages

| What you see | What happened |
|---|---|
| `AttributeError: module 'modal' has no attribute 'App'` | A file named `modal.py` is shadowing the package. Rename it. |
| `IndexError: index out of range in self` | The model's `vocab_size` disagrees with the data. Re-run `data3.py`, then `train5.py`. Never hand-edit `vocab_size` in `config1.py` — the data sets it. |
| `FileNotFoundError: .../train.bin` | Run `data3.py` before `train5.py`. |
| Checkpoint gone after training on Modal | A missing `vol.commit()`. It is the last line of `train_on_gpu` for exactly this reason. |
| Modal run dies at 5 minutes | Modal's default `timeout` is 300 seconds. Ours is set to 3600. |
| Loss goes to `nan` | Learning rate too high. `TINY` uses 3e-4 for a reason. |

---

## What we deliberately did not build

Worth naming out loud, because it is the honest boundary of the session:

- **Instruction tuning and RLHF.** We only did pretraining. ARGPT continues text;
  it cannot follow instructions. That gap is exactly what the agent sessions were
  working around.
- **Mixed precision, `torch.compile`, multi-GPU, gradient accumulation.** All real,
  all worth roughly 2-10x speed, none of them teach you what a transformer is.
- **A tokenizer that handles the messy parts** — special tokens, byte fallback
  edge cases. Ours is honest BPE, just not battle-hardened.

You now have the foundation everything else is bolted onto.
