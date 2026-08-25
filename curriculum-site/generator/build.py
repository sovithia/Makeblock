# -*- coding: utf-8 -*-
"""Static-site builder. Reads content/*.yaml, writes site/.

Usage: python generator/build.py [--locale km] [--project ../Grade4-5-6]

Locales other than the default `en` read content-<loc>/ and write site/<loc>/, so
the English site stays exactly where it was and every added language is additive.

`--project DIR` points the same generator at a sibling content tree (DIR/content*
→ DIR/site). This is how Grades 4-5-6 are built: they are a separate *content*
tree, not a separate project, so there is exactly one copy of the generator,
renderer, scenes and part catalogue. Part and block photos stay shared too — the
sibling's site/assets is a symlink back here rather than 1.4 MB of duplicates.
Grades are discovered by globbing `grade*`, so each tree simply builds whichever
grades it contains.
"""
import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parts_catalog
import render
import teacher
import demo_prep
import glossary
import i18n
from i18n import t, num

ROOT = Path(__file__).resolve().parents[1]
# opcode -> one-line explanation, shown the first time a block appears in a
# course. Optional: a block with no note simply gets no line.
def _notes_file(name):
    """The active locale's copy if it has one, else the English original.

    Lets `content-km/block-notes.yaml` exist without the generator caring, and
    keeps the English text showing until it does.
    """
    for f in (CONTENT / name, ROOT / "content" / name):
        if f.exists():
            return yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    return {}


def _load_block_notes():
    return _notes_file("block-notes.yaml")


# The IDEA a step introduces, keyed by its `concept:` string. Shown once per
# course, on the first step declaring it. Optional, and deliberately sparse.
def _load_concept_notes():
    return _notes_file("concept-notes.yaml")
CONTENT = ROOT / "content"
SITE = ROOT / "site"

# A school funding 40 hours should be able to see where that lands.
FORTY = 40.0

# Grades 4-6 ship in two timings from one source file; 7-9 are 1 h only.
# `lkey` is looked up per build so the label follows the active locale.
VARIANTS = {
    "short": {"sfx": "", "per": "1 h", "total": "20 h", "lkey": "v_short"},
    "long": {"sfx": "-long", "per": "2 h", "total": "40 h", "lkey": "v_long"},
}


def vlabel(v, grade=None):
    """Human label for a timing. Follows the grade's declared hours when it
    overrides them, so a 2 h grade never gets labelled "1-hour version"."""
    if grade and grade.get("per"):
        return t("v_long" if grade["per"].startswith("2") else "v_short")
    return t(VARIANTS[v]["lkey"])


def timing_of(grade, variant):
    """(per-session, course total) — a grade may override the variant defaults.

    Grades 4-6 ship two timings from one source, so the defaults in VARIANTS
    apply. Grades 7-9 run a single timing whose length is a per-grade decision,
    declared as `per:` / `total:` in grade.yaml.
    """
    V = VARIANTS[variant]
    return grade.get("per", V["per"]), grade.get("total", V["total"])


def variants_of(grade):
    return grade.get("timings", ["short"])


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        # imply() is applied here, the one funnel every step and session passes
        # through, so a lesson's parts list can never disagree with its code.
        return parts_catalog.imply(_graft_use(yaml.safe_load(f), path))


def _graft_use(unit, path):
    """Copy each phase's `use:` list from the English lesson.

    Which blocks a phase picks up is language-neutral — the same opcodes render
    with the same artwork in every locale — so it is authored once, in
    `content/`, and grafted onto the translation here by flow position. Keeping
    one copy is the whole point: a `use:` list duplicated per locale is exactly
    the kind of parallel data that has silently drifted before.
    """
    if not isinstance(unit, dict) or not unit.get("steps"):
        return unit
    src = Path(str(path).replace(str(CONTENT), str(ROOT / "content"), 1))
    if src == Path(path) or not src.exists():
        return unit
    en = yaml.safe_load(src.read_text(encoding="utf-8")) or {}
    en_steps = en.get("steps") or []
    if len(en_steps) != len(unit["steps"]):
        raise SystemExit(
            f"{path}: flow has {len(unit['steps'])} phases but the English "
            f"lesson has {len(en_steps)} — they must stay aligned for `use:` "
            f"to graft. Fix the translation before rebuilding.")
    for mine, theirs in zip(unit["steps"], en_steps):
        if theirs.get("use"):
            mine["use"] = theirs["use"]
    return unit


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    # a --project build writes outside ROOT, where relative_to() would raise
    print("wrote", os.path.relpath(path, ROOT))


def strip_tags(t):
    return re.sub(r"<[^>]+>", "", t)


def chrome(links, rel):
    """The screen-only nav bar. `rel` is this page's path under its own site root
    ("grade7/step-01.html"), which is what the language switch needs to aim at the
    same page in the other locale tree — so every caller states where it is being
    written, and the switch can never point at a page that is not there."""
    glossary = "../" * rel.count("/") + "glossary.html"
    glossary_link = (f'<a class="glossary-link" href="{glossary}" target="_blank" '
                     f'rel="noopener noreferrer">{t("glossary_new_tab")}</a>')
    inner = "".join(links) + glossary_link + render.lang_toggle(rel)
    return f'<div class="chrome">{inner}</div>'


def session_search_record(gnum, s):
    L = s.get("long") or {}
    long_text = [L.get("goal", "")] + [L[k]["text"] for k in ("warmup", "maker", "share") if L.get(k)]
    long_text += [ch["text"] for ch in L.get("challenges", [])] + L.get("success", [])
    text = " ".join(
        [s["goal"]] + [strip_tags(p) for p in s["teach"]]
        + [st["text"] for st in s["steps"]] + s.get("tips", []) + s["success"]
        + [f'{g["label"]} {g["value"]}' for g in s.get("guide", [])]
        + ([s["code"]["source"]] if s.get("code") else []) + long_text)
    return {"grade": gnum, "n": s["n"], "title": s["title"], "goal": s["goal"],
            "label": f'G{gnum} · S{s["n"]}',
            "url": f"grade{gnum}/session-{s['n']:02d}.html", "text": text.lower()}


SEARCH_JS = """
<script>
function doSearch(q) {
  const out = document.getElementById('results');
  q = q.trim().toLowerCase();
  if (q.length < 2) { out.innerHTML = ''; return; }
  const terms = q.split(/\\s+/);
  const hits = SEARCH_INDEX.filter(r => terms.every(t =>
    r.title.toLowerCase().includes(t) || r.text.includes(t)));
  out.innerHTML = hits.length === 0 ? '<p class="muted">' + NO_MATCH + '</p>' :
    hits.map(r => `<a class="hit" href="${document.body.dataset.root}${r.url}">
      <span class="hitgrade">${r.label}</span> <b>${r.title}</b>
      <span class="hitgoal">${r.goal}</span></a>`).join('');
}
</script>
"""

