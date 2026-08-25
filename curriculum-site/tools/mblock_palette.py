# -*- coding: utf-8 -*-
"""Build an authoritative block catalogue from mBlock's own app bundle.

Two sources, both inside /Applications/mBlock.app -> Resources/app.asar:

  packages/renderer/dist/mblock/langs.zip -> en/<ext>.json
      What the palette *reads*: the label template with [SLOT] placeholders, and
      one entry per menu option.
  packages/renderer/dist/mblock/exts.zip  -> <ext>/src/cates/*/{blocks.js,index.js}
      What the palette *is*: every block's blockType, branchCount and typed
      argument list, plus each menu's option list as {text: <i18n key>,
      value: <what goes in the file>}.

The second source is the one that matters when writing a .mblock. A slot is not
a slot: `type: "image"` is a decorative icon that must not be emitted at all,
`fieldMenu` becomes a `fields` entry, `inputMenu` becomes an input pointing at a
shadow menu block — and the value written is the menu's `value`, not the label
the palette shows. Guessing any of that from the label alone was how
tools/mblock_compile.py came to emit files mBlock would not open.

Emits reference/mblock-palette.json:
  {opcode: {ext, opcode, template, slots, menus:{slot:[label]},
            args:{slot:{type, default, menu}}, options:{slot:[[label, value]]},
            blockType, branchCount, cate, cateName, cateColor, alsoIn, hidden,
            order}}

`cate`/`cateName`/`cateColor` and `hidden`/`order` describe the toolbox: which
drawer a block sits in, what that drawer is called and coloured, and where in it
the block appears. `hidden` blocks are superseded variants mBlock still loads for
old projects but no longer offers. `alsoIn` is present only on the handful of
blocks a second drawer offers as well -- the Wi-Fi four, which head AI and IoT
alike -- and holds the same three fields for each of those extra drawers.

Usage: .venv/bin/python tools/mblock_palette.py [--app /path/to/mBlock.app]
"""
import io
import json
import re
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = Path("/Applications/mBlock.app")
OUT = ROOT / "reference" / "mblock-palette.json"

# The extensions a CyberPi + mBot2 (+ Rover add-on) classroom actually loads.
# bluetooth_controller is where the gamepad blocks live — `joystick [LY]` and
# `button [R2] pressed`, which Grade 8's "connects" project is built on.
# firefly_bluetoothcontroller is the Bluetooth Controller that WORKS: unlike the
# bundled `bluetooth_controller` device, its blocks carry MicroPython
# (gamepad.get_joystick / gamepad.is_key_pressed) so they survive an upload.
# mBlock declares it in a project as the extension id `firefly`.
EXTS = ["cyberpi", "mbot2", "mbuild", "mbuild_quad_color_sensor",
        "firefly_bluetoothcontroller",
        "cyberpi_mbuild_ultrasonic2", "cyberpi_upload_message", "cyberpi_sprite",
        "cyberpi_ai_emotion"]

# 21 extensions ship an English lang file but no `<ext>/src/cates/` in exts.zip —
# mBlock downloads those on demand, so there are no definitions to scrape and the
# drawer they belong to has to be stated. Labels still come from langs.zip, and
# the OPCODE_SLOT_N fallback still recovers their menus.
DOWNLOADED_CATE = {
    "cyberpi_ai_emotion": ("Magic emoji", "#613bb0"),   # colour read off the app
}

# Keys in a downloaded extension's lang file that read like blocks but are not:
# mBlock's flyout also holds buttons that open a modal. With no definitions,
# nothing distinguishes such a button from a block, so they are named here.
NOT_BLOCKS = {
    "cyberpi_ai_emotion": {"BLOCK_1710138113343"},      # "AI Emoji Workshop" button
}
# NOT `bluetooth_controller`: the bundled device and the firefly extension declare
# IDENTICAL templates (`joystick[AXIS]`, `button [AXIS] pressed`), so having both
# in the palette makes resolution a coin toss -- and the device's blocks compile
# to nothing. Only the working one is offered.

