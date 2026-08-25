# -*- coding: utf-8 -*-
"""The block glossary: every block in the palette, what it does, when to use it.

One page, `site/glossary.html`, built from three sources that are each already
authoritative for their part:

  reference/mblock-palette.json   which blocks exist, in which drawer, in what
                                  order, in mBlock's own colours
  content/block-glossary.yaml     the writing — what / when / example / watch
  content/grade*/steps/*.yaml     which lessons use the block, so every entry
                                  can point at where it is met in the course

The examples are authored in the same block source language the lessons use and
drawn by the same renderer, so a glossary example and a lesson script are the
same thing. `audit()` refuses any example line the resolver cannot place — an
unresolved line still draws, as a flat pill carrying the raw text, and would be
a picture of a block that does not exist.
"""
import json
import pathlib
import re

import yaml

import i18n
import render
import svgblocks as S

ROOT = pathlib.Path(__file__).resolve().parent.parent
PALETTE = ROOT / "reference" / "mblock-palette.json"
EN_WORDS = ROOT / "content" / "block-glossary.yaml"


def words_path():
    return (EN_WORDS if i18n.LOCALE == "en"
            else ROOT / f"content-{i18n.LOCALE}" / "block-glossary.yaml")

# The drawers a student sees, in toolbox order — the same list and the same
# reasoning as tools/export_block_images.py, which draws the PNG library.
KIT = {"cyberpi", "mbot2", "mbuild_quad_color_sensor", "cyberpi_mbuild_ultrasonic2",
       "firefly_bluetoothcontroller", "cyberpi_upload_message", "cyberpi_sprite",
       "cyberpi_ai_emotion",
       "control", "operators", "variables", "myblocks", "events"}
CATE_ORDER = ["Events", "Control", "Operators", "Variables", "My Blocks",
              "mBot2 Chassis", "mBot2 Extension Port", "Quad RGB Sensor",
              "Ultrasonic Sensor 2", "Bluetooth controller", "Display", "LED",
              "Audio", "Sensing", "Motion Sensing", "LAN", "Upload Mode Broadcast",
              "AI", "IoT", "Magic emoji", "Sprites"]

# A few individual blocks use a colour different from their drawer. Keep those
# exceptions here so the standalone glossary block matches the same block when
# it is rendered inside an example script.
BLOCK_COLORS = {
    "control_stop": "#FFAB19",
}

