# -*- coding: utf-8 -*-
"""Page rendering: print/theme CSS (VERBATIM from legacy common.py) + HTML templates."""
import scenes
import parts_catalog
import blocks
import i18n
from i18n import t, num

# A4 (210mm) less the 13mm side margins in @page, times the .cols right-hand
# column's 43%. The widest a block script can be and still print at full size
# inside that column.
R_COL_MM = (210 - 13 - 13) * 0.43

# ---- css(c): copied byte-for-byte from curriculum-source-annotated/common.py ----
def css(c):
    """c = grade dict with color/dark/light."""
    # cross-grade pages (landing, demo tour, prep sheet) pass num="" — they belong
    # to no single grade, so the footer drops the grade segment rather than
    # printing a bare "Grade ·"
    grade_seg = f"{t('grade_n', n=num(c['num']))} · " if str(c.get("num", "")) else ""
    return f"""
@page {{ size: A4; margin: 14mm 13mm 16mm 13mm;
  @bottom-center {{ content: "{c.get('program', 'mBot2 Rover Program')} \u00b7 {grade_seg}" counter(page);
    font-size: 8pt; color: #94a3b8; font-family: Helvetica; }} }}
@page cover {{ margin: 0; @bottom-center {{ content: none; }} }}
* {{ box-sizing: border-box; }}
/* margin: 0 added to legacy rule — WeasyPrint's paged UA sheet already yields a
   zero body margin, but Chrome's print engine applies its 8px default, which
   pushes the full-bleed cover onto a blank second page */
body {{ font-family: Helvetica, Arial, sans-serif; color: #1e293b; font-size: 9.2pt; line-height: 1.42; margin: 0; }}
p {{ margin: 0 0 2.2mm 0; }}
.muted {{ color: #64748b; font-size: 8.4pt; }}
.center {{ text-align: center; }}

/* deviation from legacy css(): 296.5mm (not 297mm) + explicit break — Chrome's print
   engine spills a 297mm full-bleed box onto a blank second page by a rounding hair */
.cover {{ page: cover; height: 296.5mm; page-break-after: always; color: #fff; padding: 28mm 20mm; position: relative;
  background: linear-gradient(160deg, #0f172a 0%, {c['dark']} 70%, {c['color']} 130%); }}
.cover .kicker {{ text-transform: uppercase; letter-spacing: 3px; font-size: 10pt; font-weight: bold; color: {c['tint']}; }}
.cover h1 {{ font-size: 27pt; margin: 5mm 0 2mm 0; line-height: 1.1; }}
.cover .sub {{ font-size: 12pt; color: #e2e8f0; }}
.badges {{ margin: 9mm 0; }}
.badge {{ display: inline-block; background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.35);
  border-radius: 10px; padding: 4mm 5.5mm; margin-right: 3.5mm; text-align: center; }}
.badge b {{ display: block; font-size: 15pt; color: {c['tint']}; }}
.badge span {{ font-size: 7.5pt; color: #e2e8f0; text-transform: uppercase; letter-spacing: 1px; }}
.coverbox {{ background: rgba(255,255,255,0.08); border-radius: 12px; padding: 6mm; margin-top: 8mm; }}
.coverbox h3 {{ margin: 0 0 2mm 0; color: {c['tint']}; font-size: 11pt; }}
.coverbox p {{ color: #e2e8f0; font-size: 9.5pt; }}
.coverfoot {{ position: absolute; bottom: 16mm; left: 20mm; right: 20mm; font-size: 8.5pt; color: #cbd5e1;
  border-top: 1px solid rgba(255,255,255,0.25); padding-top: 3.5mm; }}

h2.section {{ font-size: 15pt; color: #0f172a; border-bottom: 3px solid {c['color']}; padding-bottom: 1.5mm; margin: 0 0 4mm 0; }}
.notecard {{ background: #f8fafc; border-left: 4px solid {c['color']}; border-radius: 0 8px 8px 0; padding: 3mm 4mm; margin-bottom: 3mm; font-size: 8.8pt; }}
.warncard {{ background: #fef9ec; border-left: 4px solid #d97706; border-radius: 0 8px 8px 0; padding: 3mm 4mm; margin-bottom: 3mm; font-size: 8.8pt; }}
.objbox {{ background: {c['light']}; border-radius: 10px; padding: 4mm 5mm; margin-bottom: 4mm; }}
.objbox h4 {{ margin: 0 0 2mm 0; font-size: 10.5pt; color: {c['dark']}; }}
.objbox ul {{ margin: 0; padding-left: 5mm; }} .objbox li {{ margin-bottom: 1mm; }}

.sess {{ page-break-before: always; }}
.shead {{ border-radius: 10px; color: #fff; padding: 3.5mm 5mm; margin-bottom: 3mm; }}
.shead .sno {{ font-size: 8pt; text-transform: uppercase; letter-spacing: 2px; opacity: 0.9; }}
.shead h2 {{ margin: 0.5mm 0 0 0; font-size: 15pt; }}
.goal {{ background: {c['light']}; border-radius: 8px; padding: 2.5mm 4mm; margin-bottom: 3mm; font-size: 9.4pt; }}
.goal b {{ color: {c['dark']}; }}

.cols {{ width: 100%; border-collapse: collapse; }}
.cols td {{ vertical-align: top; }}
.cols td.l {{ width: 57%; padding-right: 4.5mm; }}
.cols td.r {{ width: 43%; }}
h4.blk {{ font-size: 9.5pt; text-transform: uppercase; letter-spacing: 1.4px; color: {c['dark']};
  margin: 0 0 1.6mm 0; border-bottom: 1.5px solid {c['color']}; padding-bottom: 0.8mm; }}
.teach p {{ margin-bottom: 2mm; }}
table.flow {{ width: 100%; border-collapse: collapse; margin-bottom: 3mm; }}
table.flow td {{ padding: 1.2mm 1.8mm; border-bottom: 1px solid #e2e8f0; vertical-align: top; font-size: 8.8pt; }}
table.flow td.t {{ width: 9mm; font-weight: bold; color: {c['dark']}; white-space: nowrap; }}
.codebox {{ background: #0f172a; color: #e2e8f0; border-radius: 8px; padding: 3mm 3.5mm; font-family: "DejaVu Sans Mono", monospace;
  font-size: 7.6pt; line-height: 1.5; margin-bottom: 3mm; white-space: pre-wrap; }}
.codebox .cm {{ color: #94a3b8; }}
.codelabel {{ font-size: 7.6pt; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; color: #64748b; margin-bottom: 1mm; }}
.codewide {{ margin: 2mm 0 1mm 0; }}
.fortyline {{ margin: 4mm 0 3mm 0; padding: 2mm 3mm; border: 1.5px dashed {c['color']};
  border-radius: 8px; background: {c['light']}; font-size: 8.4pt; font-weight: bold;
  color: {c['dark']}; }}
/* the official assembly diagrams, straight from the manual */
.buildstrip {{ margin: 0 0 3mm 0; }}
.bsh {{ font-size: 7.6pt; font-weight: bold; text-transform: uppercase;
  letter-spacing: 1px; color: #64748b; margin-bottom: 1.4mm; }}
.bscap {{ font-weight: normal; text-transform: none; letter-spacing: 0;
  color: #94a3b8; }}
.bsgrid {{ display: flex; flex-wrap: wrap; gap: 2.5mm; }}
.bimgcell {{ flex: 1 1 78mm; min-width: 60mm; border: 1px solid #e2e8f0;
  border-radius: 8px; padding: 1.6mm; background: #fff; break-inside: avoid; }}
.bimgcell img {{ display: block; width: 100%; height: auto; }}
.conceptnote {{ background: {c['light']}; border-left: 3px solid {c['color']};
  border-radius: 0 8px 8px 0; padding: 2.4mm 3.2mm; margin: 0 0 2.5mm 0;
  font-size: 8.6pt; line-height: 1.5; break-inside: avoid; }}
.cnhead {{ font-size: 7.2pt; font-weight: bold; text-transform: uppercase;
  letter-spacing: 0.08em; color: {c['dark']}; margin-bottom: 1mm; }}
.tips {{ background: #fef9ec; border-radius: 8px; padding: 2.6mm 3.5mm; font-size: 8.6pt; margin-bottom: 3mm; }}
.tips b {{ color: #9a4f08; }}
.tips ul {{ margin: 1mm 0 0 0; padding-left: 4.5mm; }} .tips li {{ margin-bottom: 0.8mm; }}
.guidebox {{ background: #eef4fb; border-left: 3px solid {c['color']}; border-radius: 0 8px 8px 0;
  padding: 1.8mm 3mm; font-size: 8pt; line-height: 1.25; margin-bottom: 2.4mm; }}
.guidebox b.h {{ font-size: 7.6pt; text-transform: uppercase; letter-spacing: 1px; color: {c['dark']}; }}
.guidebox table {{ border-collapse: collapse; margin-top: 1mm; }}
.guidebox td {{ vertical-align: top; padding: 0.5mm 0; }}
.guidebox td.k {{ font-weight: bold; color: {c['dark']}; padding-right: 3mm; white-space: nowrap; }}

.result {{ border: 2px solid {c['color']}; border-radius: 12px; margin-top: 2mm; padding: 3mm 4mm; background: #ffffff;
  page-break-inside: avoid; }}
.result .rk {{ font-size: 8pt; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; color: {c['dark']}; }}
.result table {{ width: 100%; border-collapse: collapse; }}
.result td {{ vertical-align: middle; }}
.result td.img {{ width: 55%; text-align: center; }}
.result td.crit {{ width: 45%; padding-left: 4mm; }}
.result ul {{ margin: 1mm 0 0 0; padding-left: 0; list-style: none; }}
.result li {{ margin-bottom: 1.2mm; font-size: 8.8pt; padding-left: 5.5mm; text-indent: -5.5mm; }}
.result li::before {{ content: "\\2611  "; color: #16a34a; font-size: 10pt; }}
/* the child-facing half of the result box */
.checks {{ margin-bottom: 2mm; }}
.ckrow {{ display: flex; align-items: flex-start; gap: 2.4mm; margin-bottom: 1.8mm;
  break-inside: avoid; }}
.cktrig {{ flex: 0 0 auto; width: 15mm; border-radius: 7px; color: #fff;
  text-align: center; padding: 1mm 0 0.8mm 0; }}
.ckg {{ display: block; font-size: 13pt; font-weight: bold; line-height: 1.05; }}
.ckk {{ display: block; font-size: 5.2pt; font-weight: bold; letter-spacing: 0.06em; }}
.cksee {{ font-size: 10pt; line-height: 1.35; color: #0f172a; padding-top: 0.6mm; }}
.tcheck {{ border-top: 1px solid #e2e8f0; padding-top: 1.4mm; margin-top: 1mm; }}
.tck {{ font-size: 6.4pt; font-weight: bold; text-transform: uppercase;
  letter-spacing: 0.08em; color: #94a3b8; }}
.tcheck ul {{ margin-top: 0.8mm; }}
.tcheck li {{ font-size: 7.6pt; color: #64748b; }}
.tcheck li::before {{ font-size: 8pt; }}

.mats {{ border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 1.6mm 2mm 1mm 2mm; margin-bottom: 2.6mm; background: #fcfcfd; }}
.mats .mhead {{ font-size: 7.6pt; font-weight: bold; text-transform: uppercase; letter-spacing: 1.6px; color: {c['dark']}; margin: 0.4mm 0 1mm 1mm; }}
.mat {{ display: inline-block; width: 20.5mm; text-align: center; vertical-align: top; margin: 0 0.6mm 1mm 0.6mm; }}
.mat .mlbl {{ font-size: 6.9pt; font-weight: bold; color: #1e293b; line-height: 1.15; margin-top: 0.4mm; }}
.mat .mnote {{ font-size: 6.3pt; color: #64748b; line-height: 1.12; }}
.mat .pill {{ display: inline-block; font-size: 5.6pt; font-weight: bold; color: #fff; border-radius: 6px; padding: 0.25mm 1.5mm; margin-top: 0.6mm; letter-spacing: 0.4px; }}
/* addition to legacy css(): real manual photos in the parts panel, constrained
   to the exact 52x36px footprint of the hand-drawn SVG icons so pagination
   and cell alignment are unchanged */
.mat .mimg {{ height: 36px; }}
.mat .mimg img {{ max-width: 50px; max-height: 36px; }}

.boxcard {{ border: 2px solid; border-radius: 12px; margin-bottom: 4mm; overflow: hidden; }}
.boxhead {{ color: #fff; font-weight: bold; font-size: 10pt; padding: 2mm 4mm; letter-spacing: 1px; }}
.pgrid {{ padding: 2.5mm 3mm; column-count: 3; column-gap: 4mm; }}
.pitem {{ font-size: 8.4pt; padding: 0.9mm 0; border-bottom: 1px solid #f1f5f9; break-inside: avoid; }}
.pitem span {{ color: #64748b; font-size: 7.8pt; }}
.boxnote {{ font-size: 7.8pt; color: #64748b; padding: 1.5mm 4mm 2.5mm 4mm; border-top: 1px solid #e2e8f0; }}

.capstone {{ page-break-before: always; border-radius: 14px; padding: 5mm 6mm; border: 2.5px solid {c['color']}; background: {c['light']}; }}
.chips {{ margin-top: 2mm; }}
.chip {{ display: inline-block; background: #fff; border: 1.2px solid {c['color']}; border-radius: 20px;
  padding: 0.8mm 3mm; font-size: 8pt; font-weight: bold; color: {c['dark']}; margin: 0 1.5mm 1.5mm 0; }}

/* ---- 2-hour version lanes (grades 4-6; rendered only when variant == "long") ---- */
.longband {{ border: 1.8px solid {c['color']}; border-radius: 12px; padding: 2.6mm 3.5mm 1.6mm 3.5mm;
  margin: 1mm 0 2.6mm 0; background: {c['light']}; page-break-inside: avoid; }}
.longband .lk {{ font-size: 8pt; font-weight: bold; text-transform: uppercase; letter-spacing: 2px;
  color: {c['dark']}; margin-bottom: 1.8mm; }}
.lanes {{ width: 100%; border-collapse: collapse; }}
.lanes td {{ vertical-align: top; width: 50%; padding: 0 2.5mm 2mm 0; }}
.lane h5 {{ margin: 0 0 1mm 0; font-size: 8.4pt; text-transform: uppercase; letter-spacing: 1.1px;
  color: {c['dark']}; }}
.lane h5 span {{ float: right; font-weight: normal; color: #64748b; letter-spacing: 0; }}
.lane p {{ font-size: 8.5pt; margin: 0 0 1.4mm 0; }}
.chal {{ margin: 0; padding: 0; list-style: none; }}
.chal li {{ font-size: 8.4pt; margin-bottom: 1.2mm; padding-left: 9mm; text-indent: -9mm; }}
.chal .st {{ color: #d97706; font-weight: bold; letter-spacing: -0.5px; }}
/* Grades 7-9 extend tasks carry a tolerance instead of a star tier. The star
   list's 9mm hanging indent is sized for "★★☆" and splits a wider spec chip
   across lines, so spec lists opt out of it. */
.chal.specs li {{ padding-left: 0; text-indent: 0; margin-bottom: 1.6mm; }}
.chal .spec {{ display: inline-block; background: {c['light']}; color: {c['dark']};
  border: 1px solid {c['color']}; border-radius: 4px; padding: 0.1mm 1.4mm;
  margin-right: 1.2mm; font-size: 7.2pt; font-weight: bold; white-space: nowrap; }}
/* Contingent, not scheduled: dashed border and no time budget, so it reads as
   "only if there is time left" beside the solid-bordered result box below it. */
.stripbox {{ background: #f8fafc; border-left: 4px solid {c['color']}; border-radius: 0 8px 8px 0;
  padding: 2.4mm 3.5mm; margin-bottom: 3mm; font-size: 8.8pt; line-height: 1.55; }}
.stripbox.cp {{ border-left-color: #d97706; background: #fef9ec; }}
.stripbox .proj {{ font-family: "DejaVu Sans Mono", monospace; font-size: 8pt;
  background: {c['light']}; border: 1px solid {c['color']}; border-radius: 4px; padding: 0.2mm 1.4mm; }}
.stripbox .k {{ font-size: 7.4pt; text-transform: uppercase; letter-spacing: 1.4px;
  color: #64748b; margin-right: 1.5mm; }}
.bpill {{ display: inline-block; background: {c['light']}; color: {c['dark']};
  border: 1px solid {c['color']}; border-radius: 4px; padding: 0.1mm 1.4mm;
  margin: 0 1mm 0.6mm 0; font-size: 7.2pt; font-weight: bold; }}
.result li.xtra::before {{ content: "\\2610  "; color: {c['color']}; }}
.result li.xtra {{ color: {c['dark']}; }}
.vtag {{ display: inline-block; border-radius: 20px; padding: 0.6mm 2.6mm; font-size: 7.4pt;
  font-weight: bold; letter-spacing: 0.6px; text-transform: uppercase; }}
""" + blocks.CSS + blocks.HINT_CSS + (KHMER_CSS if i18n.is_khmer() else "")


