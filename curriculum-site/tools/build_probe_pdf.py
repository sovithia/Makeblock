# -*- coding: utf-8 -*-
"""Render the .mblock compiler probe as one illustrated PDF: ../MBLOCK-PROBE.pdf.

Why this exists: tools/mblock_compile.py writes .mblock files the mBlock IDE
refuses to open. The eight official Makeblock lesson projects answer most of the
schema questions, but none of them use lists, parameterised custom blocks or
`count with i` — which is most of what Grades 7-8 are built from — and they were
saved by mBlock 5.3 in 2021, not by the version on the bench today.

So: three short scripts, built by hand in the IDE, saved, and diffed against what
the compiler emits for the same source. This sheet is what you build from. The
blocks are drawn by generator/svgblocks.py — the same renderer the site uses — so
the shapes and category colours on paper match the palette on screen.

Usage: .venv/bin/python tools/build_probe_pdf.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "generator"))
sys.path.insert(0, str(ROOT / "tools"))

import re                   # noqa: E402
import blocks as B          # noqa: E402  category colours
import svgblocks as S       # noqa: E402  scratch-blocks SVG renderer

OUT = ROOT.parent / "MBLOCK-PROBE.pdf"

# WeasyPrint rasterises inline SVG with its own renderer, which does not see the
# document's stylesheet — so svgblocks' class-based styling (.bl, .bf, .bm …)
# lands as unstyled black-on-black. The site is a browser and does not have this
# problem. Restate each class as presentation attributes on the way to the PDF.
FONT_STACK = "Helvetica, Arial, sans-serif"
ATTRS = {
    "bl": f'font-family="{FONT_STACK}" font-size="12" font-weight="bold" '
          'fill="#ffffff" dominant-baseline="central"',
    "bft": f'font-family="{FONT_STACK}" font-size="12" font-weight="bold" '
           'fill="#575e75" dominant-baseline="central" text-anchor="middle"',
    "bf": 'fill="#ffffff" stroke="rgba(0,0,0,.15)"',
    "bm": 'fill="rgba(0,0,0,.18)" stroke="none"',
    "bc": 'fill="#ffffff"',
    "bcm": f'font-family="{FONT_STACK}" font-size="11" font-style="italic" '
           'fill="#64748b" dominant-baseline="central"',
    "bsvg": "",
}


def render_fit(source, max_mm=158.0):
    """One script as a self-contained SVG, styled and scaled to fit the card.

    Scaling is done by re-rendering at a smaller mm-per-pixel rather than by CSS:
    the SVG carries a physical size in mm, and WeasyPrint honours it literally, so
    a script wider than the column would otherwise run off the page.
    """
    svg = S.render(source)
    w = float(re.search(r'width="([\d.]+)mm"', svg).group(1))
    if w > max_mm:
        svg = S.render(source, S.MM_PER_PX * max_mm / w)
    return re.sub(r'class="([a-z ]+)"',
                  lambda m: " ".join(ATTRS.get(c, "") for c in m.group(1).split()),
                  svg)

# ---------------------------------------------------------------- the probes
# Written in curriculum block-script syntax, so the renderer resolves every line
# against reference/mblock-palette.json and draws the real block rather than a
# pill. `drive_square 20` is the one deliberate exception — a My Block call has
# no palette entry until the student defines it, which is exactly how the
# curriculum's own scripts render it.
PROBE_A = """when CyberPi starts up
  set  count  to 0
  delete all of  route
  add  north  to  route
  add  east  to  route
  count with  i  from 1 to (length of route) by step 1 repeat
    print (join (item (i) of route)  (count))  and move to a newline
    change  count  by 1
  if  (count) > 1  then
    drive_square  20
  else
    print  empty  and move to a newline
  delete  1  of  route
"""

PROBE_B = """define  drive_square (size)
  repeat 4
    moves forward  (size)  cm  until done
    turns right  90  ° until done