# A short standfirst per drawer: what this whole family of blocks is for. The
# glossary is read by somebody who does not yet know which drawer to open.
CATE_INTRO = {}
CATE_INTRO["en"] = {
    "Events": "Hat blocks. Each one starts a script when something happens, and a "
              "script can only have one. Which hat you choose decides when — and "
              "whether — your program runs at all.",
    "Control": "The shape of a program: what repeats, what only happens sometimes, "
               "and what waits. These blocks hold other blocks rather than doing "
               "anything themselves.",
    "Operators": "Arithmetic and questions. None of these do anything on their own "
                 "— they are reporters, and they go INTO the slots of other blocks.",
    "Variables": "Named boxes. A variable holds one thing; a list holds a numbered "
                 "row of things. Both are made in the drawer before they can be "
                 "used.",
    "My Blocks": "Blocks you invent. Give a group of blocks a name and it becomes "
                 "one block — which is how a long script turns into a short one "
                 "that says what it means.",
    "mBot2 Chassis": "The two driving wheels use encoder motors: each motor has "
                     "a built-in sensor that counts its rotation, so the robot "
                     "can measure wheel speed and turning angle instead of only "
                     "sending power and hoping. The encoder measures the motor's "
                     "rotation, not actual distance across the floor, so wheel "
                     "slip can still make a move inaccurate. EM1 and EM2 are the "
                     "two numbered encoder-motor ports, not two different kinds "
                     "of motor. On the standard mBot2, EM1 controls the left "
                     "wheel and EM2 the right. On this course's Rover build, the "
                     "cables are deliberately crossed: left is EM2 and right is "
                     "EM1. The blocks whose "
                     "labels say \u201cuntil "
                     "done\u201d or \u201cfor \u2026 secs\u201d hold the script "
                     "while they run; the others start the wheels and let the script "
                     "carry on, which is what you need to move and watch at once. "
                     "RPM means revolutions per minute: 50 RPM asks a wheel to "
                     "complete 50 full turns in one minute. A higher RPM means "
                     "faster wheel rotation.",
    "mBot2 Extension Port": "The four ports on the front for things you add "
                            "yourself: servos, extra motors, LED strips, and raw "
                            "pins for your own electronics. A pin is one small "
                            "electrical contact in a connector. Different pins "
                            "have different jobs: some supply power, one is "
                            "ground, and others carry control signals or sensor "
                            "readings. The pin order and voltage must match the "
                            "part you connect; guessing can damage the part or "
                            "the Shield. A digital read compares a signal with "
                            "ground: near ground is low/false, while near the "
                            "positive logic supply is high/true. A common "
                            "pull-down switch is low while open and high when "
                            "closed, but an active-low sensor deliberately "
                            "reverses that meaning. An unconnected signal can "
                            "float unpredictably and is not a valid reading. "
                            "For a plain DC motor, "
                            "M1 controls the motor connected to port M1, M2 "
                            "controls the motor connected to port M2, and all "
                            "sends the same command to both. M1/M2 are plain "
                            "extension-motor ports; do not confuse them with "
                            "EM1/EM2, the encoder-motor ports for the driving "
                            "wheels.",
    "Quad RGB Sensor": "The four colour probes underneath, which read the floor. "
                       "They can answer a yes-or-no question about one probe, or "
                       "report how far off a line the whole robot has drifted.",
    "Ultrasonic Sensor 2": "The forward-looking distance sensor, with two ring "
                           "lights for eyes. It belongs to the standard mBot2 — the "
                           "Rover build does not have one.",
    "Bluetooth controller": "The gamepad. These blocks come from the Bluetooth "
                            "Controller EXTENSION and work in Upload mode; the "
                            "identical-looking blocks from the bundled controller "
                            "device do not.",
    "Display": "The colour screen. Labels stay in fixed slots and update in place; "
               "printing scrolls; charts and tables are for numbers that change.",
    "LED": "The five lights in a ring on the front of the CyberPi. The fastest way "
           "for a robot to say what it is thinking to a whole room.",
    "Audio": "The speaker and the microphone: built-in sounds, tones, notes, "
             "recordings, and the volume they all come out at.",
    "Sensing": "The CyberPi's own inputs — its buttons, its joystick, its "
               "microphone and light sensor, its timer, and facts about the board "
               "itself.",
    "Motion Sensing": "The motion sensor inside the board: which way it is tilted, "
                      "how hard it is shaken, and how far it has turned.",
    "LAN": "Robot-to-robot messages over the local network. For robots working "
           "together in the same room.",
    "Upload Mode Broadcast": "Messages between an uploaded program and mBlock on "
                             "the computer — the way to see what a robot running on "
                             "its own is doing.",
    "AI": "Cloud services: speaking, listening, translating, and the Wi-Fi they all "
          "depend on. Every one of these needs a network, a signed-in mBlock "
          "account, and Upload mode.",
    "IoT": "The internet: messages that can cross a building, and data from the "
           "outside world such as weather, air quality and the real time.",
    "Magic emoji": "Faces for the CyberPi screen — generated by AI, drawn by you, "
                   "or picked from a set of ready-made animations.",
    "Sprites": "Named pictures on the screen that you move about independently, "
               "rather than lines of text that scroll. The basis of games and "
               "dials on the robot itself.",
}
CATE_INTRO["km"] = {
    "Events": "ប្លុកមួក។ ប្លុកនីមួយៗចាប់ផ្ដើមស្គ្រីបពេលមានអ្វីមួយកើតឡើង ហើយស្គ្រីបមួយអាចមានតែមួយ។ "
              "ប្លុកមួកណាដែលអ្នកជ្រើស សម្រេចថា ពេលណា — និងថាតើ — កម្មវិធីរបស់អ្នកដំណើរការឬអត់។",
    "Control": "រូបរាងនៃកម្មវិធី៖ អ្វីដែលធ្វើម្ដងទៀត អ្វីដែលកើតឡើងតែពេលខ្លះ និងអ្វីដែលរង់ចាំ។ "
               "ប្លុកទាំងនេះផ្ទុកប្លុកដទៃ ជាជាងធ្វើអ្វីដោយខ្លួនឯង។",
    "Operators": "នព្វន្ត និងសំណួរ។ គ្មានប្លុកណាមួយក្នុងចំណោមនេះធ្វើអ្វីដោយខ្លួនឯងទេ — "
                 "វាជាអ្នករាយការណ៍ ហើយវាចូល ក្នុង រន្ធរបស់ប្លុកដទៃ។",
    "Variables": "ប្រអប់មានឈ្មោះ។ អថេរផ្ទុករបស់តែមួយ; បញ្ជីផ្ទុកជួររបស់ដែលមានលេខរៀង។ "
                 "ទាំងពីរត្រូវបង្កើតក្នុងថតមុនពេលអាចប្រើបាន។",
    "My Blocks": "ប្លុកដែលអ្នកបង្កើត។ ដាក់ឈ្មោះឲ្យក្រុមប្លុកមួយ នោះវាក្លាយជាប្លុកតែមួយ — "
                 "ដែលជារបៀបដែលស្គ្រីបវែងក្លាយជាស្គ្រីបខ្លីដែលប្រាប់ថាវាមានន័យអ្វី។",
    "mBot2 Chassis": "កង់បើកបរទាំងពីរ។ ប្លុកដែលស្លាករបស់វាសរសេរថា «until done» ឬ «for … secs» "
                     "ទប់ស្គ្រីបខណៈវាដំណើរការ; ប្លុកឯទៀតចាប់ផ្ដើមកង់ ហើយឲ្យស្គ្រីបបន្ត "
                     "ដែលជាអ្វីដែលអ្នកត្រូវការដើម្បីធ្វើចលនា និងមើលក្នុងពេលតែមួយ។",
    "mBot2 Extension Port": "រន្ធបួននៅខាងមុខសម្រាប់របស់ដែលអ្នកបន្ថែមដោយខ្លួនឯង៖ ស៊ែវ៉ូ "
                            "ម៉ូទ័របន្ថែម ខ្សែ LED និងម្ជុលដើមសម្រាប់អេឡិចត្រូនិករបស់អ្នក។",
    "Quad RGB Sensor": "ឧបករណ៍ចាប់ពណ៌បួននៅខាងក្រោម ដែលអានឥដ្ឋ។ វាអាចឆ្លើយសំណួរបាទ/ទេ "
                       "អំពីឧបករណ៍ចាប់មួយ ឬរាយការណ៍ថារូបយន្តទាំងមូលរេចេញពីបន្ទាត់ប៉ុណ្ណា។",
    "Ultrasonic Sensor 2": "ឧបករណ៍ចាប់ចម្ងាយដែលមើលទៅមុខ មានភ្លើងរង្វង់ពីរជាភ្នែក។ "
                           "វាជារបស់ mBot2 ស្តង់ដារ — តួរូបយន្ត Rover គ្មានវាទេ។",
    "Bluetooth controller": "ឈ្នាន់បញ្ជា។ ប្លុកទាំងនេះមកពី ផ្នែកបន្ថែម Bluetooth Controller "
                            "ហើយដំណើរការក្នុងរបៀប Upload; ប្លុកដែលមើលទៅដូចគ្នាបេះបិទ "
                            "ពីឧបករណ៍បញ្ជាដែលភ្ជាប់មកស្រាប់ មិនដំណើរការទេ។",
    "Display": "អេក្រង់ពណ៌។ ស្លាកនៅក្នុងរន្ធថេរ ហើយធ្វើបច្ចុប្បន្នភាពនៅនឹងកន្លែង; ការបោះពុម្ពរមូរ; "
               "គំនូសតាង និងតារាងសម្រាប់លេខដែលប្ដូរ។",
    "LED": "ភ្លើងប្រាំជារង្វង់នៅខាងមុខ CyberPi។ វិធីលឿនបំផុតសម្រាប់រូបយន្តដើម្បីប្រាប់ "
           "អ្វីដែលវាកំពុងគិត ដល់មនុស្សទាំងបន្ទប់។",
    "Audio": "ឧបករណ៍បំពង និងមីក្រូហ្វូន៖ សំឡេងមានស្រាប់ សំឡេងតាមប្រេកង់ ណូត ការថត "
             "និងកម្រិតសំឡេងដែលវាទាំងអស់ចេញមក។",
    "Sensing": "ធាតុចូលផ្ទាល់របស់ CyberPi — ប៊ូតុង ឈ្នាន់ មីក្រូហ្វូន និងឧបករណ៍ចាប់ពន្លឺ "
               "នាឡិកា និងការពិតអំពីផ្ទាំងខ្លួនឯង។",
    "Motion Sensing": "ឧបករណ៍ចាប់ចលនាក្នុងផ្ទាំង៖ វាផ្អៀងទៅទិសណា វាត្រូវអង្រួនខ្លាំងប៉ុណ្ណា "
                      "និងវាបានបង្វិលឆ្ងាយប៉ុណ្ណា។",
    "LAN": "សាររវាងរូបយន្តតាមបណ្តាញមូលដ្ឋាន។ សម្រាប់រូបយន្តដែលធ្វើការជាមួយគ្នាក្នុងបន្ទប់តែមួយ។",
    "Upload Mode Broadcast": "សាររវាងកម្មវិធីដែលអាប់ឡូតរួច និង mBlock លើកុំព្យូទ័រ — "
                             "វិធីមើលថារូបយន្តដែលដំណើរការដោយខ្លួនឯងកំពុងធ្វើអ្វី។",
    "AI": "សេវាកម្មពពក៖ ការនិយាយ ការស្តាប់ ការបកប្រែ និង Wi-Fi ដែលវាទាំងអស់អាស្រ័យលើ។ "
          "ប្លុកនីមួយៗក្នុងចំណោមនេះត្រូវការបណ្តាញ គណនី mBlock ដែលចូលរួច និងរបៀប Upload។",
    "IoT": "អ៊ីនធឺណិត៖ សារដែលអាចឆ្លងកាត់អគារ និងទិន្នន័យពីពិភពខាងក្រៅ ដូចជាអាកាសធាតុ "
           "គុណភាពខ្យល់ និងម៉ោងពិត។",
    "Magic emoji": "មុខសម្រាប់អេក្រង់ CyberPi — បង្កើតដោយ AI គូរដោយអ្នក ឬជ្រើសពីសំណុំ "
                   "ចលនាដែលមានស្រាប់។",
    "Sprites": "រូបភាពមានឈ្មោះលើអេក្រង់ដែលអ្នកផ្លាស់ទីដោយឯករាជ្យ ជាជាងបន្ទាត់អត្ថបទដែលរមូរ។ "
               "មូលដ្ឋាននៃហ្គេម និងមុខនាឡិកានៅលើរូបយន្តខ្លួនឯង។",
}

