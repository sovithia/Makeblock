# -*- coding: utf-8 -*-
"""SVG scene library — ported VERBATIM from curriculum-source-annotated/common.py (svg section).
Do not redraw diagrams here; edits belong upstream in content, not in scenes."""

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

def sc_calibrate(c, target="50 cm", caption="measured, adjusted, repeated — robot stops on the mark", **k):
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
          f'<text x="280" y="48" font-size="9" font-weight="bold" fill="#ef4444" text-anchor="middle">target: {target}</text>'
          f'<text x="160" y="140" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">{caption}</text>')
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

def sc_patrol(c, **k):
    """G7-06: a fixed square driven forever. No sensor, no walls -- the robot
    does not know the arena is there, which is exactly the lesson. The old
    `wander` art promised detect-and-turn and this program has no sensor in it."""
    b = arrow_marker("pt1", c['color'])
    # the square it actually drives: four 30 cm sides
    b += (f'<rect x="90" y="34" width="120" height="82" fill="none" stroke="{c["color"]}" '
          f'stroke-width="2" stroke-dasharray="5,4"/>')
    b += (f'<path d="M 150,34 L 208,34" fill="none" stroke="{c["color"]}" stroke-width="2" '
          f'marker-end="url(#pt1)"/>')
    for x, y in ((90, 34), (210, 34), (210, 116), (90, 116)):
        b += f'<circle cx="{x}" cy="{y}" r="4" fill="#ffbf00"/>'
    b += ('<text x="150" y="26" font-size="7.5" fill="#64748b" text-anchor="middle">'
          '30 cm, then turn 90\u00b0</text>')
    b += ('<text x="248" y="60" font-size="7.5" fill="#ffbf00" text-anchor="middle" '
          'font-weight="bold">beep +</text>'
          '<text x="248" y="70" font-size="7.5" fill="#ffbf00" text-anchor="middle" '
          'font-weight="bold">new colour</text>')
    b += bot(90, 116, c['color'], c['dark'], "wheel", 0, 0.95)
    b += ('<text x="155" y="146" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">the same square, over and over, until B stops it</text>')
    return _svg(310, 152, b, 260)


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
    # The line stops at the rescue ring rather than running through it: at full
    # width the 5px path crossed the word RESCUE and neither could be read. For
    # the same reason the robot sits a little way along the curve instead of on
    # the start point, which put it on top of the flag and its START label on
    # top of the caption.
    b = (f'<path d="M 20,120 C 80,120 70,50 140,50 C 200,50 190,110 240,110" fill="none" stroke="#334155" stroke-width="5" stroke-linecap="round"/>'
         f'<rect x="130" y="35" width="24" height="24" fill="#ef4444" rx="4" transform="rotate(12 142 47)"/>'
         f'<text x="142" y="27" font-size="8" font-weight="bold" fill="#ef4444" text-anchor="middle">obstacle!</text>'
         f'<path d="M 118,58 Q 142,88 166,55" fill="none" stroke="{c["color"]}" stroke-width="2.2" stroke-dasharray="4,3"/>')
    b += bot(52, 113, c['color'], c['dark'], "wheel", -14, 0.95)
    b += flag(12, 126)
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
    slot = 230 / len(bars)
    width = min(42, slot * 0.68)
    x = 52 + (slot - width) / 2
    for label, v in bars:
        mid = x + width / 2
        b += (f'<rect x="{x}" y="{115-v}" width="{width}" height="{v}" fill="{c["color"]}" rx="3" opacity="0.9"/>'
              f'<text x="{mid}" y="128" font-size="8.5" fill="#334155" text-anchor="middle">{label}</text>'
              f'<text x="{mid}" y="{110-v}" font-size="8" font-weight="bold" fill="{c["dark"]}" text-anchor="middle">{v}</text>')
        x += slot
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
         '<text x="55" y="96" font-size="8" fill="#64748b" text-anchor="middle">camera input</text>')
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

def sc_controller(c, left="left stick = drive", right="right stick = turn",
                  buttons="buttons = emotions / sounds / speed modes",
                  caption="every control mapped and labeled by the team", **k):
    b = ('<rect x="55" y="30" width="200" height="80" rx="26" fill="#334155"/>'
         '<circle cx="95" cy="70" r="19" fill="#1e293b" stroke="#64748b" stroke-width="2"/>'
         '<circle cx="95" cy="70" r="8" fill="#94a3b8"/>'
         '<circle cx="215" cy="70" r="19" fill="#1e293b" stroke="#64748b" stroke-width="2"/>'
         '<circle cx="215" cy="70" r="8" fill="#94a3b8"/>')
    for (x, y, col) in [(150, 52, "#ef4444"), (138, 68, "#16a34a"), (162, 68, "#3b82f6"), (150, 84, "#facc15")]:
        b += f'<circle cx="{x}" cy="{y}" r="6.5" fill="{col}"/>'
    b += (f'<text x="95" y="122" font-size="7.6" fill="#334155" text-anchor="middle">{left}</text>'
          f'<text x="215" y="122" font-size="7.6" fill="#334155" text-anchor="middle">{right}</text>'
          f'<text x="150" y="24" font-size="7.6" fill="#334155" text-anchor="middle">{buttons}</text>'
          f'<text x="155" y="140" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">{caption}</text>')
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
    elif pose == "place":
        # One servo per arm: grip height and grip force are the same number, so the
        # Rover releases where it stands. No stacking pose exists for this robot.
        b += ('<rect x="215" y="98" width="24" height="20" rx="3" fill="#facc15" stroke="#ca8a04" stroke-width="1.5"/>'
              '<rect x="205" y="88" width="46" height="36" rx="4" fill="none" stroke="#16a34a" stroke-width="2" stroke-dasharray="5,4"/>')
        cap = "carried, then released inside the target zone"
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

def sc_worksheet(c, caption, items, **k):
    b = ('<rect x="30" y="14" width="150" height="118" rx="6" fill="#fffbeb" stroke="#d6bb6f" stroke-width="1.6"/>'
         '<line x1="52" y1="14" x2="52" y2="132" stroke="#fca5a5" stroke-width="1.2"/>')
    y = 36
    for t in items[:5]:
        b += f'<text x="60" y="{y}" font-size="7.8" fill="#334155">{t}</text><line x1="58" y1="{y+4}" x2="172" y2="{y+4}" stroke="#e2e8f0"/>'
        y += 19
    b += f'<text x="160" y="150" font-size="8.5" fill="#334155" text-anchor="middle" font-weight="bold">{caption}</text>'
    b += bot(245, 66, c['color'], c['dark'], "tank", 0, 1.2)
    return _svg(315, 156, b, 258)

# ------------------------------------------------------------------ grades 4-6
# mBot2 Box 1 only. These lean on CyberPi's own hardware (screen, LED strip,
# speaker, mic, joystick, gyro) — the surface grades 7-9 barely touch.

def sc_hello(c, name="BOLT", **k):
    b = screen(95, 18, 120, 66, [(name, "#7dd3fc", 17, True), ("ready!", "#facc15", 9, False)])
    for i in range(5):
        b += (f'<rect x="{104 + i*22}" y="100" width="15" height="11" rx="2.5" '
              f'fill="{["#ef4444","#f59e0b","#22c55e","#3b82f6","#a855f7"][i]}"/>')
    b += ('<text x="155" y="126" font-size="7.6" fill="#64748b" text-anchor="middle">5 RGB LEDs</text>'
          '<text x="155" y="144" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">every team’s robot boots, is named, and says hello</text>')
    return _svg(310, 150, b, 250)

def sc_garage(c, **k):
    b = (f'<rect x="200" y="46" width="86" height="62" rx="4" fill="#fef9ec" '
         f'stroke="#d97706" stroke-width="3" stroke-dasharray="7,5"/>'
         f'<text x="243" y="38" font-size="9" font-weight="bold" fill="#d97706" '
         f'text-anchor="middle">THE GARAGE</text>')
    b += flag(30, 118)
    b += arrow_marker("ga4", c['color'])
    b += (f'<line x1="70" y1="77" x2="196" y2="77" stroke="{c["color"]}" stroke-width="2" '
          f'stroke-dasharray="6,4" marker-end="url(#ga4)"/>')
    b += bot(52, 77, c['color'], c['dark'], "wheel", 0, 1.15)
    b += ('<text x="155" y="142" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">drive, then stop — fully inside the box, no bumping</text>')
    return _svg(305, 150, b, 255)