SEARCH_CSS = """
<style>
.searchbox { width: 100%; font-size: 11pt; padding: 3mm; border: 1.5px solid #cbd5e1;
  border-radius: 8px; font-family: inherit; margin-bottom: 4mm; }
.hit { display: block; padding: 2.5mm 3mm; border: 1px solid #e2e8f0; border-radius: 8px;
  margin-bottom: 2mm; text-decoration: none; color: #1e293b; }
.hit:hover { border-color: #0e7fc1; background: #f0f7fc; }
.hitgrade { display: inline-block; background: #0e7fc1; color: #fff; border-radius: 6px;
  padding: 0.4mm 2mm; font-size: 7.5pt; font-weight: bold; margin-right: 2mm; }
.hitgoal { display: block; color: #64748b; font-size: 8.5pt; margin-top: 1mm; }
.gradecard { display: block; border: 2px solid; border-radius: 12px; padding: 5mm;
  margin-bottom: 4mm; text-decoration: none; color: #1e293b; }
.gradecard h3 { margin: 0 0 1mm 0; }
.gradecard a { text-decoration: none; }
.gradecard a:hover { text-decoration: underline; }
.gradecard:hover { background: #f8fafc; }
.slist { list-style: none; padding: 0; }
.slist li { margin-bottom: 1.5mm; }
.slist .dl { margin-left: 2mm; white-space: nowrap; font-size: 8.4pt; }
.slist a { text-decoration: none; color: #0e7fc1; font-weight: bold; }
.slist .todo { color: #94a3b8; }
.slist .un { color: #64748b; font-size: 8.4pt; margin-left: 2mm; }
.course-intro { margin: 5mm 0 7mm; }
.course-intro > h2 { margin-bottom: 1.5mm; }
.course-intro .intro-lede { color: #475569; margin: 0 0 4mm; max-width: 175mm; }
.orient-grid { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 4mm; }
.orient-card { border: 1.5px solid #dbe7ef; border-radius: 10px; padding: 4mm 4.5mm;
  background: #fff; break-inside: avoid; }
.orient-card.wide { grid-column: 1 / -1; }
.orient-card h3 { margin: 0 0 2mm; color: #0a5c8c; font-size: 13pt; }
.orient-card p { margin: 0 0 2mm; }
.orient-card p:last-child { margin-bottom: 0; }
.orient-card ul, .orient-card ol { margin: 1.5mm 0 0; padding-left: 6mm; }
.orient-card li { margin-bottom: 1.4mm; }
.session-flow { counter-reset: flow; list-style: none; padding: 0 !important; display: grid;
  grid-template-columns: repeat(3,minmax(0,1fr)); gap: 2.5mm; }
.session-flow li { counter-increment: flow; border-left: 3px solid #0e7fc1;
  background: #f4f9fc; border-radius: 0 7px 7px 0; padding: 2.5mm 3mm; }
.session-flow li::before { content: counter(flow); display: inline-grid; place-items: center;
  width: 5mm; height: 5mm; margin-right: 1.5mm; border-radius: 50%;
  background: #0e7fc1; color: white; font-size: 7.5pt; font-weight: bold; }
.session-flow small { display: block; color: #64748b; margin: 1mm 0 0 6.5mm; }
@media (max-width: 760px) {
  .orient-grid, .session-flow { grid-template-columns: 1fr; }
  .orient-card.wide { grid-column: auto; }
}
</style>
"""


COURSE_HOME = {
    "en": {
        "head": "How to run this course",
        "lede": "A practical structure for preparing the room, pacing the curriculum, supporting hands-on work, and closing each session well.",
        "setup_h": "Setup",
        "setup": "Create one dedicated Gmail account for each student group. Students use that account to sign in to mBlock and save their work in the cloud throughout the course.",
        "rules_h": "General rules",
        "rules": [
            "The timetable provides up to 44 scheduled hours, with additional buffer or extension time where students need it.",
            "The teacher may accelerate, skip, repeat, or slow down lessons. Understanding is more important than simply finishing the curriculum.",
            "If a student or group falls far behind, the teacher may give them the relevant .mblock solution file so they can rejoin the class.",
            "If a lesson finishes early, the teacher may continue directly to the next lesson.",
            "If the curriculum is completed and teaching hours remain, contact the course author for additional lessons.",
        ],
        "prep_h": "Course preparation",
        "prep": [
            "Before class, the teacher builds and tests the expected result. The solution section and answer project may be used as a reference.",
            "Print one lesson sheet for every student.",
            "Print one solution sheet for the teacher.",
            "Prepare and charge the robots, then confirm that every required part and account is ready.",
        ],
        "structure_h": "Session structure",
        "structure": [
            ("Theory", "Introduce the idea and the vocabulary students need."),
            ("Expected result", "Show what a successful result looks like before students begin."),
            ("Distribute", "Give each student the printed lesson sheet."),
            ("Hands-on work", "Students program, build, test, and debug the hardware themselves."),
            ("Teacher support", "Answer questions and assist when needed, but leave the thinking and building to students."),
            ("Pacing", "Watch the time, support groups that are falling behind, and move ahead when the class is ready."),
        ],
        "wrap_h": "Wrapping up · 5–15 minutes",
        "wrap": [
            "End with an open discussion. Everyone should be free to ask questions and explain what they understood, attempted, or found difficult.",
            "The teacher checks each student’s progress and notes who may need support in the next session.",
        ],
        "assessment_h": "Lesson assessment",
        "assessment": [
            "Complete one rubric for each student, even when the robot was built by a group. A group result is evidence, but it is not automatically every member’s grade.",
            "Score only behavior observed in that lesson: understanding, practical problem-solving, helpful collaboration, and engagement and attitude.",
            "Use N/O when absence, equipment failure, or the assigned role gave no fair opportunity to observe a criterion. Do not convert N/O into zero.",
            "Write one short piece of evidence and one useful next step. Compare a student with their earlier work as well as the lesson standard.",
        ],
    },
    "km": {
        "head": "របៀបដំណើរការវគ្គសិក្សានេះ",
        "lede": "រចនាសម្ព័ន្ធអនុវត្តសម្រាប់រៀបចំថ្នាក់ កំណត់ល្បឿនកម្មវិធី សម្របសម្រួលការអនុវត្ត និងបញ្ចប់មេរៀននីមួយៗ។",
        "setup_h": "ការរៀបចំ",
        "setup": "បង្កើតគណនី Gmail មួយដាច់ដោយឡែកសម្រាប់ក្រុមសិស្សនីមួយៗ។ សិស្សប្រើគណនីនោះដើម្បីចូល mBlock និងរក្សាទុកការងារនៅលើ cloud ពេញមួយវគ្គ។",
        "rules_h": "គោលការណ៍ទូទៅ",
        "rules": [
            "កាលវិភាគមានរហូតដល់ ៤៤ ម៉ោង រួមជាមួយម៉ោងបន្ថែម ឬម៉ោងបម្រុងនៅពេលសិស្សត្រូវការ។",
            "គ្រូអាចបង្កើនល្បឿន រំលង ធ្វើឡើងវិញ ឬបន្ថយល្បឿនមេរៀន។ ការយល់ដឹងសំខាន់ជាងការបញ្ចប់កម្មវិធីតែប៉ុណ្ណោះ។",
            "បើសិស្ស ឬក្រុមណាមួយយឺតខ្លាំង គ្រូអាចផ្តល់ឯកសារចម្លើយ .mblock ដែលពាក់ព័ន្ធ ដើម្បីឱ្យពួកគេតាមទាន់ថ្នាក់។",
            "បើមេរៀនណាមួយបញ្ចប់មុនម៉ោង គ្រូអាចបន្តទៅមេរៀនបន្ទាប់បានភ្លាម។",
            "បើបានបញ្ចប់កម្មវិធីទាំងមូល ហើយនៅសល់ម៉ោងបង្រៀន សូមទាក់ទងអ្នករៀបចំវគ្គសម្រាប់មេរៀនបន្ថែម។",
        ],
        "prep_h": "ការត្រៀមវគ្គសិក្សា",
        "prep": [
            "មុនចូលថ្នាក់ គ្រូត្រូវបង្កើត និងសាកល្បងលទ្ធផលរំពឹងទុក។ អាចប្រើផ្នែកចម្លើយ និងគម្រោងចម្លើយជាឯកសារយោង។",
            "បោះពុម្ពសន្លឹកមេរៀនមួយសម្រាប់សិស្សម្នាក់ៗ។",
            "បោះពុម្ពសន្លឹកចម្លើយមួយសម្រាប់គ្រូ។",
            "រៀបចំ និងសាកថ្មរូបយន្ត ហើយពិនិត្យថាផ្នែក និងគណនីចាំបាច់ទាំងអស់រួចរាល់។",
        ],
        "structure_h": "រចនាសម្ព័ន្ធមេរៀន",
        "structure": [
            ("ទ្រឹស្តី", "ណែនាំគំនិត និងពាក្យដែលសិស្សត្រូវការ។"),
            ("លទ្ធផលរំពឹងទុក", "បង្ហាញថាលទ្ធផលជោគជ័យមានរូបរាងដូចម្តេច មុនសិស្សចាប់ផ្តើម។"),
            ("ចែកសន្លឹក", "ផ្តល់សន្លឹកមេរៀនដែលបានបោះពុម្ពដល់សិស្សម្នាក់ៗ។"),
            ("ការអនុវត្ត", "សិស្សសរសេរកម្មវិធី សាងសង់ សាកល្បង និងកែកំហុសលើឧបករណ៍ដោយខ្លួនឯង។"),
            ("ការគាំទ្ររបស់គ្រូ", "ឆ្លើយសំណួរ និងជួយនៅពេលចាំបាច់ ប៉ុន្តែទុកឱ្យសិស្សគិត និងសាងសង់ដោយខ្លួនឯង។"),
            ("ល្បឿនមេរៀន", "តាមដានពេលវេលា ជួយក្រុមដែលយឺត និងបន្តទៅមុខនៅពេលថ្នាក់រួចរាល់។"),
        ],
        "wrap_h": "ការបញ្ចប់ · ៥–១៥ នាទី",
        "wrap": [
            "បញ្ចប់ដោយការពិភាក្សាបើកចំហ។ គ្រប់គ្នាគួរអាចសួរសំណួរ និងពន្យល់អ្វីដែលពួកគេយល់ បានសាកល្បង ឬជួបការលំបាក។",
            "គ្រូពិនិត្យវឌ្ឍនភាពរបស់សិស្សម្នាក់ៗ និងកំណត់ថានរណាត្រូវការជំនួយនៅមេរៀនបន្ទាប់។",
        ],
        "assessment_h": "ការវាយតម្លៃមេរៀន",
        "assessment": [
            "បំពេញ rubric មួយសម្រាប់សិស្សម្នាក់ៗ ទោះបីរូបយន្តត្រូវបានសាងសង់ជាក្រុមក៏ដោយ។ លទ្ធផលក្រុមជាភស្តុតាង ប៉ុន្តែមិនមែនជាពិន្ទុរបស់សមាជិកគ្រប់គ្នាដោយស្វ័យប្រវត្តិទេ។",
            "ដាក់ពិន្ទុតែអាកប្បកិរិយាដែលបានសង្កេតក្នុងមេរៀននោះ៖ ការយល់ដឹង ការដោះស្រាយបញ្ហាជាក់ស្តែង ការសហការជួយគ្នា និងការចូលរួមនិងឥរិយាបថ។",
            "ប្រើ N/O នៅពេលអវត្តមាន ឧបករណ៍ខូច ឬតួនាទីដែលបានចាត់ឲ្យមិនផ្តល់ឱកាសសមរម្យដើម្បីសង្កេតលក្ខណៈវិនិច្ឆ័យ។ កុំប្តូរ N/O ទៅជាសូន្យ។",
            "សរសេរភស្តុតាងខ្លីមួយ និងជំហានបន្ទាប់ដែលមានប្រយោជន៍មួយ។ ប្រៀបធៀបសិស្សជាមួយការងារមុនរបស់ខ្លួន និងស្តង់ដារមេរៀន។",
        ],
    },
}