# The lesson pages draw blocks at a scale chosen by the print budget. A glossary
# is read on a screen and the block IS the heading, so it is drawn half again as
# large. Only the on-screen size changes; the geometry is identical.
BLOCK_MM = S.MM_PER_PX * 1.55


def palette():
    """[(cate, order, key, label, spec)] — every block a student can reach."""
    pal = json.loads(PALETTE.read_text(encoding="utf-8"))
    out = []
    for key, spec in pal.items():
        if (not spec.get("cateName") or spec.get("hidden")
                or spec["ext"] not in KIT or spec["cateName"] == "Doodle"):
            continue
        spec = dict(spec, showDefaults=True)
        if spec.get("cateColor"):
            spec["paletteColor"] = BLOCK_COLORS.get(key, spec["cateColor"])
        try:
            label = S.blank_node(spec)["label"]
        except Exception:                                     # noqa: BLE001
            continue
        if not label:
            continue
        for drawer in [spec, *(spec.get("alsoIn") or [])]:
            here = dict(spec, **{k: drawer[k] for k in
                                 ("cate", "cateName", "cateColor")})
            if here["cateColor"]:
                here["paletteColor"] = BLOCK_COLORS.get(key, here["cateColor"])
            out.append((here["cateName"], here.get("order", 0), key, label, here))
    rank = {c: i for i, c in enumerate(CATE_ORDER)}
    out.sort(key=lambda b: (rank.get(b[0], len(rank)), b[0], b[1], b[3]))
    return out


def _by_opcode():
    """{opcode: palette key}. blocks_used() reports a bare opcode while resolve()
    reports `ext.opcode`, and the catalogue is keyed both ways — core blocks are
    bare, extension blocks are prefixed. Everything is folded to the catalogue's
    own key here, or half the usage links point at nothing."""
    pal = json.loads(PALETTE.read_text(encoding="utf-8"))
    return {spec["opcode"]: key for key, spec in pal.items()}


def usage():
    """{palette key: [(grade, step number, title)]} across the block lessons."""
    canon = _by_opcode()
    seen = {}

    def groups_of(line):
        _inner, groups = S.M.split_holes(line)
        for g in groups:
            yield g
            yield from groups_of(g)

    for grade in (7, 8):
        for f in sorted((ROOT / "content" / f"grade{grade}" / "steps").glob("*.yaml")):
            d = yaml.safe_load(f.read_text(encoding="utf-8"))
            code = d.get("code") or {}
            if code.get("lang") != "blocks":
                continue
            where = (grade, d.get("n"), d.get("title") or "")
            keys = set()
            for key, _spec in S.blocks_used(code.get("source") or ""):
                keys.add(key)
            for line in (code.get("source") or "").split("\n"):
                for g in groups_of(line.strip()):
                    hit, _hg = S.M.resolve(g)
                    if hit:
                        keys.add(hit[0])
            for k in keys:
                k = k if k.startswith("my:") else canon.get(k.split(".")[-1], k)
                seen.setdefault(k, []).append(where)
    return seen


def words():
    """The prose for this locale, with the language-neutral fields grafted in.

    `example` is block source and `see` is a list of palette keys — neither is
    translatable, and a second copy of either would be a second thing to keep in
    step. They are authored once, in English, and read from there.
    """
    en = yaml.safe_load(EN_WORDS.read_text(encoding="utf-8")) or {}
    path = words_path()
    if path == EN_WORDS:
        return en
    if not path.exists():
        return {}
    loc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out = {}
    for key, entry in loc.items():
        entry = dict(entry or {})
        for field in ("example", "see", "ide_image"):
            if (en.get(key) or {}).get(field) is not None:
                entry[field] = en[key][field]
        out[key] = entry
    return out


# --------------------------------------------------------------------- audit
def audit():
    """Report entries that are missing, stale, or draw a block that is not real."""
    pal = palette()
    have = words()
    keys = {k for _c, _o, k, _l, _s in pal}
    missing = [k for k in keys if k not in have]
    orphan = [k for k in have if k not in keys]
    broken = []

    def groups_of(line):
        _inner, groups = S.M.split_holes(line)
        for g in groups:
            yield g
            yield from groups_of(g)

    for k, e in have.items():
        src = (e or {}).get("example") or ""
        for line in src.split("\n"):
            t = line.strip()
            if not t or t.startswith("#"):
                continue
            if not (S.control_node(t) or t.startswith("define ")
                    or S.M.resolve(t)[0]):
                broken.append((k, t))
            # A nested reporter that fails to resolve draws as a flat pill inside
            # an otherwise correct block, which is harder to spot than a whole
            # bad line and just as wrong.
            for g in groups_of(t):
                g = g.strip()
                # A single token in brackets is a variable, a number, or part of
                # the block's own wording — `(cm)`, `(RPM)`, `left wheel(EM1)`.
                # Only a group with several words is claiming to be a block.
                if " " not in g or S.M.resolve(g)[0]:
                    continue
                if any(op in f" {g} " for _t, op, *_ in S.M.INFIX):
                    continue
                broken.append((k, f"(nested) {g}"))
    return {"total": len(keys), "written": len(keys) - len(missing),
            "missing": sorted(missing), "orphan": sorted(orphan), "broken": broken}