"""

PROBE_C = """when button A pressed
  wait until  (ultrasonic 2 1 distance to an object (cm)) < 15
  if  quad rgb sensor 1 probe  L1  detects  line ?  then
    stop encoder motor  all
  speak  auto  hello
  recognize  English  3  secs
  print (speech recognition result)  and move to a newline
"""

# mBlock palette category names, keyed by generator/blocks.py category key.
PALETTE_NAME = {
    "events": "Events", "control": "Control", "operators": "Operators",
    "variables": "Variables", "myblocks": "My Blocks", "display": "Display",
    "led": "LED", "audio": "Audio", "sensing": "Sensing",
    "motionsense": "Motion Sensing", "lan": "LAN", "ai": "AI",
    "chassis": "Chassis", "extport": "Extension Port",
    "quadrgb": "Quad RGB Sensor", "ultra": "Ultrasonic Sensor 2",
}


def legend(source):
    """The palette drawers this script pulls from, as coloured chips."""
    seen = []
    for line in source.splitlines():
        t = line.strip()
        if not t:
            continue
        cat = B.category(t)
        if cat not in seen:
            seen.append(cat)
    chips = "".join(
        f'<span class="chip" style="background:{B.COLORS[cat]}">'
        f'{PALETTE_NAME.get(cat, cat)}</span>' for cat in seen)
    return f'<div class="legend"><span class="lgl">Palette drawers</span>{chips}</div>'


def script(n, title, source, probes, notes=""):
    return (f'<div class="card">'
            f'<div class="chead"><span class="cnum">{n}</span>{title}</div>'
            f'{legend(source)}'
            f'<div class="scr">{render_fit(source)}</div>'
            f'{notes}'
            f'<div class="probes"><div class="ptitle">What this answers</div>'
            + "".join(f"<div class='pitem'>{p}</div>" for p in probes)
            + "</div></div>")


CSS = """
@page { size: A4; margin: 12mm 12mm 14mm 12mm;
  @bottom-center { content: "mBlock compiler probe · build by hand · page "
    counter(page); font-size: 8pt; color: #94a3b8; font-family: Helvetica; } }
body { font-family: Helvetica, Arial, sans-serif; color: #1e293b; font-size: 9.2pt;
  line-height: 1.45; margin: 0; }
h1 { font-size: 18pt; margin: 0 0 1mm 0; color: #0f172a; }
.sub { color: #64748b; font-size: 9.2pt; margin-bottom: 4mm; }
h3 { font-size: 10.5pt; color: #0f172a; margin: 4mm 0 1.5mm 0; }
.brk { page-break-before: always; }
.card { border: 1.4px solid #e2e8f0; border-radius: 9px; padding: 3mm 3.5mm 2mm 3.5mm;
  margin: 3mm 0; page-break-inside: avoid; }
.chead { font-size: 11pt; font-weight: bold; color: #0f172a; margin-bottom: 2mm; }
.cnum { display: inline-block; width: 6mm; height: 6mm; line-height: 6mm;
  text-align: center; border-radius: 50%; background: #0f172a; color: #fff;
  font-size: 8.5pt; margin-right: 2.5mm; }
.legend { margin-bottom: 2mm; }
.lgl { font-size: 7pt; text-transform: uppercase; letter-spacing: 1.2px;
  color: #94a3b8; margin-right: 2mm; }
.chip { display: inline-block; color: #fff; font-size: 7pt; font-weight: bold;
  border-radius: 3px; padding: 0.5mm 1.6mm; margin-right: 1.2mm; }
.scr { margin: 1mm 0 2mm 0; }
.probes { background: #f8fafc; border-left: 3.5px solid #0e7fc1;
  border-radius: 0 6px 6px 0; padding: 2mm 3mm; margin-top: 2mm; }
.ptitle { font-size: 7pt; text-transform: uppercase; letter-spacing: 1.2px;
  color: #475569; font-weight: bold; margin-bottom: 1mm; }
.pitem { font-size: 8.4pt; margin-bottom: 0.8mm; }
.pitem:before { content: "→ "; color: #0e7fc1; font-weight: bold; }
ol.st { margin: 1.5mm 0 3mm 0; padding-left: 5.5mm; }
ol.st li { margin-bottom: 1.3mm; }
ul.ck { list-style: none; margin: 1mm 0 3mm 0; padding-left: 0; }
ul.ck li { margin-bottom: 1.2mm; }
.warn { background: #fef9ec; border-left: 4px solid #d97706;
  border-radius: 0 8px 8px 0; padding: 2.5mm 3.5mm; margin: 2.5mm 0; font-size: 8.7pt; }
.note { background: #f1f7fc; border-left: 4px solid #0e7fc1;
  border-radius: 0 8px 8px 0; padding: 2.5mm 3.5mm; margin: 2.5mm 0; font-size: 8.7pt; }
table.tb { width: 100%; border-collapse: collapse; margin: 1.5mm 0 3mm 0; }
table.tb td, table.tb th { border-bottom: 1px solid #e2e8f0; padding: 1.4mm 2mm;
  font-size: 8.3pt; text-align: left; vertical-align: top; }
table.tb th { background: #f1f5f9; font-size: 7.4pt; text-transform: uppercase;
  letter-spacing: 1px; color: #475569; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8pt;
  background: #f1f5f9; border-radius: 3px; padding: 0 1mm; }
"""

INTRO = """
<h1>mBlock compiler probe</h1>
<div class="sub">Build these three scripts by hand in mBlock 5, save once, send the
file back. It becomes the ground truth <code>tools/mblock_compile.py</code> is
diffed against — the same three scripts compile from curriculum syntax, so every
difference between the two files is a compiler bug, with nothing else in the way.</div>

<p class="warn"><b>Build them on the CyberPi device, not on a sprite.</b> In the left-hand
panel pick the <b>Devices</b> tab and select <b>CyberPi</b> before dragging anything.
Blocks dropped on the Stage or on Panda land in the wrong target and the probe answers
nothing. Script&nbsp;3 needs two mBuild extensions added first — <b>+ Extension</b> at the
bottom of the block palette → <b>Quad RGB Sensor</b> and <b>Ultrasonic Sensor 2</b>.</p>

<h3>Before you start</h3>
<ol class="st">
<li>New project, device <b>mBot2 / CyberPi</b> added. Nothing needs to be plugged in or
uploaded — the file is what matters, not running it.</li>
<li>Make two variables named <code>count</code> and <code>i</code>, and one <b>list</b>
named <code>route</code> (Variables drawer → <i>Make a Variable</i> / <i>Make a List</i>).
Leave them <b>“For all sprites”</b>.</li>
<li>Make the custom block <code>drive_square</code> with <b>one number input named
<code>size</code></b> (My Blocks → <i>Make a Block</i> → <i>Add an input: number or
text</i>). Leave <i>Run without screen refresh</i> unchecked.</li>
<li>Text typed into a slot must match exactly — <code>north</code>, <code>east</code>,
<code>empty</code>, <code>hello</code>. Numbers stay in number slots.</li>
</ol>
"""

CLOSING = """
<h3>Save and send</h3>
<ol class="st">
<li><b>File → Save to your computer</b>, name it <code>probe.mblock</code>. One file with
all three scripts in it — do not split them.</li>
<li>Tell me the version from <b>Help → About mBlock</b> (e.g. 5.4.0). The 2021 reference
projects were written by 5.3.0 and some of the schema has moved since.</li>
<li>Also useful: what the IDE does when you try to open
<code>curriculum-site/site/assets/projects/G7-A-obeys.mblock</code> — an error dialog, a
silent no-op, or a project that opens but is empty. Those are three different bugs.</li>
</ol>

<h3>What the diff will settle</h3>
<p>Five faults are already confirmed against the official 2021 lesson projects and against the
compiler's own output, before this probe adds anything:</p>
<table class="tb">
<tr><th>#</th><th>Official file</th><th>What the compiler emits</th></tr>
<tr><td>1</td><td>zip carries <code>mscratch.json</code> — the sprite/device registry
(<code>deviceId: "cyberpi"</code>) plus extension versions</td>
<td>only <code>project.json</code> + <code>mblock5</code>. No device registration at all —
the likeliest reason the IDE will not open it.</td></tr>
<tr><td>2</td><td><code>extensions: ["cyberpi.cyberpi", "mbot2.mbot2", "mbuild"]</code> —
dotted pairs, and every mBuild sensor registers as plain <code>mbuild</code></td>
<td><code>["cyberpi", "cyberpi_mbuild_ultrasonic2", "mbot2"]</code> — names that do not
resolve to any installed extension.</td></tr>
<tr><td>3</td><td>variables and lists live on the <b>Stage</b> target</td>
<td>written onto the <code>cyberpi</code> device target.</td></tr>
<tr><td>4</td><td><code>cyberpi_when_launch</code> has <code>"inputs": {}</code>; the button
hat has no <code>image_1</code></td>
<td>emits <code>ICON</code> and <code>image_1</code> as real inputs — the palette lists them
as slots, but they are decorative icons, not sockets.</td></tr>
<tr><td>5</td><td><code>join</code> holds two slots, and a reporter dropped in one is a
nested block</td>
<td>a literal first operand swallows the second:
<code>join ok, (item (i) of commands)</code> compiles to
<code>STRING1: ""</code> and <code>STRING2: "ok, (item (i) of commands)"</code> — the
reporter is flattened into <b>text</b>. Four of these are in G7-C alone
(<code>"walls: (walls)"</code>, <code>"speed: (speed)"</code> …). This one is not a file-format
bug: it would survive the file opening.</td></tr>
</table>
<p class="note">Everything the probe adds is on top of that: lists, custom-block arguments
and <code>count with i</code> appear in <b>none</b> of the eight official projects, and
they are most of what Grades 7-8 are built from.</p>
"""


def html():
    return (f"<html><head><meta charset='utf-8'><style>{CSS}{B.CSS}</style></head>"
            "<body>" + INTRO
            + script(1, "Lists, loop counter, branch, My Block call", PROBE_A, [
                "How a <b>list</b> is declared and on which target — and whether "
                "<code>route</code> lands on the Stage like a variable does.",
                "The real opcode and input shape of <code>count with i</code> "
                "(<code>control_for_new</code> is a guess taken from the palette).",
                "Whether <code>if/else</code> really is one block with "
                "<code>SUBSTACK2</code>, and how the reporter nests inside "
                "<code>join</code> inside <code>print</code>.",
                "How a My Block <b>call</b> passes its argument — the "
                "<code>argumentids</code> mutation the compiler currently invents.",
            ])
            + script(2, "The custom block it calls", PROBE_B, [
                "<code>procedures_prototype</code> with <b>one argument</b> — every "
                "official project defines argument-less blocks only, so the whole "
                "<code>argumentnames</code> / <code>argumentdefaults</code> / "
                "<code>argument_reporter</code> shape is unverified.",
                "Whether <code>warp</code> is <code>\"false\"</code> here — the "
                "compiler hard-codes <code>\"true\"</code>.",
                "How <code>(size)</code> is referenced inside a numeric slot.",
            ], notes='<p class="note" style="margin:1mm 0 0 0">Define it once; the call in '
                     'script&nbsp;1 is the same block.</p>')
            + script(3, "Sensors and speech — the extension registry", PROBE_C, [
                "How <b>this</b> version of mBlock lists mBuild sensors in "
                "<code>extensions</code> — fault&nbsp;2 below, confirmed on 2021 files, "
                "re-checked on yours.",
                "Current opcode suffixes for speech: the palette holds "
                "<code>speak_with_some_language</code>, <code>_2</code> and "
                "<code>_3</code>, and the compiler picks by wording alone.",
                "Menu field casing — official files write <code>\"a\"</code> where the "
                "compiler writes <code>\"A\"</code>.",
                "Whether a boolean sensor block drops straight into "
                "<code>CONDITION</code> the way the compiler assumes.",
            ])
            + CLOSING + "</body></html>")


def main():
    from weasyprint import HTML
    HTML(string=html(), base_url=str(ROOT)).write_pdf(str(OUT))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
