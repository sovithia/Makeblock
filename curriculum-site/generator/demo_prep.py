# -*- coding: utf-8 -*-
"""The manager-demo run-of-show — prep sheets, not curriculum.

Two demos, one per page, because the two grades prove different things and need
different hardware:

  page_g7 → Rescue Run.       Wheeled mBot2, **Box 1 only**. Autonomy: it works.
  page_g8 → A Job Worth Doing. Rover, **needs the add-on pack**. It takes instructions.

Keeping the base-kit demo free of the add-on is the point of the split — a
manager can be shown a complete Grade 7 year without the second purchase ever
appearing on the table. Run back-to-back, G7 first, the two pages also read as
one "reliable → relatable" arc; see the closing note on each page.

Deliberately NOT driven by the session YAML: these are one-off operational
documents (what to build, in what order, what to say, what to do when it fails),
not lesson content. They link into the session pages rather than duplicating
them, so the programs stay in one place.

English only. They fall through to English under --locale km like any
untranslated string would; translate if they ever go to someone who needs Khmer.
"""

CSS = """
<style>
.dp h3 { font-size: 12.5pt; margin: 7mm 0 2mm 0; }
.dp .lede { color: #475569; font-size: 9.6pt; margin-bottom: 4mm; }
.dp table { width: 100%; border-collapse: collapse; margin-bottom: 3mm; }
.dp td, .dp th { border-bottom: 1px solid #e8edf3; padding: 1.8mm 2mm; vertical-align: top;
  font-size: 8.8pt; text-align: left; }
.dp th { background: #f8fafc; color: #475569; font-size: 8pt; text-transform: uppercase;
  letter-spacing: 1px; }
.dp td.n { width: 8mm; font-weight: bold; color: var(--dpc, #0e7fc1); }
.dp td.t { width: 16mm; font-weight: bold; white-space: nowrap; }
.dp .say { display: block; color: #475569; font-style: italic; margin-top: 1mm; }
.dp .risk { border-left: 4px solid #d97706; background: #fef9ec; border-radius: 0 8px 8px 0;
  padding: 2.5mm 3.5mm; margin-bottom: 2.5mm; font-size: 8.8pt; }
.dp .risk b { color: #9a4f08; }
.dp .fix { display: block; margin-top: 1mm; color: #475569; }
.dp .chk { list-style: none; padding-left: 0; }
.dp .chk li { font-size: 9pt; margin-bottom: 1.6mm; padding-left: 6mm; text-indent: -6mm; }
.dp .chk li::before { content: "\\2610  "; color: var(--dpc, #0e7fc1); font-size: 11pt; }
.dp .dpmat { text-align: center; margin: 3mm 0 4mm 0; }
.dp .warn { border: 2px solid #dc2626; border-radius: 10px; padding: 3mm 4mm; margin-bottom: 4mm;
  font-size: 9pt; }
.dp .warn b { color: #dc2626; }
.dp .kit { border: 2px solid var(--dpc, #0e7fc1); background: #fff; border-radius: 10px;
  padding: 3mm 4mm; margin-bottom: 4mm; font-size: 9pt; }
.dp .kit b { color: var(--dpc, #0e7fc1); }
.dp .pair { border-top: 1px solid #e8edf3; margin-top: 7mm; padding-top: 3mm;
  color: #475569; font-size: 8.8pt; }
@media print { .dp { font-size: 9pt; } }
</style>
"""


