"""
Theme + layout toolkit for the AI Season slide decks.
Light background, black + orange, 16:9.

Everything is built from a few primitives so every slide looks the same:
    slide(kicker, title)   a new content slide with header + footer
    bullets(...)           a text block with the ** ` ~~ mini-markup
    code(...)              a monospace panel
    table(...)             an orange-headed table
    box(...)               a tinted callout
    chip(...) / arrow(...) diagram pieces
    grid(...)              a matrix of cells (used for the causal mask etc.)
"""

import re

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

# ------------------------------------------------------------------ palette
# Yellowish orange (amber) + black. Two ambers on purpose:
#   ORANGE_HI is the bright brand fill — always put BLACK text on it.
#   ORANGE is the deeper amber used for TEXT, so it stays readable on white.
ORANGE = RGBColor(0xC2, 0x7A, 0x00)   # amber text: headings, kickers, emphasis
ORANGE_HI = RGBColor(0xF7, 0xB0, 0x22)   # bright yellow-orange: fills, bars, chips
ORANGE_DK = RGBColor(0x8A, 0x57, 0x00)   # small text / inline code, must stay legible
TINT = RGBColor(0xFF, 0xF7, 0xE8)   # callout background
TINT2 = RGBColor(0xFE, 0xE9, 0xBF)   # stronger tint
INK = RGBColor(0x15, 0x15, 0x15)   # body text / "black"
GRAY = RGBColor(0x5C, 0x5C, 0x5C)
GRAY_LT = RGBColor(0x92, 0x92, 0x92)
LINE = RGBColor(0xDF, 0xDF, 0xDF)
CODEBG = RGBColor(0xFA, 0xF9, 0xF7)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x1D, 0x7A, 0x4C)   # only for "good / yes" marks
RED = RGBColor(0xB3, 0x261, 0x0 % 256) if False else RGBColor(0xB3, 0x26, 0x1E)

BODY = "Segoe UI"
MONO = "Consolas"

# ------------------------------------------------------------------ geometry
W, H = 13.333, 7.5
M = 0.55                      # side margin
CW = W - 2 * M                # content width  = 12.233
BODY_TOP = 1.42
BODY_BOT = 6.92
BODY_H = BODY_BOT - BODY_TOP  # 5.5

FOOTER = "AI Season   ·   Build an LLM from Scratch, Part 2   ·   Abdul Rahman Azam"

_n = [0]   # slide counter


def reset_counter():
    _n[0] = 0


# ------------------------------------------------------------------ markup
_TOK = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|~~[^~]+~~)")


def _runs(par, text, size, color=INK, bold=False, font=BODY):
    """Fill a paragraph, honouring **bold**, *italic*, `code` and ~~orange~~."""
    for piece in _TOK.split(text):
        if not piece:
            continue
        r = par.add_run()
        if piece.startswith("**") and piece.endswith("**"):
            r.text = piece[2:-2]
            r.font.bold = True
            r.font.color.rgb = color
            r.font.name = font
        elif piece.startswith("*") and piece.endswith("*"):
            r.text = piece[1:-1]
            r.font.italic = True
            r.font.bold = bold
            r.font.color.rgb = color
            r.font.name = font
        elif piece.startswith("`") and piece.endswith("`"):
            r.text = piece[1:-1]
            r.font.bold = False
            r.font.color.rgb = ORANGE_DK
            r.font.name = MONO
            r.font.size = Pt(size - 0.5)
        elif piece.startswith("~~") and piece.endswith("~~"):
            r.text = piece[2:-2]
            r.font.bold = True
            r.font.color.rgb = ORANGE
            r.font.name = font
        else:
            r.text = piece
            r.font.bold = bold
            r.font.color.rgb = color
            r.font.name = font
        if r.font.size is None:
            r.font.size = Pt(size)


def _tb(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP, wrap=True):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tf


def _noline(shp):
    shp.line.fill.background()
    return shp


def _noshadow(shp):
    try:
        shp.shadow.inherit = False
    except Exception:
        pass
    return shp


# ------------------------------------------------------------------ slides
def _fit_title(title, width=CW, max_pt=25.0, min_pt=17.0):
    """Shrink the title just enough to keep it on one line."""
    n = len(re.sub(r"[*`~]", "", title))
    if n == 0:
        return max_pt
    # Segoe UI Bold averages ~0.0072 inches of width per point of size, per char
    return max(min_pt, min(max_pt, width / (n * 0.0072)))