def sc_quarter(c, **k):
    b = (f'<path d="M 40,110 L 150,110" stroke="{c["color"]}" stroke-width="2.5" '
         f'stroke-dasharray="6,4" fill="none"/>'
         f'<path d="M 150,110 L 150,32" stroke="{c["color"]}" stroke-width="2.5" '
         f'stroke-dasharray="6,4" fill="none"/>')
    b += (f'<path d="M 150,86 A 24,24 0 0 0 126,110" fill="none" stroke="#d97706" stroke-width="2"/>'
          f'<rect x="150" y="96" width="14" height="14" fill="none" stroke="#94a3b8" stroke-width="1.2"/>'
          f'<text x="176" y="98" font-size="11" font-weight="bold" fill="#d97706">90°</text>'
          f'<text x="176" y="112" font-size="7.6" fill="#64748b">a quarter turn</text>')
    b += bot(150, 110, c['color'], c['dark'], "wheel", -90, 1.1)
    b += flag(34, 122)
    b += ('<text x="155" y="144" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">one quarter turn, then straight on — tested both ways</text>')
    return _svg(305, 152, b, 255)

def sc_repeat(c, **k):
    b = (f'<rect x="14" y="24" width="118" height="92" rx="8" fill="#fff" '
         f'stroke="{c["color"]}" stroke-width="2.5"/>'
         f'<rect x="14" y="24" width="118" height="20" rx="8" fill="{c["color"]}"/>'
         f'<text x="73" y="38" font-size="10" font-weight="bold" fill="#fff" '
         f'text-anchor="middle">repeat 4</text>')
    for i, t in enumerate(("move forward 30 cm", "turn right 90°")):
        b += (f'<rect x="24" y="{52 + i*26}" width="98" height="19" rx="4" fill="#e2e8f0"/>'
              f'<text x="73" y="{65 + i*26}" font-size="7.6" fill="#1e293b" '
              f'text-anchor="middle">{t}</text>')
    b += (f'<path d="M 24,110 A 9,9 0 0 0 24,92" fill="none" stroke="{c["dark"]}" '
          f'stroke-width="2"/><polygon points="24,92 20,98 28,98" fill="{c["dark"]}"/>')
    b += f'<text x="150" y="76" font-size="15" fill="#64748b">→</text>'
    b += (f'<polyline points="185,40 275,40 275,120 185,120 185,40" fill="none" '
          f'stroke="{c["color"]}" stroke-width="2.5" stroke-dasharray="6,4"/>')
    b += bot(230, 40, c['color'], c['dark'], "wheel", 0, 0.85)
    b += ('<text x="150" y="142" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">two blocks inside a repeat replace eight blocks in a row</text>')
    return _svg(300, 150, b, 258)

def sc_lights(c, **k):
    b = ('<rect x="18" y="30" width="128" height="46" rx="7" fill="#334155"/>'
         '<text x="82" y="22" font-size="8" font-weight="bold" fill="#64748b" '
         'text-anchor="middle">CyberPi — 5 RGB LEDs</text>')
    for i in range(5):
        col = ["#ef4444", "#f59e0b", "#22c55e", "#3b82f6", "#a855f7"][i]
        b += (f'<rect x="{27 + i*24}" y="42" width="17" height="22" rx="3" fill="{col}"/>'
              f'<circle cx="{35.5 + i*24}" cy="53" r="12" fill="{col}" opacity="0.22"/>')
    b += ('<rect x="176" y="30" width="112" height="46" rx="7" fill="#1e293b"/>'
          '<text x="232" y="22" font-size="8" font-weight="bold" fill="#64748b" '
          'text-anchor="middle">Ultrasonic 2 — 8 blue LEDs</text>')
    for i in range(8):
        b += (f'<circle cx="{190 + i*13}" cy="53" r="4.4" fill="#38bdf8" '
              f'opacity="{0.35 + 0.08*i:.2f}"/>')
    b += ('<text x="232" y="92" font-size="7.8" fill="#334155" text-anchor="middle">'
          'the robot’s “eyes” — blink, sweep, pulse</text>')
    b += bot(82, 106, c['color'], c['dark'], "wheel", 0, 1.0)
    b += ('<text x="153" y="146" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">a light pattern the team designed and can name</text>')
    return _svg(305, 152, b, 258)

def sc_music(c, **k):
    keys = ""
    for i in range(6):
        keys += (f'<rect x="{20 + i*20}" y="66" width="18" height="46" rx="2" fill="#fff" '
                 f'stroke="#334155" stroke-width="1.3"/>')
    for i in (0, 1, 3, 4):
        keys += f'<rect x="{32 + i*20}" y="66" width="11" height="28" rx="1.5" fill="#1e293b"/>'
    b = keys
    for x, y, s in [(214, 46, 15), (240, 32, 18), (264, 52, 14), (286, 36, 16)]:
        b += f'<text x="{x}" y="{y}" font-size="{s}" fill="{c["dark"]}">♫</text>'
    b += (f'<path d="M 186,64 A 16,16 0 0 1 186,96" fill="none" stroke="{c["color"]}" '
          f'stroke-width="2"/>'
          f'<path d="M 196,56 A 26,26 0 0 1 196,104" fill="none" stroke="{c["color"]}" '
          f'stroke-width="2" opacity="0.6"/>'
          f'<polygon points="152,72 164,72 174,60 174,100 164,88 152,88" fill="#334155"/>')
    b += ('<text x="86" y="34" font-size="8.5" font-weight="bold" fill="#64748b" '
          'text-anchor="middle">notes chosen by the team</text>'
          '<text x="152" y="140" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">a short tune the robot plays on its own speaker</text>')
    return _svg(305, 148, b, 258)

def sc_joystick(c, **k):
    b = ('<rect x="24" y="26" width="104" height="92" rx="9" fill="#334155"/>'
         '<rect x="32" y="34" width="88" height="42" rx="3" fill="#0f172a"/>'
         '<text x="76" y="60" font-size="10" fill="#7dd3fc" text-anchor="middle">drive!</text>')
    b += (f'<circle cx="60" cy="97" r="15" fill="#1e293b" stroke="#64748b" stroke-width="1.5"/>'
          f'<circle cx="66" cy="92" r="7.5" fill="{c["color"]}"/>')
    for dx, dy in ((0, -22), (0, 22), (-22, 0), (22, 0)):
        b += (f'<polygon points="{60+dx*1.05},{97+dy*1.05} {60+dx*0.75+(4 if dy else 0)},'
              f'{97+dy*0.75+(4 if dx else 0)} {60+dx*0.75-(4 if dy else 0)},'
              f'{97+dy*0.75-(4 if dx else 0)}" fill="#64748b"/>')
    b += (f'<circle cx="105" cy="92" r="7" fill="#22c55e"/>'
          f'<circle cx="105" cy="108" r="7" fill="#ef4444"/>'
          f'<text x="105" y="95.5" font-size="7" fill="#fff" text-anchor="middle" '
          f'font-weight="bold">A</text>'
          f'<text x="105" y="111.5" font-size="7" fill="#fff" text-anchor="middle" '
          f'font-weight="bold">B</text>')
    b += arrow_marker("jy", c['color'])
    b += (f'<path d="M 140,72 C 170,50 195,96 224,72" fill="none" stroke="{c["color"]}" '
          f'stroke-width="2" stroke-dasharray="5,4" marker-end="url(#jy)"/>')
    b += bot(258, 72, c['color'], c['dark'], "wheel", 12, 1.15)
    b += ('<text x="152" y="140" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">the robot steers live — no cable, no remote, just CyberPi</text>')
    return _svg(305, 148, b, 258)

def sc_tilt(c, **k):
    b = ('<line x1="20" y1="118" x2="290" y2="118" stroke="#334155" stroke-width="2"/>')
    b += bot(80, 96, c['color'], c['dark'], "wheel", 0, 1.1)
    b += ('<text x="80" y="140" font-size="8" fill="#64748b" text-anchor="middle">flat → asleep</text>')
    b += f'<g transform="rotate(-28 220 92)">{bot(220, 92, c["color"], c["dark"], "wheel", 0, 1.1)}</g>'
    b += (f'<path d="M 250,110 A 34,34 0 0 0 236,80" fill="none" stroke="#d97706" stroke-width="2"/>'
          f'<text x="264" y="86" font-size="10" font-weight="bold" fill="#d97706">tilt!</text>')
    for r_ in (18, 27):
        b += (f'<path d="M {220+r_},{56-r_*0.2} A {r_},{r_} 0 0 1 {224+r_},{62}" fill="none" '
              f'stroke="#ef4444" stroke-width="1.8" opacity="0.7"/>')
    b += ('<text x="220" y="140" font-size="8" fill="#64748b" text-anchor="middle">picked up '
          '→ squeals</text>'
          '<text x="152" y="20" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">the gyroscope notices — no button pressed, no `if` written</text>')
    return _svg(305, 148, b, 258)

