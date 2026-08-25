# -*- coding: utf-8 -*-
"""Shared design library for the per-grade mBot2 Rover teaching PDFs."""

# ---------------------------------------------------------------- CSS

def css(c):
    """c = grade dict with color/dark/light."""
    return f"""
@page {{ size: A4; margin: 14mm 13mm 16mm 13mm;
  @bottom-center {{ content: "mBot2 Rover Program \u00b7 Grade {c['num']} \u00b7 " counter(page);
    font-size: 8pt; color: #94a3b8; font-family: Helvetica; }} }}
@page cover {{ margin: 0; @bottom-center {{ content: none; }} }}
* {{ box-sizing: border-box; }}
body {{ font-family: Helvetica, Arial, sans-serif; color: #1e293b; font-size: 9.2pt; line-height: 1.42; }}
p {{ margin: 0 0 2.2mm 0; }}
.muted {{ color: #64748b; font-size: 8.4pt; }}
.center {{ text-align: center; }}

.cover {{ page: cover; height: 297mm; color: #fff; padding: 28mm 20mm; position: relative;
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

.mats {{ border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 1.6mm 2mm 1mm 2mm; margin-bottom: 2.6mm; background: #fcfcfd; }}
.mats .mhead {{ font-size: 7.6pt; font-weight: bold; text-transform: uppercase; letter-spacing: 1.6px; color: {c['dark']}; margin: 0.4mm 0 1mm 1mm; }}
.mat {{ display: inline-block; width: 20.5mm; text-align: center; vertical-align: top; margin: 0 0.6mm 1mm 0.6mm; }}
.mat .mlbl {{ font-size: 6.9pt; font-weight: bold; color: #1e293b; line-height: 1.15; margin-top: 0.4mm; }}
.mat .mnote {{ font-size: 6.3pt; color: #64748b; line-height: 1.12; }}
.mat .pill {{ display: inline-block; font-size: 5.6pt; font-weight: bold; color: #fff; border-radius: 6px; padding: 0.25mm 1.5mm; margin-top: 0.6mm; letter-spacing: 0.4px; }}

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
"""

# ---------------------------------------------------------------- svg primitives

def _svg(w, h, body, width=None):
    width = width or w
    return (f'<svg viewBox="0 0 {w} {h}" width="{width}">'
            f'<g font-family="Helvetica">{body}</g></svg>')

def bot(x, y, c, dark, kind="wheel", r=0, s=1.0):
    """Top-view robot at x,y (center). kind: wheel|tank|arm."""
    b = f'<g transform="translate({x},{y}) rotate({r}) scale({s})">'
    if kind == "wheel":
        b += (f'<rect x="-16" y="-13" width="32" height="26" rx="6" fill="{c}"/>'
              f'<rect x="-19" y="-15" width="7" height="10" rx="2" fill="#1e293b"/>'
              f'<rect x="-19" y="5" width="7" height="10" rx="2" fill="#1e293b"/>'
              f'<rect x="12" y="-15" width="7" height="10" rx="2" fill="#1e293b"/>'
              f'<rect x="12" y="5" width="7" height="10" rx="2" fill="#1e293b"/>'
              f'<rect x="-9" y="-8" width="18" height="12" rx="2" fill="#0f172a"/>'
              f'<circle cx="-4" cy="-3" r="2" fill="#facc15"/><circle cx="4" cy="-3" r="2" fill="#facc15"/>'
              f'<path d="M -4,1 Q 0,4 4,1" stroke="#facc15" stroke-width="1.4" fill="none"/>'
              f'<polygon points="16,-5 24,0 16,5" fill="{dark}"/>')
    else:
        b += (f'<rect x="-20" y="-16" width="40" height="8" rx="4" fill="#1e293b"/>'
              f'<rect x="-20" y="8" width="40" height="8" rx="4" fill="#1e293b"/>'
              f'<rect x="-16" y="-11" width="32" height="22" rx="5" fill="{c}"/>'
              f'<rect x="-9" y="-7" width="18" height="12" rx="2" fill="#0f172a"/>'
              f'<circle cx="-4" cy="-2" r="2" fill="#facc15"/><circle cx="4" cy="-2" r="2" fill="#facc15"/>'
              f'<path d="M -4,2 Q 0,5 4,2" stroke="#facc15" stroke-width="1.4" fill="none"/>')
        if kind == "arm":
            b += (f'<line x1="16" y1="0" x2="32" y2="-12" stroke="{dark}" stroke-width="4" stroke-linecap="round"/>'
                  f'<line x1="32" y1="-12" x2="40" y2="-4" stroke="{dark}" stroke-width="4" stroke-linecap="round"/>'
                  f'<rect x="36" y="-6" width="9" height="8" rx="1.5" fill="#facc15" stroke="#ca8a04"/>')
        else:
            b += f'<polygon points="16,-5 24,0 16,5" fill="{dark}"/>'
    return b + '</g>'

def screen(x, y, w, h, lines, bg="#0f172a", fg="#7dd3fc", fs=9):
    out = (f'<rect x="{x-6}" y="{y-6}" width="{w+12}" height="{h+12}" rx="8" fill="#334155"/>'
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{bg}"/>')
    ly = y + fs + 6
    for ln, col, size, bold in lines:
        out += (f'<text x="{x + w/2}" y="{ly}" font-size="{size or fs}" fill="{col or fg}" '
                f'text-anchor="middle" {"font-weight=\"bold\"" if bold else ""}>{ln}</text>')
        ly += (size or fs) + 5
    return out

def flag(x, y, color="#16a34a", label="START"):
    return (f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y-18}" stroke="#334155" stroke-width="2"/>'
            f'<polygon points="{x},{y-18} {x+14},{y-14} {x},{y-10}" fill="{color}"/>'
            f'<text x="{x+2}" y="{y+11}" font-size="7.5" font-weight="bold" fill="{color}">{label}</text>')

def arrow_marker(mid="m1", col="#64748b"):
    return (f'<defs><marker id="{mid}" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
            f'<path d="M0,0 L7,3 L0,6 Z" fill="{col}"/></marker></defs>')

# ---------------------------------------------------------------- scene library
# every scene(c) takes the grade colors dict and optional params, returns svg string

def sc_cards(c, **k):
    items = [("vacuum robot", True), ("drone", True), ("calculator", False),
             ("thermostat", True), ("hammer", False)]
    b = ('<rect x="10" y="30" width="130" height="105" rx="8" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>'
         '<rect x="160" y="30" width="130" height="105" rx="8" fill="#fee2e2" stroke="#ef4444" stroke-width="2"/>'
         '<text x="75" y="22" font-size="10" font-weight="bold" fill="#16a34a" text-anchor="middle">SENSES + DECIDES + ACTS</text>'
         '<text x="225" y="22" font-size="10" font-weight="bold" fill="#ef4444" text-anchor="middle">MISSING A PIECE</text>')
    yy, yn = 45, 45
    for name, is_r in items:
        if is_r:
            b += f'<rect x="22" y="{yy}" width="106" height="20" rx="4" fill="#fff" stroke="#16a34a"/><text x="75" y="{yy+13}" font-size="8.5" text-anchor="middle">{name}</text>'
            yy += 26
        else:
            b += f'<rect x="172" y="{yn}" width="106" height="20" rx="4" fill="#fff" stroke="#ef4444"/><text x="225" y="{yn+13}" font-size="8.5" text-anchor="middle">{name}</text>'
            yn += 26
    return _svg(300, 145, b, 260)