# ---- Khmer typography --------------------------------------------------------
# Appended to css() only under --locale km. Three problems to solve:
#   1. Helvetica has no Khmer glyphs, so every page needs a Khmer face.
#   2. Khmer stacks subscript consonants (coeng) below the baseline; the legacy
#      line-height of 1.42 clips them, so leading goes up across the board.
#   3. Khmer has no spaces between words and runs longer than English, which
#      threatens the one-session-per-A4-page rule — so sizes come back down
#      slightly to buy back the vertical space the leading costs.
# The two src URLs are a depth trick, not a typo: this CSS is inlined into pages
# at site/km/*.html AND site/km/grade4/*.html, and a relative font URL resolves
# against the page. Browsers try each src in turn and use the first that loads.
KHMER_CSS = """
@font-face {
  font-family: "Khmer OS Battambang";
  src: local("Khmer OS Battambang"),
       url("assets/fonts/KhmerOSBattambang-Regular.ttf") format("truetype"),
       url("../assets/fonts/KhmerOSBattambang-Regular.ttf") format("truetype");
  font-weight: normal; font-style: normal; font-display: swap;
}
body, .chrome, .buildson {
  font-family: "Khmer OS Battambang", "Khmer MN", "Khmer Sangam MN", Helvetica, Arial, sans-serif;
  line-height: 1.62;
}
/* headings carry coeng too, and were tuned tight for Latin caps */
.cover h1 { line-height: 1.35; font-size: 24pt; }
.shead h2 { font-size: 13.5pt; line-height: 1.4; }
h2.section { line-height: 1.4; }
/* uppercase/letter-spacing are meaningless in Khmer and actively break clusters
   by pulling diacritics away from their base consonant */
.shead .sno, h4.blk, .codelabel, .guidebox b.h, .result .rk, .mats .mhead, .badge span,
.cover .kicker, .vtag {
  text-transform: none; letter-spacing: 0;
}
/* buy back the vertical space the extra leading costs, so a session still fits
   one A4 page — measured against the English layout, not guessed */
body { font-size: 8.8pt; }
.teach p, table.flow td, .tips, .result li, .lane p { font-size: 8.3pt; }
.goal { font-size: 8.9pt; }
.guidebox { font-size: 7.6pt; line-height: 1.5; }
.chal li { font-size: 8pt; }
/* the code box stays Latin monospace — mBlock block names are not translated */
.codebox { font-family: "DejaVu Sans Mono", monospace; line-height: 1.45; }
"""