def sc_clap(c, **k):
    b = ('<text x="48" y="72" font-size="30">\U0001f44f</text>')
    for i, r_ in enumerate((16, 26, 36)):
        b += (f'<path d="M {96},{62-r_*0.62} A {r_},{r_} 0 0 1 {96},{62+r_*0.62}" fill="none" '
              f'stroke="{c["color"]}" stroke-width="2" opacity="{0.85-i*0.24:.2f}"/>')
    b += ('<rect x="150" y="28" width="26" height="86" rx="4" fill="#e2e8f0"/>')
    b += (f'<rect x="150" y="52" width="26" height="62" rx="4" fill="{c["color"]}"/>'
          f'<line x1="144" y1="52" x2="182" y2="52" stroke="#ef4444" stroke-width="2.5"/>'
          f'<text x="188" y="50" font-size="8" font-weight="bold" fill="#ef4444">threshold</text>'
          f'<text x="163" y="126" font-size="7.6" fill="#64748b" text-anchor="middle">loudness</text>')
    b += bot(255, 76, c['color'], c['dark'], "wheel", 0, 1.15)
    b += (f'<text x="255" y="34" font-size="9" font-weight="bold" fill="#16a34a" '
          f'text-anchor="middle">GO!</text>')
    b += ('<text x="152" y="146" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">clap once — the routine starts itself</text>')
    return _svg(305, 152, b, 258)

def sc_storyboard(c, **k):
    labels = ("1 · entrance", "2 · the trick", "3 · the wave", "4 · exit")
    b = ""
    for i, lab in enumerate(labels):
        x = 14 + i * 72
        b += (f'<rect x="{x}" y="30" width="64" height="52" rx="5" fill="#fff" '
              f'stroke="{c["color"]}" stroke-width="1.8"/>'
              f'<text x="{x+32}" y="94" font-size="7.4" fill="{c["dark"]}" '
              f'text-anchor="middle" font-weight="bold">{lab}</text>')
    b += bot(46, 56, c['color'], c['dark'], "wheel", 0, 0.62)
    b += (f'<text x="118" y="62" font-size="15" fill="#facc15" text-anchor="middle">★</text>'
          f'<text x="190" y="63" font-size="16" text-anchor="middle">\U0001f44b</text>')
    b += bot(262, 56, c['color'], c['dark'], "wheel", 180, 0.62)
    b += (f'<rect x="14" y="104" width="280" height="24" rx="5" fill="#fef9ec" '
          f'stroke="#d97706" stroke-width="1.4"/>'
          f'<text x="154" y="120" font-size="8" fill="#92400e" text-anchor="middle">'
          f'name · character · one sentence of story · who says what</text>')
    b += ('<text x="154" y="20" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">four panels: the whole act, planned before any code</text>')
    return _svg(308, 138, b, 262)

def sc_parade(c, **k):
    b = (f'<path d="M 16,118 C 80,118 70,60 150,60 C 230,60 220,104 296,104" fill="none" '
         f'stroke="#cbd5e1" stroke-width="16" stroke-linecap="round"/>')
    bunting = ("#ef4444", "#f59e0b", "#22c55e", "#3b82f6")
    for i, x in enumerate((40, 110, 190, 262)):
        col = bunting[i]
        b += f'<circle cx="{x}" cy="16" r="4" fill="{c["color"]}" opacity="0.5"/>'
        b += f'<polygon points="{x},16 {x+13},21 {x},26" fill="{col}"/>'
    b += (f'<line x1="20" y1="16" x2="290" y2="16" stroke="#94a3b8" stroke-width="1.2"/>')
    for i, (x, y, r_) in enumerate([(66, 108, 0), (150, 60, -8), (238, 82, 10)]):
        b += bot(x, y, c['color'], c['dark'], "wheel", r_, 0.95)
        b += f'<text x="{x}" y="{y-22}" font-size="11" fill="#facc15" text-anchor="middle">★</text>'
    for x in (30, 60, 90, 200, 235, 268):
        b += (f'<circle cx="{x}" cy="{136}" r="5.5" fill="#94a3b8"/>'
              f'<rect x="{x-5}" y="141" width="10" height="8" rx="2.5" fill="#cbd5e1"/>')
    b += ('<text x="152" y="132" font-size="8" fill="#64748b" text-anchor="middle">'
          'the audience</text>')
    return _svg(308, 154, b, 262)


def sc_buttons(c, **k):
    b = ('<rect x="18" y="34" width="96" height="76" rx="8" fill="#334155"/>'
         '<rect x="26" y="42" width="80" height="34" rx="3" fill="#0f172a"/>'
         '<text x="66" y="64" font-size="9" fill="#7dd3fc" text-anchor="middle">ready</text>')
    b += (f'<circle cx="46" cy="94" r="9" fill="#22c55e"/>'
          f'<text x="46" y="97.5" font-size="9" fill="#fff" text-anchor="middle" '
          f'font-weight="bold">A</text>'
          f'<circle cx="86" cy="94" r="9" fill="#ef4444"/>'
          f'<text x="86" y="97.5" font-size="9" fill="#fff" text-anchor="middle" '
          f'font-weight="bold">B</text>')
    b += arrow_marker("bt1", "#22c55e") + arrow_marker("bt2", "#ef4444")
    b += (f'<path d="M 124,88 C 158,88 158,48 190,48" fill="none" stroke="#22c55e" '
          f'stroke-width="2" marker-end="url(#bt1)"/>'
          f'<path d="M 124,100 C 158,100 158,116 190,116" fill="none" stroke="#ef4444" '
          f'stroke-width="2" marker-end="url(#bt2)"/>')
    b += bot(228, 48, c['color'], c['dark'], "wheel", 0, 0.85)
    b += (f'<text x="228" y="26" font-size="8.4" font-weight="bold" fill="#22c55e" '
          f'text-anchor="middle">A → drive the route</text>')
    b += (f'<text x="216" y="112" font-size="14" fill="{c["dark"]}">♫</text>'
          f'<text x="252" y="120" font-size="8.4" font-weight="bold" fill="#ef4444" '
          f'text-anchor="middle">B → sing</text>')
    b += ('<text x="152" y="142" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">two programs in one robot — the button chooses</text>')
    return _svg(305, 150, b, 258)

def sc_charsheet(c, name="BOLT", feats=None, **k):
    b = bot(62, 62, c['color'], c['dark'], "wheel", 0, 1.5)
    b += (f'<polygon points="62,20 50,38 74,38" fill="#f59e0b"/>'
          f'<circle cx="62" cy="18" r="4" fill="#ef4444"/>')
    b += (f'<rect x="24" y="102" width="76" height="18" rx="9" fill="{c["dark"]}"/>'
          f'<text x="62" y="114.5" font-size="8.5" fill="#fff" text-anchor="middle" '
          f'font-weight="bold">“{name}”</text>')
    feats = feats or ["a name and one line of story", "a costume that does not block sensors",
                      "drives the parade route alone", "waves — lights + sound",
                      "a face on screen at the end"]
    y = 30
    for t in feats:
        b += (f'<text x="124" y="{y}" font-size="10" fill="#16a34a">☑</text>'
              f'<text x="138" y="{y}" font-size="8.6" fill="#334155">{t}</text>')
        y += 20
    return _svg(320, 136, b, 265)

def sc_rehearse(c, **k):
    runs = [("run 1", "#ef4444", "✗", "wandered off"), ("run 2", "#f59e0b", "~", "nearly"),
            ("run 3", "#16a34a", "✓", "clean")]
    b = ""
    for i, (lab, col, mark, note) in enumerate(runs):
        x = 22 + i * 96
        b += (f'<rect x="{x}" y="26" width="84" height="72" rx="7" fill="#fff" '
              f'stroke="{col}" stroke-width="2"/>'
              f'<text x="{x+42}" y="44" font-size="8.6" font-weight="bold" fill="{col}" '
              f'text-anchor="middle">{lab}</text>'
              f'<text x="{x+42}" y="72" font-size="22" font-weight="bold" fill="{col}" '
              f'text-anchor="middle">{mark}</text>'
              f'<text x="{x+42}" y="90" font-size="7.6" fill="#64748b" '
              f'text-anchor="middle">{note}</text>')
    b += (f'<rect x="22" y="108" width="276" height="22" rx="6" fill="#fef9ec" '
          f'stroke="#d97706" stroke-width="1.5"/>'
          f'<text x="160" y="123" font-size="8.6" fill="#92400e" text-anchor="middle" '
          f'font-weight="bold">three clean runs in a row → freeze the program, no more changes</text>')
    return _svg(320, 140, b, 265)


# --- grade 5: sense & react -------------------------------------------------

