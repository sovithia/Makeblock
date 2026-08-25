# -*- coding: utf-8 -*-
"""Render the bench build guide as one illustrated PDF: ../DEMO-PREP.pdf.

⚠️ This file holds its own copy of the prose in DEMO-PREP-G7/G8/G9.md. It does
NOT read them. Edit one and you must edit the other, or the PDF goes stale — it
already did once, when the markdown was split into three tracks and this script
kept emitting the old merged three-capstone guide. If the duplication becomes a
problem again, the fix is to generate from the markdown, not to re-sync by hand.

Pulls real part photos from site/assets/parts/ and build/result schematics from
generator/scenes.py. Output: ../DEMO-PREP.pdf (next to DEMO-PREP.md, the index).

Usage: .venv/bin/python tools/build_demo_prep_pdf.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "generator"))
import scenes

C7 = {"color": "#0e7fc1", "dark": "#0a5c8c", "light": "#e3f1fa"}
C8 = {"color": "#8b3fc6", "dark": "#5f2b8a", "light": "#f2e8fa"}
C9 = {"color": "#d97706", "dark": "#9a4f08", "light": "#fdf0dd"}

P = "site/assets/parts"  # relative to base_url = ROOT


def img(pid, h=46):
    return f'<img src="{P}/{pid}.png" style="max-height:{h}px; max-width:70px"/>'


def strip(title, items):
    cells = "".join(
        f'<div class="cell">{img(pid)}<div class="clbl">{label}</div></div>'
        for pid, label in items)
    return f'<div class="strip"><div class="stitle">{title}</div>{cells}</div>'


def tanksvg(c):
    return (f'<svg viewBox="0 0 64 44" width="130"><g>'
            f'{scenes.bot(32, 22, c["color"], c["dark"], "tank", 0, 1.0)}</g></svg>')


def small(svg, w=195):
    """Shrink a scene SVG's display width (first width attr) to fit tight pages."""
    import re
    return re.sub(r'width="\d+"', f'width="{w}"', svg, count=1)


def steps(items):
    return "<ol class='st'>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>"


def checks(items):
    return ("<ul class='ck'>"
            + "".join(f"<li>☐&nbsp; {i}</li>" for i in items) + "</ul>")


def head(c, kicker, title):
    return (f'<div class="ghead" style="background:linear-gradient(110deg,{c["dark"]},{c["color"]})">'
            f'<div class="gk">{kicker}</div><h2>{title}</h2></div>')


def tb(headers, rows, cls="tb"):
    h = "".join(f"<th>{x}</th>" for x in headers)
    b = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><tr>{h}</tr>{b}</table>'


def score_sheet(c, title, phases):
    rows = [(p, pts, "", "") for p, pts in phases]
    rows.append(("<b>Total</b>", f"<b>{sum(int(p[1]) for p in phases)}</b>", "", ""))
    return (f'<div class="score" style="border-color:{c["color"]}">'
            f'<div class="stitle" style="color:{c["dark"]}">Score sheet — {title} '
            f'(print one per run)</div>'
            + tb(["Phase", "Points", "Attempt 1", "Attempt 2"], rows) + "</div>")