def sc_build(c, stage="half", **k):
    b = arrow_marker("ba", "#94a3b8")
    if stage == "half":
        b += ('<rect x="25" y="45" width="70" height="50" rx="8" fill="' + c['color'] + '"/>'
              '<rect x="112" y="40" width="14" height="24" rx="4" fill="#1e293b"/>'
              '<rect x="112" y="76" width="14" height="24" rx="4" fill="#1e293b"/>'
              '<circle cx="160" cy="52" r="10" fill="#94a3b8"/><circle cx="160" cy="88" r="10" fill="#94a3b8"/>'
              '<text x="93" y="128" font-size="8.5" fill="#64748b" text-anchor="middle">chassis \u00b7 motors \u00b7 wheels laid out in order</text>'
              '<line x1="185" y1="70" x2="215" y2="70" stroke="#94a3b8" stroke-width="2.5" marker-end="url(#ba)"/>')
        b += bot(255, 70, c['color'], c['dark'], "wheel", 0, 1.35)
        b += '<text x="255" y="122" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">target for next session</text>'
    else:
        b += bot(90, 72, c['color'], c['dark'], "wheel", 0, 1.7)
        checks = ["wheels turn freely", "cables tucked away", "battery secured", "nothing loose when shaken"]
        y = 34
        for t in checks:
            b += (f'<text x="175" y="{y}" font-size="10" fill="#16a34a">\u2611</text>'
                  f'<text x="188" y="{y}" font-size="9" fill="#334155">{t}</text>')
            y += 22
        b += '<text x="90" y="132" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">fully assembled + QC checklist passed</text>'
    return _svg(320, 145, b, 275)

def _callout(x, y, tx, ty, label, col="#dc2626"):
    return (f'<line x1="{x}" y1="{y}" x2="{tx}" y2="{ty}" stroke="{col}" stroke-width="1" stroke-dasharray="3 2"/>'
            f'<text x="{tx+3}" y="{ty+3}" font-size="7.6" fill="{col}" font-weight="bold">{label}</text>')

def sc_expl(c, variant="drive", **k):
    """Redrawn (original) exploded-step schematics for the four build sessions."""
    b = ""
    cap = ""
    if variant == "drive":
        cap = "redrawn from guide steps \u2460\u2013\u2462 (pp. 9\u201310)"
        b += (f'<rect x="30" y="42" width="95" height="62" rx="10" fill="none" stroke="{c["color"]}" stroke-width="2.5"/>'
              f'<rect x="44" y="52" width="26" height="18" rx="3" fill="#1e293b"/>'
              f'<rect x="44" y="78" width="26" height="18" rx="3" fill="#1e293b"/>')
        b += _callout(70, 61, 128, 34, "M4\u00d78 \u00d74")
        b += (f'<circle cx="185" cy="56" r="15" fill="none" stroke="#334155" stroke-width="3"/>'
              f'<circle cx="185" cy="94" r="15" fill="none" stroke="#334155" stroke-width="3"/>'
              f'<line x1="152" y1="56" x2="168" y2="56" stroke="#94a3b8" stroke-width="2"/>'
              f'<line x1="152" y1="94" x2="168" y2="94" stroke="#94a3b8" stroke-width="2"/>')
        b += _callout(185, 75, 225, 72, "M2.5\u00d712 \u00d72")
        b += '<text x="78" y="126" font-size="8" fill="#334155">motors into chassis \u00b7 wheels onto shafts</text>'
    elif variant == "sense":
        cap = "redrawn from guide steps \u2463\u2013\u2468 (pp. 11\u201313)"
        b += (f'<rect x="55" y="66" width="120" height="30" rx="8" fill="{c["color"]}"/>'
              f'<rect x="70" y="42" width="90" height="20" rx="4" fill="#334155"/>'
              f'<circle cx="52" cy="74" r="7" fill="#0f172a"/><circle cx="52" cy="88" r="7" fill="#0f172a"/>'
              f'<rect x="62" y="99" width="46" height="8" rx="3" fill="#0f172a"/>'
              f'<circle cx="185" cy="98" r="8" fill="none" stroke="#334155" stroke-width="2.5"/>')
        b += _callout(115, 52, 178, 36, "shield M4\u00d725 \u00d74")
        b += _callout(52, 81, 20, 118, "ultrasonic M4\u00d714 \u00d72", )
        b += _callout(85, 103, 120, 126, "RGB + mini wheel M4\u00d714 \u00d72")
        b += ('<text x="200" y="60" font-size="8" fill="#16a34a" font-weight="bold">\u2714 10 cm cable</text>'
              '<text x="200" y="72" font-size="8" fill="#dc2626" font-weight="bold">\u2718 20 cm cable</text>'
              '<text x="200" y="86" font-size="7.6" fill="#334155">left\u2192EM1 \u00b7 right\u2192EM2</text>')
    elif variant == "trackmod":
        cap = "redrawn from guide pp. 5\u201324 \u00b7 build TWO, mirrored"
        b += (f'<path d="M60 30 L95 30 L78 62 Z" fill="none" stroke="{c["color"]}" stroke-width="2.5"/>'
              f'<rect x="52" y="62" width="52 " height="26" rx="4" fill="#1e293b"/>'
              f'<path d="M150 26 L232 58 L150 104 Z" fill="none" stroke="#334155" stroke-width="5" stroke-linejoin="round"/>'
              f'<circle cx="160" cy="44" r="11" fill="none" stroke="#334155" stroke-width="2.5"/>'
              f'<circle cx="163" cy="88" r="15" fill="none" stroke="#334155" stroke-width="2.5"/>')
        b += _callout(160, 44, 118, 22, "M4\u00d730 + bearing + nut")
        b += _callout(163, 88, 96, 122, "M4\u00d722 + bearing")
        b += _callout(214, 60, 238, 34, "M2.5\u00d712 (mBot2 box)")
        b += ('<text x="150" y="132" font-size="7.8" fill="#dc2626" font-weight="bold">nut back 90\u00b0 CCW \u2014 wheel must spin \u00b7 mind track grain</text>')
    else:  # roverchassis
        cap = "redrawn from guide pp. 25\u201375"
        b += (f'<path d="M30 40 L82 60 L30 92 Z" fill="none" stroke="#334155" stroke-width="4" stroke-linejoin="round"/>'
              f'<path d="M290 40 L238 60 L290 92 Z" fill="none" stroke="#334155" stroke-width="4" stroke-linejoin="round"/>'
              f'<rect x="82" y="58" width="156" height="12" rx="4" fill="{c["color"]}"/>'
              f'<path d="M110 58 L114 46 L118 58 M122 58 L126 46 L130 58" stroke="#b91c1c" stroke-width="2" fill="none"/>'
              f'<path d="M190 58 L194 46 L198 58 M202 58 L206 46 L210 58" stroke="#b91c1c" stroke-width="2" fill="none"/>'
              f'<rect x="138" y="26" width="44" height="26" rx="5" fill="#334155"/>'
              f'<path d="M132 34 L118 24 M188 34 L202 24" stroke="#1e293b" stroke-width="3"/>')
        b += _callout(126, 50, 52, 24, "metal shocks \u00d74")
        b += _callout(160, 66, 160, 96, "collars \u00d712 \u00b7 M3\u00d76 (pre-assemble)")
        b += _callout(180, 32, 236, 20, "servos \u00d72 \u2192 arms")
        b += '<text x="160" y="130" font-size="7.8" fill="#dc2626" font-weight="bold" text-anchor="middle">cross the motor cables L\u2194R \u00b7 peel board film first</text>'
    b += f'<text x="160" y="143" font-size="7.2" fill="#94a3b8" text-anchor="middle">{cap}</text>'
    return _svg(320, 148, b, 275)