def sc_sensortour(c, **k):
    b = bot(150, 72, c['color'], c['dark'], "wheel", 0, 1.0)
    labels = [(120, 28, "Ultrasonic — how far?", "end", 132, 34, 140, 58),
              (120, 120, "Quad RGB — what colour?", "end", 132, 112, 140, 86),
              (180, 28, "microphone — how loud?", "start", 168, 34, 160, 58),
              (182, 75, "light — how bright?", "start", 178, 72, 172, 72),
              (180, 120, "gyro — which way up?", "start", 168, 112, 160, 86)]
    for x, y, t, anch, x1, y1, x2, y2 in labels:
        b += (f'<text x="{x}" y="{y}" font-size="8" font-weight="bold" fill="{c["dark"]}" '
              f'text-anchor="{anch}">{t}</text>')
        b += (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#94a3b8" '
              f'stroke-width="1.2" stroke-dasharray="3,2"/>')
    b += ('<text x="150" y="146" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">five senses, all live on screen — read them before using them</text>')
    return _svg(300, 152, b, 262)

def sc_ifelse(c, **k):
    b = (f'<polygon points="150,18 226,54 150,90 74,54" fill="#fff" stroke="{c["color"]}" '
         f'stroke-width="2.2"/>'
         f'<text x="150" y="50" font-size="8.4" fill="{c["dark"]}" text-anchor="middle" '
         f'font-weight="bold">distance</text>'
         f'<text x="150" y="62" font-size="8.4" fill="{c["dark"]}" text-anchor="middle" '
         f'font-weight="bold">&lt; 15 cm ?</text>')
    b += (f'<line x1="74" y1="54" x2="40" y2="54" stroke="#16a34a" stroke-width="2"/>'
          f'<line x1="40" y1="54" x2="40" y2="86" stroke="#16a34a" stroke-width="2"/>'
          f'<line x1="226" y1="54" x2="260" y2="54" stroke="#ef4444" stroke-width="2"/>'
          f'<line x1="260" y1="54" x2="260" y2="86" stroke="#ef4444" stroke-width="2"/>')
    b += (f'<text x="56" y="48" font-size="8" font-weight="bold" fill="#16a34a">YES</text>'
          f'<text x="234" y="48" font-size="8" font-weight="bold" fill="#ef4444">NO</text>')
    for x, col, t1, t2 in [(40, "#16a34a", "stop", "eyes red"), (260, "#ef4444", "drive on", "eyes green")]:
        b += (f'<rect x="{x-46}" y="86" width="92" height="34" rx="6" fill="#fff" '
              f'stroke="{col}" stroke-width="2"/>'
              f'<text x="{x}" y="100" font-size="8.6" fill="#334155" text-anchor="middle" '
              f'font-weight="bold">{t1}</text>'
              f'<text x="{x}" y="112" font-size="7.8" fill="#64748b" text-anchor="middle">{t2}</text>')
    b += ('<text x="150" y="136" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">one question, two answers — the robot always does exactly one of them</text>')
    return _svg(310, 144, b, 265)

def sc_sdaloop(c, **k):
    import math
    steps = [("SENSE", "#0891b2", "distance"), ("DECIDE", c["color"], "too close?"),
             ("ACT", "#d97706", "stop / go")]
    b = ""
    cx, cy, r_ = 150, 68, 44
    for i, (name, col, sub) in enumerate(steps):
        a = math.radians(-90 + i * 120)
        x, y = cx + r_ * math.cos(a), cy + r_ * math.sin(a)
        b += (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="25" fill="{col}"/>'
              f'<text x="{x:.0f}" y="{y+2:.0f}" font-size="8.2" font-weight="bold" fill="#fff" '
              f'text-anchor="middle">{name}</text>'
              f'<text x="{x:.0f}" y="{y+12:.0f}" font-size="6.4" fill="#fff" opacity="0.85" '
              f'text-anchor="middle">{sub}</text>')
    b += arrow_marker("sda", "#94a3b8")
    for i in range(3):
        a1 = math.radians(-90 + i * 120 + 32)
        a2 = math.radians(-90 + (i + 1) * 120 - 32)
        b += (f'<path d="M {cx + r_*math.cos(a1):.0f},{cy + r_*math.sin(a1):.0f} '
              f'A {r_},{r_} 0 0 1 {cx + r_*math.cos(a2):.0f},{cy + r_*math.sin(a2):.0f}" '
              f'fill="none" stroke="#94a3b8" stroke-width="2" marker-end="url(#sda)"/>')
    b += (f'<rect x="6" y="6" width="288" height="126" rx="10" fill="none" '
          f'stroke="{c["color"]}" stroke-width="2.5" stroke-dasharray="8,5"/>'
          f'<rect x="18" y="0" width="74" height="13" fill="#fff"/>'
          f'<text x="55" y="10" font-size="8.6" font-weight="bold" fill="{c["dark"]}" '
          f'text-anchor="middle">forever</text>')
    b += ('<text x="150" y="146" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">forever + if = the robot is alive and deciding for itself</text>')
    return _svg(302, 152, b, 258)

def sc_colours(c, **k):
    cols = [("#ef4444", "red"), ("#22c55e", "green"), ("#3b82f6", "blue"), ("#facc15", "yellow")]
    b = ('<rect x="16" y="86" width="272" height="26" rx="4" fill="#fff" stroke="#cbd5e1" '
         'stroke-width="1.5"/>'
         '<text x="152" y="103" font-size="8" fill="#64748b" text-anchor="middle">'
         'calibrate on white paper first — 12–13 mm off the floor</text>')
    for i, (col, name) in enumerate(cols):
        x = 30 + i * 66
        b += (f'<rect x="{x}" y="30" width="46" height="34" rx="4" fill="{col}"/>'
              f'<text x="{x+23}" y="76" font-size="8" font-weight="bold" fill="{col}" '
              f'text-anchor="middle">“{name}”</text>')
    b += ('<text x="152" y="20" font-size="8.4" font-weight="bold" fill="#64748b" '
          'text-anchor="middle">the Quad RGB sensor names 8 colours</text>')
    b += bot(152, 128, c['color'], c['dark'], "wheel", 0, 0.85)
    return _svg(304, 148, b, 258)

def sc_colourcmd(c, **k):
    b = '<line x1="16" y1="76" x2="292" y2="76" stroke="#e2e8f0" stroke-width="26"/>'
    cmds = [(96, "#ef4444", "STOP"), (172, "#22c55e", "TURN"), (244, "#3b82f6", "DANCE")]
    for x, col, t in cmds:
        b += (f'<rect x="{x-14}" y="64" width="28" height="24" rx="3" fill="{col}"/>'
              f'<text x="{x}" y="{54}" font-size="8.2" font-weight="bold" fill="{col}" '
              f'text-anchor="middle">{t}</text>')
    b += bot(44, 76, c['color'], c['dark'], "wheel", 0, 1.0)
    b += arrow_marker("cc5", "#64748b")
    b += (f'<line x1="60" y1="104" x2="270" y2="104" stroke="#64748b" stroke-width="1.4" '
          f'stroke-dasharray="4,3" marker-end="url(#cc5)"/>')
    b += ('<text x="152" y="126" font-size="8" fill="#64748b" text-anchor="middle">'
          'the floor is the program — rearrange the cards, change the behaviour</text>'
          '<text x="152" y="142" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">colours the robot reads as commands</text>')
    return _svg(304, 150, b, 258)

def sc_lightdark(c, **k):
    b = (f'<rect x="12" y="20" width="138" height="98" rx="8" fill="#0f172a"/>'
         f'<rect x="152" y="20" width="138" height="98" rx="8" fill="#fef9ec"/>')
    b += (f'<text x="81" y="36" font-size="8.4" font-weight="bold" fill="#94a3b8" '
          f'text-anchor="middle">DARK → night mode</text>'
          f'<text x="221" y="36" font-size="8.4" font-weight="bold" fill="#92400e" '
          f'text-anchor="middle">BRIGHT → wide awake</text>')
    b += bot(81, 76, c['color'], c['dark'], "wheel", 0, 1.15)
    for i in range(5):
        b += f'<circle cx="{57 + i*12}" cy="106" r="3.4" fill="#3b82f6" opacity="0.85"/>'
    b += bot(221, 76, c['color'], c['dark'], "wheel", 0, 1.15)
    b += (f'<polygon points="252,32 268,44 258,54" fill="#facc15"/>')
    for a in (0, 25, -25):
        import math
        b += (f'<line x1="256" y1="44" x2="{256 - 22*math.cos(math.radians(a)):.0f}" '
              f'y2="{44 + 22*math.sin(math.radians(a)):.0f}" stroke="#facc15" stroke-width="2"/>')
    b += ('<text x="151" y="138" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">the CyberPi light sensor — same robot, two behaviours</text>')
    return _svg(302, 146, b, 258)