def _mat_g7():
    """Grade 7 course: calibration strip, line loop, movable obstacle, rescue zone."""
    return """
<svg viewBox="0 0 640 250" width="620" style="max-width:100%">
  <rect x="8" y="8" width="624" height="234" rx="10" fill="#f8fafc" stroke="#cbd5e1"/>
  <!-- calibration strip -->
  <line x1="45" y1="45" x2="185" y2="45" stroke="#0e7fc1" stroke-width="3"/>
  <line x1="45" y1="38" x2="45" y2="52" stroke="#0e7fc1" stroke-width="3"/>
  <line x1="185" y1="38" x2="185" y2="52" stroke="#0e7fc1" stroke-width="3"/>
  <text x="115" y="32" font-size="11" fill="#0e7fc1" text-anchor="middle" font-weight="bold">50 cm strip</text>
  <text x="115" y="66" font-size="10" fill="#64748b" text-anchor="middle">moment 1 · calibration</text>
  <!-- line loop -->
  <path d="M 70,150 L 300,150 Q 340,150 340,120 L 340,100 Q 340,78 375,78 L 430,78"
        stroke="#1e293b" stroke-width="7" fill="none" stroke-linecap="round"/>
  <text x="140" y="172" font-size="10" fill="#64748b">line-following map</text>
  <circle cx="70" cy="150" r="7" fill="#16a34a"/>
  <text x="70" y="192" font-size="10" fill="#16a34a" text-anchor="middle" font-weight="bold">START</text>
  <!-- obstacle, two positions: the autonomy proof -->
  <rect x="232" y="137" width="26" height="26" fill="#d97706" rx="2"/>
  <text x="245" y="130" font-size="10" fill="#9a4f08" text-anchor="middle">run 1</text>
  <rect x="327" y="88" width="26" height="26" fill="none" stroke="#d97706" stroke-width="2.5"
        stroke-dasharray="5,3" rx="2"/>
  <text x="300" y="106" font-size="10" fill="#9a4f08" text-anchor="end">run 2</text>
  <path d="M 262,150 Q 300,150 325,112" stroke="#d97706" stroke-width="1.6" fill="none"
        stroke-dasharray="4,3" marker-end="url(#dparr)"/>
  <defs><marker id="dparr" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
    <path d="M0,0 L7,3.5 L0,7 z" fill="#d97706"/></marker></defs>
  <text x="245" y="215" font-size="10" fill="#9a4f08" text-anchor="middle" font-weight="bold">
    obstacle MOVES between runs</text>
  <!-- rescue zone -->
  <rect x="450" y="45" width="130" height="70" fill="#dcfce7" stroke="#16a34a"
        stroke-width="2.5" stroke-dasharray="7,5" rx="4"/>
  <text x="515" y="74" font-size="11" fill="#166534" text-anchor="middle" font-weight="bold">RESCUE</text>
  <text x="515" y="90" font-size="11" fill="#166534" text-anchor="middle" font-weight="bold">ZONE</text>
  <text x="515" y="130" font-size="10" fill="#64748b" text-anchor="middle">moments 2 &amp; 3</text>
  <text x="515" y="180" font-size="10" fill="#94a3b8" text-anchor="middle">no tablet on this mat</text>
  <text x="575" y="30" font-size="10" fill="#94a3b8" text-anchor="middle">≈120 × 80 cm</text>
</svg>"""


def _mat_g8():
    """Grade 8 layout: a job course — fetch from one zone, deliver to another."""
    return """
<svg viewBox="0 0 640 250" width="620" style="max-width:100%">
  <rect x="8" y="8" width="624" height="234" rx="10" fill="#f8fafc" stroke="#cbd5e1"/>
  <rect x="30" y="60" width="112" height="70" rx="8" fill="#f2e8fa" stroke="#8b3fc6" stroke-width="2.5"/>
  <text x="86" y="88" font-size="11" fill="#5f2b8a" text-anchor="middle" font-weight="bold">STAND HERE</text>
  <text x="86" y="104" font-size="10" fill="#5f2b8a" text-anchor="middle">and talk to it</text>
  <text x="86" y="120" font-size="10" fill="#64748b" text-anchor="middle">moment 1</text>
  <rect x="190" y="150" width="110" height="62" rx="6" fill="#fff" stroke="#8b3fc6"
        stroke-width="2.5" stroke-dasharray="7,5"/>
  <text x="245" y="176" font-size="11" fill="#5f2b8a" text-anchor="middle" font-weight="bold">PICK UP</text>
  <rect x="232" y="186" width="24" height="18" rx="3" fill="#d97706"/>
  <text x="245" y="228" font-size="10" fill="#64748b" text-anchor="middle">moment 2</text>
  <path d="M 300,180 Q 380,180 400,120 Q 418,66 470,66" stroke="#8b3fc6" stroke-width="2.6"
        fill="none" stroke-dasharray="7,5"/>
  <rect x="470" y="36" width="122" height="66" rx="6" fill="#dcfce7" stroke="#16a34a"
        stroke-width="2.5" stroke-dasharray="7,5"/>
  <text x="531" y="64" font-size="11" fill="#166534" text-anchor="middle" font-weight="bold">DELIVER</text>
  <text x="531" y="80" font-size="11" fill="#166534" text-anchor="middle" font-weight="bold">HERE</text>
  <rect x="360" y="150" width="240" height="72" rx="8" fill="#fff" stroke="#cbd5e1"
        stroke-dasharray="6,4"/>
  <rect x="404" y="170" width="22" height="22" fill="#d97706" rx="2"/>
  <rect x="470" y="186" width="22" height="22" fill="#d97706" rx="2"/>
  <rect x="536" y="168" width="22" height="22" fill="#d97706" rx="2"/>
  <text x="480" y="238" font-size="10" fill="#64748b" text-anchor="middle">
    moment 3 &#183; a manager drives it</text>
  <text x="575" y="26" font-size="10" fill="#94a3b8" text-anchor="middle">&#8776;150 &#215; 90 cm</text>
</svg>"""