# ---- helpers ----------------------------------------------------------------

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def grade_c(grade):
    """Rebuild the legacy `C` color/meta dict from grade.yaml data."""
    c = {"num": grade["num"], "theme": grade["theme"], "form": grade["form"],
         "codemode": grade["codemode"], "capstone": grade["capstone"],
         "program": grade.get("program", "mBot2 Rover Program"),
         "units": [(u["name"], u["sessions"], u["color"]) for u in grade["units"]]}
    c.update(grade["colors"])
    return c


def unit_of_session(c, n):
    i = 0
    for name, count, color in c["units"]:
        i += count
        if n <= i:
            return name, color
    return c["units"][-1][0], c["units"][-1][2]


# ---- session page (ported from common.session_page, YAML-shaped input) ------

STARS = {1: "★☆☆", 2: "★★☆", 3: "★★★"}


def is_secondary_long(s):
    """True when a session's `long:` block uses the Grades 7-9 lane set.

    Detected from the content shape rather than the grade number, so a grade can
    be moved between bands without touching the renderer.
    """
    L = s.get("long") or {}
    return any(k in L for k in ("recap", "extend", "log", "review"))


def long_band_secondary(c, s):
    """The Grades 7-9 second hour: recap/debug, extend-to-spec, log, design review.

    Deliberately not the 4-6 lane set. Extend tasks carry an engineering tolerance
    instead of star tiers — at 12-15 the target is a spec you either met or did
    not, and the log/review pair is where the evidence gets argued.
    """
    L = s.get("long") or {}
    cells = []
    if L.get("recap"):
        r = L["recap"]
        cells.append(f'<div class="lane"><h5>{t("lane_recap")} <span>{r["time"]}</span></h5>'
                     f'<p>{r["text"]}</p></div>')
    if L.get("extend"):
        lis = "".join(
            f'<li><span class="spec">{x["spec"]}</span> {x["text"]}</li>'
            for x in L["extend"])
        cells.append(f'<div class="lane"><h5>{t("lane_extend")} <span>25′</span></h5>'
                     f'<ul class="chal specs">{lis}</ul></div>')
    if L.get("log"):
        g = L["log"]
        cells.append(f'<div class="lane"><h5>{t("lane_log")} <span>{g["time"]}</span></h5>'
                     f'<p>{g["text"]}</p></div>')
    if L.get("review"):
        v = L["review"]
        cells.append(f'<div class="lane"><h5>{t("lane_review")} <span>{v["time"]}</span></h5>'
                     f'<p>{v["text"]}</p></div>')
    rows = ""
    for i in range(0, len(cells), 2):
        pair = cells[i:i + 2]
        tds = "".join(f"<td>{x}</td>" for x in pair)
        if len(pair) == 1:
            tds += "<td></td>"
        rows += f"<tr>{tds}</tr>"
    return (f'<div class="longband"><div class="lk">{t("band_lead_sec")}</div>'
            f'<table class="lanes">{rows}</table></div>')