def sc_counter(c, **k):
    b = ('<rect x="90" y="10" width="124" height="70" rx="8" fill="#334155"/>'
         '<rect x="96" y="16" width="112" height="58" rx="4" fill="#0f172a"/>'
         '<text x="152" y="34" font-size="9" fill="#94a3b8" text-anchor="middle">obstacles</text>'
         '<text x="152" y="66" font-size="28" font-weight="bold" fill="#7dd3fc" '
         'text-anchor="middle">7</text>')
    boxes = 4
    for i in range(boxes):
        b += (f'<rect x="{28 + i*66}" y="98" width="26" height="20" fill="#d6bb6f"/>'
              f'<text x="{41 + i*66}" y="{134}" font-size="9" font-weight="bold" '
              f'fill="{c["dark"]}" text-anchor="middle">+1</text>')
    b += (f'<text x="152" y="92" font-size="8" fill="#64748b" text-anchor="middle">'
          f'every time it sees one, the number goes up by one</text>')
    return _svg(304, 144, b, 258)

def sc_stations(c, st=None, caption=None, **k):
    st = st or [("① drive & turn", "#16a34a"), ("② repeat a shape", "#0891b2"),
                ("③ lights + sound", "#7c3aed")]
    st = [tuple(x) for x in st]
    b = ""
    for i, (t, col) in enumerate(st):
        x = 18 + i * 95
        b += (f'<rect x="{x}" y="26" width="84" height="74" rx="8" fill="#fff" stroke="{col}" '
              f'stroke-width="2"/>'
              f'<text x="{x+42}" y="44" font-size="8.2" font-weight="bold" fill="{col}" '
              f'text-anchor="middle">{t}</text>')
        b += bot(x + 42, 72, col, c['dark'], "wheel", 0, 0.72)
    b += arrow_marker("stn", "#94a3b8")
    for i in range(2):
        x = 104 + i * 95
        b += (f'<line x1="{x}" y1="112" x2="{x+72}" y2="112" stroke="#94a3b8" stroke-width="1.6" '
              f'marker-end="url(#stn)"/>')
    cap = caption or "rotate the stations — everything from last year, recalled in 45 minutes"
    b += (f'<text x="152" y="132" font-size="8.5" fill="#334155" text-anchor="middle" '
          f'font-weight="bold">{cap}</text>')
    return _svg(304, 140, b, 262)

def sc_talentshow(c, **k):
    b = ('<rect x="18" y="16" width="268" height="16" rx="4" fill="#7c2d12"/>')
    for i in range(9):
        b += (f'<path d="M {26 + i*30},32 q 15,16 30,0" fill="#b91c1c" opacity="0.9"/>')
    b += (f'<rect x="30" y="106" width="150" height="11" rx="4" fill="#94a3b8"/>')
    b += bot(104, 86, c['color'], c['dark'], "wheel", 0, 1.35)
    b += (f'<text x="104" y="56" font-size="15" fill="#facc15" text-anchor="middle">★</text>')
    judges = [("reliable", "#16a34a"), ("a real sensor", "#0891b2"), ("character", "#7c3aed")]
    b += ('<text x="242" y="50" font-size="7.6" fill="#64748b" text-anchor="middle" '
          'font-weight="bold">JUDGED ON</text>')
    for i, (t, col) in enumerate(judges):
        y = 58 + i * 22
        b += (f'<rect x="198" y="{y}" width="88" height="18" rx="9" fill="#fff" stroke="{col}" '
              f'stroke-width="1.6"/>'
              f'<text x="242" y="{y+12}" font-size="7.6" fill="{col}" text-anchor="middle" '
              f'font-weight="bold">{t}</text>')
    for x in (42, 66, 90, 114, 138, 162):
        b += (f'<circle cx="{x}" cy="126" r="5.5" fill="#94a3b8"/>'
              f'<rect x="{x-5}" y="131" width="10" height="8" rx="3" fill="#cbd5e1"/>')
    b += ('<text x="152" y="148" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">three tricks, one of them genuinely sensor-driven — judged live</text>')
    return _svg(304, 152, b, 250)


# --- grade 6: autonomy & teamwork -------------------------------------------

def sc_healthcheck(c, checks=None, caption=None, **k):
    checks = checks or [("motors turn", True), ("ultrasonic reads", True),
                        ("Quad RGB calibrates", False), ("screen + LEDs", True),
                        ("battery charged", True)]
    checks = [(item, True) if isinstance(item, str) else item for item in checks]
    b = bot(58, 62, c['color'], c['dark'], "wheel", 0, 1.4)
    y = 24
    for t, ok in checks:
        mark, col = ("☑", "#16a34a") if ok else ("☒", "#ef4444")
        b += (f'<text x="122" y="{y}" font-size="10.5" fill="{col}">{mark}</text>'
              f'<text x="138" y="{y}" font-size="8.4" fill="#334155">{t}</text>')
        y += 19
    b += (f'<rect x="118" y="108" width="176" height="20" rx="6" fill="#fee2e2" '
          f'stroke="#ef4444" stroke-width="1.4"/>'
          f'<text x="206" y="122" font-size="8" fill="#991b1b" text-anchor="middle" '
          f'font-weight="bold">one fault found → now find out why</text>')
    caption = caption or "every robot passes the same five checks before we start"
    b += (f'<text x="152" y="144" font-size="8.5" fill="#334155" text-anchor="middle" '
          f'font-weight="bold">{caption}</text>')
    return _svg(304, 152, b, 262)


def sc_roverbuild(c, stage="modules", **k):
    """Honest build outcomes for the two Rover assembly steps."""
    b = ""
    if stage == "modules":
        for x, flip in ((86, -1), (218, 1)):
            b += (f'<rect x="{x-45}" y="50" width="90" height="38" rx="18" fill="#1e293b"/>'
                  f'<circle cx="{x-26}" cy="69" r="11" fill="#64748b"/>'
                  f'<circle cx="{x+26}" cy="69" r="11" fill="#64748b"/>'
                  f'<path d="M {x},{69} l {flip*18},-12" stroke="{c["tint"]}" stroke-width="4"/>')
        b += (f'<text x="152" y="27" font-size="9" font-weight="bold" fill="{c["dark"]}" '
              f'text-anchor="middle">LEFT and RIGHT track modules mirror each other</text>'
              '<text x="152" y="112" font-size="8" fill="#64748b" text-anchor="middle">'
              'both hubs spin freely · track grain points the same way</text>')
        caption = "two finished, cross-checked track modules"
    else:
        b += bot(152, 67, c['color'], c['dark'], "tank", 0, 2.0)
        b += ('<text x="152" y="112" font-size="8" fill="#64748b" text-anchor="middle">'
              'crossed motor cables · eight boards fitted · cables clear</text>')
        caption = "the Rover is assembled, secure, and rolls freely by hand"
    b += (f'<text x="152" y="140" font-size="8.5" fill="#334155" text-anchor="middle" '
          f'font-weight="bold">{caption}</text>')
    return _svg(304, 148, b, 262)

def _blockstack(x, y, w, rows, col, head):
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{22 + len(rows)*24}" rx="7" fill="#fff" '
           f'stroke="{col}" stroke-width="2"/>'
           f'<rect x="{x}" y="{y}" width="{w}" height="20" rx="7" fill="{col}"/>'
           f'<text x="{x + w/2}" y="{y+14}" font-size="8.6" font-weight="bold" fill="#fff" '
           f'text-anchor="middle">{head}</text>')
    for i, t in enumerate(rows):
        out += (f'<rect x="{x+8}" y="{y + 28 + i*24}" width="{w-16}" height="18" rx="4" '
                f'fill="#e2e8f0"/>'
                f'<text x="{x + w/2}" y="{y + 40 + i*24}" font-size="7.4" fill="#1e293b" '
                f'text-anchor="middle">{t}</text>')
    return out

def sc_myblock(c, **k):
    b = _blockstack(14, 20, 120, ["move forward 20 cm", "turn right 90°", "play note G4"],
                    "#64748b", "define  wave")
    b += f'<text x="150" y="72" font-size="16" fill="#64748b">→</text>'
    b += (f'<rect x="176" y="30" width="112" height="26" rx="13" fill="{c["color"]}"/>'
          f'<text x="232" y="47" font-size="10" font-weight="bold" fill="#fff" '
          f'text-anchor="middle">wave</text>')
    for i in range(2):
        b += (f'<rect x="176" y="{66 + i*26}" width="112" height="20" rx="10" '
              f'fill="{c["color"]}" opacity="{0.6 - i*0.2}"/>'
              f'<text x="232" y="{80 + i*26}" font-size="8.4" font-weight="bold" fill="#fff" '
              f'text-anchor="middle">wave</text>')
    b += ('<text x="232" y="132" font-size="7.8" fill="#64748b" text-anchor="middle">'
          'written once, used everywhere</text>'
          '<text x="150" y="146" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">your own block, with a name you chose</text>')
    return _svg(302, 152, b, 258)

