#!/usr/bin/env python3
"""One transparent PNG per instruction block, for building lesson handouts.

Writes `block-images/<Category>_<block-name>.png` — the same drawn blocks the
step pages use, one file each, on a transparent background so they drop into
slides or a printed reference sheet. Also writes an index.html contact sheet,
since a couple of hundred files are not browsable by name alone.

    tools/export_block_images.py            the whole classroom palette
    tools/export_block_images.py --used     only the blocks the lessons use
    tools/export_block_images.py --all      add the mBuild add-on modules
    tools/export_block_images.py --scale 4  bigger PNGs (default 3x)

The default set is every drawer a student sees in mBlock with the mBot2/Rover
device and this course's extensions loaded, in the order the toolbox lists them.
`hidden` blocks are left out: they are superseded variants mBlock still opens old
projects with but no longer offers — the LED drawer, for instance, declares 15
blocks and shows 11.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
import tempfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "generator"))
import svgblocks as S                                         # noqa: E402

OUT = ROOT / "block-images"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# The extensions loaded in this classroom. `mbuild` is deliberately absent: its
# 107 blocks drive the separate mBuild modules (LED Matrix, LED Drive, Speaker,
# Motion), which are not in the kit and do not appear in the palette unless
# somebody adds those extensions. --all puts them back.
KIT = {"cyberpi", "mbot2", "mbuild_quad_color_sensor", "cyberpi_mbuild_ultrasonic2",
       "firefly_bluetoothcontroller", "cyberpi_upload_message", "cyberpi_sprite",
       "cyberpi_ai_emotion",
       "control", "operators", "variables", "myblocks", "events"}

# Toolbox order. mBlock lists the device's own drawers first, then the Scratch
# core ones, then whatever extensions are loaded.
CATE_ORDER = ["Display", "Audio", "LED", "Sensing", "Motion Sensing", "AI", "IoT",
              "LAN", "mBot2 Chassis", "mBot2 Extension Port", "Sprites", "Doodle",
              "Events", "Control", "Operators", "Variables", "My Blocks",
              "Quad RGB Sensor", "Ultrasonic Sensor 2", "Bluetooth controller",
              "Upload Mode Broadcast", "Magic emoji"]


def palette_blocks(include_mbuild=False):
    """[(cate, order, opcode, label, spec)] — the drawers, in toolbox order."""
    pal = json.loads((ROOT / "reference" / "mblock-palette.json")
                     .read_text(encoding="utf-8"))
    out = []
    for key, spec in pal.items():
        cate = spec.get("cateName")
        if not cate or spec.get("hidden"):
            continue
        if not include_mbuild and spec["ext"] not in KIT:
            continue
        spec = dict(spec, showDefaults=True)
        if spec.get("cateColor"):
            spec["paletteColor"] = spec["cateColor"]
        try:
            label = S.blank_node(spec)["label"]
        except Exception:                                     # noqa: BLE001
            continue
        if not label:
            continue
        # A block can stand in two drawers at once: the four Wi-Fi blocks head
        # AI as well as IoT, because AI cannot do anything without a network.
        # Draw one PNG per drawer, or the AI sheet opens on `speak` with its
        # first four blocks missing.
        for drawer in [spec, *(spec.get("alsoIn") or [])]:
            here = dict(spec, cate=drawer["cate"], cateName=drawer["cateName"],
                        cateColor=drawer["cateColor"])
            if here["cateColor"]:
                here["paletteColor"] = here["cateColor"]
            out.append((here["cateName"], here.get("order", 0), key, label, here))
    rank = {c: i for i, c in enumerate(CATE_ORDER)}
    out.sort(key=lambda b: (rank.get(b[0], len(rank)), b[0], b[1], b[3]))
    return out


def course_blocks():
    """(opcodes the lessons use, {key: spec} for the lessons' own custom blocks).

    A My Block has no fixed wording — `procedures_call` is the bare slot `[PROC]`
    — so the palette cannot supply them. The ones worth a picture are the ones
    this course defines, which only the lesson sources know about.
    """
    used, custom = set(), {}

    def groups_of(line):
        _inner, groups = S.M.split_holes(line)
        for g in groups:
            yield g
            yield from groups_of(g)

    for grade in (7, 8, 9):
        base = ROOT / "content" / f"grade{grade}"
        for f in sorted([*base.glob("steps/*.yaml"), *base.glob("sessions/*.yaml")]):
            d = yaml.safe_load(f.read_text(encoding="utf-8"))
            code = d.get("code") or {}
            # Grade 9 is authored as `lang: python` — text, not drawn blocks.
            if code.get("lang") != "blocks":
                continue
            src = code.get("source") or ""
            for key, spec in S.blocks_used(src):
                used.add(key)
                if key.startswith("my:"):
                    custom.setdefault(key, spec)
            for line in src.split("\n"):
                for g in groups_of(line.strip()):
                    hit, _hg = S.M.resolve(g)
                    if hit:
                        used.add(hit[0])
                        if hit[0].startswith("my:"):
                            custom.setdefault(hit[0], hit[1])
    return used, custom


# Operators are pure symbols, and stripping punctuation leaves nothing to name
# the file after. Spell them instead.
SYMBOLS = {"+": "plus", "-": "minus", "*": "times", "/": "divided-by",
           "<": "less-than", ">": "greater-than", "=": "equals"}

# mBlock labels `if` and `if / else` identically — the `else` only shows in the
# block's shape — so the wording alone cannot name these two files apart.
SLUG_BY_OPCODE = {"control_if": "if-then", "control_if_else": "if-then-else"}


def slug(label):
    """`moves forward at ( ) RPM` -> `moves-forward-at-rpm`."""
    bare = label.strip()
    if bare in SYMBOLS:
        return SYMBOLS[bare]
    s = re.sub(r"[\[\]()<>?°]", " ", label)
    for sym, word in SYMBOLS.items():
        # only a symbol standing on its own, so `Wi-Fi` keeps its hyphen
        s = re.sub(rf"(?<=\s){re.escape(sym)}(?=\s)", f" {word} ", s)
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")
    return (s[:58] or "block").lower()


def standalone(svg, scale):
    """The page SVG as a file Chrome can screenshot, at `scale` times its size.

    The page stylesheet has to come with it. Without it every input slot renders
    solid black (`.bf` supplies the white) and the labels fall back to a serif
    face wide enough to overflow the block it is sitting in.
    """
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    w, h = (float(m.group(1)), float(m.group(2))) if m else (200.0, 44.0)
    body = re.sub(r"^<svg[^>]*>", "", svg).rsplit("</svg>", 1)[0]
    W, H = round(w * scale), round(h * scale)
    css = S.CSS + f"\nsvg.bsvg{{max-width:none;width:{W}px;height:{H}px;margin:0}}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" class="bsvg" '
            f'width="{W}" height="{H}" viewBox="0 0 {w} {h}">'
            f"<style>{css}</style>{body}</svg>"), W, H


INDEX_CSS = """
body { font: 15px/1.5 "Helvetica Neue", Helvetica, Arial, sans-serif;
       margin: 0; padding: 32px 40px 64px; color: #1e293b; background: #f8fafc; }
h1 { font-size: 24px; margin: 0 0 4px; }
p.sub { color: #64748b; margin: 0 0 8px; max-width: 70ch; }
p.key { color: #64748b; margin: 0 0 28px; font-size: 13px; }
.dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%;
       background: #16a34a; margin-right: 5px; vertical-align: 1px; }
h2 { font-size: 15px; text-transform: uppercase; letter-spacing: .06em;
     margin: 34px 0 12px; padding: 0 0 6px 14px; position: relative;
     border-bottom: 1px solid #e2e8f0; }
h2::before { content: ""; position: absolute; left: 0; top: 2px; bottom: 8px;
             width: 5px; border-radius: 3px; background: var(--c, #94a3b8); }
h2 span { color: #94a3b8; font-weight: 400; letter-spacing: 0; text-transform: none; }
ul { list-style: none; margin: 0; padding: 0;
     display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
     gap: 16px; align-items: start; }
li { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px;
     padding: 14px 16px; }
li.used { border-color: #86efac; box-shadow: 0 0 0 1px #86efac inset; }
/* the chequerboard is the point: it shows the PNG really is transparent */
.img { background-image:
         linear-gradient(45deg, #eef2f7 25%, transparent 25%, transparent 75%, #eef2f7 75%),
         linear-gradient(45deg, #eef2f7 25%, transparent 25%, transparent 75%, #eef2f7 75%);
       background-size: 16px 16px; background-position: 0 0, 8px 8px;
       border-radius: 4px; padding: 8px; }
img { max-width: 100%; height: auto; display: block; }
code { display: block; margin-top: 10px; font-size: 12px; color: #64748b;
       word-break: break-all; }
li.used code::before { content: ""; display: inline-block; width: 9px; height: 9px;
       border-radius: 50%; background: #16a34a; margin-right: 5px; }
"""


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def write_index(sheet, colors, n_used):
    out = ['<!doctype html><meta charset="utf-8">',
           "<title>Block images</title>", f"<style>{INDEX_CSS}</style>",
           "<h1>Block images</h1>",
           f'<p class="sub">{len(sheet)} blocks &middot; every instruction in the '
           "mBlock palette for this classroom&rsquo;s robot, one transparent PNG "
           "each, in the order the toolbox lists them. Drag any of them into a "
           "slide or a worksheet.</p>",
           f'<p class="key"><span class="dot"></span>{n_used} of them are used by '
           "a lesson in Grade 7 or 8.</p>"]
    last = None
    for cate, _order, label, name, used, w in sheet:
        if cate != last:
            if last is not None:
                out.append("</ul>")
            n = sum(1 for r in sheet if r[0] == cate)
            out.append(f'<h2 style="--c:{esc(colors.get(cate, "#94a3b8"))}">'
                       f"{esc(cate)} <span>{n}</span></h2><ul>")
            last = cate
        cls = " class=\"used\"" if used else ""
        out.append(f'<li{cls}><div class="img">'
                   f'<img src="{esc(name)}" alt="{esc(label)}" loading="lazy" '
                   f'style="width:{w}px">'
                   f"</div><code>{esc(name)}</code></li>")
    out.append("</ul>")
    (OUT / "index.html").write_text("\n".join(out), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scale", type=float, default=3.0)
    ap.add_argument("--used", action="store_true",
                    help="only the blocks the lessons use")
    ap.add_argument("--all", action="store_true",
                    help="include the mBuild add-on modules")
    args = ap.parse_args()

    if not pathlib.Path(CHROME).exists():
        sys.exit(f"Chrome not found at {CHROME}")

    blocks = palette_blocks(include_mbuild=args.all)
    used, custom = course_blocks()
    if args.used:
        blocks = [b for b in blocks if b[2] in used]
    for i, (key, spec) in enumerate(sorted(custom.items())):
        try:
            label = S.blank_node(spec)["label"]
        except Exception:                                     # noqa: BLE001
            continue
        blocks.append(("My Blocks", 100 + i, key, label, spec))
    rank = {c: i for i, c in enumerate(CATE_ORDER)}
    blocks.sort(key=lambda b: (rank.get(b[0], len(rank)), b[0], b[1], b[3]))
    pal = json.loads((ROOT / "reference" / "mblock-palette.json")
                     .read_text(encoding="utf-8"))
    colors = {s["cateName"]: s.get("cateColor") for s in pal.values()
              if s.get("cateName") and s.get("cateColor")}

    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()

    made, failed, taken, sheet = 0, [], {}, []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        for cate, order, key, label, spec in blocks:
            try:
                svg, W, H = standalone(S.render_blank(spec), args.scale)
            except Exception as e:                            # noqa: BLE001
                failed.append((key, str(e)[:60]))
                continue
            src = tmp / "b.svg"
            src.write_text(svg, encoding="utf-8")
            stem = SLUG_BY_OPCODE.get(spec.get("opcode"), slug(label))
            name = f"{cate.replace(' ', '-')}_{stem}.png"
            if name in taken and taken[name] != key:
                name = f"{name[:-4]}-{slug(spec.get('opcode', key))[-14:]}.png"
            taken[name] = key
            subprocess.run(
                [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                 "--default-background-color=00000000",
                 f"--window-size={W},{H}",
                 f"--screenshot={OUT / name}", src.as_uri()],
                capture_output=True, check=False)
            if (OUT / name).exists():
                made += 1
                sheet.append((cate, order, label, name, key in used,
                              round(W / args.scale)))
            else:
                failed.append((key, "chrome produced nothing"))

    write_index(sheet, colors, sum(1 for r in sheet if r[4]))
    print(f"wrote {made} block images + index.html to {OUT.relative_to(ROOT.parent)}")
    seen = []
    for cate, *_ in sheet:
        if not seen or seen[-1][0] != cate:
            seen.append([cate, 0])
        seen[-1][1] += 1
    for cate, n in seen:
        print(f"    {cate:24s} {n}")
    for key, why in failed:
        print(f"    ! {key}: {why}")


if __name__ == "__main__":
    main()