def sc_screen_text(c, lines=None, caption="", **k):
    lines = lines or [("Hello!", "#7dd3fc", 16, True)]
    b = screen(90, 25, 130, 78, lines)
    b += f'<circle cx="105" cy="118" r="5" fill="#475569"/><circle cx="205" cy="118" r="5" fill="#475569"/>'
    if caption:
        b += f'<text x="155" y="142" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">{caption}</text>'
    return _svg(310, 148, b, 250)

def sc_path(c, shape="square", caption="", kind="wheel", **k):
    b = arrow_marker("pa2", c['color'])
    if shape == "square":
        pts = "80,35 220,35 220,120 80,120 80,35"
        b += f'<polyline points="{pts}" fill="none" stroke="{c["color"]}" stroke-width="2.5" stroke-dasharray="6,4"/>'
        rb = (150, 35, 0)
    elif shape == "triangle":
        b += f'<polyline points="150,30 235,125 65,125 150,30" fill="none" stroke="{c["color"]}" stroke-width="2.5" stroke-dasharray="6,4"/>'
        rb = (150, 30, 42)
    else:  # star
        import math
        pts = []
        for i in range(5):
            a = -90 + i * 144
            pts.append((150 + 55 * math.cos(math.radians(a)), 80 + 55 * math.sin(math.radians(a))))
        seq = " ".join(f"{p[0]:.0f},{p[1]:.0f}" for p in pts + [pts[0]])
        b += f'<polyline points="{seq}" fill="none" stroke="{c["color"]}" stroke-width="2.5" stroke-dasharray="6,4"/>'
        rb = (150, 25, 72)
    b += flag(58, 132)
    b += bot(rb[0], rb[1], c['color'], c['dark'], kind, rb[2], 1.0)
    if caption:
        b += f'<text x="150" y="150" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">{caption}</text>'
    return _svg(300, 155, b, 250)

def sc_calibrate(c, **k):
    b = ('<line x1="30" y1="105" x2="280" y2="105" stroke="#334155" stroke-width="2"/>')
    for i in range(11):
        x = 30 + i * 25
        b += f'<line x1="{x}" y1="105" x2="{x}" y2="{98 if i % 5 else 92}" stroke="#334155" stroke-width="1.5"/>'
        if i % 5 == 0:
            b += f'<text x="{x}" y="120" font-size="8" fill="#334155" text-anchor="middle">{i*5} cm</text>'
    b += bot(55, 70, c['color'], c['dark'], "wheel", 0, 1.1)
    b += arrow_marker("ca", c['color'])
    b += f'<line x1="85" y1="70" x2="270" y2="70" stroke="{c["color"]}" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#ca)"/>'
    b += (f'<line x1="280" y1="55" x2="280" y2="112" stroke="#ef4444" stroke-width="2"/>'
          f'<text x="280" y="48" font-size="9" font-weight="bold" fill="#ef4444" text-anchor="middle">target: 50 cm</text>'
          f'<text x="160" y="140" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">measured, adjusted, repeated \u2014 robot stops on the mark</text>')
    return _svg(310, 148, b, 265)

def sc_dance(c, **k):
    b = bot(150, 85, c['color'], c['dark'], "wheel", -15, 1.5)
    for (x, y, s) in [(90, 40, 13), (215, 35, 16), (245, 75, 12), (70, 95, 11)]:
        b += (f'<text x="{x}" y="{y}" font-size="{s}" fill="{c["dark"]}">\u266a</text>')
    for a in (-40, -15, 15, 40):
        b += f'<line x1="150" y1="85" x2="{150 + 68 * __import__("math").cos(__import__("math").radians(a-90)):.0f}" y2="{85 + 68 * __import__("math").sin(__import__("math").radians(a-90)):.0f}" stroke="#facc15" stroke-width="2.5" opacity="0.7"/>'
    b += '<text x="150" y="140" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">motion + LED rays + music, all in sync for 30 s</text>'
    return _svg(300, 148, b, 240)

def sc_sonar(c, dist="24 cm", stop=False, **k):
    b = bot(70, 75, c['color'], c['dark'], "wheel", 0, 1.25)
    for r_ in (28, 44, 60):
        b += f'<path d="M {70+r_*0.5},{75-r_*0.85} A {r_},{r_} 0 0 1 {70+r_*0.5},{75+r_*0.85}" fill="none" stroke="{c["color"]}" stroke-width="1.6" opacity="{1.05 - r_/70:.2f}" transform="translate({r_*0.35},0)"/>'
    b += ('<rect x="205" y="30" width="14" height="95" fill="#64748b"/>'
          '<text x="212" y="140" font-size="8" fill="#64748b" text-anchor="middle">wall</text>')
    if stop:
        b += arrow_marker("sa", "#ef4444")
        b += ('<line x1="103" y1="112" x2="205" y2="112" stroke="#ef4444" stroke-width="1.6" marker-end="url(#sa)"/>'
              '<line x1="205" y1="112" x2="103" y2="112" stroke="#ef4444" stroke-width="1.6" marker-end="url(#sa)"/>'
              '<text x="154" y="126" font-size="9" font-weight="bold" fill="#ef4444" text-anchor="middle">exactly 5 cm</text>')
    b += screen(238, 42, 58, 42, [(dist, "#7dd3fc", 12, True), ("live", "#94a3b8", 7, False)])
    return _svg(320, 148, b, 265)