CSS = """
@page { size: A4; margin: 13mm 13mm 15mm 13mm;
  @bottom-center { content: "Demo prep · Session-20 capstones · " counter(page);
    font-size: 8pt; color: #94a3b8; font-family: Helvetica; } }
body { font-family: Helvetica, Arial, sans-serif; color: #1e293b; font-size: 9.3pt;
  line-height: 1.45; margin: 0; }
h1 { font-size: 19pt; margin: 0 0 1mm 0; color: #0f172a; }
.sub { color: #64748b; font-size: 9.5pt; margin-bottom: 5mm; }
h3 { font-size: 11pt; color: #0f172a; margin: 4mm 0 2mm 0; }
h4 { font-size: 9.6pt; color: #0f172a; margin: 3mm 0 1.5mm 0; text-transform: uppercase;
  letter-spacing: 1px; }
.ghead { border-radius: 9px; color: #fff; padding: 3mm 5mm; margin: 5mm 0 3mm 0; }
.ghead .gk { font-size: 7.5pt; text-transform: uppercase; letter-spacing: 2px; opacity: .9; }
.ghead h2 { margin: .5mm 0 0 0; font-size: 13.5pt; }
.brk { page-break-before: always; }
table.alloc { width: 100%; border-collapse: collapse; margin-bottom: 4mm; }
table.alloc th { background: #f1f5f9; font-size: 8.4pt; text-transform: uppercase;
  letter-spacing: 1px; color: #475569; padding: 2mm; text-align: left; }
table.alloc td { border-bottom: 1px solid #e2e8f0; padding: 2mm; vertical-align: middle;
  font-size: 9pt; }
table.alloc td.pic { text-align: center; width: 34mm; }
.strip { border: 1.4px solid #e2e8f0; border-radius: 8px; background: #fcfcfd;
  padding: 2mm 2.5mm; margin: 2.5mm 0; }
.stitle { font-size: 7.6pt; font-weight: bold; text-transform: uppercase;
  letter-spacing: 1.4px; color: #475569; margin-bottom: 1.5mm; }
.cell { display: inline-block; width: 21mm; text-align: center; vertical-align: top;
  margin: 0 .8mm 1.5mm .8mm; }
.clbl { font-size: 6.8pt; font-weight: bold; line-height: 1.15; margin-top: .6mm; }
ol.st { margin: 1.5mm 0 3mm 0; padding-left: 5.5mm; }
ol.st li { margin-bottom: 1.4mm; }
ul.ck { list-style: none; margin: 1mm 0 3mm 0; padding-left: 1.5mm; }
ul.ck li { margin-bottom: 1mm; }
.warn { background: #fef9ec; border-left: 4px solid #d97706; border-radius: 0 8px 8px 0;
  padding: 2.5mm 3.5mm; margin: 2.5mm 0; font-size: 8.8pt; }
.note { background: #f8fafc; border-left: 4px solid #0e7fc1; border-radius: 0 8px 8px 0;
  padding: 2.5mm 3.5mm; margin: 2.5mm 0; font-size: 8.8pt; }
.scene { text-align: center; margin: 2mm 0; }
.tworow { width: 100%; border-collapse: collapse; }
.tworow td { width: 50%; vertical-align: top; text-align: center; padding: 1mm; }
.code { background: #0f172a; color: #e2e8f0; border-radius: 8px; padding: 3mm 3.5mm;
  font-family: "DejaVu Sans Mono", monospace; font-size: 7.4pt; line-height: 1.5;
  white-space: pre-wrap; margin: 2mm 0; }
.code .cm { color: #94a3b8; }
.codelabel { font-size: 7.4pt; font-weight: bold; text-transform: uppercase;
  letter-spacing: 1px; color: #64748b; margin: 2mm 0 .5mm 0; }
table.tb { width: 100%; border-collapse: collapse; margin: 1.5mm 0 3mm 0; }
table.tb td, table.tb th { border-bottom: 1px solid #e2e8f0; padding: 1.5mm 2mm;
  font-size: 8.6pt; text-align: left; vertical-align: top; }
table.tb th { background: #f1f5f9; font-size: 7.8pt; text-transform: uppercase;
  letter-spacing: 1px; color: #475569; }
.score { border: 1.8px solid; border-radius: 9px; padding: 2.5mm 3mm 1mm 3mm; margin: 3mm 0; }
.score table.tb td:nth-child(3), .score table.tb td:nth-child(4) { width: 22mm; }
"""

# ------------------------------------------------------------------ content

INTRO = f"""
<h1>Demo Prep — the bench guide</h1>
<div class="sub">From sealed kits to working capstone robots. Companion to
<b>DEMO-PREP-G7.md</b> · <b>-G8.md</b> · <b>-G9.md</b> (per-track markdown, indexed by
DEMO-PREP.md). Manuals: <b>mbot2.pdf</b> (wheeled build) · <b>printed booklet in each add-on
box</b> (Rover, and the only Rover guide there is). <b>mbot2_addons.pdf</b> builds the
<b>Ranger</b> and is used by no grade — ignore it.</div>

<p class="warn"><b>The manager demo is two demos, run back-to-back.</b> Track A is
<b>Grade 7 · Rescue Run</b> and runs on <b>Box 1 alone</b> — keep the add-on box out of the
room, so a manager can watch a whole Grade 7 year without a second purchase appearing on the
table. Track B is <b>Grade 8 · A Job Worth Doing</b> and is where the add-on earns its budget
line. Run A first; the handover line is the pitch: <i>"That one is reliable. Now let me show
you the one that is likeable."</i> Track C (Grade 9) is <b>not in the current demo</b> — it is
kept ready for when Grade 9 is what is being sold.</p>

<p class="note">What to say on the day — the run-of-show, the timings, and what to do when it
fails — is on the site, not here: <b>site/demo-prep-g7.html</b> and
<b>site/demo-prep-g8.html</b>. This document is only about getting the robots built and
programmed.</p>

<table class="alloc">
<tr><th></th><th>Robot</th><th>Kits used</th><th>Form</th><th>Demo</th></tr>
<tr><td class="pic">{img('robot_wheel', 60)}</td><td><b>A</b></td><td>mBot2 kit #1</td>
  <td>wheeled mBot2</td><td>G7 Rescue Run (blocks)</td></tr>
<tr><td class="pic">{tanksvg(C8)}</td><td><b>B</b></td><td>mBot2 kit #2 + add-on #1</td>
  <td>Rover — tracked tank + grip arms</td><td>G8 A Job Worth Doing (blocks)</td></tr>
<tr><td class="pic">{img('robot_arm', 62)}</td><td><b>C</b></td><td>mBot2 kit #3 + add-on #2</td>
  <td>Rover — same form as B; Grade 9 adds no hardware</td><td>G9 Robots at Work (Python)</td></tr>
</table>
<p class="note">Exactly enough hardware, no spare robot. Build <b>A → B</b>; <b>C is a second
Rover</b>, built identically to B, and exists only so the Grade 8 demo can stay frozen while
Grade 9 runs on its own robot. <b>Grade 9 has no build sessions at all</b> — it inherits the
Grade 8 robot standing.</p>

<h3>1 · Unbox &amp; prep (~30 min, once)</h3>
{steps([
 "Open all boxes over trays; <b>sort screws by size immediately</b> — the #1 time-saver. Label the trays (M4×8 / M4×10 / M4×14 / M4×22 / M4×25 / M4×30 / M2.5×12 / M3×6 / nuts).",
 "Peel films: CyberPi screens, and the Rover body Boards (1–8) ship covered in paper film — peel while sorting, not mid-build.",
 "Charge everything now via USB-C: the battery is <b>built into the mBot2 Shield</b> (one per kit). A full charge comfortably covers a build-and-tune evening.",
 "The plastic shock absorbers in the add-on boxes are spares — the builds use the <b>metal</b> ones (×4).",
 "Photograph each sorted kit before you start — it is the reference when a part seems missing mid-build."])}
{strip("Prep — what these look like", [("shield","mBot2 Shield (battery inside)"),
 ("cyberpi","CyberPi (peel screen film)"), ("boards","Boards — peel paper film"),
 ("damper","metal (use) + plastic (spare) shocks"), ("screwdriver","kit screwdriver"),
 ("socket","socket wrench (add-on)")])}
"""

