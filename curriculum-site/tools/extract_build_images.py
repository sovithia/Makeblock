# -*- coding: utf-8 -*-
"""Pull the assembly diagrams out of the official manuals into site/assets/build/.

Sources (project root):
  mbot2.pdf         - mBot2 Quick Start Guide. Printed as 2-UP SPREADS: PDF page 6
                      carries printed pages 9 and 10, and so on. The wheeled build
                      is printed pp. 9-14, i.e. PDF pages 6-8, split in half.
  mbot2_addons.pdf  - the RANGER build. NO GRADE USES IT. 63 pp, one printed page
                      per PDF page. Its cover reads "Rover Robotics Add-on Pack
                      ... (mBot2 Ranger)" and its first page then says "keep the
                      parts for building mBot2 Rover" -- Makeblock's own naming
                      contradicts itself, and an earlier version of this file
                      argued from that muddle that the PDF was the Rover guide.
                      It is NOT. The Ranger wires its motors STRAIGHT and puts the
                      servos on S3/S4; the Rover crosses the motors and uses S1,
                      which is what every Grade 8 program expects. Diagrams were
                      once extracted from here for Grade 8 Steps 1-2 and showed
                      the wrong robot; someone followed them and built a Ranger.

                      *** There is NO digital Rover guide. *** Grade 8 builds from
                      the printed booklet in the add-on box (pp. 5-75) and its
                      pages carry no diagrams for that reason. Do not "restore"
                      them from this PDF.

                      Grade 9 used to build a Ranger here, mid-course, after a
                      teardown. It no longer builds anything: Grade 8 assembles
                      the Rover including both grip arms, and Grade 9 inherits
                      that robot standing. So no grade extracts from the Ranger
                      guide and RANGER_PAGES below is dead weight kept only so
                      nobody re-derives it.

Only representative pages are extracted, not all 63 — the class follows the
booklet for detail; the site shows what each phase looks like.

Usage: .venv/bin/python tools/extract_build_images.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MBOT2 = ROOT.parent / "mbot2.pdf"
RANGER = ROOT.parent / "mbot2_addons.pdf"      # used by no grade; see module docstring
# Grade 8's robot. The Rover guide is print-only, so this is a photographed copy
# of the booklet: 78 pages, no text layer, each page shot against a dark desk.
ROVER = ROOT.parent / "mbot2_rover.pdf"
OUT = ROOT / "site" / "assets" / "build"
DPI = 150

# printed page -> (pdf page, which half). The guide is imposed 2-up.
G7_SPREADS = {9: (6, "L"), 10: (6, "R"), 11: (7, "L"),
              12: (7, "R"), 13: (8, "L"), 14: (8, "R")}
# Deliberately empty: these page numbers used to feed Grade 8, from the RANGER
# guide. Grade 8's robot has no digital manual. Kept as a named constant so the
# next person sees why rather than re-deriving it.
# One page per phase of the Rover build, by PDF page. Section openers wherever
# possible, plus the three pages carrying a warning the class must not miss.
G8_PAGES = [7, 11, 15, 19, 24,          # brackets, left wheel, hub, right wheel, grain
            27, 43, 50, 53, 54, 55, 70, 76]   # chassis .. cross-cables .. arms, done
# Unused. Grade 9 has no build sessions, and if it ever regains one it will build
# the Rover from G8_PAGES, not a Ranger. Kept only to document what these were.
RANGER_PAGES = [8, 12, 16, 24, 28, 32, 36, 44, 48, 56, 60]


def page_crop(im, thresh=150, margin=6):
    """Crop a photographed booklet page out of the desk around it.

    The Rover guide exists only on paper, so its pages arrive as phone photos
    rather than vector PDF pages: a bright page on a dark surface, sometimes
    with a thumb in frame. trim() looks for white margins and finds none, so
    this thresholds instead and keeps the bounding box of everything bright.
    """
    from PIL import ImageFilter
    g = im.convert("L").filter(ImageFilter.GaussianBlur(4))
    box = g.point(lambda v: 255 if v > thresh else 0).getbbox()
    if not box:
        return im
    l, t, r, b = box
    return im.crop((max(0, l - margin), max(0, t - margin),
                    min(im.width, r + margin), min(im.height, b + margin)))


def render(pdf, page):
    tmp = Path(tempfile.mkdtemp())
    subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-png",
                    "-r", str(DPI), str(pdf), str(tmp / "p")], check=True)
    return Image.open(next(tmp.glob("p-*.png"))).convert("RGB")


def trim(im, pad=10):
    """Crop the white margin away, so the diagram fills its box on the page."""
    g = im.convert("L").point(lambda v: 0 if v > 244 else 255)
    box = g.getbbox()
    if not box:
        return im
    l, t, r, b = box
    return im.crop((max(0, l - pad), max(0, t - pad),
                    min(im.width, r + pad), min(im.height, b + pad)))


def main():
    missing = [p for p in (MBOT2, ROVER) if not p.exists()]
    if missing:
        raise SystemExit(f"manual not found: {', '.join(str(m) for m in missing)}")
    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.glob("*.png"):
        f.unlink()

    n = 0
    for printed, (page, half) in sorted(G7_SPREADS.items()):
        im = render(MBOT2, page)
        w = im.width // 2
        im = im.crop((0, 0, w, im.height)) if half == "L" else \
            im.crop((w, 0, im.width, im.height))
        trim(im).save(OUT / f"g7-{printed:02d}.png")
        n += 1
    for page in G8_PAGES:
        # photos, not vector pages: JPEG at a sane width, or the site gains 24 MB
        im = page_crop(render(ROVER, page))
        if im.width > 1500:
            im = im.resize((1500, round(im.height * 1500 / im.width)))
        im.convert("RGB").save(OUT / f"g8-{page:02d}.jpg", quality=82, optimize=True)
        n += 1

    kb = sum(f.stat().st_size for f in OUT.glob("*.png")) // 1024
    print(f"wrote {n} build diagrams to {OUT.relative_to(ROOT)} ({kb} KB)")


if __name__ == "__main__":
    sys.exit(main())