def course_home_html():
    d = COURSE_HOME.get(i18n.LOCALE, COURSE_HOME["en"])
    rules = "".join(f"<li>{x}</li>" for x in d["rules"])
    prep = "".join(f"<li>{x}</li>" for x in d["prep"])
    flow = "".join(f"<li><b>{h}</b><small>{p}</small></li>" for h, p in d["structure"])
    wrap = "".join(f"<li>{x}</li>" for x in d["wrap"])
    assessment = "".join(f"<li>{x}</li>" for x in d["assessment"])
    return f'''<section class="course-intro">
<h2>{d["head"]}</h2><p class="intro-lede">{d["lede"]}</p>
<div class="orient-grid">
  <div class="orient-card"><h3>{d["setup_h"]}</h3><p>{d["setup"]}</p></div>
  <div class="orient-card"><h3>{d["prep_h"]}</h3><ul>{prep}</ul></div>
  <div class="orient-card wide"><h3>{d["rules_h"]}</h3><ul>{rules}</ul></div>
  <div class="orient-card wide"><h3>{d["structure_h"]}</h3><ol class="session-flow">{flow}</ol></div>
  <div class="orient-card wide"><h3>{d["wrap_h"]}</h3><ul>{wrap}</ul></div>
  <div class="orient-card wide"><h3>{d["assessment_h"]}</h3><ul>{assessment}</ul></div>
</div></section>'''


# demo tour: milestone sessions shown per grade (n, one-line hook for managers)
DEMO_MILESTONES = {
    "4": [(4, "The robot boots, gets a name, and says hello — the moment it becomes theirs"),
          (8, "One repeat block replaces twenty — the first taste of real programming"),
          (12, "Motion, light and sound become a 30-second routine they invented"),
          (16, "Clap, and the robot answers — reactive behaviour with no `if` in sight")],
    "5": [(5, "The first `if` — the robot stops itself before the wall"),
          (10, "Colour cards become commands the robot reads off the floor"),
          (13, "A variable remembers — the robot starts keeping score"),
          (16, "Line following, tuned by timed laps")],
    "6": [(4, "Students build their own block and name it — abstraction, age 11"),
          (11, "A rule, not a route: the robot solves a maze it has never seen"),
          (14, "Two robots talk to each other over the classroom network"),
          (15, "The relay: robot A finishes and hands off to robot B by message")],
    # 7 and 8 are ladders into the capstone each demo shows: every card is one
    # ingredient of the Rescue Run / Companion Robot the manager just watched.
    # See generator/demo_prep.py.
    "7": [(5, "Precision needs calibration — students discover it with a ruler"),
          (12, "First real autonomy — the robot roams and avoids on its own"),
          (15, "Line following, tuned by timed laps and one-change-at-a-time discipline"),
          (16, "The floor becomes an instruction: a colour patch stops the robot on the spot")],
    "8": [(7, "Original animated emojis, designed pixel by pixel"),
          (8, "Shake it, clap at it, cover its eyes — the robot answers with a mood"),
          (12, "The flagship: an ML model mirrors your facial expression"),
          (16, "Full manual mastery on an obstacle course")],
    "9": [(6, "Proportional control defeats the wobble planted in Grade 7"),
          (7, "Engineering arguments are graphs, not opinions"),
          (11, "The arms earn their keep: grip, carry through a turn, release on target"),
          (13, "The full pipeline in miniature: navigate, detect, pick, deliver")],
}

# Grades 7-8 are step courses now, so their tour cards come from steps rather
# than sessions. Chosen for what a manager can watch and immediately understand.
STEP_MILESTONES = {
    "7": [(2, "Command 100 cm, measure the miss with a ruler — a tolerance, in hour three"),
          (13, "Drive it by hand and it replays the route by itself — a list, made visible"),
          (18, "Line following, written as a block the students named themselves"),
          (19, "One variable decides what the robot is doing — a state machine, age 12")],
    "8": [(2, "Same brain, rebuilt on tracks — and every number from last year is now wrong"),
          (11, "Two sticks and sixteen buttons, and why a controller must be asked, not told"),
          (17, "Say a word and the robot obeys — speech matched against a vocabulary it holds"),
          (19, "Voice, controller and sensors all feeding one job machine")],
}