SOFTWARE = f"""
<div class="brk"></div>
<h3>2 · Software setup (~30 min, once)</h3>
{steps([
 "Install <b>mBlock 5 desktop</b> (not the web editor — fewer moving parts); create an account so projects save to the cloud.",
 "Connect each CyberPi via <b>USB</b> → Add device “CyberPi” → connect → accept the <b>firmware update</b>. Do all three now — first pairing is the slow part and it must not happen on demo day.",
 "After the wired first connection, wireless works. Keep a USB cable in the demo bag — USB always works when Bluetooth sulks.",
 "Robot C uses mBlock’s <b>Python mode</b> (toggle top-right). Exact API names vary by mBlock version — trust the editor’s autocomplete, not memory or blog posts."])}

<h4>Know the CyberPi (the brain on every robot)</h4>
<p>One brick carries everything you’ll program against: a full-color screen, a joystick,
buttons <b>A</b> and <b>B</b>, a speaker, a microphone, a light sensor and an LED strip.
It slides into the Shield (battery + motor/servo ports) and talks to mBuild sensors over
the chained cable ports. Everything below — the screen, menus, telemetry, celebration —
happens through this brick, so spend 10 minutes poking at it with a “hello” program
before the first build.</p>

<h4>Live mode vs Upload mode — the one mBlock concept that bites</h4>
{tb(["Mode", "Where code runs", "Use it for"], [
 ("<b>Upload</b>", "Flashed to the CyberPi — robot runs untethered",
  "Robot A’s Rescue Run and robot C’s mission: autonomous, laptop optional"),
 ("<b>Live</b>", "On the laptop, robot obeys over the link — stage/webcam available",
  "Nothing in these two demos — both robots run untethered; Live mode is a Grade 9 concern")])}
<p class="warn"><b>Symptom to remember:</b> a program that works tethered and “stops working”
when you unplug was running in Live mode. Robot B’s character is the only demo that
legitimately stays tethered (for ML); switch everything else to Upload before rehearsal.</p>

<h4>The connection ritual (repeat before every work session)</h4>
{checks(["Power on the robot (Shield switch)", "Open mBlock → your saved project",
 "Devices → CyberPi → Connect (USB first time, wireless after)",
 "If prompted: accept firmware update (only happens after mBlock upgrades)",
 "Run a 1-block test (beep or LED flash) before trusting anything else"])}

<h4>Cabling cheat sheet — the three forms differ, this table is the demo-saver</h4>
{tb(["", "Robot A · mBot2", "Robot B · Rover", "Robot C · Rover #2"], [
 ("<b>Motor cables</b>", "straight: left → EM1, right → EM2",
  "<b>CROSSED: left ↔ right</b>", "<b>CROSSED: left ↔ right</b>"),
 ("<b>Servos</b>", "—", "×2 grip arms → <b>S1 / S2</b>", "×2 grip arms → <b>S1 / S2</b>"),
 ("<b>Sensor cable</b>", "10 cm mBuild (never the 20 cm)", "10 cm mBuild", "10 cm mBuild"),
 ("<b>Wheel/track note</b>", "hub pressed into tyre", "nut back 90° CCW · track grain",
  "identical to Rover"),
])}
"""

