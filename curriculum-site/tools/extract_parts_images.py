# -*- coding: utf-8 -*-
"""Extract real part pictures from the official manuals into site/assets/parts/.

Sources (project root):
  mbot2.pdf         - mBot2 Quick Start Guide; parts-list spread on page 2 (vector art)
  mbot2_addons.pdf  - Rover Robotics Add-on Pack QSG (mBot2 Ranger); parts list pp. 3-4

The mBot2 spread uses explicit crop boxes (multilingual captions make label
parsing unreliable). The add-on pages have single-line English labels, so crop
boxes are derived from the text layer: cell x-range = midpoints between
neighboring labels in the same row, y-range = a band above the label. Every
crop is auto-trimmed to its content and saved as PNG.

Icons keep their generator ids: parts_catalog.panel() prefers
site/assets/parts/<id>.png over the hand-drawn SVG when the file exists.

Usage: .venv/bin/python tools/extract_parts_images.py
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MBOT2 = ROOT.parent / "mbot2.pdf"
ADDONS = ROOT.parent / "mbot2_addons.pdf"
OUT = ROOT / "site" / "assets" / "parts"
DPI = 300
PT = DPI / 72.0  # pt -> px at DPI

NEAR_WHITE = 245


def render(pdf, page):
    tmp = Path(tempfile.mkdtemp())
    subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-png",
                    "-r", str(DPI), str(pdf), str(tmp / "p")], check=True)
    return Image.open(next(tmp.glob("p-*.png"))).convert("RGB")


def trim(im, pad=8):
    gray = im.convert("L").point(lambda v: 0 if v > NEAR_WHITE else 255)
    box = gray.getbbox()
    if not box:
        return im
    l, t, r, b = box
    l, t = max(0, l - pad), max(0, t - pad)
    r, b = min(im.width, r + pad), min(im.height, b + pad)
    return im.crop((l, t, r, b))


def save(name, im):
    OUT.mkdir(parents=True, exist_ok=True)
    im.save(OUT / f"{name}.png")
    print(f"  {name}.png  {im.width}x{im.height}")


def hstack(images, gap=24):
    ims = [trim(i) for i in images]
    h = min(i.height for i in ims)
    ims = [i.resize((round(i.width * h / i.height), h)) for i in ims]
    w = sum(i.width for i in ims) + gap * (len(ims) - 1)
    out = Image.new("RGB", (w, h), "white")
    x = 0
    for i in ims:
        out.paste(i, (x, 0))
        x += i.width + gap
    return out


# ---------------- mBot2 QSG page 2: explicit boxes (150dpi coords, scaled) ----

MBOT2_BOXES = {  # id -> (x0, y0, x1, y1) at 150 dpi
    "cyberpi":     (80, 170, 280, 330),
    "shield":      (290, 170, 470, 330),
    "ultra":       (480, 170, 660, 330),
    "quadrgb":     (665, 170, 850, 330),
    "motor":       (860, 170, 1060, 330),
    "chassis":     (80, 570, 280, 720),
    "usb":         (290, 570, 470, 720),
    "_hub":        (480, 570, 660, 720),
    "_tyre":       (665, 570, 850, 720),
    "miniwheel":   (860, 570, 1060, 720),
    "motorcable":  (1281, 55, 1481, 200),
    "mbuild":      (1531, 55, 1721, 200),
    "map":         (2041, 55, 2221, 200),
    "screws7":     (1301, 475, 1491, 625),
    "screws7s":    (1861, 475, 2021, 625),
    "screwdriver": (2051, 475, 2251, 625),
}


def extract_mbot2():
    print("mbot2.pdf page 2 (parts list):")
    page = render(MBOT2, 2)
    s = DPI / 150.0
    crops = {}
    for pid, (x0, y0, x1, y1) in MBOT2_BOXES.items():
        crops[pid] = trim(page.crop((round(x0*s), round(y0*s), round(x1*s), round(y1*s))))
    for pid, im in crops.items():
        if not pid.startswith("_"):
            save(pid, im)
    save("wheelset", hstack([crops["_hub"], crops["_tyre"]]))

    # assembled mBot2 render: embedded raster + alpha mask on the cover
    tmp = Path(tempfile.mkdtemp())
    subprocess.run(["pdfimages", "-f", "1", "-l", "1", "-png", str(MBOT2),
                    str(tmp / "c")], check=True)
    rgb = Image.open(tmp / "c-000.png").convert("RGB")
    mask = Image.open(tmp / "c-001.png").convert("L")
    flat = Image.composite(rgb, Image.new("RGB", rgb.size, "white"), mask)
    save("robot_wheel", trim(flat))


# ---------------- add-on QSG pages 3-4: label-anchored boxes ------------------

def text_lines(pdf, page):
    """[(text, x_center_pt, y_top_pt)] for single-line labels on the page."""
    xml = subprocess.run(["pdftotext", "-bbox", "-f", str(page), "-l", str(page),
                          str(pdf), "-"], capture_output=True, text=True).stdout
    words = [(float(m[0]), float(m[1]), float(m[2]), float(m[3]), m[4])
             for m in re.findall(
                 r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" '
                 r'yMax="([\d.]+)">([^<]+)</word>', xml)]
    words.sort(key=lambda w: (round(w[1] / 6), w[0]))
    lines = []
    for w in words:
        if lines and abs(w[1] - lines[-1][1][1]) < 4 and w[0] - lines[-1][1][2] < 12:
            t, (x0, y0, _, _) = lines[-1]
            lines[-1] = (f"{t} {w[4]}", (x0, y0, w[2], w[3]))
        else:
            lines.append((w[4], (w[0], w[1], w[2], w[3])))
    return [(t, (b[0] + b[2]) / 2, b[1]) for t, b in lines]


# label prefix (page, first line) -> icon id ("_" = intermediate for composites)
ADDON_LABELS = {
    3: {"Servo pack": "servopack", "Bluetooth Controller": "controller",
        "Track": "track", "Wheel hub": "_awh", "Small wheel hub": "_aswh",
        "Slide beam 2*6": "_sb26", "Plate 3*8": "_p38",
        "Bracket 90° 3*3": "_b90", "U bracket": "_bu",
        "Metal shock": "_msh", "Plastic shock": "_psh",
        "D shaft": "dshaft", "Shaft collar": "_sc", "Flange bearing": "_fb",
        "Socket wrench": "socket"},
    4: {"Screw M4*10mm": "_s410", "Nut": "_nut", "Rubber band": "rubber",
        "Board 7": "_b7", "Board 8": "_b8"},
}
BAND_PT = 66   # picture band height above a label
GAP_PT = 4     # gap between picture band and label


def extract_addons():
    crops = {}
    for pageno, wanted in ADDON_LABELS.items():
        print(f"mbot2_addons.pdf page {pageno} (parts list):")
        page = render(ADDONS, pageno)
        lines = text_lines(ADDONS, pageno)
        # group labels into rows to compute cell x-boundaries at midpoints
        rows = {}
        for t, cx, top in lines:
            rows.setdefault(round(top / 20), []).append((t, cx, top))
        for row in rows.values():
            row.sort(key=lambda r: r[1])
            for i, (t, cx, top) in enumerate(row):
                pid = next((v for k, v in wanted.items() if t.startswith(k)), None)
                if not pid:
                    continue
                left = (row[i-1][1] + cx) / 2 if i else max(0, cx - 47)
                right = (cx + row[i+1][1]) / 2 if i + 1 < len(row) else cx + 47
                band_top = max(top - BAND_PT, 42)  # 42pt: below the page heading
                box = (round(left * PT), round(band_top * PT),
                       round(right * PT), round((top - GAP_PT) * PT))
                crops[pid] = trim(page.crop(box))
    for pid, im in crops.items():
        if not pid.startswith("_"):
            save(pid, im)
    save("trackhubs", hstack([crops["_awh"], crops["_aswh"]]))
    save("beamplate", hstack([crops["_sb26"], crops["_p38"]]))
    save("bracket", hstack([crops["_b90"], crops["_bu"]]))
    save("damper", hstack([crops["_msh"], crops["_psh"]]))
    save("collarflange", hstack([crops["_sc"], crops["_fb"]]))
    save("screwsR", hstack([crops["_s410"], crops["_nut"]]))
    save("boards", hstack([crops["_b7"], crops["_b8"]]))

    # assembled Ranger render on the cover (vector -> crop right half, trim);
    # the cover title overlaps the crop's top-left corner - white it out first
    print("mbot2_addons.pdf page 1 (cover render):")
    cover = render(ADDONS, 1)
    arm = cover.crop((round(cover.width * 0.40), 0, cover.width, cover.height))
    from PIL import ImageDraw
    ImageDraw.Draw(arm).rectangle(
        (0, 0, round(arm.width * 0.12), round(arm.height * 0.60)), fill="white")
    save("robot_arm", trim(arm))


if __name__ == "__main__":
    if not (MBOT2.exists() and ADDONS.exists()):
        sys.exit("manuals not found next to curriculum-site/")
    extract_mbot2()
    extract_addons()
    print("done ->", OUT.relative_to(ROOT))
