# -*- coding: utf-8 -*-
"""Build the three per-grade teaching-support PDFs."""
import common
import grade7, grade8, grade9

def unit_strip(c):
    W, X0, bh = 600, 20, 34
    parts = ['<svg viewBox="0 0 660 100" width="620"><g font-family="Helvetica">']
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

def rhythm(c):
    segs = [(0,5,c["color"],"Setup"),(5,10,c["dark"],"Briefing"),(10,48,"#16a34a","Core hands-on work"),
            (48,55,"#d97706","Journal"),(55,60,"#64748b","Reset")]
    W, X0 = 600, 30
    parts = ['<svg viewBox="0 0 660 100" width="620"><g font-family="Helvetica">']
    for a,b,col,label in segs:
        x = X0 + a/60*W; w = (b-a)/60*W
        parts.append(f'<rect x="{x:.0f}" y="30" width="{w:.0f}" height="34" fill="{col}" rx="4"/>')
        cx = x + w/2
        if w > 70:
            parts.append(f'<text x="{cx:.0f}" y="51" font-size="11" font-weight="bold" fill="#fff" text-anchor="middle">{label}</text>')
        else:
            parts.append(f'<text x="{cx:.0f}" y="82" font-size="9" font-weight="bold" fill="{col}" text-anchor="middle">{label}</text>')
    for m in (0,5,10,48,55,60):
        x = X0 + m/60*W
        parts.append(f'<line x1="{x:.0f}" y1="26" x2="{x:.0f}" y2="68" stroke="#334155" stroke-width="1"/>'
                     f'<text x="{x:.0f}" y="20" font-size="9" fill="#334155" text-anchor="middle">{m}\u2032</text>')
    parts.append('</g></svg>')
    return "".join(parts)

MBOT2_BOX = [
    ("CyberPi", "\u00d71"), ("mBot2 Shield", "\u00d71 \u00b7 battery built in"), ("Chassis", "\u00d71"),
    ("Encoder motor", "\u00d72"), ("Wheel hub", "\u00d72"), ("Slick tyre", "\u00d72"), ("Mini wheel", "\u00d71"),
    ("Ultrasonic Sensor 2", "\u00d71"), ("Quad RGB Sensor", "\u00d71"),
    ("Motor cable", "\u00d72"), ("mBuild cable 10 cm", "\u00d72"), ("mBuild cable 20 cm", "\u00d71"),
    ("M4\u00d725 mm screw", "\u00d76"), ("M4\u00d714 mm screw", "\u00d76"), ("M4\u00d78 mm screw", "\u00d76"), ("M2.5\u00d712 mm screw", "\u00d74"),
    ("Line-following track map", "\u00d71"), ("USB cable", "\u00d71"), ("Screwdriver", "\u00d71"),
]
# Quantities marked "\u2265" are minimums derived by summing the guide's per-step callouts
# (the printed parts list shows names only, no counts \u2014 photo-verified 2026-07).
ROVER_BOX = [
    ("Servo pack", "\u00d72 used"), ("Bluetooth Controller", "\u00d71"), ("Track", "\u00d72"),
    ("Wheel hub", "\u00d74 halves used"), ("Small wheel hub", "\u00d72 used"), ("D shaft", "\u2265\u00d76"),
    ("Bracket 90\u00b0 3\u00d73", "\u2265\u00d76"), ("Bracket 120\u00b0 3\u00d73", "\u2265\u00d73"), ("U bracket", "\u2265\u00d74"),
    ("T plate", "\u00d72 used"), ("Slide beam 2\u00d74", "\u2265\u00d71"), ("Slide beam 2\u00d76", "\u2265\u00d71"), ("Plate 3\u00d78", "\u2265\u00d71"),
    ("Shaft collar", "\u00d712 used"), ("Flange bearing", "\u2265\u00d74"), ("Socket wrench", "\u00d71"),
    ("Screw M3\u00d76 mm", "\u00d712 used"), ("Screw M4\u00d710 mm", "\u2265\u00d730"), ("Screw M4\u00d722 mm", "\u2265\u00d714"), ("Screw M4\u00d730 mm", "\u2265\u00d78"), ("Nut", "\u2265\u00d730"),
    ("Plastic shock absorber", "spares \u2014 unused in build"), ("Metal shock absorber", "\u00d74 used"),
    ("Long plastic ring", "\u2265\u00d72"), ("Short plastic ring", "\u2265\u00d78"), ("Rubber band", "\u2265\u00d76"),
    ("Board 1\u20138 (body shells)", "peel paper film"), ("Quick Start Guide", "\u00d71"),
]