BUILD_A = f"""
<div class="brk"></div>
{head(C7, "Robot A · mBot2 kit #1 · ~1 h build", "Build A — wheeled mBot2 (mbot2.pdf pp. 9–14)")}
{strip("Parts for this build (all from the mBot2 box)", [
 ("chassis","Chassis"), ("motor","Encoder motor ×2"), ("motorcable","Motor cable ×2"),
 ("wheelset","Hub + slick tyre ×2"), ("miniwheel","Mini wheel"), ("ultra","Ultrasonic Sensor 2"),
 ("quadrgb","Quad RGB Sensor"), ("mbuild","mBuild 10 cm cables"), ("screws7","M4 screws"),
 ("screws7s","M2.5×12 ×2"), ("shield","Shield (M4×25 ×4)"), ("cyberpi","CyberPi — last")])}
{steps([
 "<b>Plug the cables into the motors FIRST</b> — the port is unreachable once the motor is in the chassis (step ① order).",
 "Motors into chassis: M4×8 ×4 — check orientation against the diagram before screwing; a backwards motor is the classic error. Finger-tight first, then snug — <b>never overtighten into plastic</b>.",
 "Press each hub into its tyre; wheels onto the motor shafts: M2.5×12 ×2.",
 "Underside: Quad RGB sensor + mini wheel together (M4×14 ×2). Front: ultrasonic (M4×14 ×2) — it must face <b>exactly</b> forward; a few degrees of tilt = weeks of garbage readings.",
 "Sensors on the <b>10 cm</b> mBuild cables (the guide red-crosses the 20 cm one). Motor cables per the cheat sheet: <b>left → EM1, right → EM2</b>.",
 "Shield on top with the four long M4×25 screws; CyberPi slides in last. Route and tuck every cable — a loose cable in a wheel is the #1 cause of “randomly stops”.",
])}
<table class="tworow"><tr>
<td>{scenes.sc_expl(C7, variant="drive")}</td>
<td>{scenes.sc_expl(C7, variant="sense")}</td>
</tr></table>
<h4>QC before first power-on (the curriculum makes students sign this)</h4>
{checks(["Both wheels spin freely by hand", "Nothing rattles when gently shaken",
 "Ultrasonic faces dead forward, RGB sensor flat under the nose",
 "Cables tucked — nothing can reach a wheel", "EM1/EM2 correct (test: “forward” must not turn)",
 "No leftover “mystery screws” beyond the spares"])}
"""

PROG_A = f"""
<div class="brk"></div>
{head(C7, "Robot A · program · 2–4 h incl. tuning", "Program A — G7 Rescue Run (blocks, Upload mode)")}
<p>Mission: follow line → obstacle ON the line → arc around, re-find → stop in the red zone →
celebrate. Build one behavior at a time and test each before adding the next — the same
order the students use (site pages named per step).</p>
{steps([
 "<b>Calibrate the line sensor</b> on your actual floor: hold the Quad RGB’s button, sweep the sensor across the line until its LEDs confirm. Redo whenever floor or light changes — this ritual is 80% of line-following reliability.",
 "<b>3-state follower</b> (G7 S15): the wobble-killer is the explicit “straight” state — without it the robot over-corrects constantly.",
 "<b>Zone stop</b> (S16): the Quad RGB also reads color. RED under the sensor → stop + celebrate. If it slides past the zone, add a slow-approach state near the end of the course (S11’s two-speed idea).",
 "<b>Avoid + re-find</b> (S19) — the only new engineering: back up, timed arc around the obstacle, then creep forward until any line sensor fires, resume following. The S19 session page now carries this as a full block script; build from there rather than from this outline. Tune the arc with the obstacle at 2 different positions — the run-of-show moves it between runs.",
 "<b>Buttons</b> (S16): B starts, A stops. No re-flashing between runs — this is what makes the demo feel like a product, not a dev board.",
 "Freeze parameters · save as <b>demo-g7-rescue-final</b> · switch to Upload mode."])}
<div class="codelabel">Block script outline — the canonical version is on site page G7 S19</div>
<div class="code">when button B pressed → set running = 1
when button A pressed → set running = 0, stop moving

forever (if running = 1):
  if ultrasonic distance &lt; 12          <span class="cm">← avoid takes priority</span>
    move backward 10 cm
    set motors L 55 / R 15 · wait 1.2 s     <span class="cm">← arc out, tune this</span>
    set motors L 15 / R 55 · wait 1.2 s     <span class="cm">← arc back</span>
    move forward at 20 RPM until any line sensor fires   <span class="cm">← re-find</span>
  else if color sensor sees RED
    stop moving · play sound · LED animation             <span class="cm">← celebrate in the zone</span>
    set running = 0
  else if line under CENTER  → move forward at 55 RPM
  else if line under LEFT    → set motors L 15 / R 55
  else if line under RIGHT   → set motors L 55 / R 15</div>
<h4>Tuning table — change ONE value per run, note the result</h4>
{tb(["Parameter", "Start at", "Symptom → adjustment"], [
 ("Base speed (straight state)", "55 RPM", "flies off curves → lower · crawls → raise"),
 ("Correction split (15/55)", "15/55", "still wobbles → widen split · loses tight curves → strengthen"),
 ("Obstacle threshold", "12 cm", "kisses the box → raise · flinches at nothing → lower"),
 ("Arc split · duration", "55/15 · 1.2 s", "clips obstacle → longer/wider · lands far from line → shorter"),
 ("Zone approach speed", "20 RPM", "slides past red → slower approach state earlier")])}
<table class="tworow"><tr>
<td>{scenes.sc_line(C7, wobble=False, states=True, caption="the 3-state follower")}</td>
<td>{scenes.sc_rescue(C7)}</td>
</tr></table>

"""