DEMO_CSS = """
<style>
.reveal { background: #fef9ec; border-left: 4px solid #d97706; border-radius: 0 8px 8px 0;
  padding: 2.4mm 3.5mm; font-size: 8.6pt; color: #7c4a06; margin-top: 2mm; }
.gsec { margin-bottom: 12mm; }
.ghead { border-radius: 10px; color: #fff; padding: 4mm 6mm; margin-bottom: 3mm; }
.ghead .gk { font-size: 8pt; text-transform: uppercase; letter-spacing: 2px; opacity: .9; }
.ghead h2 { margin: 1mm 0 0 0; font-size: 16pt; }
.glede { color: #475569; font-size: 9.6pt; }
.dmile { font-size: 10.5pt; text-transform: uppercase; letter-spacing: 1.5px; margin: 5mm 0 3mm 0; }
.dgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.dcard { border: 1.8px solid; border-radius: 10px; padding: 3.5mm 4mm; text-decoration: none;
  color: #1e293b; display: block; background: #fff; }
.dcard:hover, .dcap:hover { box-shadow: 0 2px 12px rgba(15,23,42,.15); }
.dk { font-weight: bold; font-size: 10pt; margin-bottom: 1mm; }
.dhook { font-size: 8.8pt; color: #475569; margin-bottom: 2mm; }
.dimg { text-align: center; }
.dimg svg { max-width: 100%; }
.dcrit { margin: 1.5mm 0 0 0; padding-left: 0; list-style: none; font-size: 8.4pt; }
.dcrit li { margin-bottom: 1mm; padding-left: 5mm; text-indent: -5mm; }
.dcrit li::before { content: "\\2611  "; color: #16a34a; }
.dcap { display: block; border: 2.5px solid; border-radius: 12px; padding: 4mm 5mm;
  margin-top: 4mm; text-decoration: none; color: #1e293b; }
.dcaptab { width: 100%; border-collapse: collapse; }
.dcaptab td { vertical-align: middle; }
.dcaptab td:first-child { width: 55%; text-align: center; }
.dmore { font-size: 8.8pt; font-weight: bold; margin-top: 2mm; }
@media (max-width: 700px) { .dgrid { grid-template-columns: 1fr; } }
</style>
"""


def program_name(grades):
    """Program label for the print footer of the cross-grade pages.

    Taken from the content rather than hardcoded: css() otherwise falls back to
    the Rover-era name, which is wrong for the Box-1-only 4-6 strand.
    """
    for _g, (grade, _s) in sorted(grades.items()):
        if grade.get("program"):
            return grade["program"]
    return t("program_default")


def _demo_section(c, grade, gnum, by_n, picks, cap, url, lede):
    """One grade's block on the demo tour: milestone cards + the capstone card."""
    cards = []
    for n, hook in picks:
        s = by_n.get(n)
        if not s:
            continue
        svg = render.scenes.SCENES[s["result"]["scene"]](c, **s["result"].get("params", {}))
        crit = "".join(f"<li>{x}</li>" for x in s["success"][:2])
        cards.append(f"""
<a class="dcard" href="{url(n)}" style="border-color:{c['color']}">
  <div class="dk" style="color:{c['dark']}">{render.esc(s['title'])}</div>
  <div class="dhook">{hook}</div>
  <div class="dimg">{svg}</div>
  <ul class="dcrit">{crit}</ul>
</a>""")
    cb = grade["capstone_blurb"]
    cap_svg = render.scenes.SCENES[cap["result"]["scene"]](c, **cap["result"].get("params", {}))
    cap_crit = "".join(f"<li>{x}</li>" for x in cap["success"])
    return f"""
<div class="gsec">
  <div class="ghead" style="background: linear-gradient(110deg, {c['dark']}, {c['color']})">
    <div class="gk">{t("demo_kicker", n=num(gnum), form=grade['form'],
                       codemode=grade['codemode'])}</div>
    <h2>{grade['theme']}</h2>
  </div>
  <p class="glede">{lede}</p>
  <h3 class="dmile" style="color:{c['dark']}">{t("demo_milestones")}</h3>
  <div class="dgrid">{''.join(cards)}</div>
  <a class="dcap" href="{url(cap['n'])}" style="border-color:{c['color']}; background:{c['light']}">
    <div class="dk" style="color:{c['dark']}">{t("demo_capstone", name=cb['name'])}</div>
    <div class="dhook">{cb['text']}</div>
    <table class="dcaptab"><tr><td>{cap_svg}</td><td><ul class="dcrit">{cap_crit}</ul></td></tr></table>
    <div class="dmore" style="color:{c['dark']}">{t("demo_open")}</div>
  </a>
</div>"""


def demo_page(grades):
    sections = []
    for gnum, (grade, sessions) in sorted(grades.items()):
        c = render.grade_c(grade)
        # a converted grade tours its steps; the last step is the capstone
        sdir = CONTENT / f"grade{gnum}" / "steps"
        if sdir.is_dir():
            items = [load_yaml(f) for f in sorted(sdir.glob("*.yaml"))]
            by_n = {s["n"]: s for s in items}
            picks = STEP_MILESTONES.get(gnum, [])
            last = items[-1]
            hrs = sum(float(s.get("hours", 0)) for s in items)
            sections.append(_demo_section(
                c, grade, gnum, by_n, picks, last,
                url=lambda n: f"grade{gnum}/step-{n:02d}.html",
                lede=f"{len(items)} steps · {hrs:g} hours · "
                     f"{grade['form']} · {grade['codemode']}"))
            continue
        by_n = {s["n"]: s for s in sessions}
        if 20 not in by_n:      # grade still being authored — no capstone card yet
            continue
        cards = []
        for n, hook in DEMO_MILESTONES.get(gnum, []):
            s = by_n.get(n)
            if not s:
                continue
            hook = i18n.hook(gnum, n) or hook
            svg = render.scenes.SCENES[s["result"]["scene"]](c, **s["result"].get("params", {}))
            crit = "".join(f"<li>{x}</li>" for x in s["success"][:2])
            cards.append(f"""
<a class="dcard" href="grade{gnum}/session-{n:02d}.html" style="border-color:{c['color']}">
  <div class="dk" style="color:{c['dark']}">{t("demo_card", n=num(n), title=s['title'])}</div>
  <div class="dhook">{hook}</div>
  <div class="dimg">{svg}</div>
  <ul class="dcrit">{crit}</ul>
</a>""")
        s20 = by_n[20]
        cb = grade["capstone_blurb"]
        cap_svg = render.scenes.SCENES[s20["result"]["scene"]](
            c, **s20["result"].get("params", {}))
        cap_crit = "".join(f"<li>{x}</li>" for x in s20["success"])
        vl = variants_of(grade)
        timing = (t("demo_or").join(timing_of(grade, v)[0] for v in vl)) + t("demo_sessions_word")
        totals = (" / ".join(timing_of(grade, v)[1] for v in vl))
        sections.append(f"""
<div class="gsec">
  <div class="ghead" style="background: linear-gradient(110deg, {c['dark']}, {c['color']})">
    <div class="gk">{t("demo_kicker", n=num(gnum), form=grade['form'],
                       codemode=grade['codemode'])}</div>
    <h2>{grade['theme']}</h2>
  </div>
  <p class="glede">{t("demo_glede", timing=timing, units=num(len(c['units'])), totals=totals)}</p>
  <div class="center">{render.unit_strip(c)}</div>
  <h3 class="dmile" style="color:{c['dark']}">{t("demo_milestones")}</h3>
  <div class="dgrid">{''.join(cards)}</div>
  <a class="dcap" href="grade{gnum}/session-20.html" style="border-color:{c['color']}; background:{c['light']}">
    <div class="dk" style="color:{c['dark']}">{t("demo_capstone", name=cb['name'])}</div>
    <div class="dhook">{cb['text']}</div>
    <table class="dcaptab"><tr><td>{cap_svg}</td><td><ul class="dcrit">{cap_crit}</ul></td></tr></table>
    <div class="dmore" style="color:{c['dark']}">{t("demo_open")}</div>
  </a>
</div>""")
    dchrome = chrome([f'<a href="index.html">{t("all_grades")}</a>',
                      '<span class="spacer"></span>',
                      f'<span class="dim">{t("demo_nav")}</span>'], "demo.html")
    body = f"""
{dchrome}
<h2 class="section">{t("demo_head")}</h2>
<p class="glede" style="margin-bottom:5mm">{t("demo_lede")}</p>
{''.join(sections)}"""
    theme = render.css({"num": "", "color": "#0e7fc1", "dark": "#0a5c8c",
                        "light": "#e3f1fa", "tint": "#7dd3fc",
                        "program": program_name(grades)})
    return render.page(t("demo_title"), theme, body, DEMO_CSS)


