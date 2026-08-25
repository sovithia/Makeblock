# mBot2 Curriculum — Grades 7–9 — Static Website

Static-site version of the secondary courses (Grades 7–9 × 20 sessions = 60
sessions). Content lives in YAML files that non-programmers can edit; a small
Python generator renders HTML. No PDF build step — teachers print straight from
the browser.

Sessions used to print on exactly one A4 page. That no longer holds and the
change was deliberate (2026-08-12): a session carrying the second-hour `long:`
band takes two pages, and the `bonus:` box pushes most 1 h sessions onto a second
page too. See **Print checks** below for the current measured counts.

| Strand | Hardware | Coding | Timings |
|---|---|---|---|
| Grade 7 | Box 1 only | blocks | 1–2 h per step (44 h, build included) |
| Grade 8 | Box 1 → Rover add-on | blocks | 1–5 h per step (44 h, including a 7 h build) |
| Grade 9 | Ranger + robotic arm | Python | 2 h per week (40 h) |

Grades 7–9 run a **single 2 h timing**, declared as `per:`/`total:` in each
`grade.yaml`, so there is no 1-hour variant of those pages to switch to.

## One content tree

Grades 7–9 live in `content/` (and `content-km/`). Grades 7 and 8 are **step
courses** — 25 and 24 steps, one `steps/` directory per grade; Grade 9 is still a
20-session course under `sessions/`. `build.py` skips the whole session
apparatus for a grade with no `sessions/`, so 7–8 emit no `index.html`,
`print.html` or `session-*.html`.

Grades were once split across trees and the generator still carries `--project
DIR` for it, but **there is no second tree now**: Grades 4–6 were archived on
2026-08-19 to `../archive/Grade4-5-6/`, along with the 20-session Grade 7 and 8
course they predate (`../archive/2026-08-12-g7-g8-sessions/`). Neither is built.
`--project ../Grade4-5-6` no longer resolves — do not put it back into a script
without moving the tree out of the archive first.

Grades are discovered by globbing `grade*`, so the tree builds whichever grades
it contains, which is why `site/demo.html` covers 7–9.

## Languages

`--locale km` reads `content-km/` and writes `site/km/`. The English site is
unaffected by anything a locale does. Missing keys fall back to English, so a
partially translated locale still builds — which is the current state: the UI
chrome and part names are Khmer, most session content is not yet.

### The EN / ខ្មែរ switch

Every page carries a two-state switch at the right end of its nav bar, showing
which language you are in and linking to *that same page* in the other tree —
not to the other tree's front page. It is a plain static `<a>`, so it works from
`file://` and needs no JavaScript, and it is hidden in print.

It resolves without any lookup because the two trees mirror each other file for
file: an English page lives at `site/<rel>` and its twin at `site/km/<rel>`, so
the link is one extra `../` and a `km/` put back. `chrome(links, rel)` therefore
requires every caller to say what path it is being written to — that argument is
the only thing the switch needs.

**Picking a language is sticky and needs no machinery to stay that way.** Every
other link a page carries is relative — `next step`, `all grades`, the search
hits — so once a reader is inside `site/km/` every click keeps them there. The
switch is the only link allowed to cross trees.

Two pages had no nav bar and gained a minimal one so they could carry the switch:
the landing page, and each grade's `print.html` (screen-only, so pagination is
untouched — `verify_chrome.sh` still measures 43 pages for Grade 9).

`tools/check_language.py` holds both halves of this — run it after a build:

```
../.venv/bin/python tools/check_language.py     # after building BOTH locales
158 pages · 938 in-tree links · OK
```

It asserts every page has exactly one switch pointing at its own counterpart,
and that no other link leaves its tree. Build both locales first: it reads
`site/` and `site/km/` together and a stale tree will report dead links.

## Block scripts

Sessions with `code: {lang: blocks}` render as a stack of mBlock block images
(`generator/blocks.py`), not as a monospace code box; `lang: python` still uses
the code box. Blocks with no photograph yet fall back to a coloured pill in the
right palette colour, so the site is correct at every stage of the photo
migration. See `content/BLOCKS-TO-SHOOT.md` for what is still needed.

## Editing content (the normal workflow)

1. Edit a file under `content/` (see map below). Session text may contain the
   same inline HTML the PDFs used (`<b>`, `<i>`).
2. Rebuild: `../.venv/bin/python generator/build.py` (from `curriculum-site/`).
3. Open `site/index.html` — or serve `site/` from any static host.