# --------------------------------------------------------------------- page
# The site's screen sheet sizes `body` to a 210mm page, which is right for a
# lesson you will print and much too narrow for a reference you will scroll.
CSS = """
@media screen { body { max-width: 1180px; padding: 0 26px; } }
.gl-wrap { display: grid; grid-template-columns: 232px minmax(0, 1fr);
           gap: 30px; align-items: start; }
.gl-rail { position: sticky; top: 12px; font-size: 14px; }
.gl-rail a { display: flex; align-items: center; gap: 8px; padding: 5px 8px;
             border-radius: 6px; text-decoration: none; color: #334155; }
.gl-rail a:hover { background: #f1f5f9; }
.gl-rail b { margin-left: auto; color: #94a3b8; font-weight: 400; font-size: 12px; }
.gl-dot { width: 11px; height: 11px; border-radius: 50%; flex: none; }
.gl-find { width: 100%; box-sizing: border-box; padding: 9px 12px; font-size: 15px;
           border: 1px solid #cbd5e1; border-radius: 8px; margin-bottom: 10px; }
.gl-only { font-size: 13px; color: #475569; display: flex; align-items: center;
           gap: 6px; padding: 0 8px 10px; }
.gl-cat { margin: 30px 0 6px; padding-left: 13px; position: relative;
          border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; }
.gl-cat::before { content: ""; position: absolute; left: 0; top: 3px; bottom: 9px;
                  width: 5px; border-radius: 3px; background: var(--c); }
.gl-cat h2 { margin: 0; font-size: 19px; }
.gl-cat p { margin: 3px 0 0; color: #64748b; font-size: 14px; max-width: 78ch; }
.gl-create { border: 2px solid #fed7aa; background: #fff7ed; border-radius: 10px;
             padding: 14px 16px; margin: 14px 0; }
.gl-create h3 { margin: 0 0 6px; font-size: 17px; }
.gl-create > p { margin: 0 0 10px; color: #475569; }
.gl-create-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));
                  gap: 12px; }
.gl-create-step { background: #fff; border: 1px solid #fed7aa; border-radius: 8px;
                  padding: 10px; }
.gl-create-step img { display: block; width: 100%; height: 150px; object-fit: contain;
                      object-position: top center; margin-bottom: 8px; }
.gl-create-step p { margin: 0; font-size: 13.5px; color: #334155; }
.gl-quad { border: 2px solid #10b981; background: #ecfdf5; border-radius: 10px;
           padding: 16px 18px; margin: 18px 0 14px; }
.gl-quad h3 { margin: 0 0 5px; font-size: 18px; }
.gl-quad h4 { margin: 14px 0 4px; font-size: 14px; color: #047857; }
.gl-quad p { margin: 3px 0; max-width: 86ch; }
.gl-quad table { width: 100%; border-collapse: collapse; margin: 9px 0; background: #fff; }
.gl-quad th, .gl-quad td { border: 1px solid #a7f3d0; padding: 7px 9px; text-align: left; vertical-align: top; }
.gl-quad th { background: #d1fae5; }
.gl-probes { display: flex; align-items: center; justify-content: center; gap: 5px; margin: 10px 0; font-weight: 800; }
.gl-probes span { min-width: 52px; padding: 9px; text-align: center; border-radius: 7px; background: #059669; color: #fff; }
.gl-quad-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-top: 12px; }
.gl-quad-shot { background: #fff; border: 1px solid #a7f3d0; border-radius: 8px; padding: 10px; }
.gl-quad-shot img { display: block; width: 100%; height: 190px; object-fit: contain; object-position: top center; margin-bottom: 7px; }
.gl-quad-shot p { margin: 0; font-size: 13.5px; color: #334155; }
.gl-monitor { border: 2px solid #a78bfa; background: #f5f3ff; border-radius: 10px;
              padding: 16px 18px; margin: 8px 0 20px; }
.gl-monitor h2 { margin: 0 0 6px; font-size: 19px; }
.gl-monitor > p { margin: 4px 0; max-width: 86ch; }
.gl-monitor-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-top: 12px; }
.gl-monitor-step { background: #fff; border: 1px solid #c4b5fd; border-radius: 8px; padding: 10px; }
.gl-monitor-step img { display: block; width: 100%; height: 190px; object-fit: contain; object-position: top center; margin-bottom: 7px; }
.gl-monitor-step p { margin: 0; font-size: 13.5px; color: #334155; }
.gl-mini { border: 2px solid #38bdf8; background: #f0f9ff; border-radius: 10px;
           padding: 16px 18px; margin: 18px 0 14px; }
.gl-mini h3 { margin: 0 0 5px; font-size: 18px; }
.gl-mini h4 { margin: 14px 0 4px; font-size: 14px; color: #075985; }
.gl-mini p { margin: 3px 0; max-width: 82ch; }
.gl-mini table { width: 100%; max-width: 820px; border-collapse: collapse;
                 margin: 9px 0; background: #fff; }
.gl-mini th, .gl-mini td { border: 1px solid #bae6fd; padding: 7px 9px;
                           text-align: left; vertical-align: top; }
.gl-mini th { background: #e0f2fe; }
.gl-flow { display: inline-block; margin: 7px 0; padding: 8px 11px;
           border-radius: 6px; background: #0f172a; color: #f8fafc;
           font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
           white-space: pre-wrap; }
.gl-b { border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px 18px;
        margin: 14px 0; background: #fff; break-inside: avoid; }
.gl-b.gl-unused { background: #f1f5f9; border-color: #cbd5e1; }
.gl-b.gl-unused .gl-eg { background: #e2e8f0; border-color: #cbd5e1; }
.gl-b > .bsvg { margin: 0 0 12px; }
.gl-mode-badge { display: table; margin: 0 0 12px; padding: 5px 10px;
                 border-radius: 999px; background: #f00078; color: #fff;
                 font-size: 11px; font-weight: 800; letter-spacing: .08em;
                 line-height: 1; box-shadow: 0 0 0 2px #ffd2e8;
                 text-transform: uppercase; }
.gl-course-badge { display: table; margin: 0 0 12px; padding: 5px 10px;
                   border-radius: 999px; background: #dc2626; color: #fff;
                   font-size: 11px; font-weight: 800; letter-spacing: .08em;
                   line-height: 1; box-shadow: 0 0 0 2px #fecaca;
                   text-transform: uppercase; }
.gl-ide-image { display: block; width: 44px; height: 53px; object-fit: contain;
                margin: 10px 0 2px; }
.gl-ide-image.gl-wide { width: min(100%, 720px); height: auto; object-fit: initial;
                        border: 1px solid #e2e8f0; border-radius: 8px; }
.gl-ide-image.gl-medium { width: 180px; height: auto; object-fit: contain; }
.gl-image-cap { margin: 5px 0 2px !important; color: #64748b; font-size: 13px; }
.gl-b h3 { margin: 0 0 10px; font-size: 15px; }
.gl-l { font-size: 11px; text-transform: uppercase; letter-spacing: .07em;
        color: #94a3b8; margin: 12px 0 3px; }
.gl-b p { margin: 0 0 2px; max-width: 78ch; }
.gl-values { margin: 10px 0 3px; max-width: 900px; border: 1px solid #cbd5e1;
             border-radius: 7px; background: #f8fafc; }
.gl-values-title { padding: 8px 11px; color: #334155; font-size: 13.5px;
                   font-weight: 700; border-bottom: 1px solid #e2e8f0; }
.gl-values dl { margin: 0; padding: 8px 11px 10px; }
.gl-values dt { margin-top: 5px; font-size: 12.5px; font-weight: 700; color: #475569; }
.gl-values dd { margin: 2px 0 7px; font-size: 13.5px; color: #1e293b; }
.gl-value { display: inline-block; margin: 2px 3px 2px 0; padding: 2px 6px;
            border: 1px solid #cbd5e1; border-radius: 5px; background: #fff;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: 12px; }
.gl-eg { background: #f8fafc; border: 1px solid #eef2f7; border-radius: 8px;
         padding: 12px 14px; margin-top: 4px; }
.gl-eg .bsvg { margin: 0; }
.gl-eg .cap { margin: 9px 0 0; font-size: 13.5px; color: #475569; }
.gl-warn { border-left: 3px solid #f59e0b; background: #fffbeb; padding: 8px 12px;
           border-radius: 0 6px 6px 0; margin-top: 4px; }
.gl-warn p { margin: 0; font-size: 14px; }
.gl-meta { margin-top: 12px; padding-top: 10px; border-top: 1px dashed #e2e8f0;
           font-size: 13px; color: #64748b; }
.gl-meta a { color: #2563eb; }
.gl-meta .gl-see { font-weight: 700; text-decoration: underline;
                   text-underline-offset: 2px; }
.gl-used { display: inline-block; width: 8px; height: 8px; border-radius: 50%;
           background: #16a34a; margin-right: 5px; }
.gl-none { color: #94a3b8; font-style: italic; }
@media print {
  @page { size: A4; margin: 12mm 13mm 14mm; }
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  body { max-width: none !important; padding: 0 !important; font-size: 9.2pt; }
  .chrome, .gl-rail, .gl-find, .gl-only { display: none !important; }
  .gl-wrap { display: block; }
  h1 { margin-top: 0; font-size: 22pt; }
  .lede { font-size: 10pt; }
  .gl-sec { break-before: page; column-count: 2; column-gap: 6mm; }
  .gl-sec:first-of-type { break-before: auto; }
  .gl-cat { break-after: avoid; margin-top: 0; column-span: all; }
  .gl-cat h2 { font-size: 16pt; }
  .gl-b { break-inside: avoid; padding: 4mm; margin: 3mm 0; }
  .gl-create, .gl-quad, .gl-monitor, .gl-mini { break-inside: avoid; column-span: all; }
  .gl-b p, .gl-warn p { font-size: 8.8pt; }
  .gl-meta { font-size: 8pt; }
  a { color: inherit !important; text-decoration: none !important; }
}
@media (max-width: 800px) {
  .gl-wrap { grid-template-columns: 1fr; } .gl-rail { position: static; }
  .gl-create-grid, .gl-quad-grid, .gl-monitor-grid { grid-template-columns: 1fr; }
}
"""