def sc_wander(c, **k):
    b = ('<rect x="20" y="18" width="270" height="115" rx="6" fill="none" stroke="#334155" stroke-width="3"/>')
    b += arrow_marker("wa2", c['color'])
    b += (f'<path d="M 50,110 L 120,40 L 200,95 L 258,45" fill="none" stroke="{c["color"]}" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#wa2)"/>'
          f'<circle cx="120" cy="40" r="4" fill="#ef4444"/><circle cx="200" cy="95" r="4" fill="#ef4444"/>')
    b += bot(50, 110, c['color'], c['dark'], "wheel", -45, 0.95)
    b += ('<text x="120" y="30" font-size="7.5" fill="#ef4444" text-anchor="middle">detect \u2192 turn</text>'
          '<text x="155" y="146" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">robot roams the arena \u2014 never touches a wall</text>')
    return _svg(310, 152, b, 260)

def sc_line(c, wobble=True, states=False, caption=None, kind="wheel", **k):
    b = f'<path d="M 20,110 C 90,110 90,45 160,45 C 230,45 230,95 295,95" fill="none" stroke="#1e293b" stroke-width="7" stroke-linecap="round"/>'
    if wobble:
        b += f'<path d="M 20,104 C 55,118 75,88 100,102 C 125,116 130,40 160,55 C 195,68 205,80 240,102 C 260,112 275,86 295,90" fill="none" stroke="{c["color"]}" stroke-width="2" stroke-dasharray="4,3"/>'
        cap = caption or "robot follows the line \u2014 notice the zig-zag \u201cwobble\u201d"
    else:
        b += f'<path d="M 20,110 C 90,110 90,45 160,45 C 230,45 230,95 295,95" fill="none" stroke="{c["color"]}" stroke-width="2" stroke-dasharray="4,3" transform="translate(0,-6)"/>'
        cap = caption or "smooth trajectory hugging the line"
    if states:
        for x, t in [(60, "LEFT \u2192 steer right"), (160, "CENTER \u2192 straight"), (250, "RIGHT \u2192 steer left")]:
            b += f'<text x="{x}" y="22" font-size="7.6" font-weight="bold" fill="{c["dark"]}" text-anchor="middle">{t}</text>'
    b += bot(160, 45, c['color'], c['dark'], kind, 8, 0.95)
    b += f'<text x="157" y="140" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">{cap}</text>'
    return _svg(315, 148, b, 268)

def sc_events(c, **k):
    b = '<line x1="20" y1="80" x2="295" y2="80" stroke="#1e293b" stroke-width="7" stroke-linecap="round"/>'
    b += ('<rect x="95" y="70" width="18" height="20" fill="#ef4444" rx="3"/>'
          '<rect x="195" y="70" width="18" height="20" fill="#16a34a" rx="3"/>'
          '<text x="104" y="62" font-size="7.6" fill="#ef4444" text-anchor="middle" font-weight="bold">red = pause 2 s</text>'
          '<text x="204" y="62" font-size="7.6" fill="#16a34a" text-anchor="middle" font-weight="bold">green = beep + go</text>')
    b += bot(48, 80, c['color'], c['dark'], "wheel", 0, 0.95)
    b += ('<rect x="240" y="104" width="60" height="22" rx="11" fill="' + c['color'] + '"/>'
          '<text x="270" y="118" font-size="8" fill="#fff" text-anchor="middle" font-weight="bold">button B = start</text>'
          '<text x="157" y="142" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">the robot reacts to buttons and color patches on the track</text>')
    return _svg(315, 148, b, 268)

def sc_rescue(c, **k):
    b = (f'<path d="M 20,120 C 80,120 70,50 140,50 C 200,50 190,110 260,110" fill="none" stroke="#334155" stroke-width="5" stroke-linecap="round"/>'
         f'<rect x="130" y="35" width="24" height="24" fill="#ef4444" rx="4" transform="rotate(12 142 47)"/>'
         f'<text x="142" y="27" font-size="8" font-weight="bold" fill="#ef4444" text-anchor="middle">obstacle!</text>'
         f'<path d="M 118,58 Q 142,88 166,55" fill="none" stroke="{c["color"]}" stroke-width="2.2" stroke-dasharray="4,3"/>')
    b += bot(30, 120, c['color'], c['dark'], "wheel", 0, 0.95)
    b += flag(18, 138)
    b += (f'<circle cx="262" cy="110" r="21" fill="none" stroke="#16a34a" stroke-width="2.6" stroke-dasharray="5,4"/>'
          f'<text x="262" y="113" font-size="8" font-weight="bold" fill="#16a34a" text-anchor="middle">RESCUE</text>'
          f'<text x="150" y="150" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">line \u2192 avoid \u2192 precise stop \u2192 celebration, fully autonomous</text>')
    return _svg(300, 156, b, 258)

def sc_teardown(c, **k):
    trays = [("screws M4", 40), ("plates", 118), ("motors", 196), ("electronics", 274)]
    b = ""
    for label, x in trays:
        b += (f'<rect x="{x-32}" y="45" width="64" height="48" rx="6" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>'
              f'<text x="{x}" y="108" font-size="8" fill="#334155" text-anchor="middle">{label}</text>')
    b += ('<circle cx="30" cy="62" r="3" fill="#64748b"/><circle cx="42" cy="70" r="3" fill="#64748b"/><circle cx="52" cy="58" r="3" fill="#64748b"/>'
          '<rect x="98" y="58" width="38" height="8" rx="2" fill="#64748b"/><rect x="104" y="72" width="30" height="8" rx="2" fill="#64748b"/>'
          '<rect x="182" y="55" width="13" height="24" rx="4" fill="#1e293b"/><rect x="200" y="55" width="13" height="24" rx="4" fill="#1e293b"/>'
          f'<rect x="252" y="58" width="44" height="24" rx="4" fill="{c["color"]}"/>'
          '<text x="157" y="30" font-size="9" font-weight="bold" fill="#334155" text-anchor="middle">every part sorted before the tank build starts</text>')
    return _svg(315, 118, b, 268)

def sc_tank_compare(c, **k):
    b = bot(80, 70, c['color'], c['dark'], "tank", 0, 1.4)
    b += arrow_marker("tc1", c['dark'])
    b += (f'<path d="M 130,45 A 40,40 0 0 1 130,95" fill="none" stroke="{c["dark"]}" stroke-width="2.2" marker-end="url(#tc1)"/>'
          f'<text x="80" y="125" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">tracks: turns on the spot</text>'
          f'<text x="80" y="136" font-size="8" fill="#64748b" text-anchor="middle">(skid steer)</text>')
    b += bot(230, 70, "#94a3b8", "#64748b", "wheel", 0, 1.3)
    b += f'<path d="M 258,50 Q 300,70 258,92" fill="none" stroke="#64748b" stroke-width="2.2" stroke-dasharray="4,3" marker-end="url(#tc1)"/>'
    b += ('<text x="230" y="125" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">wheels: wider arc</text>'
          '<text x="230" y="136" font-size="8" fill="#64748b" text-anchor="middle">(last year\u2019s base)</text>')
    return _svg(315, 142, b, 262)