def box_table(title, color, items, note):
    rows = "".join(f'<div class="pitem"><b>{n}</b>{(" <span>" + q + "</span>") if q else ""}</div>' for n, q in items)
    return (f'<div class="boxcard" style="border-color:{color}">'
            f'<div class="boxhead" style="background:{color}">{title}</div>'
            f'<div class="pgrid">{rows}</div>'
            f'<div class="boxnote">{note}</div></div>')

def box_reference(c):
    parts_html = box_table("BOX 1 \u00b7 \u201cmBot2\u201d", "#2563eb", MBOT2_BOX,
        "Quantities from the official packing list. Bluetooth dongle NOT included \u2014 Makeblock advises it for older computers (sold separately).")
    if c["num"] != "7":
        parts_html += box_table("BOX 2 \u00b7 \u201cRover Robotics Add-on Pack\u201d", "#7c3aed", ROVER_BOX,
            "As printed on the box (no quantities given). Online docs: search \u201cmBot2 Rover\u201d at support.makeblock.com.")
        used = "Both boxes are used this year. Session parts panels tag every piece with its source box."
    else:
        used = "Grade 7 uses only Box 1. The Rover add-on box stays sealed until Grade 8 \u2014 store it safely."
    return f"""
<div style="page-break-before: always"></div>
<h2 class="section">The Boxes \u2014 Official Contents Reference</h2>
<p class="muted" style="margin-bottom:3mm">{used}</p>
{parts_html}
"""

CAP_BLURB = {
 "7": ("Rescue Run", "An autonomous mission: follow the line, avoid a surprise obstacle, stop precisely in the rescue zone, celebrate. Two scored attempts + a short team presentation.", "rescue"),
 "8": ("Companion Robot", "A robot character with custom emojis, three sensor-triggered behaviors, one ML interaction and full controller drive \u2014 presented at a Personality Fair with visitor feedback.", "fair"),
 "9": ("Robots at Work", "An autonomous mission simulating a real job: navigate by line, detect a marker, pick an object with the arm and deliver it \u2014 pitched and scored at Demo Day.", "work"),
}