# Core (non-extension) blocks. Labels come from langs/en/mblock.json, which uses
# %1-style placeholders; opcode names were confirmed by grepping the app bundles,
# so control_for_new / control_break are the product's real names, not guesses.
# A label in mblock.json is NOT proof the palette offers the block. mBlock
# declares what the toolbox shows as `{basic:!0, opcode, msgid, hidden:!1}`;
# `control_for_each` (`for each () in ()`) and `control_while` have a label and a
# handler but no such declaration — they exist only in the interpreter's dispatch
# table and in the Scratch-2 import map, for opening old .sb2 projects. Putting
# them in the catalogue produced a block image of something no student can find.
CORE_FROM_MBLOCK = {
    "CONTROL_FOR":   ("control_for_new", "control", ["VARIABLE", "START", "END", "STEP"]),
    # NOT control_break / control_continue. mBlock's own definitions carry the
    # "_new" suffix — `{opcode:"control_break_new", msgid:"CONTROL_BREAK"}` in
    # app.asar, and the interpreter dispatches control_break_new -> breakRepeat.
    # The unsuffixed guesses compiled fine and then opened in the editor as a red
    # "undefined: control_break", because nothing defines that opcode.
    "CONTROL_BREAK": ("control_break_new", "control", []),
    "CONTROL_CONTINUE": ("control_continue_new", "control", []),
}