def sc_slope(c, angle=40, **k):
    import math
    b = ('<line x1="20" y1="120" x2="295" y2="120" stroke="#334155" stroke-width="2.5"/>')
    x2, y2 = 60 + 200 * math.cos(math.radians(angle)), 120 - 200 * math.sin(math.radians(angle)) * 0.55
    b += f'<line x1="60" y1="120" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#64748b" stroke-width="5" stroke-linecap="round"/>'
    b += (f'<path d="M 100,120 A 40,40 0 0 0 92,98" fill="none" stroke="{c["color"]}" stroke-width="2"/>'
          f'<text x="112" y="107" font-size="10" font-weight="bold" fill="{c["dark"]}">{angle}\u00b0 ?</text>')
    b += bot(150, 78, c['color'], c['dark'], "tank", -24, 1.15)
    b += '<text x="157" y="142" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">measured climb data \u2014 testing the manufacturer\u2019s claim</text>'
    return _svg(315, 148, b, 262)

def sc_chart(c, bars=None, ylab="speed (cm/s)", caption="", **k):
    bars = bars or [("tile", 88), ("carpet", 64), ("gravel", 41)]
    b = ('<line x1="45" y1="20" x2="45" y2="115" stroke="#334155" stroke-width="1.6"/>'
         '<line x1="45" y1="115" x2="290" y2="115" stroke="#334155" stroke-width="1.6"/>'
         f'<text x="18" y="70" font-size="7.5" fill="#64748b" transform="rotate(-90 18 70)" text-anchor="middle">{ylab}</text>')
    x = 75
    for label, v in bars:
        b += (f'<rect x="{x}" y="{115-v}" width="42" height="{v}" fill="{c["color"]}" rx="3" opacity="0.9"/>'
              f'<text x="{x+21}" y="128" font-size="8.5" fill="#334155" text-anchor="middle">{label}</text>'
              f'<text x="{x+21}" y="{110-v}" font-size="8" font-weight="bold" fill="{c["dark"]}" text-anchor="middle">{v}</text>')
        x += 72
    if caption:
        b += f'<text x="165" y="145" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">{caption}</text>'
    return _svg(315, 150, b, 262)

def sc_pixel(c, **k):
    b = ""
    face = set()
    for i in (4, 5, 10, 11):
        for j in (4, 5):
            face.add((i, j))
    for i in range(3, 13):
        face.add((i, 11)) if i in (5, 6, 7, 8, 9, 10) else None
    face |= {(4, 10), (11, 10), (5, 11), (10, 11), (6, 12), (7, 12), (8, 12), (9, 12)}
    for gx in range(16):
        for gy in range(16):
            fill = "#facc15" if (gx, gy) in face else "#1e293b"
            b += f'<rect x="{70 + gx * 8}" y="{8 + gy * 8}" width="7.4" height="7.4" fill="{fill}" rx="1"/>'
    b += '<text x="134" y="150" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">a 16\u00d716 pixel expression, drawn frame by frame</text>'
    return _svg(270, 156, b, 225)

def sc_moods(c, **k):
    b = ""
    faces = [("HAPPY", "M -10,4 Q 0,12 10,4", None), ("SLEEPY", "M -10,6 L 10,6", "zz"),
             ("SURPRISED", None, "O")]
    x = 55
    for name, mouth, extra in faces:
        b += screen(x - 38, 30, 76, 58, [])
        if name == "SURPRISED":
            b += (f'<circle cx="{x-12}" cy="52" r="5" fill="none" stroke="#facc15" stroke-width="2.5"/>'
                  f'<circle cx="{x+12}" cy="52" r="5" fill="none" stroke="#facc15" stroke-width="2.5"/>'
                  f'<circle cx="{x}" cy="72" r="6" fill="none" stroke="#facc15" stroke-width="2.5"/>')
        else:
            eye = 'L' if name == "SLEEPY" else 'C'
            if name == "SLEEPY":
                b += (f'<line x1="{x-17}" y1="52" x2="{x-7}" y2="52" stroke="#facc15" stroke-width="2.5"/>'
                      f'<line x1="{x+7}" y1="52" x2="{x+17}" y2="52" stroke="#facc15" stroke-width="2.5"/>'
                      f'<text x="{x+26}" y="46" font-size="9" fill="#facc15">z z</text>')
            else:
                b += (f'<circle cx="{x-12}" cy="52" r="4" fill="#facc15"/><circle cx="{x+12}" cy="52" r="4" fill="#facc15"/>')
            b += f'<path d="{mouth}" transform="translate({x},68)" fill="none" stroke="#facc15" stroke-width="2.5" stroke-linecap="round"/>'
        b += f'<text x="{x}" y="112" font-size="8" font-weight="bold" fill="{c["dark"]}" text-anchor="middle">{name}</text>'
        x += 105
    b += '<text x="160" y="138" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">three mood states, each on its own button</text>'
    return _svg(320, 144, b, 268)

def sc_react(c, **k):
    b = arrow_marker("ra", "#64748b")
    triggers = [("shake", "gyroscope", 35), ("darkness", "light sensor", 75), ("loud clap", "microphone", 115)]
    for name, sensor, y in triggers:
        b += (f'<rect x="15" y="{y-13}" width="88" height="26" rx="13" fill="{c["light"]}" stroke="{c["color"]}" stroke-width="1.5"/>'
              f'<text x="59" y="{y-1}" font-size="8.5" font-weight="bold" fill="{c["dark"]}" text-anchor="middle">{name}</text>'
              f'<text x="59" y="{y+9}" font-size="7" fill="#64748b" text-anchor="middle">{sensor}</text>'
              f'<line x1="106" y1="{y}" x2="140" y2="{y}" stroke="#64748b" stroke-width="1.8" marker-end="url(#ra)"/>')
    b += screen(150, 38, 96, 72, [])
    b += ('<circle cx="182" cy="62" r="6" fill="none" stroke="#facc15" stroke-width="3"/>'
          '<circle cx="214" cy="62" r="6" fill="none" stroke="#facc15" stroke-width="3"/>'
          '<path d="M 186,90 Q 198,78 210,90" fill="none" stroke="#facc15" stroke-width="3" stroke-linecap="round"/>'
          '<text x="198" y="130" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">sensor \u2192 emotion,</text>'
          '<text x="198" y="141" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">instantly on screen</text>')
    return _svg(300, 148, b, 252)