def slide(prs, kicker, title, title_size=None):
    """A standard content slide: kicker, title, orange rule, footer."""
    if title_size is None:
        title_size = _fit_title(title)
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _n[0] += 1

    if kicker:
        tf = _tb(s, M, 0.32, CW, 0.26)
        p = tf.paragraphs[0]
        _runs(p, kicker.upper(), 10.5, ORANGE, bold=True)
        for r in p.runs:
            r.font.name = BODY
        try:
            p.runs[0].font._rPr.set("spc", "120")
        except Exception:
            pass

    tf = _tb(s, M, 0.58 if kicker else 0.5, CW, 0.62)
    _runs(tf.paragraphs[0], title, title_size, INK, bold=True)

    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(M), Inches(1.235),
                             Inches(0.9), Inches(0.045))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ORANGE_HI
    _noline(bar)
    _noshadow(bar)

    _footer(s)
    return s


def _footer(s):
    tf = _tb(s, M, 7.03, CW - 0.5, 0.28)
    _runs(tf.paragraphs[0], FOOTER, 8.5, GRAY_LT)

    tf = _tb(s, W - M - 0.7, 7.02, 0.7, 0.28)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    _runs(p, f"{_n[0]:02d}", 11, ORANGE, bold=True)


def divider(prs, number, title, subtitle, points=()):
    """A section break: big orange file number on a tinted panel."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _n[0] += 1

    panel = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0),
                               Inches(4.3), Inches(H))
    panel.fill.solid()
    panel.fill.fore_color.rgb = TINT
    _noline(panel)
    _noshadow(panel)

    tf = _tb(s, 0.7, 2.25, 3.2, 2.2)
    p = tf.paragraphs[0]
    _runs(p, "FILE", 13, ORANGE, bold=True)
    p2 = tf.add_paragraph()
    _runs(p2, str(number), 96, ORANGE, bold=True)
    p2.space_before = Pt(0)

    tf = _tb(s, 4.95, 2.28, W - 5.6, 0.75)
    _runs(tf.paragraphs[0], title, 33, INK, bold=True)

    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.95), Inches(3.12),
                             Inches(0.9), Inches(0.045))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ORANGE_HI
    _noline(bar)
    _noshadow(bar)

    tf = _tb(s, 4.95, 3.35, W - 5.6, 0.6)
    _runs(tf.paragraphs[0], subtitle, 14.5, GRAY)

    if points:
        tf = _tb(s, 4.95, 4.15, W - 5.6, 2.2)
        for i, pt in enumerate(points):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_before = Pt(0 if i == 0 else 9)
            _runs(p, "—   " + pt, 12.5, GRAY)

    _footer(s)
    return s


def title_slide(prs, title, subtitle, instructor, org, meta=()):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _n[0] += 1

    band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0),
                              Inches(W), Inches(0.32))
    band.fill.solid()
    band.fill.fore_color.rgb = ORANGE_HI
    _noline(band)
    _noshadow(band)

    tf = _tb(s, M + 0.35, 1.35, CW - 1, 0.4)
    _runs(tf.paragraphs[0], org.upper(), 14, ORANGE, bold=True)

    tf = _tb(s, M + 0.35, 1.85, CW - 1.2, 1.9)
    p = tf.paragraphs[0]
    _runs(p, title, 50, INK, bold=True)
    p.line_spacing = 1.02

    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(M + 0.35), Inches(3.75),
                             Inches(1.5), Inches(0.06))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ORANGE_HI
    _noline(bar)
    _noshadow(bar)

    tf = _tb(s, M + 0.35, 4.02, CW - 1.2, 0.5)
    _runs(tf.paragraphs[0], subtitle, 16.5, GRAY)

    tf = _tb(s, M + 0.35, 5.15, 6.0, 0.9)
    p = tf.paragraphs[0]
    _runs(p, "Instructor", 10.5, ORANGE, bold=True)
    p = tf.add_paragraph()
    p.space_before = Pt(3)
    _runs(p, instructor, 20, INK, bold=True)

    if meta:
        tf = _tb(s, W - M - 4.6, 5.15, 4.3, 1.4)
        for i, m in enumerate(meta):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.RIGHT
            p.space_before = Pt(0 if i == 0 else 5)
            _runs(p, m, 11.5, GRAY)

    band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(H - 0.12),
                              Inches(W), Inches(0.12))
    band.fill.solid()
    band.fill.fore_color.rgb = INK
    _noline(band)
    _noshadow(band)
    return s


# ------------------------------------------------------------------ blocks
def bullets(s, x, y, w, h, items, size=13.5, gap=8, dash="—"):
    """items: str, or (level, str). level 0 = bullet, 1 = indented sub-point."""
    tf = _tb(s, x, y, w, h)
    for i, it in enumerate(items):
        lvl, text = it if isinstance(it, tuple) else (0, it)
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_before = Pt(0 if i == 0 else gap)
        p.line_spacing = 1.16
        if lvl == 0:
            _runs(p, f"{dash}   ", size, ORANGE, bold=True)
            _runs(p, text, size, INK)
        elif lvl == 1:
            p.left_indent = Inches(0.34)
            _runs(p, "·   ", size - 0.5, ORANGE)
            _runs(p, text, size - 0.5, GRAY)
        else:                      # level 2 = plain paragraph, no marker
            _runs(p, text, size, INK)
    return tf


def para(s, x, y, w, h, text, size=13.5, color=INK, align=None):
    tf = _tb(s, x, y, w, h)
    p = tf.paragraphs[0]
    p.line_spacing = 1.2
    if align:
        p.alignment = align
    _runs(p, text, size, color)
    return tf


def heading(s, x, y, w, text, size=13, color=ORANGE):
    tf = _tb(s, x, y, w, 0.3)
    _runs(tf.paragraphs[0], text.upper(), size, color, bold=True)
    return tf


def code(s, x, y, w, h, lines, size=11.5, title=None, fill=CODEBG):
    """A monospace panel with an orange left edge."""
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                            Inches(w), Inches(h))
    bg.fill.solid()
    bg.fill.fore_color.rgb = fill
    bg.line.color.rgb = LINE
    bg.line.width = Pt(0.75)
    _noshadow(bg)
    bg.text_frame.text = ""

    edge = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                              Inches(0.045), Inches(h))
    edge.fill.solid()
    edge.fill.fore_color.rgb = ORANGE_HI
    _noline(edge)
    _noshadow(edge)

    top = y + 0.13
    if title:
        tf = _tb(s, x + 0.22, top, w - 0.4, 0.24)
        _runs(tf.paragraphs[0], title, 9.5, ORANGE, bold=True)
        top += 0.28

    tf = _tb(s, x + 0.22, top, w - 0.4, h - (top - y) - 0.1, wrap=False)
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_before = Pt(0)
        p.line_spacing = 1.22
        # a leading "#" comment line is grey; "//" marks an inline annotation
        if ln.strip().startswith("#"):
            _runs(p, ln, size, GRAY_LT, font=MONO)
        elif "  # " in ln:
            head, cmt = ln.split("  # ", 1)
            _runs(p, head, size, INK, font=MONO)
            _runs(p, "  # " + cmt, size, ORANGE_DK, font=MONO)
        else:
            _runs(p, ln, size, INK, font=MONO)
        for r in p.runs:
            r.font.name = MONO
    return bg


def box(s, x, y, w, h, title, body, size=12.5, fill=TINT, accent=ORANGE):
    bg = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y),
                            Inches(w), Inches(h))
    bg.fill.solid()
    bg.fill.fore_color.rgb = fill
    _noline(bg)
    _noshadow(bg)
    bg.adjustments[0] = 0.06
    bg.text_frame.text = ""

    top = y + 0.16
    if title:
        tf = _tb(s, x + 0.26, top, w - 0.5, 0.28)
        _runs(tf.paragraphs[0], title.upper(), 10.5, accent, bold=True)
        top += 0.31

    tf = _tb(s, x + 0.26, top, w - 0.5, h - (top - y) - 0.12)
    if isinstance(body, str):
        body = [body]
    for i, b in enumerate(body):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_before = Pt(0 if i == 0 else 6)
        p.line_spacing = 1.16
        _runs(p, b, size, INK)
    return bg


def table(s, x, y, w, rows, widths=None, size=11, head_size=10.5,
          row_h=0.34, head_h=0.36, aligns=None):
    """rows[0] is the header. widths are relative and get normalised."""
    nr, nc = len(rows), len(rows[0])
    h = head_h + row_h * (nr - 1)
    shp = s.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(h))
    t = shp.table
    t.first_row = False
    t.horz_banding = False

    if widths is None:
        widths = [1] * nc
    tot = float(sum(widths))
    for i, ww in enumerate(widths):
        t.columns[i].width = Emu(int(Inches(w) * ww / tot))
    t.rows[0].height = Inches(head_h)
    for r in range(1, nr):
        t.rows[r].height = Inches(row_h)

    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = t.cell(r, c)
            cell.margin_left = Inches(0.09)
            cell.margin_right = Inches(0.07)
            cell.margin_top = Inches(0.035)
            cell.margin_bottom = Inches(0.035)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            if r == 0:
                cell.fill.fore_color.rgb = ORANGE_HI
            elif r % 2 == 0:
                cell.fill.fore_color.rgb = RGBColor(0xFB, 0xFA, 0xF9)
            else:
                cell.fill.fore_color.rgb = WHITE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.line_spacing = 1.1
            if aligns and aligns[c] == "c":
                p.alignment = PP_ALIGN.CENTER
            if r == 0:
                _runs(p, str(val), head_size, INK, bold=True)
            else:
                _runs(p, str(val), size, INK)
    return t


# ------------------------------------------------------------------ diagrams
def chip(s, x, y, w, h, text, fill=WHITE, edge=ORANGE, color=INK, size=12,
         bold=True, shape=MSO_SHAPE.ROUNDED_RECTANGLE, sub=None):
    shp = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if edge is None:
        _noline(shp)
    else:
        shp.line.color.rgb = edge
        shp.line.width = Pt(1.25)
    _noshadow(shp)
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        shp.adjustments[0] = 0.12

    tf = shp.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.line_spacing = 1.05
    _runs(p, text, size, color, bold=bold)
    if sub:
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.space_before = Pt(2)
        _runs(p2, sub, size - 2.5, GRAY)
    return shp


def arrow(s, x, y, w, h, right=True, color=ORANGE_HI):
    shp = s.shapes.add_shape(
        MSO_SHAPE.RIGHT_ARROW if right else MSO_SHAPE.DOWN_ARROW,
        Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    _noline(shp)
    _noshadow(shp)
    shp.text_frame.text = ""
    return shp


def label(s, x, y, w, text, size=10, color=GRAY, align=PP_ALIGN.CENTER):
    tf = _tb(s, x, y, w, 0.28)
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = 1.05
    _runs(p, text, size, color)
    return tf


def grid(s, x, y, cell, rows, fills=None, texts=None, size=10,
         head_cols=None, head_rows=None):
    """rows x cols of square cells. fills/texts are 2-D lists."""
    nr = len(rows)
    nc = len(rows[0])
    if head_cols:
        for c, t in enumerate(head_cols):
            label(s, x + c * cell, y - 0.3, cell, t, size=9, color=ORANGE_DK)
    for r in range(nr):
        if head_rows:
            label(s, x - 0.72, y + r * cell + cell / 2 - 0.13, 0.66,
                  head_rows[r], size=9, color=ORANGE_DK, align=PP_ALIGN.RIGHT)
        for c in range(nc):
            f = fills[r][c] if fills else WHITE
            shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x + c * cell),
                                     Inches(y + r * cell), Inches(cell), Inches(cell))
            shp.fill.solid()
            shp.fill.fore_color.rgb = f
            shp.line.color.rgb = RGBColor(0xE8, 0xE8, 0xE8)
            shp.line.width = Pt(0.6)
            _noshadow(shp)
            tf = shp.text_frame
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf.margin_left = tf.margin_right = 0
            tf.margin_top = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            txt = texts[r][c] if texts else str(rows[r][c])
            col = WHITE if f == INK else INK
            _runs(p, txt, size, col, bold=True, font=MONO)
            for rr in p.runs:
                rr.font.name = MONO


def rule(s, x, y, w, color=LINE, thick=0.012):
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                             Inches(w), Inches(thick))
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    _noline(shp)
    _noshadow(shp)
    return shp


def twocol(s, gap=0.4):
    """Return (x_left, x_right, width) for a two-column body."""
    cw = (CW - gap) / 2
    return M, M + cw + gap, cw