# Stable sb3 opcodes, every one observed in the official lesson files. The list
# blocks are Scratch core and so are absent from exts.zip; their argument types
# are read off real files instead — a list index is math_integer (shadow type 7),
# not math_number, which is what mBlock writes when you drag one in.
CORE = {
    "control_forever":      ("control", "forever", [], {}),
    "control_repeat":       ("control", "repeat [TIMES]", ["TIMES"], {}),
    "control_if":           ("control", "if [CONDITION] then", ["CONDITION"], {}),
    "control_if_else":      ("control", "if [CONDITION] then else", ["CONDITION"], {}),
    "control_wait":         ("control", "wait [DURATION] seconds", ["DURATION"], {}),
    "control_wait_until":   ("control", "wait until [CONDITION]", ["CONDITION"], {}),
    "control_repeat_until": ("control", "repeat until [CONDITION]", ["CONDITION"], {}),
    "control_stop":         ("control", "stop [STOP_OPTION]", ["STOP_OPTION"],
                             {"STOP_OPTION": ["all", "this script", "other scripts in sprite"]}),
    "operator_add":      ("operators", "[NUM1] + [NUM2]", ["NUM1", "NUM2"], {}),
    "operator_subtract": ("operators", "[NUM1] - [NUM2]", ["NUM1", "NUM2"], {}),
    "operator_multiply": ("operators", "[NUM1] * [NUM2]", ["NUM1", "NUM2"], {}),
    "operator_divide":   ("operators", "[NUM1] / [NUM2]", ["NUM1", "NUM2"], {}),
    "operator_mod":      ("operators", "[NUM1] mod [NUM2]", ["NUM1", "NUM2"], {}),
    "operator_round":    ("operators", "round [NUM]", ["NUM"], {}),
    "operator_random":   ("operators", "pick random [FROM] to [TO]", ["FROM", "TO"], {}),
    "operator_lt":       ("operators", "[OPERAND1] < [OPERAND2]", ["OPERAND1", "OPERAND2"], {}),
    "operator_gt":       ("operators", "[OPERAND1] > [OPERAND2]", ["OPERAND1", "OPERAND2"], {}),
    "operator_equals":   ("operators", "[OPERAND1] = [OPERAND2]", ["OPERAND1", "OPERAND2"], {}),
    "operator_and":      ("operators", "[OPERAND1] and [OPERAND2]", ["OPERAND1", "OPERAND2"], {}),
    "operator_or":       ("operators", "[OPERAND1] or [OPERAND2]", ["OPERAND1", "OPERAND2"], {}),
    "operator_not":      ("operators", "not [OPERAND]", ["OPERAND"], {}),
    "operator_join":     ("operators", "join [STRING1] [STRING2]", ["STRING1", "STRING2"], {}),
    "operator_letter_of":("operators", "letter [LETTER] of [STRING]", ["LETTER", "STRING"], {}),
    "operator_length":   ("operators", "length of [STRING]", ["STRING"], {}),
    "operator_contains": ("operators", "[STRING1] contains [STRING2]?", ["STRING1", "STRING2"], {}),
    "data_setvariableto":  ("variables", "set [VARIABLE] to [VALUE]", ["VARIABLE", "VALUE"], {}),
    "data_changevariableby":("variables", "change [VARIABLE] by [VALUE]", ["VARIABLE", "VALUE"], {}),
    "data_addtolist":      ("variables", "add [ITEM] to [LIST]", ["ITEM", "LIST"], {}),
    "data_deleteoflist":   ("variables", "delete [INDEX] of [LIST]", ["INDEX", "LIST"], {}),
    "data_deletealloflist":("variables", "delete all of [LIST]", ["LIST"], {}),
    "data_insertatlist":   ("variables", "insert [ITEM] at [INDEX] of [LIST]", ["ITEM", "INDEX", "LIST"], {}),
    "data_replaceitemoflist":("variables", "replace item [INDEX] of [LIST] with [ITEM]", ["INDEX", "LIST", "ITEM"], {}),
    "data_itemoflist":     ("variables", "item [INDEX] of [LIST]", ["INDEX", "LIST"], {}),
    "data_itemnumoflist":  ("variables", "item # of [ITEM] in [LIST]", ["ITEM", "LIST"], {}),
    "data_lengthoflist":   ("variables", "length of [LIST]", ["LIST"], {}),
    "data_listcontainsitem":("variables", "[LIST] contains [ITEM]?", ["LIST", "ITEM"], {}),
    # Scratch-core blocks that sit in cyberpi's own control/data/events/operators
    # drawers but take their wording from mblock.json rather than the extension
    # lang file, so the scrape above never sees them. Templates copied verbatim
    # from en/mblock.json, with %1/%2 written as named slots.
    "event_whenflagclicked": ("events", "when green flag clicked", [], {}),
    "event_whenkeypressed": ("events", "when [KEY_OPTION] key pressed", ["KEY_OPTION"],
                             {"KEY_OPTION": ["space", "up arrow", "down arrow",
                                             "right arrow", "left arrow", "any"]}),
    "event_whenbroadcastreceived": ("events", "when I receive [BROADCAST_OPTION]",
                                    ["BROADCAST_OPTION"], {}),
    "event_broadcast":        ("events", "broadcast [BROADCAST_INPUT]", ["BROADCAST_INPUT"], {}),
    "event_broadcastandwait": ("events", "broadcast [BROADCAST_INPUT] and wait",
                               ["BROADCAST_INPUT"], {}),
    "data_showvariable":  ("variables", "show variable [VARIABLE]", ["VARIABLE"], {}),
    "data_hidevariable":  ("variables", "hide variable [VARIABLE]", ["VARIABLE"], {}),
    "data_showlist":      ("variables", "show list [LIST]", ["LIST"], {}),
    "data_hidelist":      ("variables", "hide list [LIST]", ["LIST"], {}),
    "operator_mathop":    ("operators", "[OPERATOR] of [NUM]", ["OPERATOR", "NUM"],
                           {"OPERATOR": ["abs", "floor", "ceiling", "sqrt", "sin",
                                         "cos", "tan", "asin", "acos", "atan",
                                         "ln", "log", "e ^", "10 ^"]}),
    # NOT data_variable. Its template is the bare slot `[VARIABLE]`, which would
    # match any text at all and make M.resolve() hand arbitrary source lines to a
    # variable reporter. The palette is a resolver as well as a catalogue.
    "procedures_definition":("myblocks", "define [PROC]", ["PROC"], {}),
    "procedures_call":      ("myblocks", "[PROC]", ["PROC"], {}),
}

