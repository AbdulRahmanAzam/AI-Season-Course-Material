"""
Build the Part 2 slide deck.

    cd slides
    python build.py

Writes ../Build-an-LLM-from-Scratch-Part-2.pptx
Edit part_a / part_b / part_c and re-run to regenerate.
"""

import os
import sys

from pptx import Presentation
from pptx.util import Inches

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import part_a
import part_b
import part_c
import theme

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "Build-an-LLM-from-Scratch-Part-2.pptx")


def main():
    prs = Presentation()
    prs.slide_width = Inches(theme.W)
    prs.slide_height = Inches(theme.H)
    theme.reset_counter()

    part_a.build(prs)
    part_b.build(prs)
    part_c.build(prs)

    prs.save(OUT)
    print(f"{len(prs.slides.__iter__.__self__._sldIdLst)} slides -> "
          f"{os.path.abspath(OUT)}")


if __name__ == "__main__":
    main()
