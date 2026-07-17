# Marketing Leads Agent

Type a request like **"coffee shops in los angeles"** and get a CSV of businesses
with their **name, phone, email, website, and address**.

Everything is **free** — no credit card, no paid API.

- **Business list:** [OpenStreetMap](https://www.openstreetmap.org) via the free
  Nominatim + Overpass services (no key, never blocked).
- **Emails:** we open each business website and look for an email.
- **The agent:** LangChain `create_agent` + the free **Groq** model — same stack as
  the rest of this session.

## Setup (one time)

```bash
pip install -r requirements.txt
```

Then copy `.env.example` to `.env` and paste your free Groq key
(get one at https://console.groq.com/keys).

## Run it

**Option A — the full agent (talk to it in English):**

```bash
python leads_agent.py
```

Then type, e.g. `coffee shops in los angeles` or `restaurants in miami and save them`.

**Option B — the engine only, no AI needed** (great first test):

```bash
python leads_core.py
```

This searches for coffee shops in Los Angeles and writes the CSV directly — handy to
prove the data part works before adding the AI.

Results are saved in the **`output/`** folder as a `.csv` you can open in Excel.

## The two files

| File | What it is |
|------|-----------|
| `leads_core.py` | The engine. Plain Python functions (find places, scrape emails, save CSV). No AI, no key. |
| `leads_agent.py` | The AI wrapper. Turns those functions into tools the Groq model can call. |

## Good to know

- **Categories that map cleanly:** coffee/cafe, restaurant, bar, pub, bakery, hotel,
  gym, pharmacy, dentist, salon, supermarket, clothing, bookstore. Anything else falls
  back to a search by business name.
- **Blank emails are normal** — not every business publishes one on their website.
- **Coverage varies by city.** OpenStreetMap has fewer small shops than Google, but it
  is free and never gets your class blocked. That is the trade-off we chose.
- **Error 429 from Groq?** The free tier has rate limits. Wait ~30 seconds and retry
  (or just use `python leads_core.py`, which needs no AI at all).
- Please use lightly — Nominatim and Overpass are free shared services.
