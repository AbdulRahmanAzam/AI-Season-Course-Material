"""
Builds ../A2A-Communication.pptx  —  44 slides, 16:9, white background,
black + yellowish-orange.

    pip install python-pptx
    python build.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pptx import Presentation
from pptx.util import Inches

import theme
import part1_concepts
import part2_code
import part3_debate

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "A2A-Communication.pptx")

EMU = 914400.0
TOL = Inches(0.02)          # ignore hairline rounding
FOOTER_TOP = Inches(7.00)   # the footer band — nothing may reach into it
MIN_AREA = Inches(0.35) * Inches(0.35)   # ignore chip-on-arrow style nudges


def _boxes(s):
    """The filled blocks that must never sit on top of each other: code panels,
    callout boxes, chips and tables. Bare textboxes are skipped — their declared
    height is a guess, so they would only generate noise."""
    out = []
    for shp in s.shapes:
        if shp.top is None or shp.height is None:
            continue
        keep = shp.has_table or (
            shp.shape_type is not None
            and not shp.has_text_frame
        ) or (
            shp.shape_type is not None and shp.has_text_frame
            and shp.name.lower().startswith(("rectangle", "rounded"))
        )
        if keep:
            out.append(shp)
    return out


def check_overflow(prs):
    """Nothing in python-pptx validates layout, so do it here: report anything
    that runs off the slide, reaches into the footer, or overlaps another block.
    A code() or box() colliding with the next one is the usual defect."""
    w, h = prs.slide_width, prs.slide_height
    problems = []
    for n, s in enumerate(prs.slides, start=1):
        for shp in s.shapes:
            if shp.top is None or shp.height is None:
                continue
            bottom, right = shp.top + shp.height, shp.left + shp.width
            if bottom > h + TOL:
                problems.append(f"  {n:02d}  off the bottom: {bottom / EMU:.2f}\" "
                                f"> 7.50\"   ({shp.name})")
            if right > w + TOL:
                problems.append(f"  {n:02d}  off the right: {right / EMU:.2f}\" "
                                f"> 13.33\"   ({shp.name})")

        blocks = _boxes(s)
        for i, a in enumerate(blocks):
            if a.height < Inches(0.30):
                continue                      # accent bars and rules
            if a.top + a.height > FOOTER_TOP + TOL:
                problems.append(f"  {n:02d}  into the footer: "
                                f"{(a.top + a.height) / EMU:.2f}\"   ({a.name})")
            for b in blocks[i + 1:]:
                if b.height < Inches(0.30):
                    continue
                ox = min(a.left + a.width, b.left + b.width) - max(a.left, b.left)
                oy = min(a.top + a.height, b.top + b.height) - max(a.top, b.top)
                if ox > TOL and oy > TOL and ox * oy > MIN_AREA:
                    # a chip drawn deliberately inside a panel is fine
                    inside = ((a.left <= b.left and a.top <= b.top
                               and a.left + a.width >= b.left + b.width
                               and a.top + a.height >= b.top + b.height)
                              or (b.left <= a.left and b.top <= a.top
                                  and b.left + b.width >= a.left + a.width
                                  and b.top + b.height >= a.top + a.height))
                    if not inside:
                        problems.append(
                            f"  {n:02d}  overlap {ox / EMU:.2f}\" x {oy / EMU:.2f}\": "
                            f"{a.name} @ y{a.top / EMU:.2f}-{(a.top + a.height) / EMU:.2f}"
                            f"  vs  {b.name} @ y{b.top / EMU:.2f}-"
                            f"{(b.top + b.height) / EMU:.2f}")
    return problems


def main():
    prs = Presentation()
    prs.slide_width = Inches(theme.W)
    prs.slide_height = Inches(theme.H)

    theme.reset_counter()
    part1_concepts.build(prs)
    part2_code.build(prs)
    part3_debate.build(prs)

    prs.save(OUT)

    count = len(prs.slides._sldIdLst)
    print(f"saved {os.path.abspath(OUT)}  ({count} slides)")

    problems = check_overflow(prs)
    if problems:
        print(f"\n{len(problems)} shape(s) run off the slide:")
        print("\n".join(problems))
    else:
        print("overflow check: clean")


if __name__ == "__main__":
    main()
