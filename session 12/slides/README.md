# Slide deck source — Agent-to-Agent (A2A) Communication

Generates `../A2A-Communication.pptx` (44 slides, 16:9, white background,
black + yellowish orange).

```bash
pip install python-pptx
cd slides
python build.py
```

## Files

| File | What's in it |
|------|--------------|
| `theme.py` | Colours, layout grid, and every reusable component (`slide`, `bullets`, `code`, `table`, `box`, `chip`, `chip_row`, `arrow`, `label`, `rule`, `vrule`, `grid`). Change the palette here and the whole deck follows. |
| `part1_concepts.py` | Slides 1–23 — why A2A exists, A2A vs MCP vs API, the architecture, and every protocol object (Card, Skills, Discovery, Messages, Tasks, Artifacts, the flow) |
| `part2_code.py` | Slides 24–35 — the eleven numbered files, from A2A by hand to the official `a2a-sdk` |
| `part3_debate.py` | Slides 36–44 — the `agent talks 2` folder, recap, closing |
| `build.py` | Assembles the three parts, saves the `.pptx`, then runs the layout check |

## Editing

Text supports a small markup inside any string:

| Markup | Renders as |
|--------|-----------|
| `**bold**` | bold |
| `*italic*` | italic |
| `` `code` `` | Consolas, orange |
| `~~emphasis~~` | bold orange |

The wrappers nest, so `` **a `code` word** `` works. A `\n` inside any string
becomes a soft line break.

Layout is in **inches** on a 13.333 × 7.5 slide. The usable body runs from
`BODY_TOP` (1.42) to 6.92, with `M` (0.55) side margins and `CW` (12.23) of
width. `twocol()` returns `(x_left, x_right, width)`. Slide titles auto-shrink
to stay on one line.

**Never hand-compute the height of a `code(...)` panel** — pass `h=None` and it
sizes itself from its own line count. Guessing is how blocks end up sitting on
top of each other.

## Checking your changes

`build.py` reports anything that runs off the slide, reaches into the footer
band, or overlaps another filled block. It cannot see text that overflows its
own textbox, so also render and look:

```powershell
$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Open("<full path>\A2A-Communication.pptx", $true, $false, $false)
$pres.Export("<some folder>", "PNG", 1400, 788)
$pres.Close(); $ppt.Quit()
```

The usual failure is a `box(...)` whose text wraps one line further than you
expected and spills past its tinted background.

## Where the content came from

Every code block is copied from the session 12 source (`01`–`11`,
`agent talks 2/debate_agent.py`, `agent talks 2/04_debate_orchestrator.py`),
trimmed only for width. Protocol field names follow the **JSON-RPC** flavour of
the spec — `message/send`, `tasks/get`, `"submitted"`, `{"kind": "text"}` — to
match the code. Slide 35 is the one place the SDK's protobuf spelling
(`Role.ROLE_USER`, `event.HasField(...)`) appears, and it says so explicitly.