def intro(c, mod):
    objectives = {
        "7": ["Assemble and maintain the mBot2 wheeled robot",
              "Explain the sense\u2013decide\u2013act loop and each sensor\u2019s role",
              "Write block programs: sequences, loops, conditionals, variables, events",
              "Calibrate precise motion; debug with predict \u2192 test \u2192 observe \u2192 fix",
              "Complete an autonomous line + obstacle mission (Rescue Run)"],
        "8": ["Rebuild into the Rover tank; explain tracked vs. wheeled trade-offs",
              "Design custom emojis and animations; build sensor-driven personality",
              "Train, break and de-bias an image-recognition model",
              "Use generative AI deliberately; write reusable prompt recipes",
              "Master the controller; read and edit first Python"],
        "9": ["Write, structure and review Python: functions, constants, state machines",
              "Implement and tune proportional control; argue with graphs",
              "Build the Ranger arm; program safe, reliable pick & place",
              "Run an engineering project: spec, sprints, reviews, recovery",
              "Deliver an autonomous mission and pitch it (Robots at Work)"],
    }[c["num"]]
    obj = "".join(f"<li>{o}</li>" for o in objectives)
    name, blurb, scene = CAP_BLURB[c["num"]]
    capsvg = common.SCENES[scene](c)
    return f"""
<div class="cover">
  <div class="kicker">Teaching Guide \u00b7 mBot2 Rover Robotics Program</div>
  <h1>Grade {c['num']}<br/>{c['theme'].split(' \u2014 ')[0]}</h1>
  <div class="sub">{c['theme'].split(' \u2014 ')[1] if ' \u2014 ' in c['theme'] else ''}</div>
  <div class="badges">
    <div class="badge"><b>20</b><span>sessions</span></div>
    <div class="badge"><b>1 h</b><span>each</span></div>
    <div class="badge"><b>{c['form'].split(' \u00b7 ')[0]}</b><span>{c['form'].split(' \u00b7 ')[1]}</span></div>
    <div class="badge"><b>{c['codemode']}</b><span>coding mode</span></div>
  </div>
  <div class="coverbox">
    <h3>\u2605 Final project: {name}</h3>
    <p>{blurb}</p>
  </div>
  <div class="coverfoot">Tutor edition \u2014 each session is one page: concept to teach \u00b7 timed lesson flow \u00b7 code \u00b7 pitfalls \u00b7 expected result with success criteria. Software: mBlock 5 \u00b7 Makeblock App \u00b7 1 kit per 2\u20133 students.</div>
</div>

<h2 class="section">Grade {c['num']} at a Glance</h2>
<div class="objbox"><h4>Learning objectives \u2014 by the end of the year, students can:</h4><ul>{obj}</ul></div>
<p><b>The 20 sessions, colored by unit</b> &nbsp;<span class="muted">\u2731 in session titles = buffer session (tolerates compression if the schedule slips)</span></p>
<div class="center">{unit_strip(c)}</div>
<p style="margin-top:4mm"><b>Every session runs on the same rhythm</b></p>
<div class="center">{rhythm(c)}</div>
<div class="notecard"><b>Non-negotiables for 1-hour sessions:</b> robots stay assembled between sessions on a labeled cart shelf \u00b7 code saved to mBlock cloud accounts every session \u00b7 battery rotation with a per-team battery manager \u00b7 extension cards at stations so fast teams never wait.</div>
<div class="warncard"><b>Known friction points this year:</b> {friction(c)}</div>
{box_reference(c)}
"""

def friction(c):
    return {
      "7": "first firmware pairing is slow (teacher dry run before Session 4) \u00b7 the Shield\u2019s battery is built in \u2014 charge robots via USB-C before class \u00b7 sensors must be mounted straight \u00b7 recalibrate the line sensor whenever floor or light changes \u00b7 the Rover box stays sealed all year.",
      "8": "the two Track assemblies mirror each other (classic build error) \u00b7 the Boards ship covered in paper film \u2014 peel while sorting \u00b7 turn calibration changes on tracks \u2014 redo it \u00b7 ML sessions need webcams + good light \u00b7 the Bluetooth Controller (Rover box) only responds after the robot is programmed (Session 16 teaches it explicitly).",
      "9": "the Ranger build guide is digital-only \u2014 download before Session 8 \u00b7 never force the arm past resistance (gears strip) \u00b7 exact Python function names vary by mBlock version: trust autocomplete \u00b7 rebuild capstone courses from tape-measure photos.",
    }[c["num"]]

def build(mod, outfile):
    c = mod.C
    for s in mod.S:
        s["parts"] = mod.PARTS.get(s["n"], [])
    common.build_grade_pdf(c, intro(c, mod), mod.S, outfile)
    print("built", outfile)

if __name__ == "__main__":
    build(grade7, "/home/claude/mbot2-grade7-teaching-guide.pdf")
    build(grade8, "/home/claude/mbot2-grade8-teaching-guide.pdf")
    build(grade9, "/home/claude/mbot2-grade9-teaching-guide.pdf")
