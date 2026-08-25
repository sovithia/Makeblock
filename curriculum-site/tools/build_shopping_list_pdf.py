# -*- coding: utf-8 -*-
"""Render the classroom shopping list as ../SHOPPING-LIST.pdf.

Unlike tools/build_demo_prep_pdf.py, this holds NO copy of the content: every
row is derived from the `parts:` tags in content/<grade>/steps/*.yaml, the part
names in generator/parts_catalog.py, and the packing lists in
content/boxes.yaml. Re-running it after a content edit is the whole update
process — there is nothing here to keep in sync by hand.

Quantities are the one editorial layer: QTY below is guidance, sized per team of
2-3 students sharing one robot, because the YAML records what a step needs, not
how many of it a room needs.

Usage: .venv/bin/python tools/build_shopping_list_pdf.py [7 8]
"""
import collections
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "generator"))
import parts_catalog as PC          # noqa: E402

GRADE_C = {"7": {"color": "#0e7fc1", "light": "#e3f1fa"},
           "8": {"color": "#8b3fc6", "light": "#f2e8fa"},
           "9": {"color": "#d97706", "light": "#fdf0dd"}}

# Per-item buying guidance. Keyed by catalog id; the YAML knows which steps need
# a thing, not how many of it to own.
QTY = {
    "journal":    ("1 per student", "A5 notebook. Used in every single step."),
    "tape":       ("1 roll per team", "Masking tape — start lines, zones, routes, "
                                      "patrol areas."),
    "boxes":      ("3-4 per team", "Cardboard is fine. Walls, arena, slalom, and "
                                   "the obstacle that sits ON the line."),
    "ruler":      ("1 per team", "Tape measure or metre rule. Commanded-vs-actual "
                                 "measuring."),
    "protractor": ("1 per team", "Turn accuracy. Grade 8 needs it after the "
                                 "rebuild — tracks turn nothing like wheels."),
    "timer":      ("1 per class", "Plus a visible scoreboard for the final scored "
                                  "runs."),
    "patches":    ("2-3 sheets per class", "MATTE red card or paper. Glossy tape "
                                           "reads badly on the colour sensor."),
    "foam":       ("2 per team", "Sized to the gripper. FOAM ONLY — a wooden "
                                 "block plus an over-tight grip strips the servo "
                                 "gears, and they are not in the spare bag."),
    "trays":      ("4 per team", "Grade 8 step 1 tears the mBot2 down into "
                                 "screws / plates / motors / electronics."),
    "craft":      ("1 kit per class", "Large paper and markers — the state "
                                      "diagrams are drawn before any code."),
    "cards":      ("~5 per team", "Index cards: controller mapping card, protocol "
                                  "table, mission rubric."),
    "torch":      ("1 per team", "A phone light works. Only for the light-sensor "
                                 "steps."),
    "router":     ("1 per room", "GRADE 8 HARD DEPENDENCY — speech recognition is "
                                 "a cloud call, so it needs real internet, not "
                                 "just a local network. Test it in the room."),
    "laptop":     ("1 per team", "Laptop with mBlock 5, or an ANDROID tablet in "
                                 "Chrome at ide.mblock.cc. An iPad cannot run it "
                                 "in any browser, and the mBlock mobile apps "
                                 "support only the original mBot, not the mBot2."),
    "tablet":     ("1 per team", "Android + Chrome only — see above."),
    "webcam":     ("1 per team", "Only if you run the older ML sessions."),
    "ramp":       ("1 per class", "Only if you run the older terrain lab."),
    "blindfold":  ("1 per team", ""),
    "phone":      ("1 per team", "Video and angle checks."),
    "colorcards": ("1 set per team", ""),
}


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def collect(grade):
    """{part id: {step numbers}} from a grade's step course."""
    used = collections.defaultdict(set)
    notes = collections.defaultdict(set)
    d = ROOT / "content" / f"grade{grade}" / "steps"
    if not d.is_dir():
        d = ROOT / "content" / f"grade{grade}" / "sessions"
    for f in sorted(d.glob("*.yaml")):
        y = yaml.safe_load(f.read_text(encoding="utf-8"))
        if not isinstance(y, dict):
            continue
        n = y.get("n")
        for blk in (y.get("parts"), (y.get("long") or {}).get("parts")):
            for p in (blk or []):
                if isinstance(p, dict) and p.get("id"):
                    used[p["id"]].add(n)
                    if p.get("note"):
                        notes[p["id"]].add(p["note"])
    return used, notes