That's it. The `site/` folder is fully self-contained static output.

## File map

| File | Holds |
|---|---|
| `content/grade7/grade.yaml` | colors, theme, units, objectives, friction list, capstone blurb |
| `content/grade9/sessions/NN.yaml` | one full session: goal, teach, guide box, timed steps, code, tips, result scene, success criteria, parts list |
| `content/grade7/steps/NN.yaml` | one step: goal, concept, teach, guide box, timed steps, the whole block script so far, tips, success criteria, parts |
| `content/boxes.yaml` | the two box packing lists |
| `generator/scenes.py` | SVG scene library — **verbatim copy** of the legacy art, do not redraw |
| `generator/parts_catalog.py` | 50 part icons + panel renderer |
| `generator/render.py` | print/theme CSS + page templates |
| `generator/build.py` | site builder: session pages, grade indexes, print.html, search index |
| `site/assets/parts/*.png` | real part photos from the official manuals (see below) — `../mbot2.pdf` p2, `../mbot2_addons.pdf` pp1/3/4 |

The "legacy" column that used to sit here described the Grades 7–9 Python
generator; it lives in `curriculum-source-annotated/` and is reference-only.

### Session YAML schema

```yaml
n: 2
title: Assembly I
goal: one sentence
teach:            # paragraphs; inline HTML allowed
  - '... <b>bold</b> ...'
guide:            # optional "Quick Start Guide" box: label/value rows
  - {label: Steps, value: ① – ③ (printed pp. 9–10)}
steps:            # timed lesson flow
  - {time: 5′, text: ...}
code:             # optional
  lang: blocks    # or: python
  source: |
    when button A pressed
      ...
tips: [ ... ]     # optional "Watch out" list
result:
  scene: expl     # key into generator/scenes.py SCENES
  params: {variant: drive}
success: [ ... ]  # checklist in the result box
parts:            # icons from generator/parts_catalog.py ICONS
  - {id: chassis}
  - {id: motor, note: check orientation!}
```

### Step courses (`steps/`) — Grades 7 and 8

Grades 7 and 8 are **step courses** — 25 steps / 44 h and 24 steps / 44 h — not 20-session ones. A grade with a
`steps/` directory is built in step mode: `content/gradeN/steps/NN.yaml` →
`site/gradeN/step-NN.html`, plus a stage-grouped index at `steps.html`. The
teacher solution follows the lesson on the same page, separated by a forced
print-page break. The old `sessions/` tree still builds alongside,
so nothing breaks mid-changeover — the landing page simply points at the course
instead.

```yaml
n: 6
stage: B                    # groups the index; A-E
stage_title: The robot decides
kind: step                  # or: checkpoint
title: What the robot can feel
concept: Sensors as live values
hours: 2                    # THIS step; the cumulative marker is computed
project: G7-B-decides       # which mBlock project to open
goal: …
build: A dashboard the robot carries with it.     # the deliverable, one line
steps:                      # the timed flow — one card per phase on the page
- time: 25′
  text: Replace them all with one variable …
  use: [data_setvariableto, data_changevariableby]   # blocks THIS phase picks up
  expect: You change the one starting number, and every speed changes with it.
# then the same keys as a session: teach / guide / code / tips /
# result / success / parts / bonus
```

**Lessons and teacher answers are one printable document.** Every Grade 7–8 step
page contains the student lesson first and a teacher-solution section immediately
after it on a new print page. “Print lesson only” temporarily removes the solution
from the print job, so the teacher can choose the required number of student
copies. “Print solution only” prints the teacher answer by itself. The solution
contains the finished block arrangement and links to the canonical `.mblock` in
`site/assets/projects/`; hardware, planning, and checkpoint lessons show their
completed-result checklist instead. Builds remove the obsolete `site/teacher/`
and `site/km/teacher/` trees so a stale separate answer site cannot survive.

**Blocks live in the flow, not in a frame beside it.** There is no lesson-wide
"blocks you will need" panel any more: each phase's `use:` list is drawn as empty
blocks inside that phase's card, and a block met for the first time anywhere in
the course still gets its own line with its explanation from `block-notes.yaml`.
`tools/flow_authoring.py --todo` lists phases with no `expect:`; its `audit()`
fails on a `use:` key that is not in that lesson's own code, and warns when a
lesson introduces a block that no phase shows — so a new block cannot slip in
unexplained.