def long_band(c, s):
    """The four 2-hour-only lanes. Returns "" when the session has no `long:` block."""
    L = s.get("long")
    if not L:
        return ""
    if is_secondary_long(s):
        return long_band_secondary(c, s)
    cells = []
    if L.get("warmup"):
        w = L["warmup"]
        cells.append(f'<div class="lane"><h5>{t("lane_warmup")} <span>{w["time"]}</span></h5>'
                     f'<p>{w["text"]}</p></div>')
    if L.get("challenges"):
        lis = "".join(f'<li><span class="st">{STARS[ch["stars"]]}</span> {ch["text"]}</li>'
                      for ch in L["challenges"])
        cells.append(f'<div class="lane"><h5>{t("lane_arena")} <span>25′</span></h5>'
                     f'<ul class="chal">{lis}</ul></div>')
    if L.get("maker"):
        m = L["maker"]
        cells.append(f'<div class="lane"><h5>{t("lane_maker")} <span>{m["time"]}</span></h5>'
                     f'<p>{m["text"]}</p></div>')
    if L.get("share"):
        sh = L["share"]
        cells.append(f'<div class="lane"><h5>{t("lane_share")} <span>{sh["time"]}</span></h5>'
                     f'<p>{sh["text"]}</p></div>')
    rows = ""
    for i in range(0, len(cells), 2):
        pair = cells[i:i + 2]
        tds = "".join(f"<td>{x}</td>" for x in pair)
        if len(pair) == 1:
            tds += "<td></td>"
        rows += f"<tr>{tds}</tr>"
    return (f'<div class="longband"><div class="lk">{t("band_lead")}</div>'
            f'<table class="lanes">{rows}</table></div>')


# ---- "do this → see this": the expected result, as cause and effect ----------
# A checklist written for a teacher ("the team can explain why …") tells a child
# nothing about whether it worked. These rows say what to press and what should
# happen, in the plainest words the behaviour allows, and colour the trigger the
# same yellow the event blocks are drawn in, so the page and the palette agree.
TRIGGERS = {
    "on":    ("⏻",  "POWER ON",  "#64748b"),
    "A":     ("A",  "BUTTON",    "#ffbf00"),
    "B":     ("B",  "BUTTON",    "#ffbf00"),
    "up":    ("↑",  "JOYSTICK",  "#ffbf00"),
    "down":  ("↓",  "JOYSTICK",  "#ffbf00"),
    "left":  ("←",  "JOYSTICK",  "#ffbf00"),
    "right": ("→",  "JOYSTICK",  "#ffbf00"),
    "mid":   ("●",  "PUSH IN",   "#ffbf00"),
    "hear":  ("((·))", "MESSAGE", "#3fbfa0"),
    "light": ("☀",  "LIGHT",     "#e8623c"),
    "see":   ("👁", "WATCH FOR", "#94a3b8"),
}


def check_rows(s):
    """The do/see rows for one step, or "" when the step declares none."""
    rows = s.get("check") or []
    out = []
    for r in rows:
        glyph, kind, col = TRIGGERS.get(r.get("do", "see"), TRIGGERS["see"])
        out.append(
            f'<div class="ckrow"><div class="cktrig" style="background:{col}">'
            f'<span class="ckg">{glyph}</span>'
            f'<span class="ckk">{kind}</span></div>'
            f'<div class="cksee">{esc(r.get("see", ""))}</div></div>')
    return f'<div class="checks">{"".join(out)}</div>' if out else ""


def build_strip(s, img_base):
    """The manual's own diagrams for a build step.

    A build lesson IS its pictures: retyping an exploded diagram as prose would be
    both worse and pointless when the official one exists. `build_images:` lists
    asset stems produced by tools/extract_build_images.py.
    """
    imgs = s.get("build_images") or []
    if not imgs:
        return ""
    # A stem means PNG (the vector guides); an explicit filename is used as given,
    # which is how the photographed Rover booklet ships its pages as JPEG.
    cells = "".join(
        f'<div class="bimgcell">'
        f'<img src="{img_base}assets/build/{i if "." in i else i + ".png"}" alt="">'
        f'</div>' for i in imgs)
    cap = s.get("build_caption", "")
    return (f'<div class="buildstrip">'
            f'<div class="bsh">{t("build_diagrams")}'
            + (f' <span class="bscap">{esc(cap)}</span>' if cap else "")
            + f'</div><div class="bsgrid">{cells}</div></div>')