def rng(nums):
    """{1,2,3,7} -> '1-3, 7' — a step list a buyer can scan."""
    xs, out, i = sorted(n for n in nums if n is not None), [], 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[j + 1] == xs[j] + 1:
            j += 1
        out.append(str(xs[i]) if j == i else f"{xs[i]}–{xs[j]}")
        i = j + 1
    return ", ".join(out)


ICON_C = {"color": "#0e7fc1", "dark": "#0a5c8c", "light": "#e3f1fa"}


def img(pid):
    """The same artwork the site's "You need" panel uses.

    Real manual photos exist only for kit parts, so classroom items fall back to
    the hand-drawn SVG in parts_catalog — which is what the site shows for them
    too, and a buyer scanning the page wants a picture either way.
    """
    p = ROOT / "site" / "assets" / "parts" / f"{pid}.png"
    if p.exists():
        return f'<img class="ic" src="site/assets/parts/{pid}.png"/>'
    return (f'<svg class="ic" viewBox="0 0 64 44" width="40">'
            f'<g>{PC.ICONS[pid][2](ICON_C)}</g></svg>')


def rows(grades):
    """One row per classroom item, merged across the grades requested."""
    per = {g: collect(g) for g in grades}
    allids = set()
    for used, _ in per.values():
        allids |= {k for k in used if PC.ICONS.get(k, ("", ""))[1] in ("CLASS", "EXTRA")}
    # busiest first — that is the order a buyer cares about
    def weight(pid):
        return -sum(len(per[g][0].get(pid, ())) for g in grades)
    out = []
    for pid in sorted(allids, key=lambda p: (weight(p), PC.ICONS[p][0])):
        name = PC.ICONS[pid][0]
        qty, why = QTY.get(pid, ("as needed", ""))
        cells = []
        for g in grades:
            steps = per[g][0].get(pid, set())
            cells.append(rng(steps) if steps else "—")
        notes = set()
        for g in grades:
            notes |= per[g][1].get(pid, set())
        out.append((pid, name, qty, why, cells, sorted(notes)))
    return out


def build(grades):
    body = []
    hdr = "".join(f'<th class="g g{g}">G{g} steps</th>' for g in grades)
    trs = []
    for pid, name, qty, why, cells, notes in rows(grades):
        note = ("<div class=\"nt\">" + esc(" · ".join(notes)) + "</div>"
                if notes else "")
        tds = "".join(f'<td class="stp">{esc(c)}</td>' for c in cells)
        trs.append(
            f'<tr><td class="bx">☐</td><td class="ic">{img(pid)}</td>'
            f'<td class="nm"><b>{esc(name)}</b>{note}</td>'
            f'<td class="qt">{esc(qty)}</td>'
            f'<td class="wy">{esc(why)}</td>{tds}</tr>')
    body.append(f'<table class="buy"><tr><th></th><th></th><th>Item</th>'
                f'<th>Suggested</th><th>What it is for</th>{hdr}</tr>'
                + "".join(trs) + "</table>")

    boxes = yaml.safe_load((ROOT / "content" / "boxes.yaml").read_text(encoding="utf-8"))
    for key in ("mbot2", "rover"):
        b = boxes[key]
        items = "".join(f'<li>{esc(i["name"])} <span class="q">{esc(i["qty"])}</span></li>'
                        for i in b["items"])
        body.append(f'<div class="box"><h3>{esc(b["title"])}</h3>'
                    f'<ul class="kit">{items}</ul></div>')
    return "\n".join(body)