def sc_ml(c, confid=True, **k):
    b = ('<rect x="20" y="30" width="70" height="52" rx="6" fill="#0f172a"/>'
         '<circle cx="55" cy="52" r="12" fill="none" stroke="#7dd3fc" stroke-width="2"/>'
         '<circle cx="55" cy="48" r="4" fill="#7dd3fc"/>'
         '<path d="M 46,60 Q 55,52 64,60" fill="none" stroke="#7dd3fc" stroke-width="2"/>'
         '<text x="55" y="96" font-size="8" fill="#64748b" text-anchor="middle">webcam input</text>')
    b += arrow_marker("ml", "#64748b")
    b += '<line x1="95" y1="56" x2="128" y2="56" stroke="#64748b" stroke-width="2" marker-end="url(#ml)"/>'
    bars = [("thumbs-up", 92, "#16a34a"), ("thumbs-down", 5, "#94a3b8"), ("flat hand", 3, "#94a3b8")]
    y = 34
    for label, v, col in bars:
        b += (f'<text x="138" y="{y+9}" font-size="8" fill="#334155">{label}</text>'
              f'<rect x="198" y="{y}" width="{v}" height="12" rx="3" fill="{col}"/>'
              f'<text x="{202+v}" y="{y+10}" font-size="8" font-weight="bold" fill="{col}">{v}%</text>')
        y += 24
    b += '<text x="160" y="125" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">the trained model recognizes the class with high confidence</text>'
    return _svg(320, 132, b, 268)

def sc_mirror(c, **k):
    b = ('<circle cx="70" cy="65" r="30" fill="#fde68a" stroke="#ca8a04" stroke-width="2"/>'
         '<circle cx="60" cy="58" r="3.5" fill="#1e293b"/><circle cx="80" cy="58" r="3.5" fill="#1e293b"/>'
         '<path d="M 58,74 Q 70,84 82,74" fill="none" stroke="#1e293b" stroke-width="3" stroke-linecap="round"/>'
         '<text x="70" y="112" font-size="8.5" fill="#334155" text-anchor="middle">you smile\u2026</text>')
    b += arrow_marker("mi", c['color'])
    b += f'<line x1="112" y1="65" x2="150" y2="65" stroke="{c["color"]}" stroke-width="2.5" marker-end="url(#mi)"/>'
    b += '<text x="131" y="55" font-size="7.5" fill="#64748b" text-anchor="middle">ML</text>'
    b += screen(160, 30, 100, 70, [])
    b += ('<circle cx="192" cy="55" r="6" fill="#facc15"/><circle cx="228" cy="55" r="6" fill="#facc15"/>'
          '<path d="M 192,78 Q 210,92 228,78" fill="none" stroke="#facc15" stroke-width="4" stroke-linecap="round"/>'
          '<text x="210" y="122" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">\u2026Rover smiles back</text>')
    return _svg(300, 130, b, 250)

def sc_prompt(c, **k):
    b = ('<rect x="15" y="35" width="130" height="58" rx="8" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>'
         '<text x="24" y="52" font-size="8" fill="#64748b">prompt:</text>'
         '<text x="24" y="66" font-size="8.6" fill="#0f172a" font-weight="bold">\u201cexcited \u00b7 orange \u00b7</text>'
         '<text x="24" y="78" font-size="8.6" fill="#0f172a" font-weight="bold">cartoon style\u201d</text>')
    b += arrow_marker("pr", c['color'])
    b += f'<line x1="150" y1="64" x2="182" y2="64" stroke="{c["color"]}" stroke-width="2.5" marker-end="url(#pr)"/>'
    b += '<text x="166" y="54" font-size="7.5" fill="#64748b" text-anchor="middle">AI</text>'
    b += screen(192, 30, 92, 68, [])
    b += ('<circle cx="222" cy="52" r="7" fill="#fb923c"/><circle cx="254" cy="52" r="7" fill="#fb923c"/>'
          '<circle cx="222" cy="52" r="3" fill="#7c2d12"/><circle cx="254" cy="52" r="3" fill="#7c2d12"/>'
          '<ellipse cx="238" cy="78" rx="14" ry="9" fill="#fb923c"/>'
          '<text x="238" y="120" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">generated emoji on the Rover</text>')
    return _svg(300, 126, b, 252)

def sc_controller(c, **k):
    b = ('<rect x="55" y="30" width="200" height="80" rx="26" fill="#334155"/>'
         '<circle cx="95" cy="70" r="19" fill="#1e293b" stroke="#64748b" stroke-width="2"/>'
         '<circle cx="95" cy="70" r="8" fill="#94a3b8"/>'
         '<circle cx="215" cy="70" r="19" fill="#1e293b" stroke="#64748b" stroke-width="2"/>'
         '<circle cx="215" cy="70" r="8" fill="#94a3b8"/>')
    for (x, y, col) in [(150, 52, "#ef4444"), (138, 68, "#16a34a"), (162, 68, "#3b82f6"), (150, 84, "#facc15")]:
        b += f'<circle cx="{x}" cy="{y}" r="6.5" fill="{col}"/>'
    b += ('<text x="95" y="122" font-size="7.6" fill="#334155" text-anchor="middle">left stick = drive</text>'
          '<text x="215" y="122" font-size="7.6" fill="#334155" text-anchor="middle">right stick = turn</text>'
          '<text x="150" y="24" font-size="7.6" fill="#334155" text-anchor="middle">buttons = emotions \u00b7 sounds \u00b7 speed modes</text>'
          '<text x="155" y="140" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">every control mapped and labeled by the team</text>')
    return _svg(310, 146, b, 258)

def sc_blocks2py(c, **k):
    blocks = ["when button A pressed", "repeat 4", "  move forward 30 cm", "  turn right 90\u00b0"]
    py = ["import mbot2, cyberpi", "for i in range(4):", "    mbot2.straight(30)", "    mbot2.turn(90)"]
    b = ""
    y = 28
    for t in blocks:
        b += (f'<rect x="12" y="{y-11}" width="128" height="17" rx="4" fill="{c["color"]}" opacity="{0.95 - 0.09*blocks.index(t)}"/>'
              f'<text x="18" y="{y+1}" font-size="7.6" fill="#fff">{t}</text>')
        y += 21
    b += arrow_marker("bp", "#64748b")
    b += '<line x1="148" y1="62" x2="172" y2="62" stroke="#64748b" stroke-width="2.5" marker-end="url(#bp)"/>'
    b += '<rect x="180" y="14" width="128" height="96" rx="6" fill="#0f172a"/>'
    y = 34
    for t in py:
        b += f'<text x="188" y="{y}" font-size="7.4" fill="#a5f3fc" font-family="DejaVu Sans Mono">{t}</text>'
        y += 20
    b += '<text x="160" y="128" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">the same program, in blocks and in Python</text>'
    return _svg(320, 134, b, 268)

def sc_character(c, **k):
    b = bot(65, 70, c['color'], c['dark'], "tank", 0, 1.5)
    b += (f'<rect x="30" y="105" width="70" height="18" rx="9" fill="{c["dark"]}"/>'
          f'<text x="65" y="117" font-size="8.5" fill="#fff" text-anchor="middle" font-weight="bold">\u201cZAPPY\u201d</text>')
    feats = ["custom emoji set (5 moods)", "shake \u2192 dizzy spin", "clap \u2192 happy dance", "ML: waves back at you", "full controller drive"]
    y = 30
    for t in feats:
        b += (f'<text x="130" y="{y}" font-size="10" fill="#16a34a">\u2611</text>'
              f'<text x="143" y="{y}" font-size="8.6" fill="#334155">{t}</text>')
        y += 21
    return _svg(320, 138, b, 265)

