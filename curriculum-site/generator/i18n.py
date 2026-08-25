# -*- coding: utf-8 -*-
"""UI string catalogue for the generator.

The YAML under content/ (and content-km/) holds the *lesson* text; this file holds
the surrounding chrome the generator emits — headings, labels, nav, the cover.

One locale is active per build (`build.py --locale km`), so the current locale is a
module global rather than a parameter threaded through every render function.

Adding a locale: copy the "en" block, translate the values, leave the keys alone.
Any key missing from a locale falls back to English, so a partial locale still builds.
"""

LOCALE = "en"


def use(loc):
    global LOCALE
    if loc not in STRINGS:
        raise SystemExit(f"unknown locale {loc!r} — have: {', '.join(STRINGS)}")
    LOCALE = loc


def t(key, **kw):
    s = STRINGS.get(LOCALE, {}).get(key)
    if s is None:
        s = STRINGS["en"][key]          # partial locales fall back, never crash
    return s.format(**kw) if kw else s


def is_khmer():
    return LOCALE == "km"


def svg_font():
    """font-family for <svg><text>, which cannot inherit the page's CSS stack.

    Khmer OS Battambang is the embedded webfont (site/assets/fonts/); the rest are
    fallbacks for machines that already have a Khmer font installed.
    """
    if LOCALE == "km":
        return "Khmer OS Battambang, Khmer MN, Khmer Sangam MN, Helvetica"
    return "Helvetica"


_KHMER_DIGITS = str.maketrans("0123456789", "០១២៣៤៥៦៧៨៩")


def num(v):
    """Counters (session no., grade no.) in Khmer numerals under the km locale.

    Deliberately NOT applied to measurements — "40 cm", "40 RPM", "45′" and the
    times in `steps:` stay in Arabic numerals, because those match the numbers
    students type into mBlock and read off a ruler.
    """
    s = str(v)
    return s.translate(_KHMER_DIGITS) if LOCALE == "km" else s


# Demo-tour milestone hooks. The (grade, session) pairs themselves live in
# build.py DEMO_MILESTONES; this only overrides the one-line hook text per locale.
# Anything missing here falls back to the English hook in build.py.
HOOKS = {
    "km": {
        ("4", 4): "រូបយន្តបើកដំណើរការ ទទួលឈ្មោះ និងនិយាយស្វាគមន៍ — ជាពេលដែលវាក្លាយជារបស់សិស្ស",
        ("4", 8): "ប្លុករង្វិលមួយជំនួសម្ភៃប្លុក — រសជាតិដំបូងនៃការសរសេរកម្មវិធីពិតប្រាកដ",
        ("4", 12): "ចលនា ពន្លឺ និងសំឡេង ក្លាយជាការសម្ដែង ៣០ វិនាទី ដែលសិស្សបង្កើតដោយខ្លួនឯង",
        ("4", 16): "ទះដៃ រួចរូបយន្តឆ្លើយតប — អាកប្បកិរិយាឆ្លើយតប ដោយមិនប្រើ `if` សោះ",
        ("5", 5): "`if` ដំបូង — រូបយន្តឈប់ដោយខ្លួនឯង មុនពេលប៉ះជញ្ជាំង",
        ("5", 10): "កាតពណ៌ក្លាយជាបញ្ជា ដែលរូបយន្តអានពីលើឥដ្ឋ",
        ("5", 13): "អថេរចងចាំ — រូបយន្តចាប់ផ្ដើមកត់ពិន្ទុ",
        ("5", 16): "ការដើរតាមខ្សែ ក្រិតតាមការចាប់ម៉ោងជុំ",
        ("6", 4): "សិស្សបង្កើតប្លុកផ្ទាល់ខ្លួន ហើយដាក់ឈ្មោះឲ្យវា — អរូបីកម្ម នៅអាយុ ១១ ឆ្នាំ",
        ("6", 11): "ជាវិធាន មិនមែនជាផ្លូវ៖ រូបយន្តដោះស្រាយផ្កាឡាដែលវាមិនធ្លាប់ឃើញ",
        ("6", 14): "រូបយន្តពីរនិយាយគ្នាតាមបណ្ដាញក្នុងថ្នាក់",
        ("6", 15): "ការបញ្ជូនបន្ត៖ រូបយន្ត A បញ្ចប់ ហើយប្រគល់ទៅរូបយន្ត B តាមសារ",
    },
}


def hook(gnum, n):
    """Locale-specific demo hook, or None to keep build.py's English text."""
    return HOOKS.get(LOCALE, {}).get((str(gnum), n))