# Argument types for the core blocks, in the same vocabulary exts.zip uses.
CORE_ARGS = {
    "data_setvariableto": {"VARIABLE": "fieldVariable", "VALUE": "string"},
    "data_changevariableby": {"VARIABLE": "fieldVariable", "VALUE": "number"},
    "data_addtolist": {"ITEM": "string", "LIST": "fieldList"},
    "data_deleteoflist": {"INDEX": "integer", "LIST": "fieldList"},
    "data_deletealloflist": {"LIST": "fieldList"},
    "data_insertatlist": {"ITEM": "string", "INDEX": "integer", "LIST": "fieldList"},
    "data_replaceitemoflist": {"INDEX": "integer", "LIST": "fieldList", "ITEM": "string"},
    "data_itemoflist": {"INDEX": "integer", "LIST": "fieldList"},
    "data_itemnumoflist": {"ITEM": "string", "LIST": "fieldList"},
    "data_lengthoflist": {"LIST": "fieldList"},
    "data_listcontainsitem": {"LIST": "fieldList", "ITEM": "string"},
    "event_whenkeypressed": {"KEY_OPTION": "fieldMenu"},
    "event_whenbroadcastreceived": {"BROADCAST_OPTION": "fieldMenu"},
    "event_broadcast": {"BROADCAST_INPUT": "string"},
    "event_broadcastandwait": {"BROADCAST_INPUT": "string"},
    "data_showvariable": {"VARIABLE": "fieldVariable"},
    "data_hidevariable": {"VARIABLE": "fieldVariable"},
    "data_showlist": {"LIST": "fieldList"},
    "data_hidelist": {"LIST": "fieldList"},
    "operator_mathop": {"OPERATOR": "fieldMenu", "NUM": "number"},
    "control_repeat": {"TIMES": "integer"},
    "control_wait": {"DURATION": "positive"},
    "control_for_new": {"VARIABLE": "fieldVariable", "START": "number",
                        "END": "number", "STEP": "number"},
}

# Display name and toolbox colour for the Scratch-core categories.
CORE_CATE = {"data":      ("Variables", "#FF8C1A"),
             "control":   ("Control",   "#FFAB19"),
             "operators": ("Operators", "#59C059"),
             "variables": ("Variables", "#FF8C1A"),
             "myblocks":  ("My Blocks", "#FF6680"),
             "events":    ("Events",    "#FFBF00")}

SLOT = re.compile(r"\[([A-Za-z_0-9]+)\]")
GENERATED = re.compile(r"^BLOCK_\d+$")
PCT = re.compile(r"%(\d+)")


# ------------------------------------------------------------------ app.asar
def asar_member(app, member):
    """One file out of an Electron asar archive, as bytes."""
    path = app / "Contents" / "Resources" / "app.asar"
    with open(path, "rb") as f:
        f.read(12)                                   # pickle framing
        hdr = json.loads(f.read(struct.unpack("<I", f.read(4))[0]).decode("utf-8"))
        base = f.tell()
        node = hdr
        for part in member.split("/"):
            node = node["files"][part]
        f.seek(base + int(node["offset"]))
        return f.read(node["size"])


def asar_zip(app, member):
    return zipfile.ZipFile(io.BytesIO(asar_member(app, member)))


# ------------------------------------------------------- tolerant JS scraping
# blocks.js and index.js are ES modules, not JSON: they call
# window.MbApi.getExtResPath(...) for icons and reference this.funcs.* for
# handlers. Only two islands inside them are wanted — a block's `arguments`
# object and a category's `menus` object — and both are plain JSON once the
# function calls are blanked out. Scanning for balanced braces is enough; a
# parser for the whole module would be a lot of machinery for two keys.
_CALL = re.compile(r"window\.[A-Za-z_.]+\([^()]*\)")


def _balanced(text, start):
    """The {...} or [...] beginning at `start`, brackets balanced, strings skipped."""
    open_ch = text[start]
    close_ch = {"{": "}", "[": "]"}[open_ch]
    depth, i, in_str, esc = 0, start, None, False
    while i < len(text):
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == in_str:
                in_str = None
        elif c in "\"'`":
            in_str = c
        elif c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
        i += 1
    return None