def sc_library(c, **k):
    names = [("wave", "#0d9488"), ("spin", "#0891b2"), ("beep twice", "#7c3aed"),
             ("go home", "#d97706"), ("scan ahead", "#16a34a"), ("celebrate", "#e11d48")]
    b = ('<text x="152" y="20" font-size="8.4" font-weight="bold" fill="#64748b" '
         'text-anchor="middle">the team’s block library</text>')
    for i, (t, col) in enumerate(names):
        x = 20 + (i % 3) * 95
        y = 32 + (i // 3) * 32
        b += (f'<rect x="{x}" y="{y}" width="84" height="23" rx="11.5" fill="{col}"/>'
              f'<text x="{x+42}" y="{y+15.5}" font-size="8.2" font-weight="bold" fill="#fff" '
              f'text-anchor="middle">{t}</text>')
    b += (f'<rect x="20" y="102" width="264" height="22" rx="6" fill="#f8fafc" '
          f'stroke="{c["color"]}" stroke-width="1.5"/>'
          f'<text x="152" y="116" font-size="8" fill="{c["dark"]}" text-anchor="middle">'
          f'a good name says what it does — not how it does it</text>')
    b += ('<text x="152" y="138" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">six blocks the team wrote, named and reuse</text>')
    return _svg(304, 146, b, 262)

# The default machine is Grade 7's three moods. A step whose states are its own
# passes `params: {states: [[NAME, colour]], trans: [[from, to, label]], caption:}`
# -- Grade 8 step 10 has four jobs, and a diagram labelled PATROL/CHASE/REST on a
# page about idle/fetch/carry/deliver is worse than no diagram at all.
DEFAULT_STATES = [("PATROL", "#16a34a"), ("CHASE", "#e11d48"), ("REST", "#0891b2")]
DEFAULT_TRANS = [(0, 1, "sees something"), (1, 2, "lost it"), (2, 0, "rested")]
STATE_CAPTION = "one variable holds the mode — the robot behaves differently in each"


def sc_states(c, states=None, trans=None, caption=None, **k):
    import math
    st = [tuple(s) for s in (states or DEFAULT_STATES)]
    trans = [tuple(x) for x in (trans if trans is not None else DEFAULT_TRANS)]
    # A state may carry a third field: what the robot is actually DOING while it
    # is in that state. Named states alone ("CARRY") say nothing a reader can
    # check against the program, so the doing-part rides inside the box.
    subs = [(s[2] if len(s) > 2 else "") for s in st]
    wide = any(subs)
    hw, hh = (38, 17) if wide else (31, 12)
    b = arrow_marker("stm", "#94a3b8")
    cx, cy, r_ = 150, 64, 52
    # Three states read best as a triangle, four as a loop around a rectangle --
    # four on a circle would put every arrow on a diagonal and every label on top
    # of a box. Boxes carrying a doing-line are wider, so both layouts spread out
    # to leave gaps the labels can sit in.
    #
    # One arrow per pair. Two arrows between the same two boxes need two lines,
    # two labels and four arrowheads inside 116px of diagonal, and nothing stays
    # legible: a machine that loops back belongs in the caption, not the picture.
    if len(st) == 4:
        ytop, ybot = 12 + hh, 126 - hh
        pts = [(cx - 82, ytop), (cx + 82, ytop), (cx + 82, ybot), (cx - 82, ybot)]
    elif len(st) == 3 and wide:
        pts = [(cx, 26), (cx + 90, 100), (cx - 90, 100)]
    else:
        pts = [(cx + r_ * math.cos(math.radians(-90 + i * (360.0 / len(st)))),
                cy + r_ * math.sin(math.radians(-90 + i * (360.0 / len(st)))))
               for i in range(len(st))]
    for i, j, lab in trans:
        x1, y1 = pts[i]; x2, y2 = pts[j]
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1
        ux, uy = dx / d, dy / d

        def edge(pad, ux=ux, uy=uy, d=d):
            """How far along the line the box boundary is, plus `pad`."""
            tx = hw / abs(ux) if abs(ux) > 1e-6 else 1e9
            ty = hh / abs(uy) if abs(uy) > 1e-6 else 1e9
            return min(tx, ty, d / 2 - 2) + pad

        # trimmed to the box edges, so the arrowhead always lands on one
        ax, ay = x1 + ux * edge(2), y1 + uy * edge(2)
        bx, by = x2 - ux * edge(7), y2 - uy * edge(7)
        b += (f'<line x1="{ax:.0f}" y1="{ay:.0f}" x2="{bx:.0f}" y2="{by:.0f}" stroke="#94a3b8" '
              f'stroke-width="1.8" marker-end="url(#stm)"/>')
        # The pill is sized to its text and interrupts the line it labels. Off the
        # rectangle the line is a diagonal, so the pill is pushed clear of the
        # middle instead -- sitting on it would collide with the box behind.
        w = max(34, len(lab) * 3.9 + 12)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if len(st) == 4:
            lx, ly = mx, my
        else:
            vx, vy = mx - cx, my - cy
            vd = math.hypot(vx, vy) or 1
            push = 30 if wide else 22
            lx, ly = mx + vx / vd * push, my + vy / vd * push
        b += (f'<rect x="{lx-w/2:.0f}" y="{ly-7:.0f}" width="{w:.0f}" height="14" rx="7" '
              f'fill="#fff" stroke="#e2e8f0"/>'
              f'<text x="{lx:.0f}" y="{ly+3.5:.0f}" font-size="6.8" fill="#64748b" '
              f'text-anchor="middle">{lab}</text>')
    for (x, y), s, sub in zip(pts, st, subs):
        name, col = s[0], s[1]
        b += (f'<rect x="{x-hw:.0f}" y="{y-hh:.0f}" width="{hw*2}" height="{hh*2}" rx="12" '
              f'fill="{col}"/>')
        b += (f'<text x="{x:.0f}" y="{(y-4) if sub else (y+3.5):.0f}" font-size="8.4" '
              f'font-weight="bold" fill="#fff" text-anchor="middle">{name}</text>')
        if sub:
            b += (f'<text x="{x:.0f}" y="{y+9:.0f}" font-size="6.2" fill="#fff" opacity="0.85" '
                  f'text-anchor="middle">{sub}</text>')
    b += (f'<text x="150" y="148" font-size="8.5" fill="#334155" text-anchor="middle" '
          f'font-weight="bold">{caption or STATE_CAPTION}</text>')
    return _svg(300, 156, b, 262)


def sc_debug(c, **k):
    steps = [("PREDICT", "#0891b2", "say what it will do"), ("TEST", "#16a34a", "run it once"),
             ("OBSERVE", "#d97706", "what actually happened"), ("FIX", "#7c3aed", "change ONE thing")]
    b = ""
    for i, (name, col, sub) in enumerate(steps):
        x = 12 + i * 72
        words = sub.split()
        mid = len(words) // 2 + len(words) % 2
        l1, l2 = " ".join(words[:mid]), " ".join(words[mid:])
        b += (f'<rect x="{x}" y="34" width="64" height="50" rx="7" fill="{col}"/>'
              f'<text x="{x+32}" y="52" font-size="8" font-weight="bold" fill="#fff" '
              f'text-anchor="middle">{name}</text>'
              f'<text x="{x+32}" y="65" font-size="6.4" fill="#fff" opacity="0.9" '
              f'text-anchor="middle">{l1}</text>'
              f'<text x="{x+32}" y="75" font-size="6.4" fill="#fff" opacity="0.9" '
              f'text-anchor="middle">{l2}</text>')
        if i < 3:
            b += (f'<text x="{x+70}" y="64" font-size="13" fill="#94a3b8" '
                  f'text-anchor="middle">→</text>')
    b += arrow_marker("dbg", "#94a3b8")
    b += (f'<path d="M 276,86 C 292,114 150,124 44,112 C 32,110 28,100 30,90" fill="none" '
          f'stroke="#94a3b8" stroke-width="1.6" stroke-dasharray="4,3" marker-end="url(#dbg)"/>')
    b += ('<text x="152" y="20" font-size="8.4" font-weight="bold" fill="#64748b" '
          'text-anchor="middle">the bug hunt, every time, in this order</text>'
          '<text x="152" y="142" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">guessing is not debugging — predicting is</text>')
    return _svg(304, 150, b, 262)

def sc_junction(c, **k):
    b = ('<path d="M 40,110 L 160,110" stroke="#1e293b" stroke-width="8" stroke-linecap="round"/>'
         '<path d="M 160,110 L 160,32" stroke="#1e293b" stroke-width="8" stroke-linecap="round"/>'
         '<path d="M 160,110 L 280,110" stroke="#1e293b" stroke-width="8" stroke-linecap="round"/>')
    b += (f'<circle cx="160" cy="110" r="20" fill="none" stroke="{c["color"]}" '
          f'stroke-width="2" stroke-dasharray="4,3"/>'
          f'<text x="160" y="{140}" font-size="8" font-weight="bold" fill="{c["dark"]}" '
          f'text-anchor="middle">all four sensors see black = a junction</text>')
    b += bot(112, 110, c['color'], c['dark'], "wheel", 0, 0.95)
    b += arrow_marker("jn1", "#16a34a") + arrow_marker("jn2", "#94a3b8")
    b += (f'<line x1="176" y1="94" x2="176" y2="46" stroke="#16a34a" stroke-width="2" '
          f'marker-end="url(#jn1)"/>'
          f'<text x="196" y="60" font-size="8" font-weight="bold" fill="#16a34a">turn</text>'
          f'<line x1="190" y1="94" x2="262" y2="94" stroke="#94a3b8" stroke-width="2" '
          f'stroke-dasharray="4,3" marker-end="url(#jn2)"/>'
          f'<text x="226" y="86" font-size="8" fill="#94a3b8" text-anchor="middle">'
          f'or straight on</text>')
    b += ('<text x="152" y="22" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">the robot notices a choice — and the program has to make one</text>')
    return _svg(304, 148, b, 262)

def sc_maze(c, **k):
    walls = [(20, 20, 264, 6), (20, 20, 6, 108), (20, 122, 264, 6), (278, 20, 6, 108),
             (76, 20, 6, 60), (132, 68, 6, 60), (188, 20, 6, 60), (76, 68, 62, 6),
             (188, 96, 62, 6)]
    b = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#475569" rx="2"/>'
                for x, y, w, h in walls)
    b += arrow_marker("mz", c['color'])
    b += (f'<path d="M 48,100 L 48,44 L 104,44 L 104,100 L 160,100 L 160,44 L 216,44 '
          f'L 216,86 L 262,86" fill="none" stroke="{c["color"]}" stroke-width="2.2" '
          f'stroke-dasharray="5,4" marker-end="url(#mz)"/>')
    b += bot(48, 100, c['color'], c['dark'], "wheel", -90, 0.62)
    b += (f'<rect x="196" y="6" width="98" height="16" rx="8" fill="#fff"/>'
          f'<text x="245" y="18" font-size="8" font-weight="bold" fill="{c["dark"]}" '
          f'text-anchor="middle">rule: keep the wall on your left</text>')
    b += ('<text x="152" y="144" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">a rule, not a route — it solves a maze it has never seen</text>')
    return _svg(304, 152, b, 262)