def reporter_watch_guide():
    """Explain the stage monitor checkbox before students meet reporter blocks."""
    if i18n.LOCALE != "en":
        return ""
    return """<aside class="gl-monitor" id="watching-reporter-values">
      <h2>Watching a value in the mBlock IDE</h2>
      <p>Some rounded value blocks have a small checkbox beside them in the
      Blocks drawer. Checking it creates a <b>monitor</b>: a small readout in the
      top-left of the mBlock stage, the white area containing the Panda. The
      readout shows the value currently reported by that block and updates while
      mBlock can read it.</p>
      <p>This is a testing and debugging display in the <b>IDE on the computer</b>.
      It is not shown on the CyberPi’s physical screen and it is not added to the
      uploaded robot program. Hardware readings normally require the device to be
      connected while testing in Live mode. Clear the checkbox to remove the
      monitor from the stage.</p>
      <div class="gl-monitor-grid">
        <div class="gl-monitor-step">
          <img src="assets/ui/reporter-monitor-checkbox.png" alt="Checkbox beside the audio speed reporter block in mBlock">
          <p><b>1.</b> Check the box beside a watchable value block in its drawer.</p>
        </div>
        <div class="gl-monitor-step">
          <img src="assets/ui/reporter-monitor-stage.png" alt="Audio speed monitor at the top-left of the mBlock stage beside the Panda">
          <p><b>2.</b> Its named monitor appears at the top-left of the IDE stage and displays the current value.</p>
        </div>
      </div>
    </aside>"""


def mode_intro_guide():
    """The execution-model distinction needed before reading any block reference."""
    if i18n.LOCALE != "en":
        return ""
    return """<section class="gl-mini" id="live-versus-upload-mode">
      <h3>Before programming: Live Mode versus Upload Mode</h3>
      <p>The mode switch in mBlock decides <b>where the program runs</b>. It is
      not merely a different way to send the same program.</p>
      <table><thead><tr><th></th><th>Live Mode</th><th>Upload Mode</th></tr></thead><tbody>
        <tr><td><b>Where code runs</b></td><td>On the computer; commands are sent to the connected robot.</td><td>On the CyberPi inside the robot.</td></tr>
        <tr><td><b>Connection</b></td><td>The robot must remain connected and mBlock must stay open.</td><td>After uploading, the cable and computer can be disconnected.</td></tr>
        <tr><td><b>How it starts</b></td><td>The IDE’s green flag, keyboard events or clicking a script can start it.</td><td><b>when CyberPi starts up</b> and the robot’s buttons or sensors start scripts.</td></tr>
        <tr><td><b>Where output appears</b></td><td>The IDE stage can show Panda, variables and reporter monitors.</td><td>Use the physical CyberPi screen, LEDs and speaker.</td></tr>
        <tr><td><b>Best for</b></td><td>Quick desk tests and watching values while connected.</td><td>An autonomous robot that drives away from the computer.</td></tr>
      </tbody></table>
      <p><b>This course normally uses Upload Mode.</b> Uploading translates the
      blocks, replaces the previous program stored on the CyberPi, and restarts
      it. The robot can then run by itself. Entries marked <b>Live Mode Only</b>
      rely on the computer or its IDE stage and are exceptions.</p>
      <div class="gl-flow">Live = the computer directs the robot now<br>Upload = give the robot the whole program, then let it work alone</div>
    </section>"""


def variable_creation_guide():
    """The Variables drawer has buttons, not blocks, until the first item exists."""
    if i18n.LOCALE != "en":
        return ""
    return """<div class="gl-create">
      <h3>Before using these blocks: create a variable or list</h3>
      <p>A variable stores one value. A list stores several values in numbered order.</p>
      <div class="gl-create-grid">
        <div class="gl-create-step">
          <img src="assets/ui/make-variable-list.png" alt="Make a Variable and Make a List buttons">
          <p><b>1.</b> Open the <b>Variables</b> drawer. Click <b>Make a Variable</b>
          or <b>Make a List</b>, depending on what you need to store.</p>
        </div>
        <div class="gl-create-step">
          <img src="assets/ui/new-variable.png" alt="New Variable dialog in mBlock">
          <p><b>2.</b> Enter a clear variable name. Choose <b>For all sprites</b>
          to share it, or <b>For this sprite only</b> to keep it inside the current
          sprite. Then click <b>OK</b>.</p>
        </div>
        <div class="gl-create-step">
          <img src="assets/ui/new-list.png" alt="New List dialog in mBlock">
          <p><b>3.</b> Lists are created the same way: enter a name, choose its
          scope, and click <b>OK</b>. mBlock then adds blocks carrying that name
          to the Variables drawer.</p>
        </div>
      </div>
    </div>"""