# Part names, keyed by generator/parts_catalog.py ICONS id, and the four set
# pills. Makeblock product names (CyberPi, mBot2 Shield, Quad RGB Sensor,
# Ultrasonic Sensor 2, Rover, Ranger, mBuild) deliberately stay in Latin script —
# they are printed on the hardware and shown in mBlock, so a teacher matching a
# label to a physical part needs to read the same string on both.
PARTS = {
    "km": {
        # --- mBot2 box
        "chassis": "គ្រោងតួ",
        "cyberpi": "CyberPi",
        "kitbox": "ប្រអប់ mBot2",
        "map": "ផែនទីដើរតាមខ្សែ",
        "mbuild": "ខ្សែ mBuild",
        "miniwheel": "កង់តូច",
        "motor": "ម៉ូទ័រ encoder ×2",
        "motorcable": "ខ្សែម៉ូទ័រ ×2",
        "quadrgb": "Quad RGB Sensor",
        "robot_wheel": "mBot2 ដែលផ្គុំរួច",
        "screwdriver": "ទួណឺវីស",
        "screws7": "វីស M4",
        "screws7s": "វីស M2.5×12",
        "shield": "mBot2 Shield",
        "ultra": "Ultrasonic Sensor 2",
        "usb": "ខ្សែ USB",
        "wheelset": "ដុំកង់ + សំបកកង់រាបស្មើ",
        # --- Rover add-on box
        "beamplate": "ធ្នឹមរអិល + បន្ទះ",
        "boards": "បន្ទះ ១–៨",
        "bracket": "ជើងទម្រ 90° / 120° / U",
        "collarflange": "ក្រវ៉ាត់ដងភ្លៅ + បេរីង",
        "controller": "ឧបករណ៍បញ្ជា Bluetooth",
        "damper": "ឧបករណ៍ទប់ការញ័រ",
        "dshaft": "ដងភ្លៅ D",
        "guide": "មគ្គុទ្ទេសក៍ចាប់ផ្ដើមរហ័ស",
        "robot_arm": "Rover ដែលមានដៃ",
        "robot_tank": "Rover ដែលផ្គុំរួច",
        "roverbox": "ប្រអប់បន្ថែម Rover",
        "rubber": "កៅស៊ូរឹត",
        "screwsR": "វីស + ខ្ចៅ Rover",
        "servopack": "ឈុត servo",
        "socket": "ប្រដាប់មូលខ្ចៅ",
        "track": "ខ្សែក្រវាត់ ×2",
        "trackhubs": "ដុំកង់ (ធំ + តូច)",
        # --- classroom
        "blindfold": "ក្រណាត់បិទភ្នែក",
        "boxes": "ប្រអប់ / ឧបសគ្គ",
        "cards": "កាតបោះពុម្ព",
        "colorcards": "កាតពណ៌ (៨ ពណ៌)",
        "craft": "ឈុតសិប្បកម្ម (ក្រដាសកាតុង ប៊ិចម៉ាកគ័រ កាសែត)",
        "foam": "ដុំហ្វូម",
        "tablet": "ថេប្លេត + mBlock",
        "tablet": "ថេប្លេត + mBlock Web",
        "patches": "បំណះពណ៌",
        "phone": "ទូរសព្ទ (វីដេអូ/មុំ)",
        "protractor": "ប្រដាប់វាស់មុំ",
        "ramp": "ក្ដារជម្រាល",
        "router": "រ៉ោតទ័រ Wi-Fi / hotspot",
        "ruler": "បន្ទាត់ / មែត្រខ្សែ",
        "tape": "កាសែតបិទ",
        "timer": "នាឡិកាចាប់ម៉ោង",
        "torch": "ពិល / ភ្លើងទូរសព្ទ",
        "trays": "ថាសរៀបចំ",
        "webcam": "កាមេរ៉ា webcam",
        # --- sold separately
        "dongle": "ដុងហ្គល Makeblock BT",
    },
}

SET_NAMES = {
    "km": {
        "MBOT2": "ប្រអប់ mBot2",
        "ROVER": "ប្រអប់បន្ថែម Rover",
        "CLASS": "ថ្នាក់រៀន",
        "EXTRA": "លក់ដាច់ដោយឡែក",
    },
}


def part_label(pid, default):
    return PARTS.get(LOCALE, {}).get(pid, default)


def set_name(sid, default):
    return SET_NAMES.get(LOCALE, {}).get(sid, default)