CSS = """
@page { size: A4; margin: 13mm 12mm 15mm 12mm;
  @bottom-center { content: "Makeblock curriculum \\00b7 classroom shopping list \\00b7 page " counter(page);
    font-size: 7.5pt; color: #94a3b8; font-family: Helvetica; } }
body { font-family: Helvetica, Arial, sans-serif; color: #1e293b; font-size: 9pt; }
h1 { font-size: 19pt; margin: 0 0 1mm 0; }
.sub { color: #475569; font-size: 9.5pt; margin-bottom: 3mm; }
.lead { background: #f8fafc; border-left: 3px solid #0e7fc1; padding: 2.5mm 3mm;
  margin-bottom: 4mm; font-size: 8.8pt; line-height: 1.5; }
.lead b { color: #0f172a; }
h2 { font-size: 12pt; margin: 5mm 0 2mm 0; padding-bottom: 1mm;
  border-bottom: 1.5px solid #cbd5e1; }
table.buy { width: 100%; border-collapse: collapse; }
table.buy th { text-align: left; font-size: 7.4pt; text-transform: uppercase;
  letter-spacing: .06em; color: #64748b; border-bottom: 1px solid #cbd5e1;
  padding: 0 2mm 1mm 0; }
/* a row split across a page break orphans its description from its name, which
   is exactly the column a buyer is reading */
table.buy tr { break-inside: avoid; }
table.buy td { border-bottom: 1px solid #e2e8f0; padding: 1.8mm 2mm 1.8mm 0;
  vertical-align: top; }
td.bx { font-size: 13pt; color: #94a3b8; width: 6mm; }
td.ic { width: 13mm; } img.ic { max-height: 30px; max-width: 12mm; }
.noic { display: inline-block; width: 12mm; }
td.nm { width: 34mm; } td.nm b { font-size: 9.3pt; }
.nt { color: #7c3aed; font-size: 7.4pt; margin-top: 0.6mm; }
td.qt { width: 24mm; font-size: 8.4pt; color: #0f172a; font-weight: bold; }
td.wy { font-size: 8.2pt; color: #475569; line-height: 1.4; }
td.stp { width: 17mm; font-size: 8pt; color: #334155; }
th.g7 { color: #0e7fc1; } th.g8 { color: #8b3fc6; } th.g9 { color: #d97706; }
.box { break-inside: avoid; margin-bottom: 3mm; }
.box h3 { font-size: 9.5pt; margin: 0 0 1.5mm 0; color: #0f172a; }
ul.kit { columns: 3; column-gap: 6mm; margin: 0; padding-left: 4mm;
  font-size: 8pt; color: #334155; }
ul.kit li { margin-bottom: 0.5mm; break-inside: avoid; }
ul.kit .q { color: #94a3b8; }
.warn { background: #fef3c7; border-left: 3px solid #f59e0b; padding: 2.5mm 3mm;
  font-size: 8.5pt; line-height: 1.5; margin: 3mm 0; }
.warn b { color: #92400e; }
"""


def main():
    grades = [a for a in sys.argv[1:] if a.isdigit()] or ["7", "8"]
    gl = " and ".join(f"Grade {g}" for g in grades)
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<style>{CSS}</style></head><body>
<h1>Classroom shopping list</h1>
<div class="sub">{esc(gl)} · mBot2 robotics</div>
<div class="lead">
Everything below is <b>outside the two Makeblock boxes</b> — the kit contents are
listed on the last page so nothing gets bought twice. Quantities assume
<b>one robot per team of 2–3 students</b>; scale by your number of teams.
The step columns show exactly which lessons need each item, so a partial buy can
still be planned around.
</div>
<div class="warn">
<b>Two things that are not optional.</b>
<b>Foam</b>, never wood, for anything the Grade 8 gripper closes on — an
over-tight grip on a hard block strips the servo gears silently, and spares are
not in the box.
<b>Wi-Fi with real internet</b> in the room for Grade 8 steps 16–20 — speech
recognition is a cloud call, so a local-only network will not do. Test it in the
actual room, on the actual network, before those lessons.
</div>
<h2>Buy this</h2>
{build(grades)}
</body></html>"""
    out = ROOT.parent / "SHOPPING-LIST.pdf"
    from weasyprint import HTML
    HTML(string=html, base_url=str(ROOT)).write_pdf(str(out))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