def session_page(c, s, img_available=None, img_base="../", show_buildson=False, step=None,
                 variant="short", block_imgs=None, block_dims=None, two_hour=None,
                 prev_code=None, first_seen=None, block_notes=None,
                 concept_note=None):
    unit_name, unit_color = unit_of_session(c, s["n"])
    # Grades 4-6 get the long treatment via a second variant; Grades 7-9 have a
    # single 2-hour timing, so the caller passes two_hour explicitly instead.
    single_timing_2h = two_hour is not None
    is_long = two_hour if single_timing_2h else (variant == "long")
    buildson_html = ""
    nextlesson_html = ""
    if step and step.get("next_href"):
        nextlesson_html = (
            f'<div class="nextlesson"><span class="nlk">{t("next_lesson")}</span>'
            f'<a href="{step["next_href"]}">{esc(step["next_label"])} &nbsp;→</a></div>')
    if show_buildson and (s.get("builds_on") or s.get("feeds")):
        bits = " · ".join(f"<b>{b}</b>" for b in s.get("builds_on", []))
        feeds = f' &nbsp;→&nbsp; {t("feeds")} <b>{s["feeds"]}</b>' if s.get("feeds") else ""
        lead = t("builds_on") if bits else "↪"
        buildson_html = f'<div class="buildson">{lead}{bits}{feeds}</div>'
    code_html = code_wide = ""
    if s.get("code"):
        lang, code = s["code"]["lang"], s["code"]["source"]
        label = {"blocks": t("code_blocks"), "python": t("code_python")}[lang]
        wide = False
        if lang == "blocks" and step and step.get("kind"):
            # A step page gives the GOAL and the blocks, not the finished script.
            # Handing over the arrangement is handing over the thinking; the
            # answer appears only after the lesson, in its teacher-solution
            # section; the student-facing flow still does not reveal it.
            # The lesson-wide "blocks you will need" frame is gone: every block
            # is now drawn at the minute the class actually picks it up, inside
            # the timed flow. What stays here is the idea before the parts —
            # what a function IS, before a list of functions — on the step that
            # introduces the concept.
            label = ""
            body = (f'<div class="conceptnote"><div class="cnhead">'
                    f'{esc(s.get("concept", ""))}</div>{concept_note}</div>'
                    if concept_note else "")
        elif lang == "blocks":
            # Grade 9 is still a session course with no per-step answer file, so
            # its script stays on the page.
            body = blocks.render(code, have=block_imgs or (), base=img_base,
                                 dims=block_dims, prev=prev_code)
            # Blocks are drawn at a fixed physical size and scaled down to fit
            # their container, labels and all. The right column is 43% of a
            # 184mm text block, so a script wider than that would be shrunk
            # until its labels stopped being readable — those get their own
            # full-width band under the two columns instead.
            wide = blocks.natural_width_mm(code) > R_COL_MM
        else:
            body = f'<div class="codebox">{esc(code)}</div>'
        html = (f'<div class="codelabel">{label}</div>{body}') if label else body
        if wide:
            code_wide = f'<div class="codewide">{html}</div>'
        else:
            code_html = html
    guide_html = ""
    if s.get("guide"):
        rows = "".join(f'<tr><td class="k">{g["label"]}</td><td>{g["value"]}</td></tr>'
                       for g in s["guide"])
        guide_html = (f'<div class="guidebox"><b class="h">{t("quick_start")}</b>'
                      f'<table>{rows}</table></div>')
    tips_html = ""
    if s.get("tips"):
        lis = "".join(f"<li>{x}</li>" for x in s["tips"])
        tips_html = f'<div class="tips"><b>{t("watch_out")}</b><ul>{lis}</ul></div>'
    # --- the timed flow -------------------------------------------------
    # Step courses draw one card per phase: the minutes, what to do, the blocks
    # that phase picks up, and the result the class should be able to point at
    # before the next phase starts. Grade 9 is still a session course whose page
    # carries the finished script, so its flow stays the compact table.
    if step:
        # Every step-course lesson gets cards, whether or not it has a script:
        # the build days, the checkpoints and the design days carry no blocks
        # but still owe the class a result it can point at.
        src = s["code"]["source"] if s.get("code", {}).get("lang") == "blocks" else ""
        index = blocks.spec_index(src) if src else {}
        cards = []
        for st in s["steps"]:
            bl = blocks.phase_frame(src, st.get("use") or [], first_seen,
                                    s.get("n"), block_notes, index=index)
            exp = (f'<div class="phexp"><span class="phk">\u2713</span>'
                   f'{st["expect"]}</div>') if st.get("expect") else ""
            cards.append(f'<div class="ph" style="border-left-color:{c["color"]}">'
                         f'<div class="phhead"><span class="pht">{st["time"]}</span>'
                         f'<span class="phx">{st["text"]}</span></div>'
                         f'{bl}{exp}</div>')
        flow = "".join(cards)
    else:
        flow = ('<table class="flow">' + "".join(
            f'<tr><td class="t">{st["time"]}</td><td>{st["text"]}</td></tr>'
            for st in s["steps"]) + "</table>")
    teach = "".join(f"<p>{p}</p>" for p in s["teach"])
    svg = scenes.SCENES[s["result"]["scene"]](c, **s["result"].get("params", {}))
    L = s.get("long") or {}
    crit = "".join(f"<li>{x}</li>" for x in s["success"])
    checks = check_rows(s)
    buildstrip = build_strip(s, img_base)
    tcheck_label = t("teacher_check")
    if is_long:
        crit += "".join(f'<li class="xtra">{x}</li>' for x in L.get("success", []))
    parts = [(p["id"], p.get("note")) for p in s.get("parts", [])]
    if is_long:
        have = {p[0] for p in parts}
        parts += [(p["id"], p.get("note")) for p in L.get("parts", [])
                  if p["id"] not in have]

    if step:
        # A step course has no 1-hour/2-hour split and no 45-minute core: the
        # phase times below simply sum to the lesson's declared hours, so the
        # heading says what the flow is rather than quoting a length that is
        # only true of the Grade 4-6 session format.
        goal_label = t("goal_two_hours") if float(s.get("hours") or 0) >= 2 \
            else t("goal_hour")
        flow_label = t("flow_step")
        goal_text, tag = s["goal"], ""
    elif is_long:
        goal_label, flow_label = t("goal_two_hours"), t("flow_long")
        goal_text = L.get("goal") or s["goal"]
        # the "2-hour version" badge only means something when a 1-hour version of
        # the same page exists; a single-timing 2-hour grade has nothing to contrast
        tag = "" if single_timing_2h else (
            f'<span class="vtag" style="background:{c["dark"]};color:#fff">'
            f'{t("tag_two_hour")}</span>')
    else:
        goal_label, flow_label = t("goal_hour"), t("flow_short")
        goal_text = s["goal"]
        tag = ""
    band = long_band(c, s) if is_long else ""
    # --- step mode: "STEP 7 · ~13 h in · The robot decides" replaces "SESSION 7 / 20".
    # A step course has no fixed length, so there is no "/ 20" to print; what a
    # teacher needs instead is where they are in the course's hours.
    strip = ""
    if step:
        kind = step.get("kind", "step")
        label = t("checkpoint_n", n=num(step["cp_no"])) if kind == "checkpoint" \
            else t("step_n", n=num(s["n"]))
        head_kicker = (f'{label} &nbsp;·&nbsp; {t("hours_in", h=step["hours_in"])}'
                       f' &nbsp;·&nbsp; {esc(step["stage_title"])}')
        bits = []
        # The FILE that holds the build at this point, not the stage key. The
        # stage key (`G7-A-obeys`) names nothing on disk since the projects went
        # per-step, so printing it sent anyone who looked for it nowhere.
        if step.get("step_file"):
            # The name a student saves their own work under, so it is printed
            # bare: mBlock adds the .mblock extension itself when saving, and
            # a name shown with one invites it being typed twice. The answer
            # answer file is linked only from the solution section below — the
            # student-facing lesson header should not reveal it.
            bits.append(f'<span class="k">{t("project")}</span> '
                        f'<code class="proj">{esc(step["step_file"])}</code>')
        if s.get("concept"):
            bits.append(f'<span class="k">{t("concept")}</span> <b>{esc(s["concept"])}</b>')
        if s.get("build"):
            bits.append(f'<span class="k">{t("you_build")}</span> {esc(s["build"])}')
        # Derived from the script, not from the YAML. The `blocks:` list was
        # hand-written when each step held a small standalone program; once the
        # steps became cumulative it went stale on 27 of 32 steps, both missing
        # categories the script needs and naming ones it never touches. It is
        # still honoured for steps that carry no block script.
        cats = blocks.palette_categories(s["code"]["source"]) \
            if (s.get("code") or {}).get("lang") == "blocks" else s.get("blocks")
        if cats:
            # Each chip carries its real mBlock palette colour, so the strip
            # reads like the palette the class is about to open rather than a
            # row of identical labels.
            pills = "".join(
                f'<span class="bpill" style="background:{blocks.category_color(b)};'
                f'border-color:{blocks.category_color(b)};'
                f'color:{blocks.readable_on(blocks.category_color(b))}">{esc(b)}</span>'
                for b in cats)
            bits.append(f'<span class="k">{t("palette")}</span> {pills}')
        cls = "stripbox cp" if kind == "checkpoint" else "stripbox"
        strip = f'<div class="{cls}">' + '<br/>'.join(bits) + '</div>'
    else:
        head_kicker = f'{t("session_n_of", n=num(s["n"]))} &nbsp;·&nbsp; {unit_name}'
    two_col = f"""<table class="cols"><tr>
    <td class="l">
      <h4 class="blk">{t("teach_concept")}</h4>
      <div class="teach">{teach}</div>
    </td>
    <td class="r">
      {guide_html}
      {code_html}
      {tips_html}
    </td>
  </tr></table>"""
    return f"""
<div class="sess">
  <div class="shead" style="background: linear-gradient(110deg, {c['dark']}, {unit_color})">
    <div class="sno">{head_kicker}</div>
    <h2>{s['title']}</h2>
  </div>
  <div class="goal"><b>{goal_label}</b> {goal_text} {tag}</div>
  {strip}
  {buildson_html}
  {parts_catalog.panel(c, parts, img_available, img_base)}
  {buildstrip}
  {two_col}
  <h4 class="blk">{flow_label}</h4>
  {flow}
  {code_wide}
  {band}
  <div class="result">
    <span class="rk">{t("expected_result")}</span>
    <table><tr>
      <td class="img">{svg}</td>
      <td class="crit">{checks}<div class="tcheck"><span class="tck">{tcheck_label}</span>
        <ul>{crit}</ul></div></td>
    </tr></table>
  </div>
  {nextlesson_html}\n</div>"""