BUILD_B = f"""
<div class="brk"></div>
{head(C8, "Robot B · kit #2 + add-on #1 · ~3–4 h build", "Build B — Rover (printed booklet, pp. 5–75)")}
<p>Phases in the printed guide’s order: brackets ×2 → left wheel module → right wheel module →
chassis → head → join → shells → grip arms. Work phase by phase; don’t pre-open later bags.</p>
{strip("Key add-on parts", [
 ("track","Track ×2 — mind grain"), ("trackhubs","Wheel hubs (large + small)"),
 ("dshaft","D shaft"), ("collarflange","Collar ×12 + flange bearing"),
 ("damper","Metal shocks ×4"), ("servopack","Servo ×2 → grip arms"),
 ("bracket","Brackets 90° / U"), ("beamplate","Slide beams + plates"),
 ("screwsR","Rover screws + nuts"), ("controller","Bluetooth Controller (for the program)")])}
{steps([
 "The two wheel modules <b>mirror</b> each other — the classic error is building two identical ones. Hold each against the guide page before screwing.",
 "Wheel hubs: after tightening the hub screws, back the nut off <b>90° counter-clockwise</b> — the wheel must spin freely or the tracks bind and the motors strain.",
 "Tracks have a <b>grain direction</b> — match the guide’s arrows on both sides.",
 "Shaft collars ×12 with M3×6 screws — pre-assemble them all at once with the socket wrench; it’s tedious mid-build.",
 "Metal shock absorbers ×4 (the red ones in the photo strip); plastic ones stay in the box.",
 "Motor cables are <b>CROSSED on the Rover: left ↔ right</b> — opposite of robot A. Sensor cable: 10 cm again.",
 "Servos ×2 drive the grip arms in the final phase — route their cables before closing the shells.",
 "After the build: re-run turn calibration. Tracks skid-steer; nothing you tuned on wheels carries over."])}
<table class="tworow"><tr>
<td>{scenes.sc_expl(C8, variant="trackmod")}</td>
<td>{scenes.sc_expl(C8, variant="roverchassis")}</td>
</tr></table>
<h4>Post-build QC</h4>
{checks(["Both tracks turn freely by hand (no binding)", "Track grain matches on both sides",
 "“Forward” drives forward (crossed cables verified)", "On-the-spot turn works both directions",
 "Grip arms move through full travel without catching the shells",
 "Shells snapped tight, no film left on the Boards"])}
"""

PROG_B = f"""
<div class="brk"></div>
{head(C8, "Robot B \u00b7 program \u00b7 3\u20135 h", "Program B \u2014 G8 A Job Worth Doing (blocks)")}
<p>The demo robot = arm verbs + a job machine + a voice + manual drive. Build in this order;
every layer demos on its own if you run out of time. <b>Blocks only</b> \u2014 there is no Python
in Grade 8 any more, that is Grade 9.</p>

<h4>1 \u00b7 Arm verbs (site: G8 Step 3\u20134)</h4>
{steps([
 "Find the arm\u2019s safe range <b>by hand, power off</b>. Those two angles are this robot\u2019s, not the class\u2019s.",
 "Put them in <b>ARM_OPEN</b> / <b>ARM_SHUT</b> and build <b>grip</b>, <b>release</b>, <b>lift(height)</b>.",
 "Half a second of wait inside each one \u2014 a servo needs a beat, and a robot that grips then drives away drops the block.",
 "<b>Never force the arm past resistance.</b> The gear teeth strip silently and are not in the spare bag."])}

<h4>2 \u00b7 The job machine (Step 9, then Step 22)</h4>
<div class="codelabel">One variable decides what it is doing</div>
<div class="code">set job to "idle"
forever:
  if job = "fetch"   \u2192 drive up, grip, job \u2190 "carry"
  if job = "carry"   \u2192 lift, drive across, job \u2190 "deliver"
  if job = "deliver" \u2192 lower, release, job \u2190 "idle"   <span class="cm">\u2190 and an arrow OUT of failure</span></div>
<p class="note">Draw the arrows before writing any of it, including the one out of \u201cthe grip
closed on nothing\u201d. That is the arrow every team forgets and the one that strands the robot
in front of an audience.</p>

<h4>3 \u00b7 Controller (Step 11)</h4>
{steps([
 "Add the <b>Bluetooth Controller</b> extension. Tank steering: <b>LY</b> \u2192 left track, <b>RY</b> \u2192 right track, divided down until it is drivable.",
 "Buttons for grip / release / celebrate. Write the mapping on a paper card \u2014 pilots do.",
 "<b>Upload the program first</b>, then pair. The controller does nothing to a robot that is not already listening.",
 "Hand the card and the controller to a manager and let THEM drive \u2014 the best 60 seconds of the demo."])}

<h4>4 \u00b7 Voice (Step 16\u201318) \u2014 the wow moment, and the one that needs the network</h4>
{steps([
 "<b>connect to Wi-Fi</b> first, and show <b>network connected?</b> on the screen. Speech is a <b>cloud</b> call: no internet, no voice.",
 "<b>recognize</b> \u2192 <b>speech recognition result</b> \u2192 match it against a <b>list</b> of known commands with <b>contains</b> \u2192 set the job.",
 "Short, distinct command words. \u201cFetch\u201d and \u201cstretch\u201d is a bad pair.",
 "Give it an <b>\u201cI didn\u2019t catch that\u201d</b> path that speaks and does <b>not</b> move. A robot that guesses when unsure is worse than one that admits it.",
 "<b>Test at the venue, on the venue\u2019s Wi-Fi, with the room talking.</b> A full room sounds nothing like an empty one, and that is when it will matter."])}
<table class="tworow"><tr>
<td>{scenes.sc_states(C8)}</td>
<td>{scenes.sc_controller(C8)}</td>
</tr></table>

"""

