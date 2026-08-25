# -*- coding: utf-8 -*-
"""Visual block-script rendering.

Session YAML carries `code: {lang: blocks, source: |-  ...}` as indented plain
text. This turns that text into a stack of mBlock block images.

Nesting is the awkward part. In mBlock, `forever` / `if` / `repeat` are C-shaped:
they wrap their children rather than sitting above them, and every one of the
course's 46 scripts nests (up to 4 deep). The palette gives a C-block as one
complete empty C, which cannot stretch, so tools/ slices each into
<id>-top / <id>-mid / <id>-bot — header, a 1px spine tile repeated vertically
behind the children, and the closing foot.

Hat blocks (`when …`) are NOT C-shaped: the script hangs below them. The YAML
indents the body under the hat for readability, so shape is decided by
is_wrapper(), never by whether a line happens to have children.

Images in site/assets/blocks/ are OPTIONAL: any line with no image yet falls back
to a coloured pill carrying the same text, so the site renders correctly at every
stage of the photo migration.
"""
import hashlib
import re

import i18n

# A session prints on exactly one A4 page, so the whole stack has to live in
# roughly 56mm of column. 4.8mm is the floor for legibility, not a free choice: in
# an mBlock command bar the label is ~50% of the block height, so 4.8mm puts that
# text at ~7pt, matching the rest of the page. Smaller makes the baked-in text
# unreadable in print, which is the whole reason for using pictures.
ROW_MM = 4.8

# mm per source pixel. Blocks are NOT forced to a common height — a hat block
# really is taller than a plain command bar in mBlock, and flattening that makes
# the stack look wrong — so one factor scales them all and each keeps its true
# relative size.
#
# Calibrated from the palette captures: a plain command bar is 98px tall there.
# Re-shoot the palettes at a different zoom and this is the single number to
# change: measure a plain bar's pixel height and divide ROW_MM by it.
MM_PER_PX = ROW_MM / 98.0

# mBlock indents a C-block's mouth by roughly this fraction of the header height.
_MOUTH_INDENT = 0.20

# mBlock 5 / Scratch 3 palette. Used for the fallback pill and the CSS spine drawn
# for C-blocks that have not been photographed yet.
# mBlock 5 palette as it actually appears with an mBot2 selected (verified from
# the editor, 2026-08-12). This is NOT Scratch's category set: the CyberPi splits
# Looks into LED + Display, Sound into Audio, and Sensing into Sensing + Motion
# Sensing — and the robot itself adds Chassis, Extension Port and one category
# per mBuild sensor. Colours are read off the palette; near-identical purples for
# LED/Display/Audio are deliberate, because mBlock uses near-identical purples.
COLORS = {
    "events":      "#ffbf00",   # yellow
    "control":     "#ffab19",   # orange
    "operators":   "#59c059",   # green
    "variables":   "#ff8c1a",   # orange  (variables AND lists)
    "myblocks":    "#ff6680",   # pink
    "display":     "#8b3fc6",   # purple
    "led":         "#9966ff",   # purple
    "audio":       "#cf63cf",   # magenta
    "sensing":     "#e8623c",   # orange-red
    "motionsense": "#e8623c",   # orange-red
    "lan":         "#3fbfa0",   # teal
    "ai":          "#7cc142",   # light green
    "iot":         "#7cc142",
    "chassis":     "#4c97ff",   # blue   — mBot2 Chassis
    "extport":     "#4c97ff",   # blue   — mBot2 Extension Port
    "quadrgb":     "#3fa373",   # green  — Quad RGB Sensor
    "ultra":       "#3fa373",   # green  — Ultrasonic Sensor 2
    "btctrl":      "#3ba98a",   # teal   — Bluetooth controller
    "comment":     "#94a3b8",
}