# ---- intro pages (ported from build_all.py, YAML-shaped input) ---------------

def unit_strip(c):
    W, X0, bh = 600, 20, 34
    parts = [f'<svg viewBox="0 0 660 100" width="620"><g font-family="{i18n.svg_font()}">']
    s = 0
    for name, count, color in c["units"]:
        x = X0 + s / 20 * W
        w = count / 20 * W
        parts.append(f'<rect x="{x:.0f}" y="34" width="{w-3:.0f}" height="{bh}" fill="{color}" rx="5"/>')
        for i in range(count):
            sx = x + (i + 0.5) / count * (w - 3)
            parts.append(f'<text x="{sx:.0f}" y="55" font-size="10" font-weight="bold" fill="#fff" text-anchor="middle">{s+i+1}</text>')
        cx = x + (w - 3) / 2
        parts.append(f'<text x="{cx:.0f}" y="{24 if s % 2 == 0 else 86}" font-size="9" font-weight="bold" fill="{color}" text-anchor="middle">{name}</text>')
        s += count
    parts.append('</g></svg>')
    return "".join(parts)


def rhythm(c, variant="short", secondary=False):
    if secondary:
        # Grades 7-9 two-hour shape: 45' core kept intact, the rest is debug,
        # extend-to-spec, log and review
        total = 120
        segs = [(0,5,c["color"],t("r_setup")),(5,15,c["dark"],t("r_recap_svg")),
                (15,60,"#16a34a",t("r_teach_core")),(60,65,"#94a3b8",t("r_break")),
                (65,90,"#0891b2",t("r_extend_svg")),(90,100,"#7c3aed",t("r_log_svg")),
                (100,115,"#d97706",t("r_review_svg")),(115,120,"#64748b",t("r_reset"))]
        ticks = (0,15,60,65,90,100,120)
        inside_min, stagger = 95, True
    elif variant == "long":
        total = 120
        segs = [(0,5,c["color"],t("r_setup")),(5,15,c["dark"],t("r_warmup")),
                (15,60,"#16a34a",t("r_teach_core")),(60,65,"#94a3b8",t("r_break")),
                (65,90,"#0891b2",t("r_arena")),(90,105,"#7c3aed",t("r_maker")),
                (105,115,"#d97706",t("r_share_svg")),(115,120,"#64748b",t("r_reset"))]
        ticks = (0,15,60,65,90,105,120)
        # 8 segments in the same width: label inside only when it really fits, and
        # stagger the outside labels over two rows so they cannot collide
        inside_min, stagger = 95, True
    else:
        total = 60
        segs = [(0,5,c["color"],t("r_setup")),(5,10,c["dark"],t("r_briefing")),(10,48,"#16a34a",t("r_core")),
                (48,55,"#d97706",t("r_notes")),(55,60,"#64748b",t("r_reset"))]
        ticks = (0,5,10,48,55,60)
        # legacy geometry — grades 7-9 print pages must stay pixel-identical
        inside_min, stagger = 70, False
    W, X0 = 600, 30
    parts = [f'<svg viewBox="0 0 660 100" width="620"><g font-family="{i18n.svg_font()}">']
    flip = 0
    for a,b,col,label in segs:
        x = X0 + a/total*W; w = (b-a)/total*W
        parts.append(f'<rect x="{x:.0f}" y="30" width="{w:.0f}" height="34" fill="{col}" rx="4"/>')
        cx = x + w/2
        if w > inside_min:
            parts.append(f'<text x="{cx:.0f}" y="51" font-size="11" font-weight="bold" fill="#fff" text-anchor="middle">{label}</text>')
        else:
            y = 82 if (not stagger or flip % 2 == 0) else 94
            flip += 1
            parts.append(f'<text x="{cx:.0f}" y="{y}" font-size="9" font-weight="bold" fill="{col}" text-anchor="middle">{label}</text>')
    for m in ticks:
        x = X0 + m/total*W
        parts.append(f'<line x1="{x:.0f}" y1="26" x2="{x:.0f}" y2="68" stroke="#334155" stroke-width="1"/>'
                     f'<text x="{x:.0f}" y="20" font-size="9" fill="#334155" text-anchor="middle">{m}′</text>')
    parts.append('</g></svg>')
    return "".join(parts)


def box_table(box):
    rows = "".join(
        f'<div class="pitem"><b>{it["name"]}</b>{(" <span>" + it["qty"] + "</span>") if it.get("qty") else ""}</div>'
        for it in box["items"])
    return (f'<div class="boxcard" style="border-color:{box["color"]}">'
            f'<div class="boxhead" style="background:{box["color"]}">{box["title"]}</div>'
            f'<div class="pgrid">{rows}</div>'
            f'<div class="boxnote">{box["note"]}</div></div>')


MATERIALS_CSS = """
<style>
.mtot { color: #475569; font-size: 9pt; margin-bottom: 5mm; }
/* groups may split across pages — forcing a 15-row group to stay whole leaves a
   near-empty page before it. Keep the heading attached to its first rows and
   never split an individual item instead. */
.mgrp { margin-bottom: 7mm; }
.mgrp h3 { margin: 0 0 0.6mm 0; font-size: 12pt;
  page-break-after: avoid; break-after: avoid; }
.mgrp .sub { color: #64748b; font-size: 8.6pt; margin: 0 0 3mm 0;
  page-break-after: avoid; break-after: avoid; }
table.mtab tr, table.sess tr { page-break-inside: avoid; break-inside: avoid; }
table.mtab { width: 100%; border-collapse: collapse; }
table.mtab td { border-bottom: 1px solid #eef2f7; padding: 1.6mm 2mm; vertical-align: middle; }
table.mtab td.ic { width: 16mm; text-align: center; }
table.mtab td.ic img { max-width: 50px; max-height: 34px; }
table.mtab td.nm { font-weight: bold; }
table.mtab td.nm .nt { display: block; font-weight: normal; color: #64748b; font-size: 8.2pt; }
table.mtab td.nm .pg { display: block; font-weight: normal; color: #475569;
  font-size: 8.2pt; line-height: 1.42; margin-top: 1mm; padding-left: 2.4mm;
  border-left: 2px solid #e2e8f0; }
table.mtab td.us { width: 46mm; color: #475569; font-size: 8.4pt; }
.lo { display: inline-block; background: #fde9c8; color: #92510a; border-radius: 5px;
  padding: 0.2mm 1.6mm; font-size: 7.4pt; font-weight: bold; margin-left: 1.5mm; }
table.kits { border-collapse: collapse; margin: 2mm 0 0 0; }
table.kits td, table.kits th { border: 1px solid #e2e8f0; padding: 1.4mm 4mm; font-size: 9pt;
  text-align: center; }
table.kits th { background: #f8fafc; color: #475569; font-size: 8.2pt; font-weight: bold; }
table.sess { width: 100%; border-collapse: collapse; }
table.sess td { border-bottom: 1px solid #eef2f7; padding: 1.2mm 2mm; font-size: 8.4pt;
  vertical-align: top; }
table.sess td.sn { width: 12mm; font-weight: bold; white-space: nowrap; }
table.sess td.st { width: 42mm; }
</style>
"""