BUILD_C = f"""
<div class="brk"></div>
{head(C9, "Robot C · kit #3 + add-on #2 · ~3–4 h build", "Build C — a second Rover (printed booklet)")}
<p class="warn"><b>Robot C is another Rover, not a Ranger.</b> Grade 9 adds no hardware to the
Grade 8 robot: it inherits it standing and spends its year in Python. Build C exists only so the
Grade 8 demo can stay frozen while Grade 9 runs. Build it from the <b>printed booklet in the
add-on box</b>, front to back — exactly as robot B. Do <b>not</b> use <code>mbot2_addons.pdf</code>;
that is the Ranger, a different robot, and no Grade 9 program will run on it.</p>
{steps([
 "Repeat build B, page for page. Everything you learned on robot B applies unchanged — this is the fastest build of the three for that reason.",
 "Track and wheel work: nut back <b>90° CCW</b> after hub screws, wheels must spin free, track grain matches the arrows.",
 "Motor cables are <b>CROSSED, exactly as on robot B: left → EM2, right → EM1</b>. Your hands will have learned this by now; check the page anyway.",
 "Servo cables: <b>left arm → S1, right arm → S2</b> — the ports every Grade 9 program expects.",
 "Route servo + sensor cables before the final shell close — re-opening is a 20-minute tax.",
 "<b>Never force an arm past resistance</b> — the servo gears strip, and there is no spare servo in your inventory. The same rule goes into the code as clamped limits."])}
<h4>Post-build QC</h4>
{checks(["Tracks free, grain correct, forward = forward (crossed cables verified)",
 "Both grip arms open/close by gentle hand pressure with power OFF",
 "Servo cables on S1 (left) / S2 (right) — mixed up = mirrored arm behavior",
 "Arm travel does not collide with the chassis at either extreme",
 "Safe range of each arm measured by hand and written on the robot's label",
 "All shells closed, cables tucked, nothing pinched"])}
"""