def _loads(chunk):
    try:
        return json.loads(_CALL.sub('""', chunk))
    except (ValueError, TypeError):
        return None


def scrape_blocks(src):
    """{opcode: {blockType, branchCount, args, hidden, order}} out of a blocks.js.

    `hidden` and the declaration order are what separate the palette a student
    actually sees from the file's full contents: the LED category declares 15
    blocks, of which 4 are superseded variants flagged hidden, and the other 11
    appear in the toolbox in exactly this order.
    """
    out = {}
    for order, m in enumerate(re.finditer(r'"opcode":\s*"([A-Za-z_0-9]+)"', src)):
        op, i = m.group(1), m.end()
        nxt = src.find('"opcode":', i)
        seg = src[i:nxt if nxt > 0 else len(src)]
        bt = re.search(r'"blockType":\s*"(\w+)"', seg)
        bc = re.search(r'"branchCount":\s*(\d+)', seg)
        args = {}
        a = seg.find('"arguments":')
        if a >= 0:
            brace = seg.find("{", a)
            parsed = _loads(_balanced(seg, brace)) or {}
            for slot, spec in parsed.items():
                if isinstance(spec, dict):
                    args[slot] = {"type": spec.get("type"),
                                  "default": spec.get("defaultValue"),
                                  "menu": spec.get("menu")}
        hid = re.search(r'"hidden":\s*(true|false)', seg)
        out[op] = {"blockType": bt.group(1) if bt else None,
                   "branchCount": int(bc.group(1)) if bc else 0,
                   "hidden": bool(hid and hid.group(1) == "true"),
                   "order": order,
                   "args": args}
    return out


def scrape_cate(src):
    """(display-name i18n key, first toolbox colour) out of one cates/*/index.js."""
    name = re.search(r'"name":\s*"([^"]+)"', src)
    col = re.search(r'"colors":\s*\[\s*"(#[0-9A-Fa-f]{6})"', src)
    return (name.group(1) if name else None), (col.group(1) if col else None)


def scrape_menus(src):
    """{MENU_KEY: [(i18n key, value)]} out of one cates/*/index.js."""
    out = {}
    m = re.search(r'"menus":\s*\{', src)
    if not m:
        return out
    block = _balanced(src, src.index("{", m.start() + 7))
    if block is None:
        return out
    for km in re.finditer(r'"([A-Z][A-Z0-9_]*)":\s*\[', block):
        arr = _loads(_balanced(block, block.index("[", km.end() - 1)))
        if not isinstance(arr, list):
            continue
        opts = [(o.get("text"), o.get("value")) for o in arr
                if isinstance(o, dict) and "value" in o]
        if opts:
            out[km.group(1)] = opts
    return out