def materials_page(c, grade, sessions, part_imgs, img_base="../",
                   part_notes=None):
    """Aggregate every session's `parts:` into one classroom shopping/prep list.

    Two timings are folded into a single page rather than two: a teacher planning
    the year wants one list, with the 2-hour-only extras flagged rather than
    hidden on a separate page.
    """
    seen = {}          # pid -> {"sessions": set, "notes": set, "long_only": bool}
    for s in sessions:
        for p in s.get("parts", []):
            e = seen.setdefault(p["id"], {"sessions": set(), "notes": set(),
                                          "long_only": True})
            e["sessions"].add(s["n"])
            e["long_only"] = False
            if p.get("note"):
                e["notes"].add(p["note"])
        for p in ((s.get("long") or {}).get("parts", [])):
            e = seen.setdefault(p["id"], {"sessions": set(), "notes": set(),
                                          "long_only": True})
            e["sessions"].add(s["n"])
            if p.get("note"):
                e["notes"].add(p["note"])

    # The Rover add-on is a box the school owns, so it gets its own "nothing to
    # buy" heading — only EXTRA is genuinely sold separately.
    groups = [("MBOT2", t("mat_from_box"), t("mat_from_box_sub")),
              ("ROVER", t("mat_from_rover"), t("mat_from_rover_sub")),
              ("CLASS", t("mat_classroom"), t("mat_classroom_sub")),
              ("EXTRA", t("mat_extra"), t("mat_extra_sub"))]

    def rows_for(setid):
        out = []
        items = [(pid, e) for pid, e in seen.items()
                 if parts_catalog.ICONS[pid][1] == setid]
        # most-used first: the things that must be ready every week head the list
        items.sort(key=lambda kv: (-len(kv[1]["sessions"]),
                                   parts_catalog.ICONS[kv[0]][0]))
        for pid, e in items:
            label, _sid, draw = parts_catalog.ICONS[pid]
            label = i18n.part_label(pid, label)
            if part_imgs and pid in part_imgs:
                icon = f'<img src="{img_base}assets/parts/{pid}.png" alt="{label}">'
            else:
                icon = f'<svg viewBox="0 0 64 44" width="52"><g>{draw(c)}</g></svg>'
            lo = f'<span class="lo">{t("mat_long_only")}</span>' if e["long_only"] else ""
            note = ("<span class='nt'>" + " · ".join(sorted(e["notes"])) + "</span>"
                    if e["notes"] else "")
            # How to CHOOSE the item, as opposed to what a given week uses it
            # for. Written once in content/part-notes.yaml so it cannot drift
            # between the lessons that happen to mention it.
            guide = (part_notes or {}).get(pid)
            if guide:
                note += f"<span class='pg'>{guide}</span>"
            ns = sorted(e["sessions"])
            # a part used nearly every week reads better as a count than as 18 numbers
            if len(ns) > 6:
                used = t("mat_sessions_n", n=num(len(ns)))
            else:
                used = ", ".join(f"S{num(x)}" for x in ns)
            out.append(f'<tr><td class="ic">{icon}</td>'
                       f'<td class="nm">{label}{lo}{note}</td>'
                       f'<td class="us">{t("mat_used_in")} {used}</td></tr>')
        return out

    blocks_html = []
    done = set()
    for setid, title, sub in groups:
        if setid in done:
            continue
        done.add(setid)
        rows = rows_for(setid)
        if not rows:
            continue
        blocks_html.append(f'<div class="mgrp"><h3 style="color:{c["dark"]}">{title}</h3>'
                           f'<p class="sub">{sub}</p>'
                           f'<table class="mtab">{"".join(rows)}</table></div>')

    kit_rows = "".join(
        f'<tr><td>{t("mat_students", n=num(n))}</td>'
        f'<td><b>{num(-(-n // 3))}–{num(-(-n // 2))}</b></td></tr>'
        for n in (12, 18, 24, 30))
    kits = (f'<div class="mgrp"><h3 style="color:{c["dark"]}">{t("mat_kits")}</h3>'
            f'<p class="sub">{t("mat_kits_rule")}</p>'
            f'<table class="kits"><tr><th>{t("mat_class_size")}</th>'
            f'<th>{t("mat_kits_needed")}</th></tr>{kit_rows}</table></div>')

    per_session = []
    for s in sessions:
        ids = [p["id"] for p in s.get("parts", [])]
        ids += [p["id"] for p in (s.get("long") or {}).get("parts", [])
                if p["id"] not in ids]
        # the robot itself is on every table; listing it 20 times is noise
        names = [parts_catalog.ICONS[i][0] for i in ids
                 if parts_catalog.ICONS[i][1] != "MBOT2"]
        per_session.append(
            f'<tr><td class="sn">S{num(s["n"])}</td><td class="st">{s["title"]}</td>'
            f'<td>{" · ".join(names) if names else t("mat_nothing")}</td></tr>')

    # "from the kit" covers both boxes the school owns; only EXTRA is a purchase
    nbox = sum(1 for p in seen if parts_catalog.ICONS[p][1] in ("MBOT2", "ROVER"))
    ncls = sum(1 for p in seen if parts_catalog.ICONS[p][1] == "CLASS")
    nex = sum(1 for p in seen if parts_catalog.ICONS[p][1] == "EXTRA")
    total = t("mat_total_line", box=num(nbox), cls=num(ncls),
              extra=t("mat_total_extra", n=num(nex)) if nex else "")

    return f"""
<h2 class="section">{t("materials_head", n=num(c['num']))}</h2>
<p class="muted">{t("materials_lede", n=num(len(sessions)))}</p>
<p class="mtot"><b>{total}</b></p>
{kits}
{"".join(blocks_html)}
<div class="mgrp"><h3 style="color:{c['dark']}">{t("mat_by_session")}</h3>
<p class="sub">{t("mat_by_session_sub")}</p>
<table class="sess">{"".join(per_session)}</table></div>
"""


def box_reference(grade, boxes):
    parts_html = "".join(box_table(boxes[key]) for key in grade["boxes"])
    return f"""
<div style="page-break-before: always"></div>
<h2 class="section">{t("boxes_head")}</h2>
<p class="muted" style="margin-bottom:3mm">{grade['box_usage']}</p>
{parts_html}
"""


def nonneg(variant, secondary=False):
    if secondary:
        return t("nonneg_sec")
    return t("nonneg_long" if variant == "long" else "nonneg_short")


def intro(grade, boxes, variant="short", secondary=False):
    c = grade_c(grade)
    obj = "".join(f"<li>{o}</li>" for o in grade["objectives"])
    if variant == "long":
        obj += "".join(f"<li>{o}</li>" for o in grade.get("long_objectives", []))
    cb = grade["capstone_blurb"]
    # Grades 7-9 ship in one timing only, so only a dual-timing grade gets the
    # timing called out on the cover. This once also kept the cover byte-identical
    # to the reference PDFs; that harness (tools/verify_print.py) was deleted on
    # 2026-08-19, but the rule still reads correctly on its own terms.
    dual = len(grade.get("timings", ["short"])) > 1
    prog = grade.get("program_full", t("program_default"))
    if dual:
        per, total = ("2 h", t("each_40h")) if variant == "long" else ("1 h", t("each_20h"))
        kicker = f'{t("teaching_guide")} · {prog} · {per} × {num(20)}'
    else:
        # single-timing grades declare their own length in grade.yaml
        per = grade.get("per", "1 h")
        total = t("each_40h") if grade.get("total") == "40 h" else \
            (t("each_20h") if grade.get("total") == "20 h" else t("each"))
        kicker = f'{t("teaching_guide")} · {prog} · {per} × {num(20)}'
    return f"""
<div class="cover">
  <div class="kicker">{kicker}</div>
  <h1>{t("grade_n", n=num(c['num']))}<br/>{c['theme'].split(' — ')[0]}</h1>
  <div class="sub">{c['theme'].split(' — ')[1] if ' — ' in c['theme'] else ''}</div>
  <div class="badges">
    <div class="badge"><b>{num(20)}</b><span>{t("sessions_unit")}</span></div>
    <div class="badge"><b>{per}</b><span>{total}</span></div>
    <div class="badge"><b>{c['form'].split(' · ')[0]}</b><span>{c['form'].split(' · ')[1]}</span></div>
    <div class="badge"><b>{c['codemode']}</b><span>{t("coding_mode")}</span></div>
  </div>
  <div class="coverbox">
    <h3>{t("final_project", name=cb['name'])}</h3>
    <p>{cb['text']}</p>
  </div>
  <div class="coverfoot">{t("cover_foot")}</div>
</div>

<h2 class="section">{t("at_a_glance", n=num(c['num']))}</h2>
<div class="objbox"><h4>{t("objectives_head")}</h4><ul>{obj}</ul></div>
<p><b>{t("sessions_by_unit")}</b> &nbsp;<span class="muted">{t("buffer_note")}</span></p>
<div class="center">{unit_strip(c)}</div>
<p style="margin-top:4mm"><b>{t("same_rhythm")}</b></p>
<div class="center">{rhythm(c, variant, secondary)}</div>
<div class="notecard">{nonneg(variant, secondary)}</div>
<div class="warncard"><b>{t("friction_head")}</b> {grade['friction']}</div>
{box_reference(grade, boxes)}
"""