def sc_fair(c, **k):
    b = ('<rect x="90" y="70" width="130" height="14" rx="4" fill="#94a3b8"/>'
         '<rect x="98" y="84" width="10" height="30" fill="#64748b"/><rect x="202" y="84" width="10" height="30" fill="#64748b"/>')
    b += bot(155, 58, c['color'], c['dark'], "tank", 0, 1.1)
    for x, y in [(40, 55), (52, 95), (268, 60), (255, 100)]:
        b += (f'<circle cx="{x}" cy="{y}" r="9" fill="#fde68a" stroke="#ca8a04" stroke-width="1.5"/>'
              f'<rect x="{x-7}" y="{y+10}" width="14" height="16" rx="4" fill="#64748b"/>')
    b += ('<rect x="230" y="20" width="72" height="26" rx="4" fill="#fff" stroke="#94a3b8"/>'
          '<text x="266" y="31" font-size="6.8" fill="#334155" text-anchor="middle">feedback card</text>'
          '<text x="266" y="41" font-size="7.5" fill="#f59e0b" text-anchor="middle">\u2605\u2605\u2605\u2605\u2606</text>'
          '<text x="155" y="138" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">visitors interact, robots respond, feedback collected</text>')
    return _svg(310, 144, b, 258)

def sc_pyeditor(c, code_lines, caption="", shape=None, **k):
    b = '<rect x="12" y="12" width="160" height="112" rx="6" fill="#0f172a"/>'
    b += '<circle cx="24" cy="22" r="3" fill="#ef4444"/><circle cx="34" cy="22" r="3" fill="#facc15"/><circle cx="44" cy="22" r="3" fill="#16a34a"/>'
    y = 40
    for t in code_lines[:7]:
        b += f'<text x="20" y="{y}" font-size="6.8" fill="#a5f3fc" font-family="DejaVu Sans Mono">{t}</text>'
        y += 13
    if shape == "square":
        b += (f'<polyline points="205,35 285,35 285,105 205,105 205,35" fill="none" stroke="{c["color"]}" stroke-width="2.5" stroke-dasharray="6,4"/>')
        b += bot(245, 35, c['color'], c['dark'], "tank", 0, 0.8)
    elif shape == "log":
        b += screen(200, 30, 100, 80, [("d = 34 cm", "#7dd3fc", 9, False), ("d = 27 cm", "#7dd3fc", 9, False), ("d = 12 cm", "#facc15", 9, True), ("STOP", "#ef4444", 10, True)])
    if caption:
        b += f'<text x="160" y="142" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">{caption}</text>'
    return _svg(320, 148, b, 268)

def sc_graph2(c, caption="", **k):
    b = ('<line x1="40" y1="15" x2="40" y2="105" stroke="#334155" stroke-width="1.5"/>'
         '<line x1="40" y1="60" x2="300" y2="60" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3,3"/>'
         '<line x1="40" y1="105" x2="300" y2="105" stroke="#334155" stroke-width="1.5"/>'
         '<text x="18" y="62" font-size="7" fill="#64748b" transform="rotate(-90 18 62)" text-anchor="middle">line error</text>'
         '<text x="170" y="118" font-size="7.5" fill="#64748b" text-anchor="middle">time \u2192</text>')
    b += ('<path d="M 45,60 L 65,30 L 85,88 L 105,32 L 125,86 L 145,35 L 165,84" fill="none" stroke="#ef4444" stroke-width="2"/>'
          '<text x="105" y="22" font-size="8" font-weight="bold" fill="#ef4444" text-anchor="middle">bang-bang</text>')
    b += (f'<path d="M 175,78 C 205,42 225,68 250,58 C 270,52 285,62 298,60" fill="none" stroke="#16a34a" stroke-width="2.2"/>'
          f'<text x="245" y="40" font-size="8" font-weight="bold" fill="#16a34a" text-anchor="middle">proportional</text>')
    b += f'<text x="170" y="134" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">{caption or "error shrinks and settles instead of bouncing"}</text>'
    return _svg(320, 140, b, 268)

def sc_arm(c, pose="lift", **k):
    b = bot(95, 85, c['color'], c['dark'], "arm", 0, 1.6)
    if pose == "lift":
        b += ('<rect x="158" y="38" width="22" height="20" rx="3" fill="#facc15" stroke="#ca8a04" stroke-width="1.5"/>'
              '<text x="169" y="30" font-size="8" fill="#334155" text-anchor="middle">held high</text>')
        cap = "the arm lifts and holds a block within its safe range"
    else:
        b += ('<rect x="215" y="98" width="24" height="20" rx="3" fill="#facc15" stroke="#ca8a04" stroke-width="1.5"/>'
              '<rect x="215" y="76" width="24" height="20" rx="3" fill="#fde68a" stroke="#ca8a04" stroke-width="1.5"/>'
              '<rect x="205" y="66" width="46" height="58" rx="4" fill="none" stroke="#16a34a" stroke-width="2" stroke-dasharray="5,4"/>')
        cap = "two blocks stacked inside the target zone"
    b += f'<text x="160" y="142" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">{cap}</text>'
    return _svg(320, 148, b, 262)

def sc_work(c, **k):
    b = ('<line x1="12" y1="112" x2="300" y2="112" stroke="#334155" stroke-width="4" stroke-linecap="round"/>'
         '<rect x="140" y="103" width="17" height="17" fill="#16a34a" transform="rotate(45 148 111)"/>'
         '<text x="148" y="136" font-size="7.5" fill="#16a34a" font-weight="bold" text-anchor="middle">marker</text>')
    b += bot(50, 92, c['color'], c['dark'], "arm", 0, 1.15)
    b += ('<rect x="238" y="62" width="48" height="46" rx="5" fill="none" stroke="#16a34a" stroke-width="2.4" stroke-dasharray="6,4"/>'
          '<rect x="252" y="90" width="17" height="14" rx="2" fill="#facc15" stroke="#ca8a04" stroke-width="1.4"/>'
          '<text x="262" y="55" font-size="8" font-weight="bold" fill="#16a34a" text-anchor="middle">deliver</text>')
    b += arrow_marker("wk", "#94a3b8")
    b += ('<path d="M 100,48 Q 165,24 235,45" fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#wk)"/>'
          '<text x="165" y="24" font-size="8" fill="#64748b" text-anchor="middle">fully autonomous</text>'
          '<text x="155" y="150" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">navigate \u2192 detect \u2192 pick \u2192 deliver, no human touch</text>')
    return _svg(315, 156, b, 262)