# ------------------------------------------------------------------- catalogue
def build(app=APP):
    langs = asar_zip(app, "packages/renderer/dist/mblock/langs.zip")
    exts = asar_zip(app, "packages/renderer/dist/mblock/exts.zip")

    lang = {}                                   # ext -> {key: english label}
    every = {}                                  # flat fallback across extensions
    for ext in EXTS + ["mblock", "common"]:
        try:
            d = json.loads(langs.read(f"en/{ext}.json"))
        except KeyError:
            continue
        lang[ext] = d
        for k, v in d.items():
            every.setdefault(k, v)

    defs, menus = {}, {}                        # ext -> scraped definitions
    where = {}                                  # ext -> {opcode: [cate dir]}
    cates = {}                                  # (ext, cate) -> (name key, colour)
    for ext in EXTS:
        bl, mn, wh = {}, {}, {}
        for name in exts.namelist():
            if not name.startswith(f"{ext}/src/cates/"):
                continue
            cate = name.split("/")[3]
            if name.endswith("/blocks.js"):
                got = scrape_blocks(exts.read(name).decode("utf-8", "replace"))
                bl.update(got)
                # A block can be declared by more than one drawer: the four
                # Wi-Fi blocks head both `ai` and `iot`, because AI needs a
                # network before it can do anything. Keeping only the last
                # one seen dropped them off the top of the AI drawer.
                for op in got:
                    wh.setdefault(op, []).append(cate)
            elif name.endswith("/index.js"):
                text = exts.read(name).decode("utf-8", "replace")
                mn.update(scrape_menus(text))
                if name.count("/") == 4:        # a category's own index.js
                    cates[(ext, cate)] = scrape_cate(text)
        defs[ext], menus[ext], where[ext] = bl, mn, wh

    cat = {}
    for ext in EXTS:
        d = lang.get(ext, {})
        for k, v in d.items():
            if not isinstance(v, str):
                continue
            # A label key names a block if the definitions say so. Falling back
            # to "looks lowercase" keeps the blocks whose definitions are not in
            # exts.zip; without the first test the camelCase opcodes of the
            # Bluetooth controller (getBluetoothJoystickValue) are invisible.
            if not (k in defs[ext] or k == k.lower() or GENERATED.match(k)):
                continue
            if k in ("extensionName", ext):
                continue
            # `cate_*` names a drawer and `widget_*` names an embedded control;
            # both are lowercase and so pass the test above.
            if k.startswith(("cate_", "widget_")):
                continue
            if k in NOT_BLOCKS.get(ext, ()):
                continue
            spec = {"ext": ext, "opcode": k, "template": v,
                    "slots": SLOT.findall(v), "menus": {}, "args": {},
                    "options": {}, "blockType": None, "branchCount": 0}
            bd = defs[ext].get(k)
            if bd:
                spec["blockType"] = bd["blockType"]
                spec["branchCount"] = bd["branchCount"]
                spec["hidden"] = bd["hidden"]
                spec["order"] = bd["order"]
                drawers = []
                for cate in where[ext].get(k) or []:
                    key_name, colour = cates.get((ext, cate), (None, None))
                    # the category's display name is itself an i18n key
                    name = d.get(key_name, every.get(key_name, key_name))
                    # The Scratch-core drawers carry no translation in an
                    # extension's lang file, so the raw key (`events`, `myBlocks`)
                    # comes back. Name them as mBlock's own toolbox does, or they
                    # split into a lowercase twin of the core category.
                    drawers.append({"cate": cate,
                                    "cateName": CORE_CATE.get(name.lower(), (name,))[0],
                                    "cateColor": colour})
                if drawers:
                    # `cate`/`cateName`/`cateColor` stay single-valued: one drawer
                    # is the block's home for everything that has to name it once
                    # (a file, a heading, a colour). `alsoIn` carries the rest, so
                    # a reference sheet can show the block under every drawer that
                    # really offers it. Only the Wi-Fi blocks have a second entry.
                    spec.update(drawers[-1])
                    if len(drawers) > 1:
                        spec["alsoIn"] = drawers[:-1]
                for slot, arg in bd["args"].items():
                    spec["args"][slot] = {"type": arg["type"], "default": arg["default"]}
                    key = arg.get("menu")
                    if not key:
                        continue
                    opts = menus[ext].get(key) or menus.get("cyberpi", {}).get(key)
                    if not opts:
                        continue
                    labelled = [(d.get(t, every.get(t, t)), val) for t, val in opts]
                    spec["options"][slot] = [list(p) for p in labelled]
                    spec["menus"][slot] = [lbl for lbl, _ in labelled]
            # An extension whose definitions mBlock downloads has no scraped
            # drawer, so the declared one stands in.
            if not spec.get("cateName") and ext in DOWNLOADED_CATE:
                name, colour = DOWNLOADED_CATE[ext]
                spec["cate"], spec["cateName"], spec["cateColor"] = ext, name, colour
            cat[f"{ext}.{k}"] = spec

        # A label key the definitions do not cover — an older variant of a block,
        # or a menu mBlock builds at runtime. Fall back to the pre-exts.zip
        # behaviour: read the options straight off the OPCODE_SLOT_N label keys.
        for k, v in d.items():
            if k == k.lower() or GENERATED.match(k) or not isinstance(v, str):
                continue
            m = re.match(r"^(.*)_(\d+)$", k)
            if not m:
                continue
            stem, idx = m.group(1).lower(), int(m.group(2))
            best = None
            for key, spec in cat.items():
                if spec["ext"] != ext:
                    continue
                op = spec["opcode"].lower()
                if stem.startswith(op + "_") and (best is None
                                                  or len(op) > len(best[1]["opcode"])):
                    best = (key, spec)
            if not best:
                continue
            spec = best[1]
            slot_raw = stem[len(spec["opcode"]) + 1:]
            slot = next((s for s in spec["slots"] if s.lower() == slot_raw), slot_raw)
            if slot in spec["options"]:
                continue                        # the definitions already said so
            spec.setdefault("_fallback", {}).setdefault(slot, {})[idx] = v

    for spec in cat.values():
        for slot, opts in spec.pop("_fallback", {}).items():
            labels = [opts[i] for i in sorted(opts)]
            spec["menus"][slot] = labels
            # No value is known for these — the label is the best guess, and it
            # is what the compiler used for every menu before exts.zip was read.
            spec["options"][slot] = [[l, l] for l in labels]

    # The Scratch-core categories carry no display name in the extension lang
    # files — mBlock translates those from its own catalogue — so they are named
    # here. The colours are the ones the cates/*/index.js files declare.
    for i, (op, (ext, tmpl, slots, opts)) in enumerate(CORE.items()):
        cat[op] = {"ext": ext, "opcode": op, "template": tmpl, "slots": slots,
                   "menus": dict(opts), "options": {s: [[o, o] for o in v]
                                                    for s, v in opts.items()},
                   "args": {s: {"type": CORE_ARGS.get(op, {}).get(s, "string"),
                                "default": ""} for s in slots},
                   "blockType": None, "branchCount": 0, "core": True,
                   "hidden": False, "order": i,
                   "cate": ext, "cateName": CORE_CATE.get(ext, (ext, None))[0],
                   "cateColor": CORE_CATE.get(ext, (ext, None))[1]}

    mb = lang.get("mblock", {})
    for i, (key, (op, ext, slots)) in enumerate(CORE_FROM_MBLOCK.items()):
        if key not in mb:
            print("  ! mblock.json has no", key, file=sys.stderr)
            continue
        tmpl = PCT.sub(lambda m: "[" + slots[int(m.group(1)) - 1] + "]"
                       if int(m.group(1)) <= len(slots) else m.group(0), mb[key])
        cat[op] = {"ext": ext, "opcode": op, "template": tmpl, "slots": slots,
                   "menus": {}, "options": {},
                   "args": {s: {"type": CORE_ARGS.get(op, {}).get(s, "string"),
                                "default": ""} for s in slots},
                   "blockType": None, "branchCount": 0, "core": True,
                   "hidden": False, "order": 100 + i,
                   "cate": ext, "cateName": CORE_CATE.get(ext, (ext, None))[0],
                   "cateColor": CORE_CATE.get(ext, (ext, None))[1]}
    return cat


def main():
    app = APP
    if "--app" in sys.argv:
        app = Path(sys.argv[sys.argv.index("--app") + 1])
    cat = build(app)
    OUT.write_text(json.dumps(cat, indent=1, ensure_ascii=False), encoding="utf-8")
    typed = sum(1 for s in cat.values() if s["args"])
    valued = sum(1 for s in cat.values() if s["options"])
    print(f"catalogue: {len(cat)} blocks  ({typed} with typed arguments, "
          f"{valued} with menus)")
    by = {}
    for s in cat.values():
        by[s["ext"]] = by.get(s["ext"], 0) + 1
    for e, n in sorted(by.items(), key=lambda x: -x[1]):
        print(f"   {e:32s} {n}")


if __name__ == "__main__":
    main()