PROG_C = f"""
<div class="brk"></div>
{head(C9, "Robot C · program · 4–6 h", "Program C — G9 Robots at Work (Python mode, Upload)")}
<h4>1 · Arm bring-up FIRST (S10–S12) — before any driving</h4>
{steps([
 "Power on, connect, switch mBlock to Python mode. Find the servo functions via autocomplete.",
 "Move each arm in small increments from the keyboard; write down the safe range you observe. The two arms are <b>mirrored</b>, so open is a large angle on one and a small angle on the other.",
 "Define <b>L_SHUT / L_OPEN / R_SHUT / R_OPEN</b> as constants; wrap every servo call in a clamp inside one <b>arm_to(left, right)</b>. From now on nothing commands a servo directly, and only <b>grip_open()</b> knows about the mirror.",
 "Build and test the verbs in isolation: <b>pick()</b> (open → creep in → close → settle), <b>place()</b> (open → reverse out), <b>carry_to(cm)</b>. Slow speeds; the arms should grip firmly, not crush.",
 "One servo per arm means <b>grip and height are the same number</b>: this robot releases where it stands and cannot stack. Design the mission around that, not against it."])}
<h4>2 · Motion + closed-loop control (S2, S6, S8, S9)</h4>
{steps([
 "Wrap drive/turn/read into small functions — this is the “clean code” beat of your pitch.",
 "P-control follower: correction proportional to line error. Tune KP: raise until the robot hugs curves, back off when it starts oscillating. Show the graph in the pitch — proportional visibly beats bang-bang.",
 "Add the D term: <b>steer = KP*err + KD*(err − last_err)</b>, with a fixed <code>sleep()</code> in the loop so the difference means something. Freeze KP, sweep KD.",
 "Calibrate the encoders: measure <b>DEG_PER_CM</b> on the actual floor, build <b>drive_cm()</b>, then drive a 50 cm square and measure how far off it closes. That number is your error budget and it sets how tight the delivery zone can be. <b>Re-measure it at the venue.</b>",
 "There is <b>no ultrasonic on this robot</b> — distance is encoder degrees and every marker is a colour under the Quad RGB."])}
<h4>3 · The mission pipeline (S13–S14)</h4>
<div class="codelabel">Python skeleton (names indicative — mBlock autocomplete is the source of truth)</div>
<div class="code">KP, KD, BASE = 0.35, 0.05, 40       <span class="cm"># tuned on the course</span>
L_SHUT, L_OPEN = 20, 80             <span class="cm"># S1 — measured by hand FIRST</span>
R_SHUT, R_OPEN = 80, 20             <span class="cm"># S2 — mirrored, so inverted</span>
DEG_PER_CM = 12.4                   <span class="cm"># measured on THIS floor</span>

def clamp(v, a, b):     lo, hi = min(a,b), max(a,b); return max(lo, min(hi, v))
def arm_to(l, r):       servo_set(clamp(l, L_SHUT, L_OPEN), "S1"); servo_set(clamp(r, R_SHUT, R_OPEN), "S2")
def grip_open():        arm_to(L_OPEN, R_OPEN)   <span class="cm"># the only place the mirror is spelled out</span>
def grip_close():       arm_to(L_SHUT, R_SHUT)
def pick():   grip_open(); drive_cm(6); grip_close(); wait(0.3)
def place():  grip_open(); wait(0.2); drive_cm(-8)   <span class="cm"># retreat BEFORE turning</span>

last_err = 0
def follow_step():
    global last_err
    err = line_position()           <span class="cm"># quad RGB: signed offset from center</span>
    motors(BASE - (KP*err + KD*(err-last_err)), BASE + (KP*err + KD*(err-last_err)))
    last_err = err

state = "FOLLOWING"
while state != "DONE":
    if state == "FOLLOWING":
        follow_step()
        if sees_marker():  stop(); state = "PICKING"
    elif state == "PICKING":
        pick();            state = "CARRYING"
    elif state == "CARRYING":
        follow_step()
        if in_delivery_zone(): stop(); state = "DELIVER"
    elif state == "DELIVER":
        place(); celebrate(); state = "DONE"</div>
<h4>Why a state machine (your 20-second pitch line)</h4>
<p>Each behavior is testable alone, failures are diagnosable (“it died in CARRYING”), and adding
a phase never breaks the others — the same structure real robots ship with.</p>
<table class="tworow"><tr>
<td>{small(scenes.sc_graph2(C9, caption="P-control vs bang-bang — the 20-second pitch graph"))}</td>
<td>{small(scenes.sc_work(C9))}</td>
</tr></table>

"""

PROPS = f"""
<div class="brk"></div>
{head(C7, "Props · one evening", "Courses &amp; props")}
{steps([
 "<b>G7 course</b>: the kit’s line map — tape it FLAT (curled edges = false readings) — or 15–19 mm black tape on light floor, curves gentle. Obstacle = small rigid box ON the line (soft/dark objects reflect ultrasound badly). Rescue zone = <b>matte</b> red paper, A5-ish (glossy tape misreads). Start line taped.",
 "<b>G8</b>: an open “fair table” + a small box slalom for controller driving; webcam on a stand + a lamp for the ML corner; the printed controller-mapping cheat card.",
 "<b>G9</b>: line path with one color-patch marker; pickup object = foam block sized to the gripper (test the grip before demo day!); taped delivery zone.",
 "Shared: masking tape, spare boxes, ruler, printed score sheets (pages above) on a clipboard — the visible scoreboard is what managers remember."])}
{strip("From the kits", [("map","Line map — tape flat"), ("usb","USB — the demo bag insurance"),
 ("controller","Controller — pair after upload"), ("shield","Charged shields ×3"),
 ("screws7","Spare screws travel too")])}

<h4>Troubleshooting master table</h4>
{tb(["Symptom", "Most likely cause", "Fix"], [
 ("Turns when told to go straight", "EM1/EM2 swapped (A/C) or not crossed (B)",
  "re-check the cabling cheat sheet for THAT form"),
 ("Randomly stops mid-run", "loose cable touching a wheel/track", "re-route and tuck; shake test"),
 ("Ultrasonic reads garbage", "sensor tilted, or target soft/angled",
  "straighten mount; use rigid boxes as obstacles"),
 ("Line following drunk or blind", "calibration stale (light/floor changed)",
  "redo the sweep ritual on-site; tape the map flat"),
 ("Loses line at the same curve", "correction too weak for that radius",
  "strengthen split or slow base speed"),
 ("Overshoots the red zone", "approaching too fast", "add the slow-approach state earlier"),
 ("Won’t connect wirelessly", "first pairing never done / interference",
  "USB cable; re-do firmware pairing at home, never on stage"),
 ("Program “stops working” untethered", "it was running in Live mode", "switch to Upload mode"),
 ("Controller does nothing", "program not uploaded first", "upload, then pair next to the CyberPi"),
 ("ML mirror wrong/confused", "venue lighting differs from training", "re-train on-site, add a lamp"),
 ("Arm strains or clicks", "commanded past its range", "re-measure limits; check the clamp is used everywhere"),
 ("Tracks bind / motors labor", "hub nut not backed off, or grain reversed",
  "loosen 90° CCW; re-seat track per arrows")])}
"""