# ── Grade 7 ──────────────────────────────────────────────────────────────────

def page_g7(base="./"):
    g7 = f'{base}grade7'
    return f"""
<div class="dp" style="--dpc:#0e7fc1">
<h2 class="section">Demo run-of-show — Grade 7 · Rescue Run</h2>
<p class="lede"><b>The story in one line: nine months of Grade 7 turn into forty seconds where nobody
touches the robot.</b> One mat, one wheeled mBot2, three moments, about ten minutes. This demo proves
the word managers actually care about — <i>reliable</i>.</p>

<div class="kit"><b>Box 1 only.</b> Everything on this page runs on the base mBot2 kit. The Rover
add-on box stays sealed and out of the room — a manager can watch a complete Grade 7 year without a
second purchase ever appearing on the table. If they ask what the next year needs, that is the cue
for the Grade 8 demo, not an interruption to this one.</div>

<div class="dpmat">{_mat_g7()}</div>

<h3>The three moments</h3>
<table>
<tr><th>#</th><th>Session</th><th>What they see</th><th>Why it lands</th></tr>
<tr><td class="n">1</td><td><a href="{g7}/step-02.html">G7 Step 2</a><br/>Calibration</td>
    <td>Robot drives 50 cm three times, inside ±1 cm; the team's measurement table on screen
    <span class="say">"Nine months earlier they could not do this. That is a tolerance, and they
    met it."</span></td>
    <td>Answers "is this real STEM?" before it gets asked. Cut this one first if time is short —
    it can be told rather than shown</td></tr>
<tr><td class="n">2</td><td><a href="{g7}/step-23.html">G7 Step 23</a><br/>Rescue Run</td>
    <td>Follows the line, meets the obstacle, arcs around it, re-finds the line, stops inside the
    rescue zone, celebrates
    <span class="say">"Nobody is touching it. That is a whole year of skills in forty seconds."</span></td>
    <td>The year's payoff, and the most legible autonomy moment in the program</td></tr>
<tr><td class="n">3</td><td><a href="{g7}/step-22.html">G7 Step 22</a><br/>Run it again, moved</td>
    <td><b>Move the obstacle to a different spot in front of them</b>, then run the identical program
    again
    <span class="say">"Same code. I just moved the box. It is not following a memorised route —
    it is following a rule."</span></td>
    <td>The single cheapest proof that this is programming and not choreography. Most adults
    silently assume the robot is replaying a recording until this moment</td></tr>
</table>

<h3>Timing — about 10 minutes</h3>
<table>
<tr><td class="t">0–3′</td><td>Moment 1 — calibration. Short, factual, sets credibility</td></tr>
<tr><td class="t">3–7′</td><td>Moment 2 — Rescue Run. The curriculum scores two official attempts,
  so a first-run miss is on-message, not a failure. Say that <i>before</i> you press start</td></tr>
<tr><td class="t">7–10′</td><td>Moment 3 — move the obstacle, run again. End here, on the rule</td></tr>
</table>

<h3>What to build</h3>
<table>
<tr><th>From the kit</th><th>Classroom</th></tr>
<tr><td>One wheeled mBot2 (Box 1). Ultrasonic and Quad RGB mounted and straight. A second built
  robot as hot spare if you have one. Charged the night before — the shield battery level changes
  the calibration numbers.</td>
  <td>Line-following map, or black tape on light card · masking tape · one cardboard box as the
  obstacle · matte <b>red</b> paper for the rescue zone (glossy tape reads badly) · ruler ·
  stopwatch · a tablet only if you want to show the code — the runs themselves need no tablet</td></tr>
</table>

<h3>Prep week</h3>
<table>
<tr><td class="t">Mon</td><td>Assemble and charge. Write and save the program:
  <a href="{g7}/step-18.html">S15</a> three-state follower →
  <a href="{g7}/step-19.html">S16</a> zone stop and button start →
  <a href="{g7}/step-22.html">S19</a> obstacle detour and line re-find.</td></tr>
<tr><td class="t">Tue</td><td>Tape the mat <b>in the actual demo room</b>. Calibrate the Quad RGB on
  that floor, under that light. Tune the detour arc with the obstacle at <b>both</b> marked
  positions. Photograph the taped layout so you can rebuild it exactly.</td></tr>
<tr><td class="t">Wed–Thu</td><td>Two clean run-throughs end to end, in order, including the
  obstacle move. Then freeze the parameters and save as <b>demo-g7-rescue-final</b>.</td></tr>
<tr><td class="t">Fri AM</td><td>Pre-flight checklist below. One silent full run before anyone
  arrives.</td></tr>
</table>

<h3>What will go wrong, and what to do</h3>

<div class="risk"><b>Floor surface and light change everything.</b> Numbers tuned on one floor will
not hold on another, and direct sun or a shiny floor wrecks line following.
<span class="fix">→ Calibrate on Tuesday, in the room, at the demo's time of day. Recalibrate on
Friday morning. The calibration ritual is 80% of line-following reliability.</span></div>

<div class="risk"><b>Calibration is distance-based, so battery level changes it.</b> A robot that ran
all morning will undershoot the 50 cm and may stop short of the zone.
<span class="fix">→ Full charge, and do not leave the robot running while people arrive.</span></div>

<div class="risk"><b>The moved obstacle is a live variable.</b> An arc tuned at one position can miss
the line at another, which turns your best moment into your worst.
<span class="fix">→ Tune at both marked positions and demo <b>only</b> those two. Mark them on the
mat with tape so you cannot improvise under pressure.</span></div>

<div class="risk"><b>A curled or taped-over map gives false readings.</b> Curled edges and glossy
tape both fool the Quad RGB.
<span class="fix">→ Tape the map flat at every edge; matte paper for the red zone.</span></div>

<h3>Friday morning pre-flight</h3>
<ul class="chk">
<li>Robot fully charged, and the spare too</li>
<li>Mat taped down flat, matching Tuesday's photo</li>
<li>Quad RGB recalibrated this morning, in this room, under this light</li>
<li>Program uploaded in <b>Upload mode</b> and run once, silently</li>
<li>Button start confirmed — B starts, A stops, no re-flashing between runs</li>
<li>Both obstacle positions taped and both tested</li>
<li>Rescue zone patch and start line down</li>
<li>Printed leave-behinds: the demo tour and the Grade 7 materials page</li>
</ul>

<h3>Leave-behind</h3>
<p class="lede">Print these and have them on the table — they answer the two questions managers ask
after the robot stops moving: what does the year look like, and what do we have to buy.
<br/>· <a href="{base}demo.html">The demo tour</a> — milestone cards for each grade
<br/>· <a href="{g7}/materials.html">Grade 7 materials</a> — Box 1, nothing sold separately</p>

<p class="pair"><b>Running both demos back-to-back?</b> Do Grade 7 first, exactly as above, then
clear the mat and move to <a href="{base}demo-prep-g8.html">Grade 8 · A Job Worth Doing</a>. The
handover line is the whole pitch: <i>"That one is reliable. Now let me show you the one that is
likeable."</i> Budget about 20 minutes for the pair, plus two minutes to reset the floor.</p>
</div>
"""