def quad_rgb_guide():
    """Decode the menus that make the Quad RGB blocks look more complex."""
    if i18n.LOCALE != "en":
        return ""
    return """<div class="gl-quad" id="quad-rgb-values-guide">
      <h3>Guide: choosing values in Quad RGB Sensor blocks</h3>
      <p>Read each long block as a sequence of choices: <b>which sensor module →
      which probe(s) → what to detect or measure → which result to test.</b></p>

      <h4>1. Sensor number: 1–8</h4>
      <p>The first number identifies a Quad RGB Sensor in an mBuild chain. It does
      not select one of its four probes. This course has one Quad RGB Sensor, so
      leave it at <b>1</b>; 2–8 are for additional modules.</p>

      <h4>2. Probe: R2, R1, L1 or L2</h4>
      <p>Left and right are from the robot’s point of view as it drives forward.
      The menu numbers count from the outer-right probe toward the left:</p>
      <div class="gl-probes"><span>(4) L2</span><span>(3) L1</span><span>(2) R1</span><span>(1) R2</span></div>
      <p>The middle probes L1 and R1 normally straddle the line. L2 and R2 help
      detect larger drift, wide bands and junctions.</p>

      <h4>3. Detection choices</h4>
      <table><thead><tr><th>Choice</th><th>Meaning</th></tr></thead><tbody>
        <tr><td><b>line / background</b></td><td>The <b>line</b> is the path the robot follows; the <b>background</b> is the surrounding track surface. With black tape on white paper, black is the line and white is the background. These are surface categories learned during calibration, not colours named in the block.</td></tr>
        <tr><td><b>white, red, yellow, green, cyan, blue, purple, black</b></td><td>A yes-or-no test for a built-in colour.</td></tr>
        <tr><td><b>self-defined color</b></td><td>The custom RGB colour and tolerance previously taught with the “define color” block.</td></tr>
      </tbody></table>

      <h4>Calibration defines “line” and “background”</h4>
      <p>Calibration is an action performed before line detection. Start it by
      double-pressing the button on the Quad RGB Sensor, or by running the
      <b>“quad rgb sensor 1 performs calibration”</b> command block. While it is
      calibrating, move the sensor across both the line and the surrounding
      background. It measures and stores the difference; later blocks use those
      stored values whenever they ask about <b>line</b> or <b>background</b>.</p>
      <p>Calibrate again when the track, room lighting, sensor height or fill-light
      setting changes. Without a suitable calibration, the sensor may confuse the
      two surfaces.</p>

      <h4>4. Measurement choices</h4>
      <table><thead><tr><th>Choice</th><th>Returned value</th></tr></thead><tbody>
        <tr><td><b>object’s R / G / B value</b></td><td>Red, green or blue intensity from 0 to 255.</td></tr>
        <tr><td><b>object’s grayscale</b></td><td>Reflected-light strength from 0 to 100, independent of a colour name.</td></tr>
        <tr><td><b>ambient light intensity</b></td><td>Light reaching the probe, from 0 to 100. The fill light contributes unless turned off.</td></tr>
        <tr><td><b>color</b></td><td>The measured colour as hexadecimal RGB, from <code>0x000000</code> to <code>0xFFFFFF</code>.</td></tr>
      </tbody></table>

      <h4>5. Status codes</h4>
      <p>Each digit belongs to one probe. <b>1</b> means it detects the condition
      selected in the block; <b>0</b> means it does not. The middle-pair order is
      <b>L1 R1</b>, so <code>10</code> means L1 yes and R1 no. The four-probe order
      is <b>L2 L1 R1 R2</b>, so <code>0110</code> means the two middle probes detect
      it and the outer probes do not. Two probes have 4 possible patterns; four
      probes have all 16 patterns from <code>0000</code> to <code>1111</code>.</p>

      <h4>6. Fill-light colour</h4>
      <p>The sensor shines red, green or blue light onto the floor before reading
      the reflection. This is illumination, not a detected colour. Changing it can
      improve contrast, but also changes readings—calibrate under the same light
      and surface conditions in which the robot will run.</p>

      <div class="gl-quad-grid">
        <div class="gl-quad-shot"><img src="assets/ui/quad-rgb-sensor-number-menu.png" alt="Sensor number menu, 1 through 8"><p><b>Sensor number:</b> choose the module; this course uses 1.</p></div>
        <div class="gl-quad-shot"><img src="assets/ui/quad-rgb-probe-menu.png" alt="Probe menu showing R2, R1, L1 and L2"><p><b>Probe:</b> choose one of the four sensing positions.</p></div>
        <div class="gl-quad-shot"><img src="assets/ui/quad-rgb-target-menu.png" alt="Target menu with line, background and colours"><p><b>Detection target:</b> ask about line/background or a colour.</p></div>
        <div class="gl-quad-shot"><img src="assets/ui/quad-rgb-measurement-menu.png" alt="Measurement menu with RGB, grayscale, ambient light and color"><p><b>Measurement:</b> report a value instead of yes or no.</p></div>
        <div class="gl-quad-shot"><img src="assets/ui/quad-rgb-pair-status-menu.png" alt="Two-probe choices 00, 01, 10 and 11"><p><b>Middle pair:</b> digits are L1 then R1.</p></div>
        <div class="gl-quad-shot"><img src="assets/ui/quad-rgb-four-status-menu.png" alt="Four-probe choices from 0000 through 1111"><p><b>All four:</b> digits are L2, L1, R1, R2.</p></div>
        <div class="gl-quad-shot"><img src="assets/ui/quad-rgb-fill-light-menu.png" alt="Fill-light menu with red, green and blue"><p><b>Fill light:</b> choose the light shone onto the surface.</p></div>
      </div>
    </div>"""


def sprite_mini_course():
    """Conceptual introduction before the CyberPi sprite block reference."""
    if i18n.LOCALE != "en":
        return ""
    return """<div class="gl-mini" id="sprite-mini-course">
      <h3>Mini-course: what is a sprite?</h3>
      <p>A <b>sprite</b> is a named visual object that a program can control
      independently. It can be text, a built-in icon, a picture drawn on a pixel
      grid, or a QR code. Unlike ordinary printed text, a sprite remembers its
      own position and appearance.</p>

      <h4>Which screen?</h4>
      <p>The blocks in this <b>Sprites</b> drawer create sprites on the
      <b>CyberPi’s physical 128×128 screen</b>. They do not create or move the
      Panda on the mBlock IDE stage. The separate “follow mBlock sprite” sensing
      block is an exception that explicitly refers to an IDE-stage sprite.</p>

      <img class="gl-ide-image gl-wide" src="assets/ui/cyberpi-sprites-concept.svg"
           alt="Three independent named sprites on the CyberPi screen">

      <h4>Why use sprites?</h4>
      <p>Suppose a game screen contains a score, a moving spaceship and a target.
      With printed text, redrawing one item can disturb the others. With sprites,
      the program can move <b>ship</b>, recolour <b>target</b>, and replace the
      text in <b>score</b> independently. Sprites are useful for games, gauges,
      arrows, status icons and small animated interfaces.</p>

      <h4>The basic workflow</h4>
      <table><thead><tr><th>Step</th><th>What the program does</th></tr></thead><tbody>
        <tr><td><b>1. Create and name</b></td><td>Use a “set sprite … show to …” block. The name—such as <code>ship</code>—is how later blocks find that same object.</td></tr>
        <tr><td><b>2. Position</b></td><td>Place it at an x and y coordinate, or move it by a number of pixels.</td></tr>
        <tr><td><b>3. Change</b></td><td>Rotate it, resize it, recolour it, flip it or change its layer.</td></tr>
        <tr><td><b>4. Interact</b></td><td>Ask whether it touches another sprite or the edge—useful for games.</td></tr>
        <tr><td><b>5. Hide or delete</b></td><td>Hide keeps the sprite ready to show again; delete removes it.</td></tr>
      </tbody></table>

      <h4>Names connect the blocks</h4>
      <div class="gl-flow">create sprite “ship” → move sprite “ship” → rotate sprite “ship” → hide sprite “ship”</div>
      <p>Every block using the name <b>ship</b> acts on the same sprite. A block
      using the name <b>target</b> acts on a different one. Choose short,
      meaningful names so it is obvious which screen object each block controls.</p>
    </div>"""