def sc_deliver(c, **k):
    b = (f'<path d="M 24,104 C 100,104 96,44 168,44 C 226,44 226,96 268,96" fill="none" '
         f'stroke="#1e293b" stroke-width="7" stroke-linecap="round"/>')
    b += (f'<rect x="244" y="66" width="46" height="46" rx="6" fill="#fef9ec" '
          f'stroke="#d97706" stroke-width="2.5" stroke-dasharray="6,4"/>'
          f'<text x="267" y="{60}" font-size="8.2" font-weight="bold" fill="#d97706" '
          f'text-anchor="middle">DROP ZONE</text>')
    b += bot(168, 44, c['color'], c['dark'], "wheel", 20, 1.05)
    b += flag(28, 118)
    b += (f'<rect x="86" y="12" width="118" height="20" rx="6" fill="#fff" stroke="{c["color"]}" '
          f'stroke-width="1.5"/>'
          f'<text x="145" y="26" font-size="7.8" fill="{c["dark"]}" text-anchor="middle">'
          f'arrive → lights, sound, message</text>')
    b += ('<text x="152" y="140" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">navigate there on its own, then say so — clearly</text>')
    return _svg(304, 148, b, 262)

def sc_console(c, **k):
    b = ('<rect x="20" y="24" width="120" height="102" rx="10" fill="#334155"/>'
         '<rect x="30" y="34" width="100" height="52" rx="4" fill="#0f172a"/>')
    b += (f'<circle cx="56" cy="66" r="7" fill="#facc15"/>'
          f'<rect x="96" y="52" width="10" height="10" fill="{c["tint"]}"/>'
          f'<rect x="110" y="70" width="10" height="10" fill="{c["tint"]}"/>'
          f'<text x="80" y="98" font-size="7" fill="#94a3b8" text-anchor="middle">'
          f'score 120</text>')
    b += (f'<circle cx="52" cy="110" r="12" fill="#1e293b" stroke="#64748b" stroke-width="1.4"/>'
          f'<circle cx="57" cy="106" r="6" fill="{c["color"]}"/>'
          f'<circle cx="98" cy="106" r="6.5" fill="#22c55e"/>'
          f'<circle cx="98" cy="120" r="6.5" fill="#ef4444"/>')
    b += (f'<rect x="164" y="24" width="126" height="102" rx="8" fill="#f8fafc" '
          f'stroke="#cbd5e1" stroke-width="1.6"/>'
          f'<text x="227" y="40" font-size="7.6" fill="#64748b" text-anchor="middle">'
          f'the same joystick, two jobs</text>')
    b += bot(200, 76, c['color'], c['dark'], "wheel", 0, 0.8)
    b += (f'<text x="227" y="112" font-size="12" fill="#94a3b8" text-anchor="middle">⇅</text>'
          f'<rect x="240" y="58" width="40" height="34" rx="4" fill="#0f172a"/>'
          f'<circle cx="252" cy="72" r="4" fill="{c["tint"]}"/>'
          f'<rect x="264" y="78" width="8" height="8" fill="#facc15"/>')
    b += ('<text x="152" y="142" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">CyberPi as a games console — drive a robot or a sprite</text>')
    return _svg(304, 148, b, 236)

def sc_network(c, **k):
    b = ""
    for i, (x, lab) in enumerate([(58, "robot A"), (246, "robot B")]):
        b += bot(x, 92, c['color'], c['dark'], "wheel", 0, 1.15)
        b += (f'<text x="{x}" y="122" font-size="8.4" font-weight="bold" fill="{c["dark"]}" '
              f'text-anchor="middle">{lab}</text>')
    b += (f'<rect x="126" y="16" width="52" height="18" rx="4" fill="#475569"/>'
          f'<circle cx="138" cy="25" r="2.4" fill="#22c55e"/>'
          f'<text x="152" y="48" font-size="7.6" fill="#64748b" text-anchor="middle">'
          f'the classroom Wi-Fi</text>')
    for side in (-1, 1):
        for j in range(3):
            r_ = 10 + j * 9
            b += (f'<path d="M {152 + side*(16+r_)},{28 - r_*0.5} A {r_},{r_} 0 0 '
                  f'{1 if side > 0 else 0} {152 + side*(16+r_)},{28 + r_*0.5}" fill="none" '
                  f'stroke="{c["color"]}" stroke-width="1.6" opacity="{0.85 - j*0.22:.2f}"/>')
    b += arrow_marker("net", c['color'])
    b += (f'<line x1="84" y1="82" x2="216" y2="82" stroke="{c["color"]}" stroke-width="2" '
          f'stroke-dasharray="5,4" marker-end="url(#net)"/>'
          f'<rect x="112" y="66" width="80" height="17" rx="8" fill="#fff" '
          f'stroke="{c["color"]}" stroke-width="1.5"/>'
          f'<text x="152" y="78" font-size="7.6" fill="{c["dark"]}" text-anchor="middle" '
          f'font-weight="bold">“your turn”</text>')
    b += ('<text x="152" y="142" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">one robot broadcasts, the other is listening for it</text>')
    return _svg(304, 150, b, 262)