# First match wins, so these run most-specific first. Order is load-bearing:
# `play LED animation` must beat `^play` (audio); `set servo`, `set print size`
# and `set LAN channel` must all beat the generic `^set` (variables); `stop all
# sounds` must beat `stop all` (control); and the Bluetooth controller's
# `button 1 pressed` must be told apart from the CyberPi's `button A pressed?`
# — the controller has numbers, arrows and shoulder buttons, the CyberPi has A/B.
_CATS = [
    (r"^#", "comment"),
    (r"^when\b", "events"),
    (r"\bon LAN\b|^LAN broadcast|^set LAN channel|^broadcast\b", "lan"),
    (r"^(connect to Wi-Fi|network connected|disconnect from Wi-Fi|speak\b|recognize\b"
     r"|speech recognition|translate\b)", "ai"),
    (r"^quad rgb sensor\b", "quadrgb"),
    (r"^ultrasonic 2\b", "ultra"),
    # Grades 7-9 quote mBlock's exact labels ("moves forward"); Grades 4-6 are
    # written in plainer wording ("move forward", "stop moving"). Both name the
    # same chassis blocks and both must come out chassis blue, or half the 4-6
    # scripts draw in the My Blocks pink that is the fallback category.
    (r"^(moves\b|turns\b|move forward\b|move backward\b|turn left\b|turn right\b"
     r"|stop moving\b|encoder motor\b|stop encoder motor\b|reset encoder motor\b"
     r"|calibrate\b)", "chassis"),
    (r"^(set servo|increase servo|servo\b|LED strip|set motor|stop motor|motor\b"
     r"|digital \w+|voltage read|analog write|pin\b)", "extport"),
    (r"^(play LED animation|LED\b|turn off LED|increase LED brightness|set brightness"
     r"|roll \d+ LEDs|display \[|set led\b)", "led"),
    # `show label 1 at ...` is matched by its `at`, not by the word `show`, which
    # Variables (`show variable`, `show list`) and Sprites (`show sprite`) also
    # open with. `set brush color` has to be named here or the generic `^set` rule
    # further down paints it Variables orange, and `screen towards` matches nothing
    # at all and falls through to My Blocks pink.
    (r"^(print\b|show\b.*\bat\b|set print size|set brush color|screen towards"
     r"|clear screen|clear data|name chart title|line chart|bar chart|table,)", "display"),
    (r"^(start recording|stop recording|play recording|play note|play sound at|stop all sounds"
     r"|set volume|increase volume|set audio speed|increase audio speed|play\b)", "audio"),
    (r"^(shaking strength|waving |tilted |rotated angle|reset yaw|reset rotated|motion sensor"
     r"|angle speed)", "motionsense"),
    (r"^(forever|repeat\b|repeat until|if\b|else\b|wait\b|count with\b|break$|continue$"
     r"|stop all$|restart CyberPi)", "control"),
    (r"^button\s+(\d|L\d|R\d|Left Thumb|Right Thumb|\+|≡|←|↑|→|↓)|^joystick\s+(RX|RY|LX|LY)\b",
     "btctrl"),
    (r"^(button [AB]\b|joystick\b|loudness|ambient light|timer\(s\)|reset timer|hostname"
     r"|battery)", "sensing"),
    (r"^[-+*/]$|^(pick random|join\b|letter \d|mod\b|round\b|abs\b|read\b)"
     r"|^\(.+\)\s*(and|or|not)\b|^\(.+\)\s*[<>=+*/-]|^not\s+\(", "operators"),
    (r"^(set|change|add|delete|insert|replace|item\b|length of)\b", "variables"),
    (r"^define\b", "myblocks"),
]

# C-shaped blocks: these wrap whatever is indented beneath them.
_WRAPPER = re.compile(r"^(forever|repeat\b|if\b.*\bthen$|else\b.*\bthen$|else$|define\b)")


def category(line):
    s = line.strip()
    for pat, cat in _CATS:
        if re.search(pat, s, re.I):
            return cat
    return "myblocks"          # custom blocks students define themselves


def color(line):
    return COLORS[category(line)]


def is_wrapper(line):
    return bool(_WRAPPER.match(line.strip()))


def block_id(line):
    """Stable filename stem for one block, values included.

    Values are part of the id on purpose: `move forward 40 cm at 40 RPM` and the
    25 cm version are different photographs, because the number is visible inside
    the block and must match the lesson text.
    """
    s = line.strip()
    slug = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)[:56].strip("-") or "block"
    # short digest keeps ids unique when two lines slugify the same, without
    # making the filenames unreadable
    return f"{slug}-{hashlib.sha1(s.encode('utf-8')).hexdigest()[:6]}"