def sc_kanban(c, **k):
    cols = [("DONE", "#16a34a", ["build base", "P-control"]), ("DOING", "#d97706", ["marker detect"]), ("BLOCKED", "#ef4444", ["grip slips"])]
    b = ""
    x = 20
    for name, col, cards in cols:
        b += (f'<rect x="{x}" y="18" width="88" height="108" rx="6" fill="#f8fafc" stroke="{col}" stroke-width="2"/>'
              f'<text x="{x+44}" y="34" font-size="8.5" font-weight="bold" fill="{col}" text-anchor="middle">{name}</text>')
        y = 44
        for t in cards:
            b += (f'<rect x="{x+8}" y="{y}" width="72" height="20" rx="4" fill="#fff" stroke="#cbd5e1"/>'
                  f'<text x="{x+44}" y="{y+13}" font-size="7.6" fill="#334155" text-anchor="middle">{t}</text>')
            y += 26
        x += 100
    b += '<text x="160" y="142" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">2-minute standup: done \u00b7 doing \u00b7 blocked</text>'
    return _svg(320, 148, b, 262)

def sc_demo(c, **k):
    b = ('<rect x="60" y="88" width="190" height="12" rx="4" fill="#94a3b8"/>')
    b += bot(155, 74, c['color'], c['dark'], "arm", 0, 1.15)
    for x in [30, 55, 255, 280]:
        b += (f'<circle cx="{x}" cy="118" r="8" fill="#fde68a" stroke="#ca8a04" stroke-width="1.4"/>'
              f'<rect x="{x-6}" y="127" width="12" height="13" rx="3" fill="#64748b"/>')
    b += ('<rect x="228" y="20" width="76" height="34" rx="5" fill="#fff" stroke="#94a3b8"/>'
          '<text x="266" y="33" font-size="7" fill="#334155" text-anchor="middle">mission score</text>'
          '<text x="266" y="47" font-size="10" font-weight="bold" fill="#16a34a" text-anchor="middle">9 / 10 tasks</text>'
          '<text x="60" y="34" font-size="8" fill="#334155" text-anchor="middle">5-min pitch +</text>'
          '<text x="60" y="45" font-size="8" fill="#334155" text-anchor="middle">live demo</text>'
          '<text x="158" y="152" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">Demo Day: scored run in front of a real audience</text>')
    return _svg(315, 158, b, 260)

def sc_journal(c, caption, items, **k):
    b = ('<rect x="30" y="14" width="150" height="118" rx="6" fill="#fffbeb" stroke="#d6bb6f" stroke-width="1.6"/>'
         '<line x1="52" y1="14" x2="52" y2="132" stroke="#fca5a5" stroke-width="1.2"/>')
    y = 36
    for t in items[:5]:
        b += f'<text x="60" y="{y}" font-size="7.8" fill="#334155">{t}</text><line x1="58" y1="{y+4}" x2="172" y2="{y+4}" stroke="#e2e8f0"/>'
        y += 19
    b += f'<text x="160" y="150" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">{caption}</text>'
    b += bot(245, 66, c['color'], c['dark'], "tank", 0, 1.2)
    return _svg(315, 156, b, 258)

SCENES = {
    "cards": sc_cards, "build": sc_build, "expl": sc_expl, "screen": sc_screen_text, "path": sc_path,
    "calibrate": sc_calibrate, "dance": sc_dance, "sonar": sc_sonar, "wander": sc_wander,
    "line": sc_line, "events": sc_events, "rescue": sc_rescue, "teardown": sc_teardown,
    "tank_compare": sc_tank_compare, "slope": sc_slope, "chart": sc_chart, "pixel": sc_pixel,
    "moods": sc_moods, "react": sc_react, "ml": sc_ml, "mirror": sc_mirror, "prompt": sc_prompt,
    "controller": sc_controller, "blocks2py": sc_blocks2py, "character": sc_character,
    "fair": sc_fair, "pyeditor": sc_pyeditor, "graph2": sc_graph2, "arm": sc_arm,
    "work": sc_work, "kanban": sc_kanban, "demo": sc_demo, "journal": sc_journal,
}

# ---------------------------------------------------------------- page assembly

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def session_page(c, s, unit_name, unit_color):
    code_html = ""
    if s.get("code"):
        lang, code = s["code"]
        label = {"blocks": "Block script (rebuild this in mBlock)", "python": "Python (mBlock \u2192 Python mode)"}[lang]
        code_html = f'<div class="codelabel">{label}</div><div class="codebox">{esc(code)}</div>'
    guide_html = ""
    if s.get("guide"):
        rows = "".join(f'<tr><td class="k">{k}</td><td>{v}</td></tr>' for k, v in s["guide"])
        guide_html = f'<div class="guidebox"><b class="h">Quick Start Guide \u2014 this session</b><table>{rows}</table></div>'
    tips_html = ""
    if s.get("tips"):
        lis = "".join(f"<li>{t}</li>" for t in s["tips"])
        tips_html = f'<div class="tips"><b>Watch out</b><ul>{lis}</ul></div>'
    flow = "".join(f'<tr><td class="t">{t}</td><td>{d}</td></tr>' for t, d in s["steps"])
    teach = "".join(f"<p>{p}</p>" for p in s["teach"])
    key, params = s["result"]
    svg = SCENES[key](c, **params)
    crit = "".join(f"<li>{x}</li>" for x in s["success"])
    return f"""
<div class="sess">
  <div class="shead" style="background: linear-gradient(110deg, {c['dark']}, {unit_color})">
    <div class="sno">Session {s['n']} / 20 &nbsp;\u00b7&nbsp; {unit_name}</div>
    <h2>{s['title']}</h2>
  </div>
  <div class="goal"><b>Goal of this hour:</b> {s['goal']}</div>
  {__import__('parts').panel(c, s.get('parts', []))}
  <table class="cols"><tr>
    <td class="l">
      <h4 class="blk">Teach it \u2014 the concept</h4>
      <div class="teach">{teach}</div>
      <h4 class="blk">Lesson flow (45\u2032 core)</h4>
      <table class="flow">{flow}</table>
    </td>
    <td class="r">
      {guide_html}
      {code_html}
      {tips_html}
    </td>
  </tr></table>
  <div class="result">
    <span class="rk">\u25c9 Expected result at the end of this session</span>
    <table><tr>
      <td class="img">{svg}</td>
      <td class="crit"><ul>{crit}</ul></td>
    </tr></table>
  </div>
</div>"""


def build_grade_pdf(c, intro_html, sessions, outfile):
    from weasyprint import HTML
    # map session index -> unit
    unit_of = []
    for ui, (uname, count, ucolor) in enumerate(c["units"]):
        unit_of += [(uname, ucolor)] * count
    pages = "".join(session_page(c, s, unit_of[i][0], unit_of[i][1]) for i, s in enumerate(sessions))
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css(c)}</style></head><body>
{intro_html}{pages}</body></html>"""
    HTML(string=html).write_pdf(outfile)
    return outfile