def pin_mini_course():
    """Electrical context needed before the raw S1/S2 pin blocks make sense."""
    if i18n.LOCALE != "en":
        return ""
    return """<div class="gl-mini" id="digital-pin-mini-course">
      <h3>Mini-course: digital pins, voltage, high and low</h3>
      <p><b>Start with the connector.</b> S1 and S2 are multifunction ports on the
      mBot2 Shield. Each connector contains separate electrical contacts for
      power, ground and a signal. The raw pin blocks read or control the
      <em>signal</em> contact—not the whole connector.</p>

      <h4>Voltage needs a reference</h4>
      <p>Voltage is a difference between two electrical points. Here, the Shield
      compares the signal with ground. Ground is the reference called 0 V.</p>
      <table>
        <thead><tr><th>Signal state</th><th>Electrical situation</th><th>Digital reading</th></tr></thead>
        <tbody>
          <tr><td><b>Low</b></td><td>Signal is deliberately held near ground.</td><td>false / 0</td></tr>
          <tr><td><b>High</b></td><td>Signal is deliberately driven near the positive logic supply.</td><td>true / 1</td></tr>
          <tr><td><b>Floating</b></td><td>Signal is connected to neither ground nor a defined high level.</td><td>Unreliable; it may jump between states.</td></tr>
        </tbody>
      </table>
      <div class="gl-flow">ground → signal = low<br>power → signal = high<br>nothing → signal = floating, not “high”</div>

      <h4>A switch example</h4>
      <p>In a common <b>pull-down</b> circuit, a resistor holds the signal low while
      the switch is open. Closing the switch connects the signal to the positive
      supply, making it high. The resistor prevents the open signal from floating.</p>

      <h4>Sensors may reverse the meaning</h4>
      <p>An active-high sensor might output high when it detects an object. An
      <b>active-low</b> sensor outputs low when it detects one. Neither convention
      is universally correct: check that sensor’s documentation.</p>

      <h4>Writing sends a signal out</h4>
      <p><b>Digital write</b> drives the signal low (0) or high (1). It is like a
      software-controlled electrical switch: there is no middle setting.
      <b>Digital read</b> observes a signal coming in; digital write creates an
      output signal.</p>

      <h4>“Analog write” is rapid digital switching</h4>
      <p>On these blocks, analog write means <b>PWM</b> (pulse-width modulation).
      The output remains digital, but switches high and low quickly. The duty
      cycle says how much of each cycle is high; the frequency says how many
      cycles happen each second.</p>
      <table>
        <thead><tr><th>Duty cycle</th><th>Output pattern</th><th>Typical effect</th></tr></thead>
        <tbody>
          <tr><td>0%</td><td>Always low</td><td>Off</td></tr>
          <tr><td>50%</td><td>High half the time</td><td>About half average power</td></tr>
          <tr><td>100%</td><td>Always high</td><td>Fully on</td></tr>
        </tbody>
      </table>

      <h4>Two real output cases</h4>
      <p><b>Digital warning lamp:</b> a distance test can write 1 to switch an
      external warning LED on when an object is too close, then write 0 when the
      path is clear. The output has two intentional states: on or off.</p>
      <p><b>PWM night light:</b> analog write can use a low duty cycle for a dim
      night mode and 100% for a bright mode. The LED averages the fast pulses into
      visible brightness. Motors, relays and high-current lights require a proper
      driver circuit; never power them directly from a signal pin.</p>

      <h4>Course boundary and safety</h4>
      <p>These raw pin blocks are reference material; this course does not require
      custom S1/S2 circuits. Never guess a connector’s pin order or voltage. Wrong
      wiring can damage the external part or the Shield.</p>
    </div>"""

JS = """
(function () {
  var box = document.getElementById('glfind');
  var only = document.getElementById('glonly');
  function apply() {
    var q = box.value.trim().toLowerCase();
    var u = only.checked;
    document.querySelectorAll('.gl-b').forEach(function (el) {
      var hit = (!q || el.dataset.find.indexOf(q) >= 0) && (!u || el.dataset.used === '1');
      el.style.display = hit ? '' : 'none';
    });
    document.querySelectorAll('.gl-sec').forEach(function (sec) {
      var any = sec.querySelectorAll('.gl-b:not([style*="none"])').length;
      sec.style.display = any ? '' : 'none';
    });
  }
  box.addEventListener('input', apply);
  only.addEventListener('change', apply);
})();
"""


# The page's own furniture. Everything else on this page is authored; these are
# the labels the generator emits itself.
UI = {
    "en": {"title": "Block glossary", "what": "What it does",
           "when": "Use it when", "eg": "Example", "used": "Used in",
           "live_only": "Live mode only",
           "not_in_course": "Not in this course — hardware unavailable",
           "not_used": "Not used in this course",
           "see": "See also", "step": "G{g} step {n}", "find": "Search blocks…",
           "only": "only blocks the course uses", "todo": "Not written up yet.",
           "pdf": "Download printable PDF",
           "values": "Possible dropdown values", "menu_showing": "Menu shown as “{value}”",
           "lede": "Every block in the mBlock palette for this classroom\u2019s "
                   "robot \u2014 {n} of them \u2014 grouped the way the toolbox "
                   "groups them. Each one says what it does, when you would reach "
                   "for it, and shows a working example."},
    "km": {"title": "សទ្ទានុក្រមប្លុក", "what": "វាធ្វើអ្វី",
           "when": "ប្រើវានៅពេល", "eg": "ឧទាហរណ៍", "used": "ប្រើក្នុង",
           "live_only": "សម្រាប់តែរបៀប Live",
           "not_in_course": "មិនមានក្នុងវគ្គសិក្សានេះ — គ្មានឧបករណ៍",
           "not_used": "មិនប្រើក្នុងវគ្គសិក្សានេះ",
           "see": "មើលផងដែរ", "step": "ថ្នាក់ទី {g} ជំហាន {n}",
           "find": "ស្វែងរកប្លុក…",
           "only": "តែប្លុកដែលវគ្គសិក្សាប្រើ", "todo": "មិនទាន់សរសេរនៅឡើយ។",
           "pdf": "ទាញយក PDF សម្រាប់បោះពុម្ព",
           "values": "តម្លៃដែលអាចជ្រើសបាន", "menu_showing": "ម៉ឺនុយបង្ហាញជា «{value}»",
           "lede": "គ្រប់ប្លុកក្នុងផ្ទាំងឧបករណ៍ mBlock សម្រាប់រូបយន្តរបស់ថ្នាក់នេះ "
                   "\u2014 សរុប {n} \u2014 ចាត់ជាក្រុមតាមរបៀបដែលផ្ទាំងឧបករណ៍ចាត់។ "
                   "ប្លុកនីមួយៗប្រាប់ថាវាធ្វើអ្វី ពេលណាដែលអ្នកគួរប្រើវា "
                   "និងបង្ហាញឧទាហរណ៍ដែលដំណើរការ។"},
}


def ui(key, **kw):
    """A UI string for this locale. Counters go through i18n.num(), so a grade
    and a step number are written in Khmer numerals on the Khmer page, the same
    as everywhere else on that site."""
    text = UI.get(i18n.LOCALE, UI["en"]).get(key) or UI["en"][key]
    return text.format(**{k: i18n.num(v) for k, v in kw.items()}) if kw else text


def esc(t):
    return render.esc(t)


def _para(text):
    return "".join(f"<p>{esc(p.strip())}</p>"
                   for p in re.split(r"\n\s*\n", (text or "").strip()) if p.strip())


def _compact_options(options):
    """Keep long consecutive integer menus complete without printing every chip."""
    vals = [str(v) for v in options]
    first_number = next((i for i, value in enumerate(vals)
                         if re.fullmatch(r"\d+", value)), len(vals))
    prefix, number_vals = vals[:first_number], vals[first_number:]
    if not number_vals or any(not re.fullmatch(r"\d+", value)
                              for value in number_vals):
        return vals
    numeric = [int(value) for value in number_vals]
    if len(numeric) >= 8 and numeric == list(range(numeric[0], numeric[-1] + 1)):
        return prefix + [f"{numeric[0]}–{numeric[-1]} (every whole number)"]
    return vals


def dropdown_values(spec):
    """Render fixed choices recorded in mBlock's palette for this block."""
    rows = []
    for slot in spec.get("slots") or []:
        options = ((spec.get("menus") or {}).get(slot)
                   or S._MENU_BY_SLOT.get((spec.get("ext"), slot)))
        if not options:
            continue
        values = _compact_options(options)
        shown = str(options[0])
        chips = " ".join(f'<span class="gl-value">{esc(v)}</span>' for v in values)
        rows.append(f'<dt>{esc(ui("menu_showing", value=shown))}</dt><dd>{chips}</dd>')
    if not rows:
        return ""
    return (f'<div class="gl-values"><div class="gl-values-title">'
            f'{esc(ui("values"))}</div><dl>{"".join(rows)}</dl></div>')