def sc_relay(c, **k):
    b = ('<rect x="16" y="52" width="128" height="42" rx="8" fill="#f8fafc" stroke="#cbd5e1"/>'
         '<rect x="160" y="52" width="128" height="42" rx="8" fill="#f8fafc" stroke="#cbd5e1"/>')
    b += (f'<text x="80" y="42" font-size="8" font-weight="bold" fill="#16a34a" '
          f'text-anchor="middle">leg 1 — team A</text>'
          f'<text x="224" y="42" font-size="8" font-weight="bold" fill="#7c3aed" '
          f'text-anchor="middle">leg 2 — team B</text>')
    b += bot(56, 73, c['color'], c['dark'], "wheel", 0, 0.9)
    b += bot(200, 73, c['color'], c['dark'], "wheel", 0, 0.9)
    b += arrow_marker("rl", "#94a3b8")
    b += (f'<line x1="76" y1="73" x2="136" y2="73" stroke="#94a3b8" stroke-width="1.6" '
          f'stroke-dasharray="4,3" marker-end="url(#rl)"/>'
          f'<line x1="220" y1="73" x2="280" y2="73" stroke="#94a3b8" stroke-width="1.6" '
          f'stroke-dasharray="4,3" marker-end="url(#rl)"/>')
    b += (f'<path d="M 144,73 C 150,20 154,20 160,73" fill="none" stroke="{c["color"]}" '
          f'stroke-width="2.2" marker-end="url(#rl)"/>'
          f'<rect x="108" y="6" width="88" height="17" rx="8.5" fill="{c["color"]}"/>'
          f'<text x="152" y="18" font-size="7.6" fill="#fff" text-anchor="middle" '
          f'font-weight="bold">“leg 1 done, GO”</text>')
    b += ('<text x="152" y="112" font-size="7.8" fill="#64748b" text-anchor="middle">'
          'nobody touches either robot — the handover is a message</text>'
          '<text x="152" y="130" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">two teams, two robots, one run</text>')
    return _svg(304, 138, b, 262)

def sc_protocol(c, **k):
    rows = [("READY", "A → B", "I am at the start"), ("GO", "A → B", "your turn now"),
            ("DONE", "B → A", "I finished"), ("HELP", "either", "I am stuck")]
    b = (f'<rect x="16" y="16" width="272" height="20" rx="5" fill="{c["dark"]}"/>'
         f'<text x="58" y="30" font-size="8" fill="#fff" text-anchor="middle" '
         f'font-weight="bold">message</text>'
         f'<text x="140" y="30" font-size="8" fill="#fff" text-anchor="middle" '
         f'font-weight="bold">who sends it</text>'
         f'<text x="228" y="30" font-size="8" fill="#fff" text-anchor="middle" '
         f'font-weight="bold">what it means</text>')
    for i, (m, who, mean) in enumerate(rows):
        y = 36 + i * 22
        bg = "#f8fafc" if i % 2 == 0 else "#fff"
        b += (f'<rect x="16" y="{y}" width="272" height="22" fill="{bg}" stroke="#e2e8f0"/>'
              f'<text x="58" y="{y+15}" font-size="8" fill="{c["dark"]}" text-anchor="middle" '
              f'font-weight="bold">{m}</text>'
              f'<text x="140" y="{y+15}" font-size="7.8" fill="#64748b" '
              f'text-anchor="middle">{who}</text>'
              f'<text x="228" y="{y+15}" font-size="7.8" fill="#334155" '
              f'text-anchor="middle">{mean}</text>')
    b += ('<text x="152" y="142" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">agree the words first — then both teams code to the same table</text>')
    return _svg(304, 150, b, 262)

def sc_gamesplan(c, **k):
    events = [("SPRINT", "#16a34a", "fastest clean lap"), ("SLALOM", "#0891b2", "no cones down"),
              ("MAZE", "#7c3aed", "out in under 2 min")]
    b = ('<text x="152" y="18" font-size="8.4" font-weight="bold" fill="#64748b" '
         'text-anchor="middle">three events + one cooperative relay</text>')
    for i, (t, col, rule) in enumerate(events):
        x = 16 + i * 92
        b += (f'<rect x="{x}" y="26" width="84" height="52" rx="8" fill="#fff" stroke="{col}" '
              f'stroke-width="2"/>'
              f'<text x="{x+42}" y="46" font-size="9" font-weight="bold" fill="{col}" '
              f'text-anchor="middle">{t}</text>'
              f'<text x="{x+42}" y="62" font-size="7" fill="#64748b" text-anchor="middle">'
              f'{rule}</text>')
    b += (f'<rect x="16" y="88" width="272" height="32" rx="8" fill="{c["light"]}" '
          f'stroke="{c["color"]}" stroke-width="2"/>'
          f'<text x="152" y="102" font-size="9" font-weight="bold" fill="{c["dark"]}" '
          f'text-anchor="middle">THE RELAY — two teams, handover by message</text>'
          f'<text x="152" y="114" font-size="7.4" fill="#64748b" text-anchor="middle">'
          f'you cannot win it alone</text>')
    b += ('<text x="152" y="136" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">every event has a written rule the teams agreed</text>')
    return _svg(304, 144, b, 262)

def sc_games(c, **k):
    b = ('<rect x="16" y="14" width="176" height="16" rx="4" fill="#7c2d12"/>'
         '<text x="104" y="26" font-size="9" font-weight="bold" fill="#fde68a" '
         'text-anchor="middle">ROBOT GAMES</text>')
    lanes = [("SPRINT", "#16a34a"), ("SLALOM", "#0891b2"), ("RELAY", "#7c3aed")]
    for i, (t, col) in enumerate(lanes):
        y = 44 + i * 30
        b += (f'<rect x="16" y="{y}" width="176" height="22" rx="5" fill="#f1f5f9"/>'
              f'<text x="30" y="{y+15}" font-size="7.4" font-weight="bold" fill="{col}">{t}</text>')
        b += bot(88 + i * 20, y + 11, col, c['dark'], "wheel", 0, 0.5)
        if i == 2:
            b += bot(170, y + 11, "#c084fc", c['dark'], "wheel", 0, 0.5)
            b += (f'<path d="M 140,{y+3} C 148,{y-7} 158,{y-7} 164,{y+3}" fill="none" '
                  f'stroke="{c["color"]}" stroke-width="1.6"/>')
    b += (f'<rect x="204" y="14" width="88" height="106" rx="8" fill="#fff" '
          f'stroke="{c["color"]}" stroke-width="2"/>'
          f'<text x="248" y="30" font-size="8" font-weight="bold" fill="{c["dark"]}" '
          f'text-anchor="middle">SCOREBOARD</text>')
    for i, (team, pts) in enumerate([("Bolt", "24"), ("Zap", "21"), ("Nova", "19"), ("Pip", "15")]):
        y = 44 + i * 18
        b += (f'<text x="216" y="{y}" font-size="7.8" fill="#334155">{team}</text>'
              f'<text x="280" y="{y}" font-size="7.8" font-weight="bold" fill="{c["dark"]}" '
              f'text-anchor="end">{pts}</text>'
              f'<line x1="214" y1="{y+3}" x2="282" y2="{y+3}" stroke="#e2e8f0"/>')
    b += ('<text x="152" y="138" font-size="8.5" fill="#334155" text-anchor="middle" '
          'font-weight="bold">heats, a relay final, and a scoreboard everyone can read</text>')
    return _svg(304, 146, b, 262)


SCENES = {
    "healthcheck": sc_healthcheck, "myblock": sc_myblock, "library": sc_library,
    "states": sc_states, "debug": sc_debug, "junction": sc_junction, "maze": sc_maze,
    "deliver": sc_deliver, "console": sc_console, "network": sc_network, "relay": sc_relay,
    "protocol": sc_protocol, "gamesplan": sc_gamesplan, "games": sc_games,
    "sensortour": sc_sensortour, "ifelse": sc_ifelse, "sdaloop": sc_sdaloop,
    "colours": sc_colours, "colourcmd": sc_colourcmd, "lightdark": sc_lightdark,
    "counter": sc_counter, "stations": sc_stations, "talentshow": sc_talentshow,
    "buttons": sc_buttons, "charsheet": sc_charsheet, "rehearse": sc_rehearse,
    "hello": sc_hello, "garage": sc_garage, "quarter": sc_quarter, "repeat": sc_repeat,
    "lights": sc_lights, "music": sc_music, "joystick": sc_joystick, "tilt": sc_tilt,
    "clap": sc_clap, "storyboard": sc_storyboard, "parade": sc_parade,
    "cards": sc_cards, "build": sc_build, "expl": sc_expl, "screen": sc_screen_text, "path": sc_path,
    "calibrate": sc_calibrate, "dance": sc_dance, "sonar": sc_sonar, "patrol": sc_patrol, "wander": sc_wander,
    "line": sc_line, "events": sc_events, "rescue": sc_rescue, "teardown": sc_teardown,
    "tank_compare": sc_tank_compare, "slope": sc_slope, "chart": sc_chart, "pixel": sc_pixel,
    "moods": sc_moods, "react": sc_react, "ml": sc_ml, "mirror": sc_mirror, "prompt": sc_prompt,
    "controller": sc_controller, "blocks2py": sc_blocks2py, "character": sc_character,
    "fair": sc_fair, "pyeditor": sc_pyeditor, "graph2": sc_graph2, "arm": sc_arm,
    "work": sc_work, "kanban": sc_kanban, "demo": sc_demo, "worksheet": sc_worksheet,
    "roverbuild": sc_roverbuild,
}