def build():
    # icon ids with real manual photos (tools/extract_parts_images.py output)
    part_imgs = {p.stem for p in (SITE / "assets" / "parts").glob("*.png")}
    # block photos are shared across locales and optional — a block with no photo
    # yet renders as a coloured pill instead (see generator/blocks.py)
    bdir = ROOT / "site" / "assets" / "blocks"
    block_imgs = {p.stem for p in bdir.glob("*.png")}
    block_dims = {p.stem: render.blocks.png_size(p) for p in bdir.glob("*.png")}
    block_dims = {k: v for k, v in block_dims.items() if v}
    boxes = load_yaml(CONTENT / "boxes.yaml")
    grades = {}
    for gdir in sorted(CONTENT.glob("grade*")):
        grade = load_yaml(gdir / "grade.yaml")
        sessions = [load_yaml(p) for p in sorted((gdir / "sessions").glob("*.yaml"))]
        grades[grade["num"]] = (grade, sessions)

    search_index = []

    for gnum, (grade, sessions) in grades.items():
        # A grade converted to steps has no sessions left. Skip the whole
        # session apparatus rather than emit an empty index and a print guide
        # with a cover and nothing behind it.
        if not sessions:
            continue
        c = render.grade_c(grade)
        theme_css = render.css(c)
        have = {s["n"] for s in sessions}
        vlist = variants_of(grade)

        for s in sessions:
            search_index.append(session_search_record(gnum, s))

        for variant in vlist:
            V = VARIANTS[variant]
            sfx = V["sfx"]
            per, total = timing_of(grade, variant)
            # single-timing grades declare their own hours; 7-9 run 2 h with the
            # secondary lane set, detected from the content shape
            two_h = per.startswith("2") if len(vlist) == 1 else None
            sec = any(render.is_secondary_long(x) for x in sessions)
            # link to the same page in the other timing, when this grade has two
            others = [v for v in vlist if v != variant]

            def switch(page_stem):
                return "".join(
                    f'<a href="{page_stem}{VARIANTS[v]["sfx"]}.html">'
                    f'{t("switch_to", label=vlabel(v, grade), total=timing_of(grade, v)[1])}</a>'
                    for v in others)

            # --- individual session pages
            for s in sessions:
                nav = [f'<a href="../index.html">{t("all_grades")}</a>',
                       f'<span class="dim">·</span>',
                       f'<a href="index{sfx}.html">{t("grade_n", n=num(gnum))}</a>',
                       f'<span class="dim">·</span>',
                       f'<span>{t("session_label", n=num(s["n"]), title=s["title"])}</span>',
                       f'<span class="dim">· {per}</span>',
                       '<span class="spacer"></span>']
                if s["n"] - 1 in have:
                    nav.append(f'<a href="session-{s["n"]-1:02d}{sfx}.html">← S{s["n"]-1}</a>')
                if s["n"] + 1 in have:
                    nav.append(f'<a href="session-{s["n"]+1:02d}{sfx}.html">S{s["n"]+1} →</a>')
                nav.append(switch(f'session-{s["n"]:02d}'))
                nav.append(f'<a href="javascript:window.print()">{t("print_session")}</a>')
                rel = f"grade{gnum}/session-{s['n']:02d}{sfx}.html"
                body = chrome(nav, rel) + render.session_page(
                    c, s, part_imgs, "../", show_buildson=True, variant=variant,
                    block_imgs=block_imgs, block_dims=block_dims, two_hour=two_h)
                write(SITE / rel,
                      render.page(t("page_title_session", g=num(gnum), n=num(s['n']),
                                    title=s['title'], per=per),
                                  theme_css, body))

            # --- grade index: session list + at-a-glance + boxes
            items = []
            n = 0
            for uname, count, ucolor in c["units"]:
                for i in range(count):
                    n += 1
                    title = next((s["title"] for s in sessions if s["n"] == n), None)
                    if title:
                        items.append(f'<li><a href="session-{n:02d}{sfx}.html">'
                                     f'S{num(n)} · {title}</a>'
                                     f'<span class="un" style="color:{ucolor}">{uname}</span></li>')
                    else:
                        items.append(f'<li class="todo">S{num(n)} · {t("not_migrated")}'
                                     f'<span class="un">{uname}</span></li>')
            glance = render.intro(grade, boxes, variant, sec)
            # drop the cover block on screen index (a full A4 dark page meant for print)
            glance = glance.split("</div>\n\n", 1)[1] if "</div>\n\n" in glance else glance
            body = chrome([f'<a href="../index.html">{t("all_grades")}</a>',
                           '<span class="spacer"></span>',
                           switch("index"),
                           f'<a href="materials.html">{t("materials")}</a>',
                           f'<a href="print{sfx}.html">{t("full_guide")}</a>'],
                          f"grade{gnum}/index{sfx}.html") + f"""
<h2 class="section">{t("grade_theme", n=num(gnum), theme=grade['theme'])}</h2>
<p class="muted">{grade['form']} · {grade['codemode']} · {t("capstone")}: {grade['capstone']}
 &nbsp;·&nbsp; <b>{t("timing_line", label=vlabel(variant, grade), per=per, total=total)}</b></p>
<h4 class="blk" style="margin-top:5mm">{t("sessions_head")}</h4>
<ul class="slist">{''.join(items)}</ul>
{glance}"""
            write(SITE / f"grade{gnum}" / f"index{sfx}.html",
                  render.page(t("page_title_index", n=num(gnum), theme=grade['theme'],
                                per=per),
                              theme_css, body, SEARCH_CSS))

            # --- print.html: the full PDF document (cover + glance + boxes + sessions)
            pages = "".join(render.session_page(c, s, part_imgs, "../", variant=variant,
                                                block_imgs=block_imgs, block_dims=block_dims,
                                                two_hour=two_h)
                            for s in sessions)
            prel = f"grade{gnum}/print{sfx}.html"
            # The guide is a print artefact, but a teacher opens it on screen
            # before hitting print — and that is the moment they need the Khmer
            # one. The bar is display:none in print, so pagination is untouched.
            pchrome = chrome([f'<a href="index{sfx}.html">{t("grade_n", n=num(gnum))}</a>',
                              '<span class="spacer"></span>'], prel)
            print_html = (f'<!DOCTYPE html><html><head><meta charset="utf-8">'
                          f'<title>{t("page_title_print", n=num(gnum), per=per)}</title>'
                          f'<style>{theme_css}</style>'
                          f'<style>{render.PRINT_CHROME_CSS}{render.LANG_CSS}</style>'
                          f'</head><body>{pchrome}'
                          f'{render.intro(grade, boxes, variant, sec)}{pages}</body></html>')
            write(SITE / prel, print_html)

        # --- materials: one per grade, both timings folded together
        mbody = chrome([f'<a href="../index.html">{t("all_grades")}</a>',
                        f'<span class="dim">·</span>',
                        f'<a href="index.html">{t("grade_n", n=num(gnum))}</a>',
                        '<span class="spacer"></span>',
                        f'<a href="javascript:window.print()">{t("print_session")}</a>'],
                       f"grade{gnum}/materials.html") \
            + render.materials_page(c, grade, sessions, part_imgs, "../",
                                   _notes_file("part-notes.yaml"))
        write(SITE / f"grade{gnum}" / "materials.html",
              render.page(t("materials_title", n=num(gnum)), theme_css, mbody,
                          render.MATERIALS_CSS))

    # --- materials for grades that have been converted to steps. The session
    # loop above skips them entirely, but the demo-prep pages link this page and
    # a step's `parts:` is the same shape a session's is, so it is built from the
    # steps instead.
    for gdir in sorted(CONTENT.glob("grade*")):
        gnum = gdir.name.removeprefix("grade")
        if grades.get(gnum, (None, []))[1] or not (gdir / "steps").is_dir():
            continue
        grade = grades[gnum][0]
        c = render.grade_c(grade)
        units = [load_yaml(f) for f in sorted((gdir / "steps").glob("*.yaml"))]
        mbody = chrome([f'<a href="../index.html">{t("all_grades")}</a>',
                        '<span class="dim">·</span>',
                        f'<a href="steps.html">{t("grade_n", n=num(gnum))}</a>',
                        '<span class="spacer"></span>',
                        f'<a href="javascript:window.print()">{t("print_session")}</a>'],
                       f"grade{gnum}/materials.html") \
            + render.materials_page(c, grade, units, part_imgs, "../",
                                   _notes_file("part-notes.yaml"))
        write(SITE / f"grade{gnum}" / "materials.html",
              render.page(t("materials_title", n=num(gnum)), render.css(c), mbody,
                          render.MATERIALS_CSS))

    # --- landing page with search
    def grade_cards(nums):
        out = []
        for gnum in nums:
            if gnum not in grades:
                continue
            grade, sessions = grades[gnum]
            col = grade["colors"]["color"]
            vl = variants_of(grade)
            # a grade converted to steps links to the course. The 20-session
            # course it replaced was retired on 2026-08-19; the content is in
            # archive/2026-08-12-g7-g8-sessions/ and is no longer built.
            stepdir = CONTENT / f"grade{gnum}" / "steps"
            if stepdir.is_dir():
                nsteps = len(list(stepdir.glob("*.yaml")))
                hours = sum(float(load_yaml(f).get("hours", 0))
                            for f in stepdir.glob("*.yaml"))
                out.append(
                    f'<div class="gradecard" style="border-color:{col}">'
                    f'<h3><a href="grade{gnum}/steps.html" '
                    f'style="color:{grade["colors"]["dark"]}">'
                    f'{t("grade_theme", n=num(gnum), theme=grade["theme"])}</a></h3>'
                    f'<span class="muted">{grade["form"]} · {grade["codemode"]} · '
                    f'{t("capstone")}: {grade["capstone"]} · '
                    f'{nsteps} steps · {hours:g} hours</span>'
                    f'<div style="margin-top:2mm;font-size:9pt">'
                    f'<a href="grade{gnum}/steps.html" style="color:{grade["colors"]["dark"]}">'
                    f'{t("open_course")}</a>'
                    f'</div></div>')
                continue
            # NB: a card cannot be one big <a> — the per-timing links inside it would be
            # nested anchors, which browsers refuse to nest and silently unwrap.
            links = " &nbsp;·&nbsp; ".join(
                f'<a href="grade{gnum}/index{VARIANTS[v]["sfx"]}.html" '
                f'style="color:{grade["colors"]["dark"]}">'
                f'{t("open_guide", per=timing_of(grade, v)[0], total=timing_of(grade, v)[1])}</a>'
                for v in vl)
            out.append(
                f'<div class="gradecard" style="border-color:{col}">'
                f'<h3><a href="grade{gnum}/index{VARIANTS[vl[0]]["sfx"]}.html" '
                f'style="color:{grade["colors"]["dark"]}">'
                f'{t("grade_theme", n=num(gnum), theme=grade["theme"])}</a></h3>'
                f'<span class="muted">{grade["form"]} · {grade["codemode"]} · '
                f'{t("capstone")}: {grade["capstone"]} · {t("n_of_20", n=num(len(sessions)))}</span>'
                f'<div style="margin-top:2mm;font-size:9pt">{links}</div></div>')
        return "".join(out)

    primary = grade_cards(["4", "5", "6"])
    secondary = grade_cards(["7", "8", "9"])
    sections = ""
    if primary:
        sections += (f'<h4 class="blk" style="margin-top:5mm">{t("primary_head")} '
                     f'<span class="muted">{t("primary_sub")}</span></h4>' + primary)
    # guarded: appending this unconditionally left a heading with no cards under it
    # during the period when 7-9 lived outside this tree
    if secondary:
        sections += (f'<h4 class="blk" style="margin-top:5mm">{t("secondary_head")} '
                     f'<span class="muted">{t("secondary_sub")}</span></h4>' + secondary)
    body = chrome(['<span class="spacer"></span>'], "index.html") + f"""
<h2 class="section">{t("landing_head")}</h2>
<p class="muted" style="margin-bottom:4mm">{t("landing_blurb")}
&nbsp;·&nbsp; <a href="demo.html" style="font-weight:bold; color:#0e7fc1">{t("demo_link")}</a>&nbsp;·&nbsp; <a href="glossary.html" style="font-weight:bold; color:#0e7fc1">{t("glossary_link")}</a></p>
{course_home_html()}
<h2 class="section">{t("browse_head")}</h2>
<input class="searchbox" id="q" type="search" placeholder="{t("search_ph")}" oninput="doSearch(this.value)">
<div id="results"></div>
{sections}"""
    generic_css = render.css({"num": "", "color": "#0e7fc1", "dark": "#0a5c8c",
                              "light": "#e3f1fa", "tint": "#7dd3fc",
                              "program": program_name(grades)})
    # index is inlined so search works from file:// as well as over HTTP
    idx_js = ("<script>const SEARCH_INDEX = "
              + json.dumps(search_index, ensure_ascii=False)
              + "; const NO_MATCH = " + json.dumps(t("no_match"), ensure_ascii=False)
              + ";</script>")
    landing = render.page(t("site_title"), generic_css, body,
                          SEARCH_CSS + idx_js + SEARCH_JS)
    landing = landing.replace("<body>", '<body data-root="./">')
    write(SITE / "index.html", landing)

    # --- step courses (Grades 7-8 redesign): content/gradeN/steps/*.yaml
    teacher_grades = {}
    # Rendered alongside the old session pages during the changeover, so nothing
    # breaks while a course is half-converted. Cumulative hours are computed here
    # rather than stored, so inserting a step cannot leave a stale marker behind.
    for gdir in sorted(CONTENT.glob("grade*")):
        sdir = gdir / "steps"
        if not sdir.is_dir():
            continue
        gnum = gdir.name.removeprefix("grade")
        grade, _sessions = grades[gnum]
        c = render.grade_c(grade)
        steps = [load_yaml(f) for f in sorted(sdir.glob("*.yaml"))]
        run = 0.0
        cp = 0
        rows, prev_code, trows = [], {}, []
        # Which step each block is met in for the first time, walking the course
        # in order. Drives the `new` badge and decides which blocks get a note.
        first_seen = {}
        for _s in steps:
            if not (_s.get("code") or {}).get("source"):
                continue
            for _k, _spec in render.blocks._svg.blocks_used(
                    render.blocks.teaching_source(_s["code"]["source"])):
                first_seen.setdefault(_k, _s["n"])
        # A stage's answer project is now the file for its LAST step with code,
        # not one file named after the stage — those stopped existing when the
        # projects went per-step. Resolved here because only this loop can see
        # the whole stage.
        last_coded, here = {}, {}
        for _s in steps:
            if _s.get("project") and _s.get("code"):
                last_coded[_s["project"]] = _s["n"]
        for s in steps:
            run += float(s.get("hours", 0))
            if s.get("kind") == "checkpoint":
                cp += 1
            proj = s.get("project")
            answer = (f'{"-".join(proj.split("-")[:2])}-{last_coded[proj]:02d}'
                      if proj in last_coded else None)
            # The file that holds the build as it stands at THIS step. Steps
            # that carry no script — design-on-paper, freeze-and-run — inherit
            # the newest file before them, because that is still the project the
            # class is working in.
            if proj:
                if s.get("code"):
                    here[proj] = f'{"-".join(proj.split("-")[:2])}-{s["n"]:02d}'
                step_file = here.get(proj)
            else:
                step_file = None
            ctx = {"hours_in": f"{run:g}", "stage_title": s.get("stage_title", ""),
                   "kind": s.get("kind", "step"), "cp_no": cp,
                   "answer_file": answer, "step_file": step_file,
                   # whether a saved project actually exists for this step —
                   # the appended teacher solution links a download only when it does
                   "has_file": bool(step_file and (
                       SITE / "assets" / "projects" / f"{step_file}.mblock").exists())}
            # neighbours in the course, for the nav and the end-of-page link
            idx = steps.index(s)
            prv = steps[idx - 1] if idx else None
            nxt = steps[idx + 1] if idx + 1 < len(steps) else None
            if nxt:
                ctx["next_href"] = f'step-{nxt["n"]:02d}.html'
                ctx["next_label"] = f'{t("step_n", n=num(nxt["n"]))} · {nxt["title"]}'
            nav = [f'<a href="../index.html">{t("all_grades")}</a>',
                   '<span class="dim">·</span>',
                   f'<a href="steps.html">{t("grade_n", n=num(gnum))}</a>',
                   '<span class="dim">·</span>',
                   f'<span>{s["title"]} · ~{run:g} h</span>',
                   '<span class="spacer"></span>']
            if prv:
                nav.append(f'<a href="step-{prv["n"]:02d}.html">'
                           f'← {t("step_n", n=num(prv["n"]))}</a>')
            if nxt:
                nav.append(f'<a href="step-{nxt["n"]:02d}.html">'
                           f'{t("step_n", n=num(nxt["n"]))} →</a>')
            nav.append(f'<a href="#" onclick="printStudentLesson();return false">'
                       f'{t("print_lesson_only")}</a>')
            nav.append(f'<a href="#" onclick="printTeacherSolution();return false">'
                       f'{t("print_solution_only")}</a>')
            # The previous step's script, so the page can dim what was already
            # built and show this lesson's addition at full strength.
            srel = f"grade{gnum}/step-{s['n']:02d}.html"
            body = chrome(nav, srel) + render.session_page(
                c, s, part_imgs, "../", block_imgs=block_imgs,
                block_dims=block_dims, two_hour=False, step=ctx,
                prev_code=prev_code.get(s.get("project")),
                first_seen=first_seen, block_notes=_load_block_notes(),
                concept_note=_load_concept_notes().get(f'G{gnum}-{s["n"]:02d}'))
            body += teacher.inline_solution(
                c, s, ctx, first_seen, _load_block_notes(), "../assets/projects/")
            print_js = """
<script>
function printStudentLesson() {
  document.documentElement.classList.add('student-copy');
  window.print();
}
function printTeacherSolution() {
  document.documentElement.classList.add('solution-copy');
  window.print();
}
window.addEventListener('afterprint', function () {
  document.documentElement.classList.remove('student-copy');
  document.documentElement.classList.remove('solution-copy');
});
</script>
"""
            if s.get("code", {}).get("lang") == "blocks":
                prev_code[s.get("project")] = s["code"]["source"]
            write(SITE / srel,
                  render.page(f"G{gnum} Step {s['n']} · {s['title']}",
                              render.css(c), body,
                              f"<style>{teacher.PRINT_CSS}</style>{print_js}"))
            rows.append((s, run, ctx))
            trows.append((s, ctx))
            # steps join the same search index; `label` keeps a step from being
            # displayed as if it were a session
            stext = " ".join(
                [s.get("goal", ""), s.get("build", ""), s.get("concept", "")]
                + [strip_tags(x) for x in s.get("teach", [])]
                + [x["text"] for x in s.get("steps", [])]
                + s.get("tips", []) + s.get("success", [])
                + ([s["code"]["source"]] if s.get("code") else []))
            search_index.append({
                "grade": gnum, "n": s["n"], "title": s["title"],
                "goal": s.get("build") or s.get("goal", ""),
                "label": f'G{gnum} · {"CP" if s.get("kind") == "checkpoint" else "Step"} {s["n"]}',
                "url": f'grade{gnum}/step-{s["n"]:02d}.html', "text": stext.lower()})

        # --- teacher answer-project page: what each stage's .mblock must contain
        stages, order = {}, []
        for s, run, _ctx in rows:
            st = s.get("stage")
            # A stage with no `project:` builds no .mblock — the assembly stage
            # is hardware, not code — so it has nothing to answer for.
            if not s.get("project"):
                continue
            if st not in stages:
                stages[st] = {"title": s.get("stage_title", ""), "proj": s.get("project", ""),
                              "items": [], "start": run - float(s.get("hours", 0)), "end": run}
                order.append(st)
            stages[st]["end"] = run
            if s.get("kind") != "checkpoint" and s.get("build"):
                stages[st]["items"].append((s["n"], s["title"], s["build"]))
        pdir = SITE / "assets" / "projects"
        cards = []
        for st in order:
            g = stages[st]
            # One .mblock per STEP, not per stage. A stage's steps are not
            # cumulative — each writes its own `when CyberPi starts up` — so a
            # unioned file had several startup hats and several handlers on one
            # button, and crashed on the robot. See tools/mblock_compile.build().
            prefix = "-".join(g["proj"].split("-")[:2])
            # Only steps that carry a script produce a file; design-on-paper
            # and freeze-and-run steps do not, and naming one here would advertise
            # a download that does not exist.
            built = [f"{prefix}-{n:02d}" for n, _t, _b in g["items"]
                     if (pdir / f"{prefix}-{n:02d}.mblock").exists()]
            li = []
            for n, ti, b in g["items"]:
                f = pdir / f"{prefix}-{n:02d}.mblock"
                link = (f'<a href="../assets/projects/{f.name}">{t("download")}</a>'
                        if f.exists() else f'<span class="todo">{t("not_built_yet")}</span>')
                li.append(f'<li><b>Step {n}</b> — {render.esc(b)}'
                          f'<span class="dl">&nbsp;·&nbsp;{link}</span></li>')
            cards.append(
                f'<div class="gsec"><div class="ghead" style="background:linear-gradient'
                f'(110deg,{c["dark"]},{c["color"]})"><div class="gk">Stage {st} · '
                f'{g["start"]:g}–{g["end"]:g} h</div><h2>{render.esc(g["title"])}</h2></div>'
                f'<p class="glede">' + (
                    f'<code>{built[0]}</code> … <code>{built[-1]}.mblock</code>'
                    f' &nbsp;·&nbsp; one project per step, each one the whole build'
                    f' so far — the last is this stage\'s finished project'
                    if built else
                    f'<span class="todo">{t("not_built_yet")}</span>'
                    f' &nbsp;·&nbsp; no step in this stage carries a script yet')
                + '</p>'
                f'<p class="muted">By the end of this stage the class must have built all of:</p>'
                f'<ul class="slist">{"".join(li)}</ul>'
                f'<p class="reveal">{t("reveal_warn", a=g["items"][0][0], b=g["items"][-1][0])}</p>'
                f'</div>' if g["items"] else f'</div>')
        # answers.html used to live here. Its content now follows each lesson;
        # remove any stale aggregate page from an earlier build.
        (SITE / f"grade{gnum}" / "answers.html").unlink(missing_ok=True)

        teacher_grades[gnum] = {"grade": grade, "steps": steps, "rows": trows,
                                "first_seen": first_seen,
                                "notes": _load_block_notes()}

        # index, grouped by stage
        out, seen = [], None
        for s, run, ctx in rows:
            if s.get("stage") != seen:
                seen = s.get("stage")
                # Where a 40-hour timetable can stop. The concept ladder and its
                # four gates finish before Stage E, within 40 h; Stage E is the
                # capstone, teaches no new block, and is the declared extra.
                # Anchored on the stage, not on the running total, because the
                # ladder ends at or below 40 h.
                if seen == "E" and run - float(s.get("hours", 0)) <= FORTY:
                    out.append(f'<div class="fortyline">{t("forty_line")}</div>')
                out.append(f'<h3 class="dmile" style="color:{c["dark"]}">'
                           f'Stage {seen} · {render.esc(s.get("stage_title",""))}</h3>')
            cls = "dcard cpcard" if s.get("kind") == "checkpoint" else "dcard"
            out.append(
                f'<a class="{cls}" href="step-{s["n"]:02d}.html" '
                f'style="border-color:{c["color"]}">'
                f'<div class="dk" style="color:{c["dark"]}">'
                f'{t("step_n", n=num(s["n"]))} &nbsp;·&nbsp; {render.esc(s['title'])}</div>'
                f'<div class="dhook">{render.esc(s.get('build',''))}</div>'
                f'<div class="muted">{render.esc(s.get('concept',''))} &nbsp;·&nbsp; '
                f'{s.get("hours")} h &nbsp;·&nbsp; ~{run:g} h in</div></a>')
        total = rows[-1][1] if rows else 0
        body = chrome([f'<a href="../index.html">{t("all_grades")}</a>',
                       '<span class="spacer"></span>'], f"grade{gnum}/steps.html") + \
            f'<h2 class="section">{render.esc(grade["theme"])}</h2>' + \
            f'<p class="glede">{len(rows)} steps · {total:g} hours</p>' + \
            "".join(out)
        write(SITE / f"grade{gnum}" / "steps.html",
              render.page(f"G{gnum} · steps", render.css(c), body, DEMO_CSS))

    write(SITE / "search-index.json", json.dumps(search_index, ensure_ascii=False))
    write(SITE / "demo.html", demo_page(grades))

    # One glossary per locale, like every other page. The block SOURCE inside
    # each example is language-neutral and grafted from the English file, so only
    # the prose differs between the two.
    html, written, total = glossary.build()
    write(SITE / "glossary.html", html)
    if written < total:
        print(f"  ! glossary ({i18n.LOCALE}): {total - written} blocks not written up")

    # operational prep sheets — one per demo. They are split because the two
    # demos need different hardware: Grade 7 runs on Box 1 alone, Grade 8 needs
    # the Rover add-on. Run back-to-back they read as one arc; each page carries
    # its own mat, prep week, risks and pre-flight so either can be run alone.
    DEMO_PREP_PAGES = [
        ("7", demo_prep.page_g7, "Demo run-of-show · Grade 7 · Rescue Run",
         "demo-prep-g8.html", "Grade 8 demo →"),
        ("8", demo_prep.page_g8, "Demo run-of-show · Grade 8 · A Job Worth Doing",
         "demo-prep-g7.html", "← Grade 7 demo"),
    ]
    for gnum, page_fn, title, sibling, sibling_label in DEMO_PREP_PAGES:
        if gnum not in grades:
            continue
        gc = render.grade_c(grades[gnum][0])
        dp_theme = render.css({"num": "", "color": gc["color"], "dark": gc["dark"],
                               "light": gc["light"], "tint": gc["tint"],
                               "program": program_name(grades)})
        dp_body = chrome([f'<a href="index.html">{t("all_grades")}</a>',
                          f'&nbsp;·&nbsp;<a href="{sibling}">{sibling_label}</a>',
                          '<span class="spacer"></span>',
                          f'<a href="javascript:window.print()">{t("print_session")}</a>'],
                         f"demo-prep-g{gnum}.html")\
            + page_fn("./", **({"steps": str(len(list(
                (CONTENT / f"grade{gnum}" / "steps").glob("*.yaml")))),
                "hours": f"{sum(float(load_yaml(f).get('hours') or 0) for f in
                                (CONTENT / f'grade{gnum}' / 'steps').glob('*.yaml')):g}"}
                if gnum == "8" else {}))
        write(SITE / f"demo-prep-g{gnum}.html",
              render.page(title, dp_theme, dp_body, demo_prep.CSS))

    # the merged Grades 7+8 sheet these two replaced
    (SITE / "demo-prep.html").unlink(missing_ok=True)

    # Teacher answers now follow each Grade 7–8 lesson in the same printable
    # page. Remove the obsolete separate tree, including stale output from an
    # older build.
    shutil.rmtree(SITE / "teacher", ignore_errors=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--locale", default="en",
                    help="en (default) reads content/ → site/; "
                         "any other reads content-<loc>/ → site/<loc>/")
    ap.add_argument("--project", default=None, metavar="DIR",
                    help="build a sibling content tree instead of this one, e.g. "
                         "--project ../Grade4-5-6 (reads DIR/content*, writes DIR/site). "
                         "The generator and the part/block photos stay shared.")
    args = ap.parse_args()
    i18n.use(args.locale)

    base = ROOT if args.project is None else Path(args.project).expanduser().resolve()
    if not base.is_dir():
        raise SystemExit(f"no project at {base}")
    CONTENT = base / ("content" if args.locale == "en" else f"content-{args.locale}")
    SITE = base / "site" if args.locale == "en" else base / "site" / args.locale
    if not CONTENT.is_dir():
        raise SystemExit(f"no content tree at {CONTENT} — create it first")

    # Photos are neither locale- nor grade-specific, so every site/assets that is
    # not the canonical one is a symlink back to it: site/<loc>/assets → ../assets
    # within a project, and a sibling project's site/assets → this project's.
    assets = SITE / "assets"
    if not assets.exists():
        assets.parent.mkdir(parents=True, exist_ok=True)
        target = (Path("..") / "assets" if args.locale != "en"
                  else Path(os.path.relpath(ROOT / "site" / "assets", assets.parent)))
        assets.symlink_to(target)
    build()