RUNBOOK = f"""
<div class="brk"></div>
<h3>Demo-day runbook</h3>
{steps([
 "Night before: charge all three Shields + the controller; laptop charged; three project files verified opening; print score sheets + controller cheat card.",
 "On site, FIRST (30 min buffer): recalibrate both line followers on the venue floor in venue light → then train/verify the G8 ML model there.",
 "One dry run per robot — then <b>stop tinkering</b>. The curriculum’s own rule: tinkering minutes before official runs is how good robots die.",
 "Show order per grade: 30 s of the site’s demo page (the ladder) → the live run → the Session 20 teacher page on screen (“this is what your teachers receive, for all 60 hours”)."])}

<h4>Pre-flight — robot A (G7)</h4>
{checks(["Battery full · program demo-g7-rescue-final · Upload mode",
 "Line calibrated on venue floor", "Obstacle placed, red zone taped, start line taped",
 "B starts / A stops verified twice"])}
<h4>Pre-flight — robot B (G8)</h4>
{checks(["Battery full · character program uploaded · controller paired",
 "Reflex thresholds sane in venue noise/light (clap + shake + cover test)",
 "ML: trained on-site, 3 classes verified — or consciously cut",
 "Cheat card ready to hand to a manager"])}
<h4>Pre-flight — robot C (G9)</h4>
{checks(["Battery full · demo-g9-work-final uploaded", "Line + marker calibrated on venue floor",
 "Foam block placed, grip tested twice, delivery zone taped",
 "Arm limits demo: show it refusing an out-of-range command (great pitch beat)"])}

<h4>Fallback ladder (in order)</h4>
{steps([
 "Bluetooth flaky → USB cable (works everywhere except the untethered runs — reduce course size).",
 "G8 ML flaky → cut it; reflexes + controller carry the character.",
 "G7 re-find unreliable → fix the obstacle at a known position and pre-tune the arc.",
 "A robot dies → robot A’s program runs on B with speed retuning (tracks). Last resort, rehearse once."])}

<div class="brk"></div>
<h4>What to SAY while each robot runs (pitch beats)</h4>
{tb(["Grade", "While it runs, say…"], [
 ("G7", "“Everything you see — sensing, deciding, moving — was built by 12-year-olds across 20 one-hour sessions, each one a single-page script for your teacher.”"),
 ("G8", "“Same kit, rebuilt on tracks with arms. This year it takes instructions — the students decide which words it knows, and what it does when it mishears.”"),
 ("G9", "“Now it’s real Python and real engineering practice: specs, code review, a state machine. This mission is their Demo Day — scored in front of an audience, like today.”")])}

<h3>Time budget (realistic, solo)</h3>
{tb(["Track", "Build", "Program", "Track total"], [
 ("<b>A · G7 Rescue Run</b> — Box 1 only", "1 h", "2–4 h", "<b>~1 day</b>"),
 ("<b>B · G8 A Job Worth Doing</b> — + add-on", "3–4 h", "3–5 h", "<b>~1.5–2 days</b>"),
 ("<b>C · G9 Robots at Work</b> — not in the demo", "3–4 h", "4–6 h", "<b>~2 days</b>"),
 ("Unbox, prep, software, firmware", "—", "—", "1 h once"),
 ("<b>A + B — the actual demo</b>", "", "", "<b>~2.5–3 working days</b>")])}
<p class="note"><b>The Rover build is the long pole and it gates track B entirely.</b> Start it
first, not last. If it is not standing with two days to spare, run the Grade 7 demo alone this
round and book Grade 8 for the next visit rather than showing a half-built robot.</p>
"""


SCORES = f"""
<div class="brk"></div>
<h3>Score sheets — print one per official run</h3>
<p class="note">The visible scoreboard is the “scored event” theater managers remember.
Score phases, not just full success — a partial run still earns points, which is itself
a teaching point worth saying out loud.</p>
{score_sheet(C7, "Rescue Run (G7)", [
 ("Clean line following to the obstacle", "2"), ("Obstacle detected + avoided", "3"),
 ("Line re-found after the arc", "2"), ("Stop fully inside the red zone", "2"),
 ("Celebration triggers (only) in the zone", "1")])}
{score_sheet(C8, "A Job Worth Doing (G8)", [
 ("Spoken command recognised and obeyed", "3"), ("Picks the block up cleanly", "3"),
 ("Delivers inside the zone", "2"), ("Visitor drives the lane via controller", "2")])}
{score_sheet(C9, "Robots at Work (G9)", [
 ("Line navigation to the marker", "2"), ("Marker detected, clean stop", "2"),
 ("Pick succeeds (object held)", "3"), ("Carry without dropping", "1"),
 ("Delivery inside the zone", "2")])}
"""

html = (f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
        + INTRO + SOFTWARE + BUILD_A + PROG_A + BUILD_B + PROG_B + BUILD_C + PROG_C
        + PROPS + SCORES + RUNBOOK + "</body></html>")

if __name__ == "__main__":
    from weasyprint import HTML
    out = ROOT.parent / "DEMO-PREP.pdf"
    HTML(string=html, base_url=str(ROOT)).write_pdf(str(out))
    print("wrote", out)