def block_entry(key, label, spec, entry, used_in, by_label):
    entry = entry or {}
    svg = S.render_blank(spec, mm_per_px=BLOCK_MM)
    live_only = bool(re.search(r"\b(?:only in live mode|live mode only)\b",
                               entry.get("when") or "", re.I))
    badge = (f'<span class="gl-mode-badge">{ui("live_only")}</span>'
             if live_only else "")
    hardware_unavailable = key.startswith("mbot2.mbot2_led_")
    not_used = key == "cyberpi.cyberpi_makex_mode"
    outside_course = hardware_unavailable or not_used
    badge_text = ui("not_in_course") if hardware_unavailable else ui("not_used")
    course_badge = (f'<span class="gl-course-badge">{badge_text}</span>'
                    if outside_course else "")
    body = [f'<h3>{esc(label)}</h3>' if False else "", course_badge, badge, svg]
    if entry.get("what"):
        body.append(f'<div class="gl-l">{ui("what")}</div>' + _para(entry["what"]))
    else:
        body.append(f'<p class="gl-none">{ui("todo")}</p>')
    body.append(dropdown_values(spec))
    if entry.get("ide_image"):
        image_class = ("gl-ide-image gl-wide" if entry.get("ide_image_wide") else
                       "gl-ide-image gl-medium" if entry.get("ide_image_medium") else
                       "gl-ide-image")
        image_html = (f'<img class="{image_class}" src="{esc(entry["ide_image"])}" '
                      f'alt="{esc(entry.get("ide_image_alt") or "")}">')
        if entry.get("ide_image_caption"):
            source = (f' <a href="{esc(entry["ide_image_source"])}">Source: Makeblock</a>.'
                      if entry.get("ide_image_source") else "")
            image_html += (f'<p class="gl-image-cap">'
                           f'{esc(entry["ide_image_caption"])}{source}</p>')
        body.append(image_html)
    if entry.get("when"):
        body.append(f'<div class="gl-l">{ui("when")}</div>' + _para(entry["when"]))
    if entry.get("example"):
        cap = (f'<p class="cap">{esc(entry["caption"])}</p>'
               if entry.get("caption") else "")
        body.append(f'<div class="gl-l">{ui("eg")}</div>'
                    f'<div class="gl-eg">'
                    f'{S.render(entry["example"], mm_per_px=BLOCK_MM)}{cap}</div>')
    if entry.get("watch"):
        body.append('<div class="gl-warn">' + _para(entry["watch"]) + "</div>")

    meta = []
    if used_in:
        links = ", ".join(
            f'<a href="grade{g}/step-{n:02d}.html">{ui("step", g=g, n=n)}</a>'
            for g, n, _t in used_in[:6])
        meta.append(f'<span class="gl-used"></span>{ui("used")} {links}')
    see = [(o, by_label[o]) for o in (entry.get("see") or []) if o in by_label]
    if see:
        meta.append(ui("see") + " "
                    + ", ".join(
                        f'<a class="gl-see" href="#block-{esc(o)}">{esc(label)}</a>'
                        for o, label in see))
    if meta:
        body.append('<div class="gl-meta">' + " &middot; ".join(meta) + "</div>")

    hay = esc((label + " " + (entry.get("what") or "") + " "
               + (entry.get("when") or "")).lower())
    unused_class = " gl-unused" if outside_course else ""
    return (f'<div class="gl-b{unused_class}" id="block-{esc(key)}" data-find="{hay}" '
            f'data-used="{"1" if used_in else "0"}">' + "".join(body) + "</div>")


def build(out_path=None):
    pal = palette()
    have = words()
    used = usage()
    by_label = {k: l for _c, _o, k, l, _s in pal}

    cats = []
    for cate, _o, _k, _l, _s in pal:
        if not cats or cats[-1][0] != cate:
            cats.append([cate, 0, _s.get("cateColor") or "#94a3b8"])
        cats[-1][1] += 1

    rail = [f'<input class="gl-find" id="glfind" type="search" '
            f'placeholder="{esc(ui("find"))}" autocomplete="off">',
            '<label class="gl-only"><input type="checkbox" id="glonly"> '
            f'{esc(ui("only"))}</label>']
    for cate, n, colour in cats:
        rail.append(f'<a href="#{_slug(cate)}"><span class="gl-dot" '
                    f'style="background:{esc(colour)}"></span>{esc(cate)}<b>{n}</b></a>')

    main, last = [mode_intro_guide(), reporter_watch_guide()], None
    for cate, _o, key, label, spec in pal:
        if cate != last:
            if last is not None:
                main.append("</section>")
            colour = spec.get("cateColor") or "#94a3b8"
            intro = CATE_INTRO.get(i18n.LOCALE, CATE_INTRO["en"]).get(cate) \
        or CATE_INTRO["en"].get(cate, "")
            main.append(f'<section class="gl-sec" id="{_slug(cate)}">'
                        f'<div class="gl-cat" style="--c:{esc(colour)}">'
                        f"<h2>{esc(cate)}</h2>"
                        + (f"<p>{esc(intro)}</p>" if intro else "") + "</div>"
                        + (variable_creation_guide() if cate == "Variables" else "")
                        + (quad_rgb_guide() if cate == "Quad RGB Sensor" else "")
                        + (sprite_mini_course() if cate == "Sprites" else ""))
            last = cate
        if key == "mbot2.mbot2_pin_write_digtial":
            main.append(pin_mini_course())
        main.append(block_entry(key, label, spec, have.get(key),
                                used.get(key), by_label))
    if last is not None:
        main.append("</section>")

    n_written = sum(1 for _c, _o, k, _l, _s in pal if have.get(k, {}).get("what"))
    head = (f"<h1>{esc(ui('title'))}</h1>"
            f'<p class="lede">{esc(ui("lede", n=len(pal)))}</p>')
    glossary_nav = ('<div class="chrome"><span class="spacer"></span>'
                    f'<a class="glossary-pdf" href="glossary.pdf" download>'
                    f'{ui("pdf")}</a>'
                    f'<a class="glossary-link" href="glossary.html" target="_blank" '
                    f'rel="noopener noreferrer">{i18n.t("glossary_new_tab")}</a>'
                    f'{render.lang_toggle("glossary.html")}</div>')
    body = (glossary_nav
            + head + '<div class="gl-wrap"><nav class="gl-rail">'
            + "".join(rail) + "</nav><div>" + "".join(main) + "</div></div>"
            + f"<script>{JS}</script>")
    # The glossary belongs to no single grade, so it borrows Grade 7's palette
    # and passes num="" — render.css() drops the grade segment from the footer.
    theme = dict(render.grade_c(yaml.safe_load(
        (ROOT / "content" / "grade7" / "grade.yaml").read_text(encoding="utf-8"))),
        num="")
    html = render.page(ui("title"), render.css(theme), body,
                       extra_head=f"<style>{S.CSS}{CSS}</style>")
    if out_path:
        pathlib.Path(out_path).write_text(html, encoding="utf-8")
    return html, n_written, len(pal)


def _slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


if __name__ == "__main__":
    import sys
    a = audit()
    print(f"  {a['written']}/{a['total']} blocks written up")
    if a["broken"]:
        print(f"  {len(a['broken'])} example lines do not resolve:")
        for k, t in a["broken"][:20]:
            print(f"      {k}: {t!r}")
    if a["orphan"]:
        print(f"  {len(a['orphan'])} entries for blocks not in the palette: "
              f"{a['orphan'][:6]}")
    if "--missing" in sys.argv:
        for k in a["missing"]:
            print("   ", k)