# ── Grade 8 ──────────────────────────────────────────────────────────────────

def page_g8(base="./", steps=None, hours=None):
    """`steps`/`hours` come from the content so the run-of-show cannot quote a
    course length the course no longer has — it said 23 steps and 44 hours for a
    while after the assembly lessons pushed Grade 8 to 24 and 46."""
    g8 = f'{base}grade8'
    g8steps, g8hours = steps or "24", hours or "46"
    return f"""
<div class="dp" style="--dpc:#8b3fc6">
<h2 class="section">Demo run-of-show &#8212; Grade 8 &#183; A Job Worth Doing</h2>
<p class="lede"><b>The story in one line: Grade 7 made the robot work; Grade 8 makes it work
<i>for you</i>.</b> One job course, one Rover, three moments, about ten minutes. This demo sells
the sentence a spreadsheet cannot &#8212; <i>you can talk to it, and it does the job</i> &#8212;
and it ends with a manager holding the controller.</p>

<div class="kit"><b>Needs the Rover add-on pack.</b> This is where the second box earns its budget
line, so let it be visible: the tracked build, the grip arms, the controller. If the audience has
just watched the Grade 7 demo, name the difference out loud &#8212; same brain, second box, and a
robot that now takes instructions.</div>

<div class="dpmat">{_mat_g8()}</div>

<h3>The three moments</h3>
<table>
<tr><th>#</th><th>Step</th><th>What they see</th><th>Why it lands</th></tr>
<tr><td class="n">1</td><td><a href="{g8}/step-17.html">G8 Step 17</a><br/>Say a word</td>
    <td>Say <b>&#8220;fetch&#8221;</b> to the Rover and it sets off &#8212; no tablet, no phone,
    no cable
    <span class="say">&#8220;That is running on the robot. A student decided which words it
    knows.&#8221;</span></td>
    <td>The flagship, and unlike last year&#8217;s version it is <b>untethered</b>. Nothing else
    in the kit lands like this with adults</td></tr>
<tr><td class="n">2</td><td><a href="{g8}/step-23.html">G8 Step 23</a><br/>The job</td>
    <td>It drives to the pick-up zone, grips the block, carries it across, sets it down in the
    delivery zone and reports
    <span class="say">&#8220;Nobody is touching it. That is a year of work doing something
    useful.&#8221;</span></td>
    <td>Managers understand <i>a job completed</i> instantly, and the arm makes it physical in a
    way driving never is</td></tr>
<tr><td class="n">3</td><td><a href="{g8}/step-11.html">G8 Step 11</a><br/>Controller</td>
    <td>Hand a manager the controller and let them drive the lane; the buttons still work the arm
    while they steer</td>
    <td>They stop watching and start participating. The most memorable ninety seconds of the day
    &#8212; always end here</td></tr>
</table>

<h3>Timing &#8212; about 10 minutes</h3>
<table>
<tr><td class="t">0&#8211;3&#8242;</td><td>Moment 1 &#8212; speak to it. Let a manager say the
  word, not you</td></tr>
<tr><td class="t">3&#8211;7&#8242;</td><td>Moment 2 &#8212; the job, start to finish, hands
  off</td></tr>
<tr><td class="t">7&#8211;10&#8242;</td><td>Moment 3 &#8212; hand over the controller. End here,
  on them driving</td></tr>
</table>

<h3>What to build</h3>
<table>
<tr><th>From the kits</th><th>Classroom</th></tr>
<tr><td>One tracked Rover &#8212; mBot2 kit + add-on pack, including the grip arms and the
  Bluetooth controller. Ultrasonic mounted. Charged the night before.</td>
  <td>Two taped zones about a metre apart &#183; a foam block sized to the gripper &#183; 3
  cardboard boxes for the driving lane &#183; masking tape &#183; <b>Wi-Fi the robot can actually
  reach</b></td></tr>
</table>

<h3>Prep week</h3>
<table>
<tr><td class="t">Mon&#8211;Tue</td><td><b>Build the Rover.</b> If it is not built yet, this is the
  whole week. Two traps: the track modules <b>mirror</b> each other, and the motor cables are
  <b>crossed</b> on the Rover &#8212; the opposite of the wheeled build.</td></tr>
<tr><td class="t">Wed</td><td>Redo turn calibration on tracks, then find the arm&#8217;s safe range
  by hand and put it into constants. Build the job:
  <a href="{g8}/step-04.html">Step 4</a> arm blocks &#8594;
  <a href="{g8}/step-22.html">Step 22</a> the full job.</td></tr>
<tr><td class="t">Thu</td><td>Connect to the venue Wi-Fi and test speech <b>in the actual room</b>,
  at the demo&#8217;s time of day. Two clean run-throughs. Freeze and save as
  <b>demo-g8-job-final</b>.</td></tr>
<tr><td class="t">Fri AM</td><td>Pre-flight below. Re-test speech in the morning &#8212; the room
  sounds different when it is full.</td></tr>
</table>

<h3>What will go wrong, and what to do</h3>

<div class="warn"><b>Check this first, today: the Wi-Fi.</b> Speech recognition is a <b>cloud</b>
call &#8212; the robot sends the audio away and gets words back. No internet, no moment 1. Test it
on the venue network, not your home one, and find out whether the guest network needs a browser
login the robot cannot perform.
<span class="fix">&#8594; If the venue Wi-Fi cannot be trusted, bring a phone hotspot and pair the
robot to it during prep week. If speech is out entirely, moment 1 becomes the controller and you
open on moment 2.</span></div>

<div class="risk"><b>The Rover build is the long pole.</b> The tracked build is hours, not minutes,
and it gates the entire demo.
<span class="fix">&#8594; Start it first, not last. If it is not standing by Tuesday, run the
Grade 7 demo alone this round rather than show a half-built robot.</span></div>

<div class="risk"><b>A room full of people sounds nothing like an empty one.</b> Recognition drops
sharply with background noise, and it will be at its worst exactly when the audience arrives.
<span class="fix">&#8594; Stand close, say one clear word, and choose command words that sound
nothing alike. Rehearse with the room talking. Have the robot show what it <i>thought</i> it heard,
so a miss is visible rather than mysterious.</span></div>

<div class="risk"><b>Servo arms strip if forced.</b> Visitors will grab them.
<span class="fix">&#8594; Never drive the arm past resistance, and say &#8220;you can drive it, the
arms are for looking&#8221; when you hand the controller over.</span></div>

<h3>Friday morning pre-flight</h3>
<ul class="chk">
<li>Rover fully charged, controller charged, spare batteries to hand</li>
<li>Robot on the venue Wi-Fi, with <b>network connected?</b> showing true on its screen</li>
<li>Speech tested this morning, in this room, with people talking</li>
<li>Zones taped, foam block in place, driving-lane boxes placed</li>
<li>Arm limits confirmed and the guard tested with a deliberately bad angle</li>
<li>The whole job run once, silently, end to end</li>
<li>Controller paired and driving &#8212; or moment 3 already swapped out</li>
<li>Printed leave-behinds: the demo tour and the Grade 8 materials page</li>
</ul>

<h3>Leave-behind</h3>
<p class="lede">Print these and have them on the table &#8212; they answer the two questions
managers ask after the robot stops moving: what does the year look like, and what do we have to
buy.
<br/>&#183; <a href="{base}demo.html">The demo tour</a> &#8212; the step ladder for each grade
<br/>&#183; <a href="{g8}/materials.html">Grade 8 materials</a> &#8212; both boxes, tagged by
source
<br/>&#183; <a href="{g8}/steps.html">The course itself</a> &#8212; {g8steps} steps, {g8hours} hours, every hour
accounted for</p>

<p class="pair"><b>Running both demos back-to-back?</b> Grade 8 goes <b>second</b>. Run
<a href="{base}demo-prep-g7.html">Grade 7 &#183; Rescue Run</a> first on its own mat, clear it,
then bring people to this course. The handover line is the whole pitch: <i>&#8220;That one works
on its own. Now let me show you the one you can talk to.&#8221;</i> Budget about 20 minutes for
the pair.</p>
</div>
"""