STRINGS = {
    # ---------------------------------------------------------------- English
    "en": {
        # session page
        "session_n_of": "Session {n} / 20",
        "goal_hour": "Goal of this hour:",
        "goal_two_hours": "Goal of these two hours:",
        "teach_concept": "Teach it — the concept",
        "flow_short": "Lesson flow (45′ core)",
        "flow_step": "Lesson flow — minute by minute",
        "flow_long": "② Teach &amp; Do — the core (45′)",
        "tag_two_hour": "2-hour version",
        "quick_start": "Quick Start Guide — this session",
        "watch_out": "Watch out",
        "code_blocks": "Block script (rebuild this in mBlock)",
        "code_hints": "Blocks you will need — work out the order yourself",
        "blocks_new": "new",
        "next_lesson": "Next lesson",
        "teacher_check": "Teacher check",
        "build_diagrams": "Build it — from the official guide",
        "forty_line": "◆ The taught course and all four gates end here, within 40 hours. Stage E below is the capstone — it teaches no new block, so a 40-hour timetable can stop at this line.",
        "code_python": "Python (mBlock → Python mode)",
        "expected_result": "◉ Expected result at the end of this session",
        "builds_on": "↪ Builds on ",
        "feeds": "feeds",
        # 2-hour band
        "lane_warmup": "① Warm-Up",
        "lane_arena": "④ Challenge Arena",
        "lane_maker": "⑤ Make It Yours",
        "lane_share": "⑥ Show &amp; Notes",
        "band_lead": "＋ 2-hour version — the extra 60′ "
                     "(② Teach &amp; Do = the 45′ core above · ③ break 5′)",
        # secondary (Grades 7-9) second hour — engineering specs, not star tiers
        "lane_recap": "① Recap &amp; Debug",
        "lane_extend": "④ Extend — to spec",
        "lane_log": "⑤ Engineering Log",
        "lane_review": "⑥ Design Review",
        "step_n": "Step {n}",
        "teacher_title": "Teacher reference — answer projects &amp; block scripts",
        "teacher_kicker": "Teacher reference",
        "teacher_lede": "The finished arrangement for every lesson, and the saved mBlock project "
                        "behind it. This is not linked from the student site: the step pages give "
                        "the goal, the blocks for each phase and the result to aim at, and working "
                        "out the arrangement is the lesson. Use these to see where a class is "
                        "heading, to hand a stuck student the file for the step they are on, or to "
                        "print a script and give it out.",
        "teacher_lesson": "Lesson",
        "teacher_lessons": "lessons",
        "teacher_projects": "saved projects",
        "teacher_file": "File",
        "teacher_open": "Open the lessons →",
        "teacher_print_all": "Print every script",
        "teacher_files_n": "{n} projects saved",
        "teacher_print_note": "Printing this page gives one script per sheet, in course order. "
                              "Hand out single sheets rather than the set — a student who has the "
                              "next three lessons has nothing left to work out.",
        "checkpoint_n": "Checkpoint {n}",
        "hours_in": "~{h} h in",
        "concept": "New concept",
        "project": "Project name",
        "answer_project": "Answer project",
        "open_course": "Open the course →",
        "answers_link": "Answer projects",
        "reveal_warn": "⚠ Each file holds <b>one step's</b> scripts and nothing else, so handing a "
                       "stuck student the file for the step they are on reveals nothing ahead of "
                       "it. Upload one at a time: two steps' scripts in one project means two "
                       "<code>when CyberPi starts up</code> hats and two handlers on the same "
                       "button, and the robot stops with a traceback on its screen.",
        "download": "download .mblock",
        "not_built_yet": "not built yet",
        "answers_title": "Answer projects — teacher reference",
        "answers_lede": "One saved mBlock project <b>per step</b>, built by working straight "
                        "through the course — each one uploads and runs on its own. They unlock "
                        "for students at the checkpoint that closes their stage; the last step of "
                        "Stage E is also the demo.",
        "you_build": "You build",
        "palette": "Blocks",
        "band_lead_sec": "＋ the 2-hour session — the other 65′ "
                         "(② Teach &amp; Do = the 45′ core above · ③ break 5′)",
        "spec_label": "spec",
        "r_recap": "① Recap &amp; Debug",
        "r_extend": "④ Extend to spec",
        "r_log": "⑤ Eng. Log",
        "r_review": "⑥ Design Review",
        "r_recap_svg": "① Recap & Debug",
        "r_extend_svg": "④ Extend to spec",
        "r_log_svg": "⑤ Eng. Log",
        "r_review_svg": "⑥ Design Review",
        "nonneg_sec": "<b>Non-negotiables for 2-hour sessions:</b> the engineering log is written "
                      "during the session, not afterwards — a change with no measurement beside it "
                      "does not count · every Extend task states its tolerance before anyone drives "
                      "· design review is against the stated criteria, not taste · robots stay "
                      "assembled on a labeled cart shelf and charge via USB-C between sessions.",
        # rhythm strip
        "r_setup": "Setup",
        "r_warmup": "① Warm-Up",
        "r_share": "⑥ Show &amp; Notes",
        "r_reset": "Reset",
        "r_briefing": "Briefing",
        "r_core": "Core hands-on work",
        "r_notes": "Notes",
        # rhythm labels live inside <svg><text>, where the legacy markup uses a bare
        # "&" rather than "&amp;" — keep these unescaped so the SVG stays identical.
        "r_teach_core": "② Teach & Do — the core",
        "r_break": "③ Break",
        "r_arena": "④ Challenge Arena",
        "r_maker": "⑤ Make It Yours",
        "r_share_svg": "⑥ Show & Notes",
        # intro / cover
        "teaching_guide": "Teaching Guide",
        "program_default": "mBot2 Rover Robotics Program",
        "sessions_unit": "sessions",
        "coding_mode": "coding mode",
        "each": "each",
        "each_20h": "each · 20 h total",
        "each_40h": "each · 40 h total",
        "final_project": "★ Final project: {name}",
        "cover_foot": "Tutor edition — each session is one page: concept to teach · timed lesson "
                      "flow · code · pitfalls · expected result with success criteria. "
                      "Software: mBlock 5 · Makeblock App · 1 kit per 2–3 students.",
        "at_a_glance": "Grade {n} at a Glance",
        "objectives_head": "Learning objectives — by the end of the year, students can:",
        "sessions_by_unit": "The 20 sessions, colored by unit",
        "buffer_note": "✱ in session titles = buffer session (tolerates compression if the "
                       "schedule slips)",
        "same_rhythm": "Every session runs on the same rhythm",
        "friction_head": "Known friction points this year:",
        "boxes_head": "The Boxes — Official Contents Reference",
        "nonneg_short": "<b>Non-negotiables for 1-hour sessions:</b> robots stay assembled between "
                        "sessions on a labeled cart shelf · code saved to mBlock cloud accounts "
                        "every session · battery rotation with a per-team battery manager · "
                        "extension cards at stations so fast teams never wait.",
        "nonneg_long": "<b>Non-negotiables for 2-hour sessions:</b> the 5′ break is not optional at "
                       "this age — take it on time · the Challenge Arena is tiered so nobody waits "
                       "and nobody is stranded: every team must clear ★☆☆ before moving on · the "
                       "maker lane needs its own table, away from tablets · robots stay assembled "
                       "on a labeled cart shelf and charge via USB-C between sessions.",
        # nav / chrome
        "all_grades": "All grades",
        "lang_switch": "Language",
        "grade_n": "Grade {n}",
        "session_label": "Session {n}: {title}",
        "print_session": "🖨 Print this session",
        "print_lesson_only": "🖨 Print lesson only",
        "print_solution_only": "🖨 Print solution only",
        "teacher_solution": "Teacher solution",
        "teacher_solution_note": "Print one complete copy for the teacher. Use “Print lesson only” for student copies.",
        "expected_completed_result": "Expected completed result",
        "switch_to": "⇄ {label} ({total})",
        "v_short": "1-hour version",
        "v_long": "2-hour version",
        "full_guide": "Full printable guide →",
        "sessions_head": "Sessions",
        "not_migrated": "(not yet migrated)",
        "grade_theme": "Grade {n} — {theme}",
        "capstone": "capstone",
        "timing_line": "{label}: {per} × 20 sessions = {total}",
        # landing + search
        "site_title": "mBot2 Teaching Guides",
        "landing_head": "mBot2 Robotics Program — Teaching Guides",
        "landing_blurb": "Read the course guidance below, then browse by grade or search all lessons.",
        "browse_head": "Browse the courses",
        "demo_link": "Demo tour for school leadership →",
        "glossary_link": "Block glossary →",
        "glossary_new_tab": "Open glossary in new tab",
        "search_ph": "Search all sessions… (e.g. calibration, ultrasonic, loop)",
        "no_match": "No sessions match.",
        "primary_head": "Primary — Grades 4–6",
        "primary_sub": "mBot2 Box 1 only · blocks only · available at 1 h or 2 h per week",
        "secondary_head": "Secondary — Grades 7–9",
        "secondary_sub": "Box 1 → Rover add-on · blocks → Python · 1 h per week",
        "open_guide": "open the <b>{per} × 20 = {total}</b> guide →",
        "n_of_20": "{n}/20 sessions",
        "page_title_session": "G{g} S{n} · {title} ({per})",
        "page_title_index": "Grade {n} · {theme} ({per})",
        "page_title_print": "mBot2 Grade {n} Teaching Guide ({per} × 20)",
        # demo tour
        "demo_nav": "Demo tour — program overview for school leadership",
        "demo_head": "mBot2 Robotics Program — the six-year arc",
        "demo_lede": "One kit family, six years. Grades 4–6 run on the mBot2 Box 1 alone, in "
                     "blocks: command it (G4) → make it sense and decide (G5) → make it autonomous "
                     "and networked (G6), each available as a 1-hour or 2-hour weekly course. "
                     "Grades 7–9 then add precision and hardware: the wheeled mBot2 on blocks (G7) "
                     "→ the tracked Rover with AI and expression (G8) → the same Rover put to "
                     "work with its grip arms, in full Python (G9). Every year is a progressive 20-session ladder "
                     "ending in a scored public event — the four milestone cards per grade show "
                     "the ladder; the capstone card is where it lands.",
        "demo_kicker": "Grade {n} · {form} · {codemode}",
        "demo_card": "Session {n} · {title}",
        "demo_glede": "20 {timing} in {units} units ({totals}) — every session is a ready-made "
                      "one-page teacher script (timed flow, code, pitfalls, success criteria). "
                      "Skills stack unit by unit and land on a scored public event in Session 20.",
        "demo_sessions_word": " sessions",
        "demo_or": " or ",
        "demo_milestones": "Milestones along the way",
        "demo_capstone": "★ Session 20 — {name} (the year's conclusion)",
        "demo_open": "Open the full Session 20 teacher page →",
        "demo_title": "Demo tour · mBot2 Robotics Program",
        # materials page
        "materials": "Classroom materials",
        "materials_title": "Grade {n} · Classroom materials",
        "materials_head": "Grade {n} — what the classroom needs",
        "materials_lede": "Everything the {n} sessions of this year call for, gathered from the "
                          "per-session parts lists. Items are grouped by where they come from.",
        "mat_kits": "Robot kits",
        "mat_kits_rule": "1 mBot2 kit per 2–3 students",
        "mat_class_size": "Class size",
        "mat_kits_needed": "Kits needed",
        "mat_students": "{n} students",
        "mat_from_box": "From the mBot2 box",
        "mat_from_box_sub": "already in the kit — nothing to buy, but these are the pieces this "
                            "year actually uses",
        "mat_from_rover": "From the Rover add-on box",
        "mat_from_rover_sub": "already in the add-on kit — nothing to buy, but these are the "
                              "pieces this year actually uses",
        "mat_classroom": "Classroom supplies",
        "mat_classroom_sub": "you provide these — not in the kit",
        "mat_extra": "Sold separately",
        "mat_extra_sub": "not in the box; order before the sessions that need them",
        "mat_used_in": "Used in",
        "mat_sessions_n": "{n} sessions",
        "mat_long_only": "2-hour version only",
        "mat_note": "Notes",
        "mat_by_session": "Session by session",
        "mat_by_session_sub": "for weekly prep — what to put on the table before each session",
        "mat_session": "Session",
        "mat_needs": "Needs",
        "mat_nothing": "nothing beyond the robot",
        "mat_total_line": "{box} pieces from the kit · {cls} classroom supplies"
                          "{extra}",
        "mat_total_extra": " · {n} sold separately",
    },

    # ------------------------------------------------------------------ Khmer
    # Register: teacher-facing (these are tutor guides, not student handouts).
    # mBlock block names and product names stay in Latin script on purpose —
    # they must match what appears on the screen in class.
    "km": {
        # session page
        "session_n_of": "មេរៀនទី {n} / ២០",
        "goal_hour": "គោលដៅនៃម៉ោងនេះ៖",
        "goal_two_hours": "គោលដៅនៃពីរម៉ោងនេះ៖",
        "teach_concept": "បង្រៀន — គំនិតគោល",
        "flow_short": "លំដាប់មេរៀន (ស្នូល ៤៥′)",
        "flow_step": "លំដាប់មេរៀន — មួយនាទី‑មួយនាទី",
        "flow_long": "② បង្រៀន និងអនុវត្ត — ស្នូល (៤៥′)",
        "tag_two_hour": "កំណែ ២ ម៉ោង",
        "quick_start": "មគ្គុទ្ទេសក៍ចាប់ផ្ដើមរហ័ស — មេរៀននេះ",
        "watch_out": "ប្រយ័ត្ន",
        "code_blocks": "ស្គ្រីបប្លុក (សាងសង់ឡើងវិញក្នុង mBlock)",
        "code_hints": "ប្លុកដែលអ្នកត្រូវការ — រកលំដាប់ដោយខ្លួនឯង",
        "blocks_new": "ថ្មី",
        "next_lesson": "មេរៀនបន្ទាប់",
        "teacher_check": "ការត្រួតពិនិត្យរបស់គ្រូ",
        "build_diagrams": "សាងសង់វា — ពីមគ្គុទ្ទេសក៍ផ្លូវការ",
        "forty_line": "◆ មេរៀនសំខាន់ និងច្រកត្រួតពិនិត្យទាំងបួន បញ្ចប់ត្រឹមនេះ ក្នុងរយៈពេល ៤០ ម៉ោង។ ដំណាក់កាល E ខាងក្រោមជាគម្រោងបញ្ចប់ — គ្មានប្លុកថ្មី ដូច្នេះកម្មវិធី ៤០ ម៉ោង អាចឈប់ត្រឹមបន្ទាត់នេះ។",
        "code_python": "Python (mBlock → របៀប Python)",
        "expected_result": "◉ លទ្ធផលរំពឹងទុកនៅចុងបញ្ចប់មេរៀននេះ",
        "builds_on": "↪ បន្តពី ",
        "feeds": "ត្រៀមទៅ",
        # 2-hour band
        "lane_warmup": "① កម្ដៅខ្លួន",
        "lane_arena": "④ សង្វៀនបញ្ហាប្រឈម",
        "lane_maker": "⑤ បង្កើតតាមរបៀបរបស់អ្នក",
        "lane_share": "⑥ បង្ហាញ និងកត់ត្រា",
        "band_lead": "＋ កំណែ ២ ម៉ោង — ៦០′ បន្ថែម "
                     "(② បង្រៀន និងអនុវត្ត = ស្នូល ៤៥′ ខាងលើ · ③ សម្រាក ៥′)",
        # secondary (Grades 7-9) second hour
        "lane_recap": "① ពិនិត្យឡើងវិញ និងកែកំហុស",
        "lane_extend": "④ ពង្រីក — តាមស្តង់ដារ",
        "lane_log": "⑤ កំណត់ហេតុវិស្វកម្ម",
        "lane_review": "⑥ ការត្រួតពិនិត្យការរចនា",
        "step_n": "ជំហានទី {n}",
        "teacher_title": "ឯកសារយោងគ្រូ — គម្រោងចម្លើយ និងស្គ្រីបប្លុក",
        "teacher_kicker": "ឯកសារយោងគ្រូ",
        "teacher_lede": "ការរៀបចំបញ្ចប់សម្រាប់មេរៀននីមួយៗ និងគម្រោង mBlock ដែលរក្សាទុកនៅពីក្រោយវា។ "
                        "វាមិនត្រូវបានភ្ជាប់ពីគេហទំព័រសិស្សទេ៖ ទំព័រជំហានផ្ដល់គោលដៅ ប្លុកសម្រាប់ដំណាក់កាល"
                        "នីមួយៗ និងលទ្ធផលដែលត្រូវសម្រេច ហើយការរកឃើញការរៀបចំគឺជាមេរៀន។ ប្រើវាដើម្បីមើល"
                        "ថាថ្នាក់កំពុងឆ្ពោះទៅណា ដើម្បីប្រគល់ឯកសារជំហាននោះដល់សិស្សដែលជាប់គាំង ឬដើម្បី"
                        "បោះពុម្ពស្គ្រីបមួយឲ្យគេ។",
        "teacher_lesson": "មេរៀន",
        "teacher_lessons": "មេរៀន",
        "teacher_projects": "គម្រោងរក្សាទុក",
        "teacher_file": "ឯកសារ",
        "teacher_open": "បើកមេរៀន →",
        "teacher_print_all": "បោះពុម្ពស្គ្រីបទាំងអស់",
        "teacher_files_n": "គម្រោង {n}",
        "teacher_print_note": "ការបោះពុម្ពទំព័រនេះផ្ដល់ស្គ្រីបមួយក្នុងមួយសន្លឹក តាមលំដាប់វគ្គសិក្សា។ "
                              "ចែកសន្លឹកម្ដងមួយ ជាជាងចែកទាំងសំណុំ — សិស្សដែលមានមេរៀនបីបន្ទាប់ "
                              "គ្មានអ្វីនៅសល់ឲ្យរកឃើញទេ។",
        "checkpoint_n": "ចំណុចត្រួតពិនិត្យទី {n}",
        "hours_in": "~{h} ម៉ោង",
        "concept": "គំនិតថ្មី",
        "project": "ឈ្មោះគម្រោង",
        "answer_project": "គម្រោងចម្លើយ",
        "answers_title": "គម្រោងចម្លើយ — ឯកសារយោងសម្រាប់គ្រូ",
        "answers_lede": "គម្រោង mBlock មួយ <b>ក្នុងមួយជំហាន</b> ដែលបង្កើតឡើងដោយធ្វើតាមវគ្គសិក្សាពីដើមដល់ចប់ — ឯកសារនីមួយៗអាចផ្ទុកឡើង និងដំណើរការដោយខ្លួនឯង។ វាបើកសម្រាប់សិស្សនៅចំណុចត្រួតពិនិត្យដែលបិទដំណាក់កាលរបស់វា។ ជំហានចុងក្រោយនៃដំណាក់កាល E ក៏ជាការបង្ហាញផងដែរ។",
        "reveal_warn": "⚠ ឯកសារនីមួយៗផ្ទុកស្គ្រីបនៃ<b>ជំហានតែមួយ</b>ប៉ុណ្ណោះ ដូច្នេះការប្រគល់ឯកសារនៃជំហានដែលសិស្សកំពុងធ្វើ មិនបង្ហាញអ្វីដែលនៅខាងមុខទេ។ ផ្ទុកឡើងម្ដងមួយ៖ ស្គ្រីបពីរជំហានក្នុងគម្រោងតែមួយ មានន័យថាមាន <code>when CyberPi starts up</code> ពីរ និងអ្នកគ្រប់គ្រងប៊ូតុងតែមួយពីរ ហើយរូបយន្តនឹងឈប់ដំណើរការ ដោយបង្ហាញ traceback នៅលើអេក្រង់របស់វា។",
        "open_course": "បើកវគ្គសិក្សា →",
        "answers_link": "គម្រោងចម្លើយ",
        "download": "ទាញយក .mblock",
        "not_built_yet": "មិនទាន់សាងសង់",
        "you_build": "អ្នកសាងសង់",
        "palette": "ប្លុក",
        "band_lead_sec": "＋ មេរៀន ២ ម៉ោង — ៦៥′ ដែលនៅសល់ "
                         "(② បង្រៀន និងអនុវត្ត = ស្នូល ៤៥′ ខាងលើ · ③ សម្រាក ៥′)",
        "spec_label": "ស្តង់ដារ",
        "r_recap": "① ពិនិត្យ និងកែកំហុស",
        "r_extend": "④ ពង្រីកតាមស្តង់ដារ",
        "r_log": "⑤ កំណត់ហេតុ",
        "r_review": "⑥ ត្រួតពិនិត្យការរចនា",
        "r_recap_svg": "① ពិនិត្យ និងកែកំហុស",
        "r_extend_svg": "④ ពង្រីកតាមស្តង់ដារ",
        "r_log_svg": "⑤ កំណត់ហេតុ",
        "r_review_svg": "⑥ ត្រួតពិនិត្យការរចនា",
        "nonneg_sec": "<b>លក្ខខណ្ឌចាំបាច់សម្រាប់មេរៀន ២ ម៉ោង៖</b> "
                      "កំណត់ហេតុវិស្វកម្មត្រូវសរសេរក្នុងអំឡុងមេរៀន មិនមែនក្រោយមកទេ — "
                      "ការផ្លាស់ប្ដូរដែលគ្មានការវាស់វែងជាប់នឹងវា មិនរាប់បញ្ចូលទេ · "
                      "កិច្ចការពង្រីកនីមួយៗត្រូវប្រាប់ស្តង់ដារជាមុន មុនពេលនរណាម្នាក់ដំណើរការរូបយន្ត · "
                      "ការត្រួតពិនិត្យការរចនាធ្វើតាមលក្ខណៈវិនិច្ឆ័យដែលបានកំណត់ មិនមែនតាមចំណូលចិត្តទេ · "
                      "រូបយន្តត្រូវទុកឲ្យផ្គុំរួចនៅលើធ្នើររទេះមានស្លាក "
                      "និងសាកថ្មតាម USB-C រវាងមេរៀននីមួយៗ។",
        # rhythm strip
        "r_setup": "រៀបចំ",
        "r_warmup": "① កម្ដៅខ្លួន",
        "r_share": "⑥ បង្ហាញ និងកត់ត្រា",
        "r_reset": "សម្អាត",
        "r_briefing": "បំភ្លឺ",
        "r_core": "ការអនុវត្តជាក់ស្ដែង",
        "r_notes": "កំណត់ចំណាំ",
        "r_teach_core": "② បង្រៀន និងអនុវត្ត — ស្នូល",
        "r_break": "③ សម្រាក",
        "r_arena": "④ សង្វៀនបញ្ហាប្រឈម",
        "r_maker": "⑤ បង្កើតតាមរបៀបរបស់អ្នក",
        "r_share_svg": "⑥ បង្ហាញ និងកត់ត្រា",
        # intro / cover
        "teaching_guide": "មគ្គុទ្ទេសក៍បង្រៀន",
        "program_default": "កម្មវិធីរូបយន្ត mBot2 Rover",
        "sessions_unit": "មេរៀន",
        "coding_mode": "របៀបសរសេរកូដ",
        "each": "ក្នុងមួយមេរៀន",
        "each_20h": "ក្នុងមួយមេរៀន · សរុប ២០ ម៉ោង",
        "each_40h": "ក្នុងមួយមេរៀន · សរុប ៤០ ម៉ោង",
        "final_project": "★ គម្រោងចុងក្រោយ៖ {name}",
        "cover_foot": "ការបោះពុម្ពសម្រាប់គ្រូ — មេរៀននីមួយៗមានមួយទំព័រ៖ គំនិតត្រូវបង្រៀន · "
                      "លំដាប់មេរៀនតាមម៉ោង · កូដ · ចំណុចប្រឈម · លទ្ធផលរំពឹងទុក "
                      "ជាមួយលក្ខណៈវិនិច្ឆ័យជោគជ័យ។ កម្មវិធី៖ mBlock 5 · Makeblock App · "
                      "ឧបករណ៍ ១ ឈុត សម្រាប់សិស្ស ២–៣ នាក់។",
        "at_a_glance": "ទិដ្ឋភាពរួមថ្នាក់ទី {n}",
        "objectives_head": "គោលបំណងសិក្សា — នៅចុងឆ្នាំសិក្សា សិស្សអាច៖",
        "sessions_by_unit": "មេរៀនទាំង ២០ ដាក់ពណ៌តាមឯកតា",
        "buffer_note": "✱ ក្នុងចំណងជើងមេរៀន = មេរៀនបម្រុង (អាចបង្រួមបាន បើកាលវិភាគយឺត)",
        "same_rhythm": "មេរៀនទាំងអស់ដំណើរការតាមចង្វាក់ដូចគ្នា",
        "friction_head": "ចំណុចលំបាកដែលគេដឹងក្នុងឆ្នាំនេះ៖",
        "boxes_head": "ប្រអប់ឧបករណ៍ — ឯកសារយោងមាតិកាផ្លូវការ",
        "nonneg_short": "<b>លក្ខខណ្ឌចាំបាច់សម្រាប់មេរៀន ១ ម៉ោង៖</b> "
                        "រូបយន្តត្រូវទុកឲ្យផ្គុំរួចរវាងមេរៀននីមួយៗ នៅលើធ្នើររទេះមានស្លាក · "
                        "កូដត្រូវរក្សាទុកក្នុងគណនី mBlock cloud រាល់មេរៀន · "
                        "ប្ដូរវេនថ្មដោយមានអ្នកគ្រប់គ្រងថ្មប្រចាំក្រុម · "
                        "កាតលំហាត់បន្ថែមដាក់នៅតាមតុ ដើម្បីកុំឲ្យក្រុមលឿនរង់ចាំ។",
        "nonneg_long": "<b>លក្ខខណ្ឌចាំបាច់សម្រាប់មេរៀន ២ ម៉ោង៖</b> "
                       "ការសម្រាក ៥′ មិនមែនជាជម្រើសទេនៅអាយុនេះ — ត្រូវសម្រាកតាមម៉ោង · "
                       "សង្វៀនបញ្ហាប្រឈមបែងចែកជាកម្រិត ដើម្បីកុំឲ្យអ្នកណារង់ចាំ "
                       "ហើយកុំឲ្យអ្នកណាជាប់គាំង៖ គ្រប់ក្រុមត្រូវឆ្លងកាត់ ★☆☆ សិន មុននឹងបន្ត · "
                       "ផ្នែកបង្កើតត្រូវមានតុរៀងៗខ្លួន ឆ្ងាយពីកុំព្យូទ័រ · "
                       "រូបយន្តត្រូវទុកឲ្យផ្គុំរួចនៅលើធ្នើររទេះមានស្លាក "
                       "និងសាកថ្មតាម USB-C រវាងមេរៀននីមួយៗ។",
        # nav / chrome
        "all_grades": "គ្រប់ថ្នាក់",
        "lang_switch": "ភាសា",
        "grade_n": "ថ្នាក់ទី {n}",
        "session_label": "មេរៀនទី {n}៖ {title}",
        "print_session": "🖨 បោះពុម្ពមេរៀននេះ",
        "print_lesson_only": "🖨 បោះពុម្ពតែមេរៀន",
        "print_solution_only": "🖨 បោះពុម្ពតែចម្លើយ",
        "teacher_solution": "ចម្លើយសម្រាប់គ្រូ",
        "teacher_solution_note": "បោះពុម្ពច្បាប់ពេញលេញមួយសម្រាប់គ្រូ។ ប្រើ «បោះពុម្ពតែមេរៀន» សម្រាប់ច្បាប់សិស្ស។",
        "expected_completed_result": "លទ្ធផលដែលរំពឹងទុកពេលបញ្ចប់",
        "switch_to": "⇄ {label} ({total})",
        "v_short": "កំណែ ១ ម៉ោង",
        "v_long": "កំណែ ២ ម៉ោង",
        "full_guide": "មគ្គុទ្ទេសក៍ពេញលេញសម្រាប់បោះពុម្ព →",
        "sessions_head": "មេរៀន",
        "not_migrated": "(មិនទាន់បញ្ចូល)",
        "grade_theme": "ថ្នាក់ទី {n} — {theme}",
        "capstone": "គម្រោងបញ្ចប់",
        "timing_line": "{label}៖ {per} × ២០ មេរៀន = {total}",
        # landing + search
        "site_title": "មគ្គុទ្ទេសក៍បង្រៀន mBot2",
        "landing_head": "កម្មវិធីរូបយន្ត mBot2 — មគ្គុទ្ទេសក៍បង្រៀន",
        "landing_blurb": "អានការណែនាំអំពីវគ្គខាងក្រោម រួចរកមើលតាមថ្នាក់ ឬស្វែងរកមេរៀនទាំងអស់។",
        "browse_head": "រកមើលវគ្គសិក្សា",
        "demo_link": "ដំណើរទស្សនកិច្ចសាកល្បងសម្រាប់ថ្នាក់ដឹកនាំសាលា →",
        "glossary_link": "សទ្ទានុក្រមប្លុក →",
        "glossary_new_tab": "បើកសទ្ទានុក្រមក្នុងផ្ទាំងថ្មី",
        "search_ph": "ស្វែងរកមេរៀនទាំងអស់… (ឧ. ការក្រិតតាំង, អ៊ុលត្រាសោនិក, រង្វិល)",
        "no_match": "រកមិនឃើញមេរៀនត្រូវគ្នាទេ។",
        "primary_head": "បឋមសិក្សា — ថ្នាក់ទី ៤–៦",
        "primary_sub": "ប្រអប់ mBot2 ទី ១ ប៉ុណ្ណោះ · ប្រើប្លុកប៉ុណ្ណោះ · មាន ១ ម៉ោង ឬ ២ ម៉ោង ក្នុងមួយសប្ដាហ៍",
        "secondary_head": "មធ្យមសិក្សា — ថ្នាក់ទី ៧–៩",
        "secondary_sub": "ប្រអប់ទី ១ → គ្រឿងបន្ថែម Rover · ប្លុក → Python · ១ ម៉ោង ក្នុងមួយសប្ដាហ៍",
        "open_guide": "បើកមគ្គុទ្ទេសក៍ <b>{per} × ២០ = {total}</b> →",
        "n_of_20": "{n}/២០ មេរៀន",
        "page_title_session": "ថ្នាក់ទី{g} មេរៀន{n} · {title} ({per})",
        "page_title_index": "ថ្នាក់ទី {n} · {theme} ({per})",
        "page_title_print": "មគ្គុទ្ទេសក៍បង្រៀន mBot2 ថ្នាក់ទី {n} ({per} × ២០)",
        # demo tour
        "demo_nav": "ដំណើរទស្សនកិច្ចសាកល្បង — ទិដ្ឋភាពរួមកម្មវិធីសម្រាប់ថ្នាក់ដឹកនាំសាលា",
        "demo_head": "កម្មវិធីរូបយន្ត mBot2 — ខ្សែសង្វាក់ ៦ ឆ្នាំ",
        "demo_lede": "ឧបករណ៍មួយគ្រួសារ រយៈពេល ៦ ឆ្នាំ។ ថ្នាក់ទី ៤–៦ ប្រើតែប្រអប់ mBot2 ទី ១ "
                     "ដោយប្រើប្លុក៖ បញ្ជាវា (ថ្នាក់ទី៤) → ធ្វើឲ្យវាដឹង និងសម្រេចចិត្ត (ថ្នាក់ទី៥) → "
                     "ធ្វើឲ្យវាដំណើរការដោយខ្លួនឯង និងភ្ជាប់បណ្ដាញ (ថ្នាក់ទី៦) "
                     "ដែលនីមួយៗមានកំណែ ១ ម៉ោង ឬ ២ ម៉ោង ក្នុងមួយសប្ដាហ៍។ "
                     "បន្ទាប់មក ថ្នាក់ទី ៧–៩ បន្ថែមភាពជាក់លាក់ និងផ្នែករឹង៖ "
                     "mBot2 កង់រុញដោយប្លុក (ថ្នាក់ទី៧) → "
                     "Rover ខ្សែក្រវាត់ ជាមួយ AI និងការបញ្ចេញមុខមាត់ (ថ្នាក់ទី៨) → "
                     "Rover ដដែល ដាក់ឲ្យធ្វើការដោយប្រើដៃចាប់ សរសេរដោយ Python ពេញលេញ (ថ្នាក់ទី៩)។ "
                     "ឆ្នាំនីមួយៗជាជណ្ដើរ ២០ មេរៀនបន្តបន្ទាប់ បញ្ចប់ដោយព្រឹត្តិការណ៍សាធារណៈមានពិន្ទុ — "
                     "កាតសមិទ្ធផលបួនក្នុងមួយថ្នាក់បង្ហាញជណ្ដើរនោះ ហើយកាតគម្រោងបញ្ចប់គឺជាទីដៅ។",
        "demo_kicker": "ថ្នាក់ទី {n} · {form} · {codemode}",
        "demo_card": "មេរៀនទី {n} · {title}",
        "demo_glede": "២០ {timing} ក្នុង {units} ឯកតា ({totals}) — មេរៀននីមួយៗជាឯកសារណែនាំគ្រូ "
                      "មួយទំព័រស្រេច (លំដាប់តាមម៉ោង កូដ ចំណុចប្រឈម លក្ខណៈវិនិច្ឆ័យជោគជ័យ)។ "
                      "ជំនាញកកើតឡើងតាមឯកតានីមួយៗ ហើយបញ្ចប់ដោយព្រឹត្តិការណ៍សាធារណៈមានពិន្ទុនៅមេរៀនទី ២០។",
        "demo_sessions_word": " មេរៀន",
        "demo_or": " ឬ ",
        "demo_milestones": "សមិទ្ធផលតាមផ្លូវ",
        "demo_capstone": "★ មេរៀនទី ២០ — {name} (ការបញ្ចប់ឆ្នាំ)",
        "demo_open": "បើកទំព័រគ្រូពេញលេញនៃមេរៀនទី ២០ →",
        "demo_title": "ដំណើរទស្សនកិច្ចសាកល្បង · កម្មវិធីរូបយន្ត mBot2",
        # materials page
        "materials": "សម្ភារៈថ្នាក់រៀន",
        "materials_title": "ថ្នាក់ទី {n} · សម្ភារៈថ្នាក់រៀន",
        "materials_head": "ថ្នាក់ទី {n} — អ្វីដែលថ្នាក់រៀនត្រូវការ",
        "materials_lede": "គ្រប់អ្វីដែលមេរៀនទាំង {n} នៃឆ្នាំនេះត្រូវការ "
                          "ប្រមូលពីបញ្ជីគ្រឿងបន្លាស់ក្នុងមេរៀននីមួយៗ។ "
                          "សម្ភារៈត្រូវបានចាត់ជាក្រុមតាមប្រភពរបស់វា។",
        "mat_kits": "ឈុតរូបយន្ត",
        "mat_kits_rule": "ឈុត mBot2 ១ សម្រាប់សិស្ស ២–៣ នាក់",
        "mat_class_size": "ចំនួនសិស្សក្នុងថ្នាក់",
        "mat_kits_needed": "ចំនួនឈុតត្រូវការ",
        "mat_students": "សិស្ស {n} នាក់",
        "mat_from_box": "ពីប្រអប់ mBot2",
        "mat_from_box_sub": "មានស្រាប់ក្នុងឈុត — មិនចាំបាច់ទិញទេ "
                            "ប៉ុន្តែនេះជាគ្រឿងបន្លាស់ដែលឆ្នាំនេះប្រើពិតប្រាកដ",
        "mat_from_rover": "ពីប្រអប់បន្ថែម Rover",
        "mat_from_rover_sub": "មានស្រាប់ក្នុងឈុតបន្ថែម — មិនចាំបាច់ទិញទេ "
                              "ប៉ុន្តែនេះជាគ្រឿងបន្លាស់ដែលឆ្នាំនេះប្រើពិតប្រាកដ",
        "mat_classroom": "សម្ភារៈថ្នាក់រៀន",
        "mat_classroom_sub": "អ្នកត្រូវរៀបចំដោយខ្លួនឯង — មិនមានក្នុងឈុតទេ",
        "mat_extra": "លក់ដាច់ដោយឡែក",
        "mat_extra_sub": "មិនមានក្នុងប្រអប់ទេ — ត្រូវបញ្ជាទិញមុនមេរៀនដែលត្រូវការ",
        "mat_used_in": "ប្រើក្នុង",
        "mat_sessions_n": "មេរៀន {n}",
        "mat_long_only": "សម្រាប់កំណែ ២ ម៉ោង ប៉ុណ្ណោះ",
        "mat_note": "កំណត់សម្គាល់",
        "mat_by_session": "តាមមេរៀននីមួយៗ",
        "mat_by_session_sub": "សម្រាប់ការរៀបចំប្រចាំសប្ដាហ៍ — អ្វីត្រូវដាក់លើតុមុនមេរៀននីមួយៗ",
        "mat_session": "មេរៀន",
        "mat_needs": "ត្រូវការ",
        "mat_nothing": "គ្មានអ្វីក្រៅពីរូបយន្ត",
        "mat_total_line": "គ្រឿងបន្លាស់ {box} ពីឈុត · សម្ភារៈថ្នាក់រៀន {cls}{extra}",
        "mat_total_extra": " · លក់ដាច់ដោយឡែក {n}",
    },
}
