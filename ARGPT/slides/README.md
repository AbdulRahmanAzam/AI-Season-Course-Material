# Slide deck source — Build an LLM from Scratch, Part 2

Generates `../Build-an-LLM-from-Scratch-Part-2.pptx` (94 slides, 16:9, light theme,
black + orange).

```bash
pip install python-pptx
cd slides
python build.py
```

## Files

| File | What's in it |
|------|--------------|
| `theme.py` | Colours, layout grid, and every reusable component (`slide`, `bullets`, `code`, `table`, `box`, `chip`, `arrow`, `grid`). Change the palette here and the whole deck follows. |
| `part_a.py` | Slides 1–33 — opening, `config1.py`, `tokenizer2.py`, `data3.py` |
| `part_b.py` | Slides 34–63 — `model4.py`, `train5.py`, `generate6.py` |
| `part_c.py` | Slides 64–94 — files 7–10, scaling, FAQ, cheat sheet, closing |
| `build.py` | Assembles the three parts and saves the `.pptx` |

## Editing

Text supports a small markup inside any string:

| Markup | Renders as |
|--------|-----------|
| `**bold**` | bold |
| `*italic*` | italic |
| `` `code` `` | Consolas, orange |
| `~~emphasis~~` | bold orange |

Layout is in **inches** on a 13.333 × 7.5 slide. The usable body runs from
`BODY_TOP` (1.42) to 6.92, with `M` (0.55) side margins and `CW` (12.23) of width.
Slide titles auto-shrink to stay on one line.

## Checking your changes

Nothing validates overflow automatically, so render and look:

```powershell
$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Open("<full path>\Build-an-LLM-from-Scratch-Part-2.pptx", $true, $false, $false)
$pres.Export("<some folder>", "PNG", 1400, 788)
$pres.Close(); $ppt.Quit()
```

The usual failure is a `grid(...)` or `code(...)` block running past 6.92 and
colliding with whatever sits below it.

## Where the numbers came from

Every figure on a dry-run slide was produced by running the actual project code —
`python config1.py`, `python tokenizer2.py`, and a script that pushed the same
tensors through `model4.py`. If you change the presets in `config1.py`, the
parameter counts on slides 9, 16 and 50 need updating too.