# ---- screen chrome (web only; hidden in print) --------------------------------

SCREEN_CSS = """
@media screen {
  html { background: #e8edf3; }
  body { max-width: 210mm; margin: 0 auto 20mm auto; background: #fff;
         padding: 12mm 13mm; box-shadow: 0 2px 18px rgba(15,23,42,.14); }
  .sess { page-break-before: auto; }
}
@media print { .chrome, .buildson, .nextlesson { display: none !important; } }
/* Where you actually are when you have finished reading a lesson. Screen only —
   on paper the next sheet is the next lesson. */
.nextlesson { font-family: Helvetica, Arial, sans-serif; margin-top: 6mm;
  padding-top: 3mm; border-top: 1px solid #e2e8f0; text-align: right; }
.nextlesson a { color: #0e7fc1; text-decoration: none; font-weight: bold;
  font-size: 10.5pt; }
.nextlesson a:hover { text-decoration: underline; }
.nextlesson .nlk { display: block; font-size: 7.6pt; color: #94a3b8;
  text-transform: uppercase; letter-spacing: 0.08em; font-weight: bold; }
.buildson { font-family: Helvetica, Arial, sans-serif; font-size: 8.2pt; color: #64748b;
  margin: -1.5mm 0 3mm 1mm; }
.buildson b { color: #334155; font-weight: bold; }
.chrome { font-family: Helvetica, Arial, sans-serif; font-size: 9.5pt; margin-bottom: 6mm;
  padding-bottom: 3mm; border-bottom: 1px solid #e2e8f0; display: flex; gap: 4mm;
  align-items: center; flex-wrap: wrap; }
.chrome a { color: #0e7fc1; text-decoration: none; font-weight: bold; }
.chrome a:hover { text-decoration: underline; }
.chrome .spacer { flex: 1; }
.chrome .dim { color: #94a3b8; }
"""

# ---- language switch ---------------------------------------------------------
# The two locale trees are built by one generator and mirror each other file for
# file (site/<rel> and site/km/<rel>), so a page's counterpart is always the same
# `rel` under the other tree. That makes the switch a static href — no JS, and it
# works from file:// as well as over HTTP.
#
# Each language is labelled in its own language and never translated: a reader
# who cannot read the current page still has to recognise the way out of it.
LANGS = [("en", "EN", ""), ("km", "ខ្មែរ", "km/")]

# Standalone so print.html, which deliberately carries no SCREEN_CSS, can pull in
# just this. The @font-face is the one from KHMER_CSS: on an *English* page there
# is no Khmer webfont loaded, and the "ខ្មែរ" label would fall back to tofu on any
# machine without a system Khmer font. Two src URLs for the same depth reason —
# this CSS is inlined at site/*.html and site/grade7/*.html both.
LANG_CSS = """
@font-face {
  font-family: "Khmer OS Battambang";
  src: local("Khmer OS Battambang"),
       url("assets/fonts/KhmerOSBattambang-Regular.ttf") format("truetype"),
       url("../assets/fonts/KhmerOSBattambang-Regular.ttf") format("truetype");
  font-weight: normal; font-style: normal; font-display: swap;
}
/* margin-left:auto, not the .chrome .spacer: the bar wraps, and the spacer only
   pushes to the right edge of the FIRST line. This keeps the switch at the right
   edge of whichever line it lands on. */
.langtog { display: inline-flex; margin-left: auto; border: 1px solid #cbd5e1;
  border-radius: 4px; overflow: hidden; line-height: 1; font-size: 8.5pt; }
.langtog > * { padding: 1.5mm 2.4mm; font-weight: bold; white-space: nowrap;
  font-family: "Khmer OS Battambang", "Khmer MN", "Khmer Sangam MN",
               Helvetica, Arial, sans-serif; }
.langtog > * + * { border-left: 1px solid #cbd5e1; }
.langtog .on { background: #0e7fc1; color: #fff; }
.langtog a { background: #fff; color: #475569; text-decoration: none; }
.langtog a:hover { background: #e3f1fa; color: #0a5c8c; text-decoration: none; }
"""

# print.html is assembled by hand from theme_css alone, so it has neither the
# .chrome rules nor the print-time hide that SCREEN_CSS carries. This is that
# pair, and nothing else: the guide's screen layout is a deliberate print
# artefact and importing all of SCREEN_CSS would restyle it.
PRINT_CHROME_CSS = """
@media print { .chrome { display: none !important; } }
.chrome { font-family: Helvetica, Arial, sans-serif; font-size: 9.5pt;
  display: flex; gap: 4mm; align-items: center; flex-wrap: wrap;
  padding: 3mm 13mm; border-bottom: 1px solid #e2e8f0; }
.chrome a { color: #0e7fc1; text-decoration: none; font-weight: bold; }
.chrome .spacer { flex: 1; }
"""


def lang_toggle(rel):
    """The EN / ខ្មែរ switch, pointing at *this* page in the other locale.

    `rel` is the page's path relative to its own site root -- the same string
    build.py writes it under, e.g. "grade7/step-01.html". An en page sits at
    site/<rel> and a km page at site/km/<rel>, which is the whole of the
    difference: one extra level to climb, one "km/" to put back.

    Nothing else is needed to keep a chosen language: every other link a page
    carries is relative, so a Khmer page's "next step" already points at the next
    Khmer page. The switch is the only link that deliberately crosses trees, and
    tools/check_language.py holds that line.
    """
    depth = rel.count("/") + (0 if i18n.LOCALE == "en" else 1)
    segs = []
    for loc, label, prefix in LANGS:
        if loc == i18n.LOCALE:
            segs.append(f'<span class="on" lang="{loc}">{label}</span>')
        else:
            segs.append(f'<a href="{"../" * depth}{prefix}{rel}" lang="{loc}" '
                        f'hreflang="{loc}">{label}</a>')
    return (f'<span class="langtog" role="group" aria-label="{t("lang_switch")}">'
            f'{"".join(segs)}</span>')



def page(title, theme_css, body, extra_head=""):
    return (f'<!DOCTYPE html><html><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{title}</title><style>{theme_css}</style>'
            f'<style>{SCREEN_CSS}{LANG_CSS}</style>{extra_head}'
            f'</head><body>{body}</body></html>')