def png_size(path):
    """(w, h) from the PNG IHDR — avoids making Pillow a build dependency."""
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return (int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big"))


def parse(source):
    """Indented text -> nested [(line, [children]), ...] (2 spaces per level)."""
    rows = [((len(l) - len(l.lstrip())) // 2, l.strip())
            for l in source.splitlines() if l.strip()]

    def build(i, depth):
        out = []
        while i < len(rows) and rows[i][0] >= depth:
            d, text = rows[i]
            if d > depth:               # malformed over-indent: treat as this level
                d = depth
            kids, i = build(i + 1, depth + 1)
            out.append((text, kids))
        return out, i

    tree, _ = build(0, 0)
    return tree


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _node(line, kids, have, dims, sc):
    bid = block_id(line)
    col = color(line)
    if line.strip().startswith("#"):
        return f'<div class="bcomment">{_esc(line.strip().lstrip("#").strip())}</div>'

    sliced = f"{bid}-top" in have and f"{bid}-bot" in have

    def img(stem, cls="bimg"):
        h = dims.get(stem, (0, 98))[1] * sc
        return (f'<img class="{cls}" style="height:{h:.2f}mm" '
                f'src="{{BASE}}assets/blocks/{stem}.png" alt="{_esc(line)}">')

    def bar_html():
        if bid in have:
            return img(bid)
        if sliced:
            # a C-block with nothing in it (e.g. an empty forever) — header only
            return img(f"{bid}-top")
        return f'<span class="bpill" style="background:{col}">{_esc(line)}</span>'

    if not kids:
        return f'<div class="brow">{bar_html()}</div>'

    inner = "".join(_node(k, kk, have, dims, sc) for k, kk in kids)

    # A hat block is not C-shaped: the script hangs BELOW it rather than inside a
    # mouth. Branch on the block's real shape, not on whether it has children.
    if not is_wrapper(line):
        return f'<div class="brow">{bar_html()}</div>{inner}'

    if not sliced:
        return (f'<div class="brow">'
                f'<span class="bpill" style="background:{col}">{_esc(line)}</span></div>'
                f'<div class="bwrap" style="border-color:{col}">{inner}</div>'
                f'<div class="bfoot" style="background:{col}"></div>')

    tw, th = dims.get(f"{bid}-top", (100, 60))
    mw, _mh = dims.get(f"{bid}-mid", (tw, 1))
    return (f'<div class="brow">{img(f"{bid}-top")}</div>'
            f'<div class="bwrapimg" style="background-image:'
            f'url({{BASE}}assets/blocks/{bid}-mid.png);'
            f'background-size:{mw * sc:.2f}mm 0.5mm;'
            f'padding-left:{th * sc * _MOUTH_INDENT:.2f}mm">{inner}</div>'
            f'{img(f"{bid}-bot", cls="bimg bfoot-img")}')


def scale_of(dims):
    return MM_PER_PX


def natural_width_mm(source):
    """Width this script wants, in mm. 0 when nothing can measure it."""
    if _svg is None:
        return 0.0
    try:
        return _svg.width_mm(source)
    except Exception:
        return 0.0


def _fully_photographed(source, have):
    """True only if EVERY block in this script has an image.

    A part-photographed script used to mix real captures with coloured pills,
    which reads as two different things stacked together. Now the choice is made
    per script: all photos, or all drawn.
    """
    for bid in used_ids(source):
        if bid in have:
            continue
        if f"{bid}-top" in have and f"{bid}-bot" in have:
            continue
        return False
    return True


def render(source, have=(), base="../", dims=None, prev=None):
    """have = set of image stems present in site/assets/blocks/.

    Three renderings, in order of fidelity: real screenshots when the whole
    script has them, generated scratch-blocks SVG otherwise, and the flat pill
    stack if the palette-backed renderer is unavailable or cannot place a line.
    """
    have = set(have)
    dims = dims or {}
    if have and _fully_photographed(source, have):
        html = "".join(_node(l, k, have, dims, scale_of(dims))
                       for l, k in parse(source))
        return f'<div class="blockstack">{html.replace("{BASE}", base)}</div>'
    if _svg is not None:
        try:
            return f'<div class="blockstack">{_svg.render(source, prev=prev)}</div>'
        except Exception:
            pass          # fall through to pills rather than fail the build
    html = "".join(_node(l, k, have, dims, scale_of(dims)) for l, k in parse(source))
    return f'<div class="blockstack">{html.replace("{BASE}", base)}</div>'


def used_ids(source):
    out = []

    def walk(nodes):
        for line, kids in nodes:
            if not line.strip().startswith("#"):
                out.append(block_id(line))
            walk(kids)

    walk(parse(source))
    return out


CSS = """
.blockstack { margin-bottom: 3mm; }
.brow { line-height: 0; }
/* one uniform scale, set per image in mm — each block keeps its true relative
   size instead of every block being forced to the same height */
.bimg { width: auto; max-width: 100%; display: block; margin-bottom: 0.35mm; }
/* fallback until a block has been photographed — same silhouette and palette
   colour, sized to match a photographed bar so a half-migrated script does not
   look like two different things stacked together */
.bpill { display: inline-block; color: #fff; font-size: 7pt; line-height: 1.25;
  font-weight: bold; border-radius: 4px; padding: 1mm 2.2mm; margin-bottom: 0.35mm;
  font-family: Helvetica, Arial, sans-serif; }
/* un-photographed C-block: children indent, spine drawn in the block's colour */
.bwrap { margin-left: 1.6mm; padding-left: 1.6mm; border-left-width: 1.2mm;
  border-left-style: solid; }
.bfoot { height: 1.2mm; width: 6mm; border-radius: 0 0 2px 2px; margin-bottom: 0.35mm; }
/* photographed C-block: the 1px spine tile repeats down behind the children, so
   the block stretches to whatever height its contents need */
.bwrapimg { background-repeat: repeat-y; background-position: left top; }
.bfoot-img { margin-bottom: 0.35mm; }
.bcomment { font-size: 6.6pt; color: #64748b; font-style: italic; margin: 0.5mm 0; }
"""

# Imported last, and defensively: svgblocks needs COLORS and category() from
# this module, so the pair is only acyclic in this direction. A machine without
# reference/mblock-palette.json still builds the site, with pills.
try:
    import svgblocks as _svg
    CSS += _svg.CSS
except Exception:                    # pragma: no cover - optional dependency
    _svg = None

# ---------------------------------------------------------------- block hints
# mBlock's own category names, as they read in the palette. Deliberately not
# translated, for the same reason block labels are not: a student matching this
# to the sidebar has to read the same string in both places.
CAT_LABEL = {
    "events": "Events", "control": "Control", "operators": "Operators",
    "variables": "Variables", "myblocks": "My Blocks", "display": "Display",
    "led": "LED", "audio": "Audio", "sensing": "Sensing",
    "motionsense": "Motion Sensing", "lan": "LAN", "ai": "AI", "iot": "IoT",
    "chassis": "mBot2 Chassis", "extport": "Extension Port",
    "quadrgb": "Quad RGB Sensor", "ultra": "Ultrasonic Sensor 2",
    "btctrl": "Bluetooth Controller",
}


def _grouped(source, first_seen=None, step_n=None):
    """[(category, [(key, spec, is_new)])] for one step, in palette-category order."""
    import collections
    out = collections.OrderedDict()
    for key, spec in _svg.blocks_used(source):
        # Categorise on the block as it READS, not on the raw template: half the
        # chassis blocks start with a slot (`[DIRECTION] at [POWER] RPM`), so
        # stripping the brackets leaves " at … RPM" and every ^-anchored rule in
        # _CATS misses. blank_node already resolves menus to their default label,
        # which puts "moves forward" back at the front where the rules expect it.
        cat = ("myblocks" if key.startswith("my:")
               else category(_svg.blank_node(spec)["label"]))
        is_new = bool(first_seen and step_n is not None
                      and first_seen.get(key) == step_n)
        out.setdefault(cat, []).append((key, spec, is_new))
    return list(out.items())


def new_blocks(source, first_seen, step_n):
    """The blocks this step meets for the FIRST TIME in the course."""
    return [(k, spec) for _cat, items in _grouped(source, first_seen, step_n)
            for k, spec, is_new in items if is_new]


def palette_frame(source, first_seen=None, step_n=None, notes=None):
    """Every block this step needs, drawn empty, with the new ones explained.

    Empty on purpose: the block as it sits in the sidebar, not somebody else's
    values. Old and new together, because by the middle of a stage most of what a
    step needs is already familiar.

    A block met for the FIRST TIME in the course gets a line to itself with its
    explanation underneath — that is the one the class has to stop and look at.
    Everything already known flows on one strip below them: a reminder of what to
    fetch, not something to read.
    """
    if _svg is None:
        return ""
    rows = []
    for cat, items in _grouped(source, first_seen, step_n):
        fresh = [(k, spec) for k, spec, is_new in items if is_new]
        known = [spec for _k, spec, is_new in items if not is_new]
        body = ""
        for key, spec in fresh:
            note = (notes or {}).get(key, "")
            body += (f'<div class="hnew"><div class="hchip">'
                     f'{_svg.render_blank(spec)}</div>'
                     f'<div class="hnote"><span class="newtag">'
                     f'{i18n.t("blocks_new")}</span>{note}</div></div>')
        if known:
            body += ('<div class="hchips">'
                     + "".join(f'<div class="hchip">{_svg.render_blank(sp)}</div>'
                               for sp in known)
                     + "</div>")
        rows.append(f'<div class="hcat"><div class="hcatname" '
                    f'style="color:{COLORS[cat]}">{CAT_LABEL.get(cat, cat)}</div>'
                    f'{body}</div>')
    return f'<div class="hints">{"".join(rows)}</div>'


# The start gate every driving launch script carries: a message and a hold on
# button A, so an upload cannot drive the robot off the desk. It is scaffolding,
# not a taught idea, and it must not count as a block's first appearance —
# without this, `wait until` would be "new" in Step 6's preamble and no longer
# new in Step 13, which is the lesson that actually teaches it.
PREAMBLE_LINES = ("show label 1  press A to start", "wait until  button  A  pressed?")


def teaching_source(source):
    """The script as the course teaches it: the safety preamble removed."""
    return "\n".join(l for l in (source or "").split("\n")
                      if not any(g in l for g in PREAMBLE_LINES))


def spec_index(source):
    """{opcode key: spec} for every block a step's cumulative code contains."""
    if _svg is None:
        return {}
    return dict(_svg.blocks_used(source))


def phase_frame(source, keys, first_seen=None, step_n=None, notes=None,
                index=None):
    """The blocks one timed phase needs, drawn empty, newest explained.

    The lesson-wide "blocks you will need" frame is gone: a block is shown at
    the minute it is actually picked up, so a teacher reads the phase and the
    parts for that phase in one place. A block met for the FIRST TIME anywhere
    in the course still gets its own line and its explanation underneath; the
    rest sit on one strip as a reminder of what to fetch.

    `keys` are opcodes from the step's own `use:` list, in authored order.
    """
    if _svg is None or not keys:
        return ""
    idx = spec_index(source) if index is None else index
    fresh, known = [], []
    for k in keys:
        spec = idx.get(k)
        if spec is None:          # authoring error; the audit names the step
            continue
        if first_seen and step_n is not None and first_seen.get(k) == step_n:
            fresh.append((k, spec))
        else:
            known.append(spec)
    body = ""
    for key, spec in fresh:
        note = (notes or {}).get(key, "")
        body += (f'<div class="hnew"><div class="hchip">{_svg.render_blank(spec)}</div>'
                 f'<div class="hnote"><span class="newtag">{i18n.t("blocks_new")}</span>'
                 f'{note}</div></div>')
    if known:
        body += ('<div class="hchips">'
                 + "".join(f'<div class="hchip">{_svg.render_blank(sp)}</div>'
                           for sp in known) + "</div>")
    return f'<div class="phblocks">{body}</div>' if body else ""


def block_label(spec):
    """How a block reads in the palette, menus resolved to their defaults."""
    if _svg is None:
        return ""
    try:
        return _svg.blank_node(spec)["label"]
    except Exception:
        return ""


def phase_width_mm(source, keys):
    """Widest block any phase asks for — decides if the flow needs full width."""
    if _svg is None or not keys:
        return 0.0
    idx = spec_index(source)
    try:
        return max((_svg.blank_width_mm(idx[k]) for k in keys if k in idx),
                   default=0.0)
    except Exception:
        return 0.0


def palette_width_mm(source):
    if _svg is None:
        return 0.0
    try:
        return max((_svg.blank_width_mm(spec) for _k, spec in _svg.blocks_used(source)),
                   default=0.0)
    except Exception:
        return 0.0


HINT_CSS = """
/* ---- timed phase cards: minutes, blocks and the result in one place ---- */
.ph { break-inside: avoid; margin-bottom: 2.6mm; padding: 2mm 2.6mm 2mm 2.6mm;
  border: 1px solid #e2e8f0; border-left-width: 2.6px; border-radius: 7px;
  background: #fff; }
.phhead { display: flex; gap: 2.6mm; align-items: baseline; }
.pht { flex: 0 0 auto; min-width: 9mm; font-size: 8.6pt; font-weight: bold;
  color: #64748b; font-variant-numeric: tabular-nums; }
.phx { flex: 1 1 auto; font-size: 8.8pt; line-height: 1.42; }
.ph .phblocks { margin: 1.6mm 0 0 11.6mm; }
.ph .hnew { margin-bottom: 1.4mm; }
.ph .hchips { gap: 1.2mm 2.4mm; }
/* what the class should be able to point at before the next phase starts */
.phexp { margin: 1.6mm 0 0 11.6mm; padding: 1.1mm 2.2mm; border-radius: 5px;
  background: #f0fdf4; border: 0.8px solid #bbf7d0; font-size: 8.1pt;
  line-height: 1.4; color: #14532d; break-inside: avoid; }
.phexp .phk { font-weight: bold; color: #16a34a; margin-right: 1.2mm; }
.hints { margin-bottom: 2mm; }
.hcat { margin-bottom: 2mm; break-inside: avoid; }
.hcatname { font-size: 6.8pt; font-weight: bold; text-transform: uppercase;
  letter-spacing: 0.06em; margin-bottom: 0.8mm; }
.hchips { display: flex; flex-wrap: wrap; gap: 1.2mm 2.4mm; align-items: flex-start; }
.hchip { break-inside: avoid; }
.hchip .bsvg { margin-bottom: 0; }
/* a newly-met block gets a line of its own, its explanation directly under it */
.hnew { break-inside: avoid; margin-bottom: 1.8mm; }
.hnote { font-size: 8pt; line-height: 1.4; color: #334155; margin-top: 0.5mm; }
.newtag { display: inline-block; font-size: 5.6pt; font-weight: bold;
  text-transform: uppercase; letter-spacing: 0.08em; color: #16a34a;
  border: 0.8px solid #86efac; border-radius: 3px; padding: 0 0.8mm;
  margin-right: 1.4mm; vertical-align: 1.5px; }
.bnotes { background: #f8fafc; border-left: 3px solid #cbd5e1; border-radius: 0 6px 6px 0;
  padding: 2mm 3mm; margin: 2mm 0 2mm 0; break-inside: avoid; }
.bnoteshead { font-size: 6.8pt; font-weight: bold; text-transform: uppercase;
  letter-spacing: 0.06em; color: #64748b; margin-bottom: 1mm; }
.bnotes ul { margin: 0; padding-left: 4mm; font-size: 8.2pt; line-height: 1.45; }
.bnotes li { margin-bottom: 0.8mm; }
.bnotes b { color: #0f172a; }
"""

def category_color(label):
    """The mBlock palette colour for a category's display label.

    Takes the label rather than the key so it also works for the `blocks:` lists
    authored by hand on lessons that carry no script.
    """
    for key, name in CAT_LABEL.items():
        if name == label:
            return COLORS.get(key, COLORS["comment"])
    return COLORS["comment"]


def readable_on(hex_color):
    """Black or white text, whichever the palette colour can carry."""
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    # perceived luminance: yellow and orange need dark text, purple needs white
    return "#1e293b" if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else "#ffffff"


def palette_categories(source):
    """Which mBlock palette categories this script needs, in palette order."""
    if _svg is None:
        return []
    order = list(CAT_LABEL)
    seen = {cat for cat, _items in _grouped(source)}
    return [CAT_LABEL[c] for c in order if c in seen]