**`use:` is authored once, in English.** Which blocks a phase picks up is
language-neutral, so `content-km` carries no `use:` at all: `build.py` grafts it
from the English lesson by flow position and refuses to build if the two flows
have different lengths. `expect:` is prose, so it is translated per locale.

**Two kinds of note on a part.** The per-lesson `note:` inside a step's `parts:`
says what *that week* uses it for ("the wall", "a slalom") and appears on the step
page. `content/part-notes.yaml` says how to *choose* the item — what makes a box
useless, why the foam must be foam — and appears once, on the materials page,
under the item's name. Keyed by the part id in `parts_catalog.ICONS`; a part with
no entry simply shows no guidance line, and `content-km/` carries its own copy
with the usual English fallback.

**Hours are never stored cumulatively.** `build.py` sums `hours` in file order, so
inserting a step cannot leave a stale "~13 h in" behind. Grade 7 is 40 h of steps
(the two assembly steps included) + 4×1 h checkpoints = **44 h**; Grade 8 is 40 h
of steps (including seven hours for the Rover build) + 4 h of checkpoints = **44 h**.

**Everything taught fits inside 40 hours.** The concept ladder and all four gates
finish at 39 h (G7) and 40 h (G8); Stage E — the capstone — is the declared extra
and introduces no new block, so a 40-hour timetable can stop where it starts.
`build.py` draws that line on the steps ladder automatically at the Stage E
boundary (`FORTY`, `forty_line`) rather than from an authored hour number.

**Checkpoints are catch-up gates**, not tests: three hands-on challenges, peer
coaching with hands off other people's robots. A **buffer hour** is offered at
every checkpoint but is deliberately *not* in the timetable or the course total —
add it only if the class is not level. The stated hours are what the course takes
when nobody needs catching up. `kind: checkpoint` styles
the page amber.

**Answer projects** are `.mblock` files written by `tools/mblock_compile.py` into
`site/assets/projects/`, named after the `project:` field and the step number.
They are linked from the teacher-solution section appended to the corresponding
lesson. That section also names the blocks new to the lesson and shows the
finished arrangement.

### The second hour (`long:`)

Every session carries a `long:` block holding the extra hour. It renders as the
banded four-lane strip under the main flow; `long.goal` **replaces** the goal on
the 2 h page, while `long.parts` and `long.success` **append** to the 1 h lists.

There are two lane sets, and `render.is_secondary_long()` picks between them from
the content shape rather than from the grade number — so a grade can move between
bands without touching the renderer.

```yaml
long:
  goal: the raised bar for the 2 h version
  # --- Grades 4-6 lane set: warmup / challenges / maker / share
  warmup:     {time: 10′, text: ...}
  challenges: [{stars: 2, text: ...}]     # star tiers
  maker:      {time: 15′, text: ...}
  share:      {time: 10′, text: ...}
  # --- Grades 7-9 lane set: recap / extend / log / review
  recap:  {time: 10′, text: ...}          # break it, swap it, confront the first hour
  extend: [{spec: ±1 cm, text: ...}]      # 3 items; header is a fixed 25′
  log:    {time: 10′, text: ...}          # what evidence to record, and the standard
  review: {time: 15′, text: ...}          # defend the claim; state the criteria
  parts:   [ ... ]  # optional, appended
  success: [ ... ]  # optional, appended
```

Extend tasks carry an engineering **tolerance** rather than star tiers: at 12–15
the target is a spec you either met or did not. The lanes sum to 60′ on top of
the 45′ core.

### `bonus:` — what a team does when it finishes everything

A **top-level** session key, sibling to `steps:` and `tips:` — *not* part of
`long:`:

```yaml
bonus:
  kind: Break it
  text: Give your chassis a gentle shake. Anything that rattles today will fall
    off in Session 5. Find it and tighten it now.
```

It renders as an untimed dashed box between the band and the result box, so it is
always the last thing on the page — **on both timings**. It briefly lived inside
`long:` and therefore only appeared on 2 h pages; that was wrong, because a fast
team exists in a one-hour lesson too and there it is their only overflow.

Untimed and dashed on purpose: the flow and the lanes are the plan, this is
contingent, and it should not read like a scheduled block beside the
solid-bordered result box beneath it.

Every entry obeys five rules, and new ones should too:

- **depth, never new scope.** Grade 4 S18 states it: *"Teams who finish early do
  not get to add a fifth moment. Send them to reliability."*
- **never runs ahead** into the next session — that would spoil the next lesson
- **needs no teacher** — being unsupervised is the whole point of the slot
- **needs no new materials** beyond what the session already lists
- **interruptible** — can be cut off at the bell with nothing lost

`kind` is one of five recurring tags, so a teacher learns to expect the shape:
**Reliability** (run it again, count it, make it 5/5) · **Teach it** (check,
explain, hand over — without touching another team's robot) · **Break it** (find
the edge where it fails, record the condition) · **Constrain it** (same result,
fewer blocks, lower speed, one control) · **Bank it** (write the card, test or
challenge another team will use later).

## Generated site

- `site/index.html` — landing + instant search across every session and step
  (index inlined, works from `file://` too)
- `site/demo.html` — manager-facing demo tour: per grade, the unit ladder,
  four milestone results and the Session 20 capstone event. Milestone picks
  and hooks live in `DEMO_MILESTONES` in `generator/build.py`.
- Session and step pages show a screen-only "↪ Builds on …" progression line
  (`builds_on` / `feeds` fields in the YAML). Hidden in print.
- `site/grade9/index.html` — session list + at-a-glance + box reference
- `site/grade7/session-NN.html` — one session; "Print this session" = 1 A4 page
- `site/grade9/print.html` — the complete guide (cover, at-a-glance, boxes,
  20 session pages); print from the browser. Grades 7–8 have no combined guide:
  each step is its own page, printed individually.
- `*-long.html` — a 2 h/week variant generated from the same YAML. Grades 4–6
  only, and those are archived, so nothing emits it today.

## Print checks

**`verify_chrome.sh` is the gate.** There was a second harness,
`tools/verify_print.py`, which diffed the built guide against the originally
shipped `reference/*.pdf`; it was deleted on 2026-08-19 because it could never
pass again by design — block scripts render as pictures now, and every session
gained a second hour and a bonus box, so Grade 7 reported 43 pages against the
reference's 23 with all 20 sessions differing. The reference PDFs stay in
`reference/` as the record of what Makeblock originally shipped.

### `tools/verify_chrome.sh` — structural, and the one to trust

```
tools/verify_chrome.sh 7 8 9      # 7 and 8 SKIP — step courses, no combined guide
```

Paginates each `print*.html` with headless Chrome — the engine teachers actually
print with — and asserts:

- the intro is exactly 3 pages, so session 1 starts on page 4
- sessions 1..20 all appear, in order, none missing or duplicated
- no session spans more than `MAX_PP` (2) pages

It deliberately does **not** assert a total page count any more. It used to
demand `pages == 23` and that page *p* held session *p − 3*; both stopped being
true in Aug 2026 when the second hour and the `bonus:` box landed, and both
changes were intended. A hardcoded total has to be re-edited whenever content
legitimately grows, and it cannot tell "the layout blew up" from "a paragraph got
longer". The ordering invariant can. Current counts, for information only:

| Guide | Pages |
|---|---|
| grade 9 `print.html` (2 h) | 43 |

**Do not "fix" a page count by trimming content.** Two pages per 2-hour session
was always true of the Grades 4–6 long guides. The 1 h growth is the accepted
price of printing the bonus on the sheet the teacher holds — a compact box was
measured and still did not fit.

English only: it matches the printed "SESSION n / 20" header, which is Khmer in
`site/km`.

## Real part photos

`tools/extract_parts_images.py` crops the part pictures out of the official
manuals in the project root (`../mbot2.pdf` parts-list spread, `../mbot2_addons.pdf`
parts list + cover render) into `site/assets/parts/<icon-id>.png` — 30 images
covering every kit part, including composites (wheel hub + tyre, brackets,
boards…) and the three assembled-robot renders. `parts_catalog.panel()`
prefers a photo when one exists and falls back to the hand-drawn SVG
(classroom items like tape keep their SVGs). Photos render in the
exact 52×36px footprint of the SVG icons, so pagination is unchanged.
Re-run the extractor only if the manuals change; it needs Pillow + poppler.

Note: the photos are Makeblock's artwork from their manuals. Fine for a guide
used inside the school with kits you own; re-check before publishing the site
on the open web.

## Setup

```
python3 -m venv ../.venv
../.venv/bin/pip install -r requirements.txt   # pyyaml (+ weasyprint for verify only)
```

The `../.venv` sits at the project root, one level above this folder.
