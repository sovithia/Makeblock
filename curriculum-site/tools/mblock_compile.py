# -*- coding: utf-8 -*-
"""Compile curriculum block scripts into real .mblock project files.

A .mblock is a zip holding an sb3-style project.json, an `mscratch.json` sprite
registry, the stage/sprite assets, and an `mblock5` marker. Everything except the
blocks themselves is taken verbatim from reference/mblock-shell/, which is a real
empty project saved by mBlock 5.6.0 — so the container is not a reconstruction of
the format, it *is* the format, with our blocks dropped into the device target.

Three things about that shell are not guessable and were all wrong before:
  * the target that carries mBot2 code is named **mbotneo**, not cyberpi;
  * variables and lists live on the **Stage**, not on the device;
  * `extensions` lists `cyberpi-cyberpi` / `mbot2-mbot2` / `mbuild` — hyphens in
    5.6 (the 2021 files use dots), and every mBuild sensor registers as `mbuild`.

Blocks are emitted from reference/mblock-palette.json, which now carries each
argument's real type and each menu's real value. That decides everything the
compiler used to guess: an `image` argument is a decorative icon and is dropped,
`fieldMenu` becomes a `fields` entry, `inputMenu` becomes an input pointing at a
shadow menu block, and the value written is the menu's internal value (`zh`,
`ALL`, `L1`), never the label the palette shows (`auto`, `all`, `(3) L1`).

Usage:
    python tools/mblock_compile.py                 # all projects, both grades
    python tools/mblock_compile.py G7-A-obeys      # just one
    python tools/mblock_compile.py --check         # compile, report, write nothing

A line that does not resolve to a real block is reported and the script it
belongs to is skipped, so a project file is either faithful or absent — never
silently wrong. Silence used to be the failure mode: an unresolved reporter
became a *variable named after itself*, so `(ultrasonic 2 1 distance to an object
(cm))` shipped as a variable in six projects. Anything that is not a plain
identifier now raises instead.
"""
import json, re, sys, time, zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PALETTE = json.loads((ROOT / "reference" / "mblock-palette.json").read_text(encoding="utf-8"))
# Two containers, because the two grades are two different mBlock devices.
# Grade 7 is an mBot2 (`mbotneo`); Grade 8 builds the Rover, which mBlock models
# as its own device (`rover`) with its own related extensions -- notably WITHOUT
# the ultrasonic, which the Rover does not carry. Both were saved from the IDE;
# neither is hand-written.
SHELLS = {"mbotneo": ROOT / "reference" / "mblock-shell",
          "rover": ROOT / "reference" / "mblock-shell-rover"}
SHELL = SHELLS["mbotneo"]
OUT = ROOT / "site" / "assets" / "projects"

SLOT = re.compile(r"\[([A-Za-z_0-9]+)\]")
WORD = re.compile(r"[a-z0-9]")
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
STAMP = 1723420800000          # fixed, so rebuilds are byte-stable
ZIP_DATE = (2024, 8, 12, 0, 0, 0)

# The target that carries the code. The shell decides which extensions exist:
# a block from one it does not declare is an error, not a silent omission.
DEVICE = "mbotneo"
# Grade 8 compiles against the Rover shell. Set by use_device() before a build.
GRADE_DEVICE = {7: "mbotneo", 8: "rover", 9: "rover"}
SHELL_EXTS = json.loads((ROOT / "reference" / "mblock-shell" / "project.json")
                        .read_text(encoding="utf-8"))["extensions"]


def use_device(grade):
    """Point the compiler at the shell for this grade's robot."""
    global SHELL, DEVICE, SHELL_EXTS
    DEVICE = GRADE_DEVICE.get(grade, "mbotneo")
    SHELL = SHELLS[DEVICE]
    SHELL_EXTS = json.loads((SHELL / "project.json").read_text(encoding="utf-8"))["extensions"]
    return DEVICE


def registration(ext, declared=None):
    """The name `extensions` uses for the extension an opcode belongs to, or None.

    Not the opcode prefix: 5.6 writes `cyberpi-cyberpi` and `mbot2-mbot2` (5.3
    used dots), and every mBuild sensor — quad colour, ultrasonic 2 — registers
    under the one bundle name `mbuild`. Reading it off the shell rather than
    hard-coding it means re-saving the shell with another extension added is all
    it takes to support that extension.
    """
    declared = SHELL_EXTS if declared is None else declared
    for name in declared:
        if name == ext or name.startswith(ext + "-") or name.startswith(ext + "."):
            return name
    if "mbuild" in ext and "mbuild" in declared:
        return "mbuild"
    # The working Bluetooth Controller: opcodes say firefly_bluetoothcontroller,
    # but a saved project declares it as plain `firefly`. Confirmed from an IDE
    # save (Desktop/controller-test.mblock, 2026-08-23).
    if ext.startswith("firefly") and "firefly" in declared:
        return "firefly"
    return None

# sb3 shadow primitives, keyed by the argument types exts.zip uses.
SHADOW = {"number": 4, "positive": 5, "whole": 6, "integer": 7, "angle": 8,
          "color": 9, "note": 4, "string": 10}


def shadow_of(arg):
    """(primitive type, default text) for a slot's obscured shadow value."""
    t = (arg or {}).get("type") or ""
    prim = SHADOW.get(t.lower(), 10)
    default = (arg or {}).get("default")
    return prim, "" if default is None else str(default)


def norm(s):
    s = s.replace(" ", " ").replace("​", "")
    s = re.sub(r"([°?])", r" \1 ", s)
    # mBlock punctuates these inconsistently — "at x: [n] y [n]" (colon on x
    # only), "displays R: [r]" on one LED block and "displays R [r]" on another.
    # Drop the colon after a single-letter axis or channel so either spelling matches.
    s = re.sub(r"(?i)\b([xyrgb]):", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def ncase(s):
    """Normalised and case-folded — for comparing against menu options."""
    return norm(str(s)).lower()


def _lit(chunk):
    n = norm(chunk)
    if not n:
        return r"\s*"
    rx = re.escape(n).replace(r"\ ", r"\s+")
    if WORD.match(n[0]):
        rx = r"\b" + rx
    if WORD.search(n[-1]):
        rx += r"\b"
    return r"\s*" + rx + r"\s*"


HOLE = "\x00%d\x00"
HOLE_RX = re.compile(r"\x00(\d+)\x00")

# Two readings of a value slot. TIGHT forbids a hole from being buried inside a
# run of text, which is what made `join ok, (item (i) of commands)` match with
# STRING1 empty and STRING2 holding the whole thing — the reporter then compiled
# to the literal text "ok, (item (i) of commands)". LOOSE allows it, because a
# slot legitimately holds an expression that has to be compiled recursively
# (`speak auto join ok, (…)`). Tight is tried across every block first.
VALUE_TIGHT = r"(?:\x00\d+\x00|[^()\x00]{0,40}?)"
VALUE_LOOSE = r"(?:\x00\d+\x00|[^()]{0,40}?)"


def _menu_alt(opts):
    outs = set()
    for o in opts:
        n = ncase(o)
        outs.add(n)
        outs.add(re.sub(r"^\(\d+\)\s*", "", n))     # "(3) l1" is also written "l1"
    return "|".join(sorted((re.escape(o) for o in outs if o), key=len, reverse=True))


def _patterns(value_rx):
    pats = []
    for key, spec in PALETTE.items():
        t, parts, last, anchors = spec["template"], [], 0, 0
        for m in SLOT.finditer(t):
            chunk = t[last:m.start()]
            parts.append(_lit(chunk))
            anchors += len(norm(chunk).split())
            slot = m.group(1)
            opts = spec["menus"].get(slot)
            if opts:
                parts.append(r"\s*(" + _menu_alt(opts) + r"|\x00\d+\x00)\s*")
            else:
                parts.append("(" + value_rx + ")")
            last = m.end()
        parts.append(_lit(t[last:]))
        anchors += len(norm(t[last:]).split())
        # A block must be named by real words rather than be a bag of slots. One
        # anchor is enough when a menu pins it down ("speak [auto] …"), or when it
        # is a core operator whose single name is already unambiguous ("join a b").
        pinned = any(spec["menus"].get(s) for s in spec["slots"])
        if anchors < 2 and not (anchors == 1 and (len(spec["slots"]) <= 1 or pinned
                                                  or spec.get("core"))):
            continue
        rx = re.sub(r"(\\s\*){2,}", r"\\s*", "".join(parts))
        try:
            pats.append((key, spec, re.compile(r"^\s*" + rx + r"\s*$", re.I), anchors))
        except re.error:
            pass
    return pats


PATTERNS_TIGHT = _patterns(VALUE_TIGHT)
PATTERNS_LOOSE = _patterns(VALUE_LOOSE)


def _role(spec, slot):
    """What a slot is: image / fieldmenu / inputmenu / fieldvariable / … / value."""
    t = (spec.get("args", {}).get(slot) or {}).get("type")
    if t:
        return t.lower()
    # A block the definitions do not cover. Fall back to the old shape rules.
    if spec["menus"].get(slot):
        return "fieldmenu" if (slot.lower().startswith("fieldmenu")
                               or slot.isupper()) else "inputmenu"
    if slot == "VARIABLE":
        return "fieldvariable"
    if slot == "LIST":
        return "fieldlist"
    return "string"


def _best(text, pats):
    n = norm(text)
    best = None
    for key, spec, rx, anchors in pats:
        m = rx.match(n)
        if not m:
            continue
        vals = {s: v.strip() for s, v in zip(spec["slots"], m.groups())}
        # A value slot must not swallow a clause — except free-text slots, which
        # legitimately hold a whole sentence ("speak auto I did not catch that").
        if any(not HOLE_RX.fullmatch(v) and len(v.split()) > 4
               and _role(spec, s) not in ("string",)
               for s, v in vals.items()):
            continue
        score = (anchors, -sum(len(v) for v in vals.values()))
        if best is None or score > best[0]:
            best = (score, key, spec, vals)
    return None if best is None else (best[1], best[2], best[3])


def find_block(text):
    """Best real block for a line whose sub-expressions are already holes."""
    return _best(text, PATTERNS_TIGHT) or _best(text, PATTERNS_LOOSE)


def resolve(text):
    """(hit, groups) for one source line, trying four readings in priority order.

    Holed before raw, because `(item (i) of route)` is a nested reporter and only
    the holed reading sees it. Raw before loose, because a block whose own label
    carries brackets — `set LAN channel to 6 (default)`, `ultrasonic 2 1 distance
    to an object (cm)` — reads as a hole that no template can match, and a loose
    match on the holed text finds some other block that swallows the lot
    (`set [VARIABLE] to [VALUE]`, in that first case).
    """
    body, groups = split_holes(text)
    for pats in (PATTERNS_TIGHT, PATTERNS_LOOSE):
        holed = _best(body, pats)
        if holed and not _menu_hole(holed):
            return holed, groups
        raw = _best(text, pats) if body != text else None
        if raw:
            # A dropdown whose label is itself bracketed — "(4) English",
            # "(3) L1". Holing it out leaves the menu holding a sentinel, and the
            # rest of the label ("English") lands in the next slot.
            return raw, []
        if holed:
            return holed, groups
    return None, groups


def _menu_hole(hit):
    _key, spec, vals = hit
    return any(HOLE_RX.fullmatch(v or "") and _role(spec, s) in ("fieldmenu", "inputmenu")
               for s, v in vals.items())


def menu_value(spec, slot, raw):
    """The value mBlock stores for a menu option shown as `raw`.

    The palette shows "all", "(3) L1", "auto"; the file holds "ALL", "L1", "zh".
    Writing the label produced a block whose dropdown was blank in the editor.
    """
    raw_n = ncase(raw)
    for label, val in spec.get("options", {}).get(slot, []):
        if raw_n in (ncase(label), re.sub(r"^\(\d+\)\s*", "", ncase(label)),
                     ncase(val)):
            return val
    return raw


# ---------------------------------------------------------------- source parse
def split_holes(text):
    """Replace top-level (...) groups with holes; return (text, [group bodies])."""
    out, groups, depth, buf, cur = "", [], 0, "", ""
    for ch in text:
        if ch == "(":
            if depth == 0:
                out += cur
                cur = ""
                buf = ""
            else:
                buf += ch
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                out += HOLE % len(groups)
                groups.append(buf)
                buf = ""
            else:
                buf += ch
        elif depth:
            buf += ch
        else:
            cur += ch
    return out + cur, groups


def parse_tree(src):
    """Indented source -> nested [(text, children)]."""
    root, stack = [], [(-1, None)]
    for raw in src.splitlines():
        if not raw.strip():
            continue
        ind = len(raw) - len(raw.lstrip(" "))
        node = [raw.strip(), []]
        while stack and stack[-1][0] >= ind:
            stack.pop()
        (root if stack[-1][1] is None else stack[-1][1][1]).append(node)
        stack.append((ind, node))
    return root


INFIX = [(" or ", "operator_or", "OPERAND1", "OPERAND2"),
         (" and ", "operator_and", "OPERAND1", "OPERAND2"),
         (" contains ", "operator_contains", "STRING1", "STRING2"),
         (" = ", "operator_equals", "OPERAND1", "OPERAND2"),
         (" > ", "operator_gt", "OPERAND1", "OPERAND2"),
         (" < ", "operator_lt", "OPERAND1", "OPERAND2"),
         (" + ", "operator_add", "NUM1", "NUM2"),
         (" - ", "operator_subtract", "NUM1", "NUM2"),
         (" * ", "operator_multiply", "NUM1", "NUM2"),
         (" / ", "operator_divide", "NUM1", "NUM2")]

NUM = re.compile(r"^-?\d+(\.\d+)?$")

# The only blocks with a mouth. Everything else that has indented children —
# a hat, or a `define` — carries them on `next`.
C_BLOCKS = {"control_forever", "control_repeat", "control_repeat_until",
            "control_while", "control_for_new", "control_for_each",
            "control_if", "control_if_else"}


class Fail(Exception):
    pass


class Project:
    """Accumulates sb3 blocks for one .mblock."""

    def __init__(self, name, arg_kinds=None):
        self.name, self.blocks = name, {}
        self.vars, self.lists, self.procs = {}, {}, {}
        self.arg_kinds = arg_kinds or {}       # proc name -> ["%n", "%s", …]
        self.defined = set()                   # custom blocks already emitted
        self.scope = []                        # custom-block parameters in scope
        self.n = 0

    def nid(self, tag="b"):
        self.n += 1
        return f"{tag}{self.n:04d}~{self.name[:6]}"

    def var(self, name):
        return self.vars.setdefault(name, f"var-{name}")

    def lst(self, name):
        return self.lists.setdefault(name, f"lst-{name}")

    def in_scope(self, name):
        return any(name in frame for frame in self.scope)

    # -- values -----------------------------------------------------------
    def argref(self, name, parent, shadow=False):
        rid = self.nid("a")
        self.blocks[rid] = {"opcode": "argument_reporter_string_number",
                            "next": None, "parent": parent, "inputs": {},
                            "fields": {"VALUE": [name, None]},
                            "shadow": shadow, "topLevel": False}
        return rid

    def name_ref(self, name, parent, obscured):
        """A bare name in a slot: a custom-block parameter, a list, or a variable."""
        if self.in_scope(name):
            return [3, self.argref(name, parent), obscured]
        if name in self.lists:
            return [3, [13, name, self.lst(name)], obscured]
        return [3, [12, name, self.var(name)], obscured]

    def value(self, text, groups, parent, arg=None):
        """Compile a slot value; returns an sb3 input entry."""
        text = text.strip()
        prim, default = shadow_of(arg)
        obscured = [prim, default]
        m = HOLE_RX.fullmatch(text)
        if m:
            inner = groups[int(m.group(1))]
            bid = self.expr(inner, parent)
            if bid is None:                       # a bare name
                return self.name_ref(inner.strip(), parent, obscured)
            return [3, bid, obscured]
        if not text:
            return [1, [prim, default]]
        if HOLE_RX.search(text):
            # an unparenthesised reporter, e.g. `join  ok,   (item (i) of commands)`
            full = HOLE_RX.sub(lambda m: "(" + groups[int(m.group(1))] + ")", text)
            bid = self.expr_text(full, parent)
            if bid is None:
                raise Fail(full)
            return [3, bid, obscured]
        if NUM.match(text):
            return [1, [prim if prim != 10 else 4, text]]
        if resolve(text)[0]:
            bid = self.expr_text(text, parent)
            if bid:
                return [3, bid, obscured]
        return [1, [prim, text]]

    def expr_text(self, text, parent):
        """Compile free text — a condition, or an unparenthesised reporter."""
        return self.expr(text, parent)

    def expr(self, text, parent):
        """Compile a (...) body into a reporter block id, or None if it is a name."""
        body, groups = split_holes(text)
        for tok, op, a, b in INFIX:
            if tok in f" {body} ":
                left, _, right = body.partition(tok)
                # The curriculum writes predicates with a trailing question mark
                # — `(heard) contains (item (i) of commands) ?` — and it belongs
                # to the block's label, not to the operand.
                right = right.strip().rstrip("?").strip()
                # The membership test pads the body, so a body that IS just the
                # operator (">") matches it — but partition then finds nothing to
                # split on and hands the whole body back as the left operand,
                # which compiles it again, forever. An operator needs two sides.
                if not left.strip() or not right:
                    continue
                bid = self.nid("e")
                self.blocks[bid] = {
                    "opcode": op, "next": None, "parent": parent,
                    "inputs": {a: self.value(left, groups, bid),
                               b: self.value(right, groups, bid)},
                    "fields": {}, "shadow": False, "topLevel": False}
                return bid

        # Getting this wrong is what turned six sensor readings into variables
        # named after themselves: `(ultrasonic 2 1 distance to an object (cm))`
        # only matches on the raw reading, which resolve() tries second.
        hit, hgroups = resolve(text)
        if hit:
            return self.emit(hit, hgroups, parent, stack=False)
        if HOLE_RX.fullmatch(body.strip()):
            return self.expr(groups[int(HOLE_RX.fullmatch(body.strip()).group(1))], parent)
        name = body.strip()
        if HOLE_RX.search(name) or not IDENT.match(name):
            raise Fail(text)
        return None                                # plain identifier

    # -- blocks -----------------------------------------------------------
    def menu_shadow(self, key, slot, value, parent):
        mid = self.nid("m")
        mop = f"{key}_{slot}_menu"
        self.blocks[mid] = {
            "opcode": mop, "next": None, "parent": parent, "inputs": {},
            "fields": {f"{mop}_option": [value, None]},
            "shadow": True, "topLevel": False}
        return mid

    def emit(self, hit, groups, parent, stack=True):
        key, spec, vals = hit
        ext = key.split(".")[0] if "." in key else None
        if ext and not registration(ext):
            # The shell decides which extensions a project declares. Emitting a
            # block from one it does not declare gives a file that opens with a
            # hole in it, so drop the script and say which shell is missing.
            raise Fail(f"{spec['template']} — extension {ext!r} is not declared "
                       f"by reference/mblock-shell")
        bid = self.nid()
        inputs, fields = {}, {}
        for slot, raw in vals.items():
            raw = (raw or "").strip()
            role = _role(spec, slot)
            arg = spec.get("args", {}).get(slot) or {}
            if role == "image":
                continue                        # a decorative icon, not a socket
            if role == "fieldmenu":
                if HOLE_RX.search(raw):
                    # A dropdown is a dropdown: mBlock has nowhere to plug a
                    # reporter into one, so `show label (i) …` is not a block
                    # that can exist.
                    full = HOLE_RX.sub(lambda m: "(" + groups[int(m.group(1))] + ")", raw)
                    raise Fail(f"{spec['template']} — the [{slot}] dropdown cannot "
                               f"hold {full!r}")
                fields[slot] = [menu_value(spec, slot, raw), None]
            elif role in ("inputmenu", "spritemenu"):
                if HOLE_RX.search(raw):
                    # An input menu can be covered by a reporter — the shadow
                    # menu stays underneath, as it does in the editor.
                    mid = self.menu_shadow(key, slot, str(arg.get("default") or ""), bid)
                    over = self.value(raw, groups, bid, arg)
                    inputs[slot] = [3, over[1], mid]
                else:
                    inputs[slot] = [1, self.menu_shadow(key, slot,
                                                        menu_value(spec, slot, raw), bid)]
            elif role == "fieldvariable":
                fields[slot] = [raw, self.var(raw)]
            elif role == "fieldlist":
                fields[slot] = [raw, self.lst(raw)]
            elif slot.lower() in ("condition", "operand") or role == "boolean":
                v = self.value(raw, groups, bid, arg)
                inputs[slot] = [2, v[1]] if v[0] == 3 and isinstance(v[1], str) else v
            else:
                inputs[slot] = self.value(raw, groups, bid, arg)
        self.blocks[bid] = {"opcode": key, "next": None, "parent": parent,
                            "inputs": inputs, "fields": fields,
                            "shadow": False, "topLevel": False}
        return bid

    # -- statements -------------------------------------------------------
    def stack(self, nodes, parent, top=False, x=0, y=0):
        """Compile a list of sibling statements; return the first block id."""
        first, prev = None, None
        i = 0
        while i < len(nodes):
            text, kids = nodes[i]
            low = ncase(text)
            if low == "else":
                i += 1
                continue

            if low.startswith("define "):
                bid = self.define(text, kids, x, y)
                i += 1
                first = first or bid
                continue

            ctl = self.control(text, parent)
            if ctl is not None:
                bid = ctl
            else:
                hit, groups = resolve(text)
                if hit is None:
                    call = self.call(text, groups, parent)
                    if call is None:
                        raise Fail(text)
                    bid = call
                else:
                    bid = self.emit(hit, groups, parent)

            b = self.blocks[bid]
            # Only C-blocks have a mouth. A hat's indented body is its `next`,
            # not a SUBSTACK — giving a hat a mouth produces a block mBlock
            # cannot render.
            if kids:
                if b["opcode"] in C_BLOCKS:
                    b["inputs"]["SUBSTACK"] = [2, self.stack(kids, bid)]
                else:
                    b["next"] = self.stack(kids, bid)
            if i + 1 < len(nodes) and ncase(nodes[i + 1][0]) == "else":
                els = nodes[i + 1][1]
                if b["opcode"] == "control_if":
                    b["opcode"] = "control_if_else"
                if els:
                    b["inputs"]["SUBSTACK2"] = [2, self.stack(els, bid)]
            if prev is None:
                first = bid
                b["parent"] = parent
                if top:
                    b["topLevel"], b["x"], b["y"] = True, x, y
            else:
                self.blocks[prev]["next"] = bid
                b["parent"] = prev
            prev = bid
            i += 1
        return first

    # Control blocks carry a whole boolean expression in their mouth, which the
    # generic matcher cannot capture (its value slots stop at four words). Peel
    # the condition off by hand and compile it as an expression.
    CTL = [
        (re.compile(r"^if\s+(?P<c>.*?)\s+then$", re.I), "control_if", "CONDITION"),
        (re.compile(r"^repeat until\s+(?P<c>.*)$", re.I), "control_repeat_until", "CONDITION"),
        (re.compile(r"^wait until\s+(?P<c>.*)$", re.I), "control_wait_until", "CONDITION"),
        (re.compile(r"^while\s+(?P<c>.*?)(?:\s+repeat)?$", re.I), "control_while", "CONDITION"),
        (re.compile(r"^repeat\s+(?P<c>\d+)$", re.I), "control_repeat", "TIMES"),
        (re.compile(r"^forever$", re.I), "control_forever", None),
        # "_new" is mBlock's own suffix, not a typo — see CORE_FROM_MBLOCK in
        # tools/mblock_palette.py. control_break opens as an undefined block.
        (re.compile(r"^break$", re.I), "control_break_new", None),
        (re.compile(r"^continue$", re.I), "control_continue_new", None),
    ]
    FOR = re.compile(r"^count with\s+(?P<v>\S+)\s+from\s+(?P<a>.*?)\s+to\s+(?P<b>.*?)"
                     r"\s+by step\s+(?P<s>.*?)\s+repeat$", re.I)

    def control(self, text, parent):
        # Match on the holed text, so a bracketed sub-expression inside the
        # header — `count with i from 1 to (length of route) …` — survives as a
        # hole and can be compiled. Matching the raw text and then compiling with
        # no groups is how the loop bound became the literal "(length of route)".
        body, groups = split_holes(re.sub(r"\s+", " ", text.strip()))
        m = self.FOR.match(body)
        if m:
            bid = self.nid("f")
            arg = {"type": "number", "default": ""}
            self.blocks[bid] = {
                "opcode": "control_for_new", "next": None, "parent": parent,
                # lowercase, as mBlock writes them — START/END/STEP are ignored
                # by the editor and the loop comes up empty.
                "inputs": {k: self.value(m.group(g), groups, bid, arg)
                           for k, g in (("start", "a"), ("end", "b"), ("step", "s"))},
                "fields": {"VARIABLE": [m.group("v"), self.var(m.group("v"))]},
                "shadow": False, "topLevel": False}
            return bid
        for rx, op, slot in self.CTL:
            m = rx.match(body)
            if not m:
                continue
            bid = self.nid("k")
            inputs = {}
            if slot == "CONDITION":
                cond = HOLE_RX.sub(lambda x: "(" + groups[int(x.group(1))] + ")",
                                   m.group("c"))
                cid = self.expr_text(cond, bid)
                if cid is None:
                    return None
                inputs["CONDITION"] = [2, cid]
            elif slot:
                inputs[slot] = [1, [4, m.group("c")]]
            self.blocks[bid] = {"opcode": op, "next": None, "parent": parent,
                                "inputs": inputs, "fields": {},
                                "shadow": False, "topLevel": False}
            return bid
        return None

    def register(self, sig):
        """Record a custom block's signature without emitting it.

        Every define in the project is registered before any step is compiled, so
        a stage that calls a block defined in a *later* step still resolves. It
        used to fail there and drop the whole script — that is where G8-C lost
        `follow_lap`.
        """
        name, args = self.signature(sig)
        kinds = (self.arg_kinds.get(name) or ["%s"] * len(args))[:len(args)]
        proccode = name + "".join(" " + k for k in kinds)
        argids = [f"arg-{name}-{a}" for a in args]
        self.procs[name] = (proccode, argids, args, kinds)
        return name, args, proccode, argids

    def define(self, text, kids, x, y):
        sig = text[len("define"):].strip()
        name, args, proccode, argids = self.register(sig)
        if name in self.defined:
            return None                        # already emitted, from another step
        self.defined.add(name)
        pid, did = self.nid("p"), self.nid("d")
        inputs = {}
        for a, aid in zip(args, argids):
            inputs[aid] = [1, self.argref(a, pid, shadow=True)]
        self.blocks[pid] = {
            "opcode": "procedures_prototype", "next": None, "parent": did,
            "inputs": inputs, "fields": {}, "shadow": True, "topLevel": False,
            "mutation": {"tagName": "mutation", "children": [], "proccode": proccode,
                         "argumentids": json.dumps(argids),
                         "argumentnames": json.dumps(args),
                         # mBlock's own default for a fresh input, and warp off —
                         # the editor writes "false" here, and a warped custom
                         # block runs its whole body in one frame.
                         "argumentdefaults": json.dumps(["todo" for _ in args]),
                         "warp": "false"}}
        self.blocks[did] = {"opcode": "procedures_definition", "next": None,
                            "parent": None, "inputs": {"custom_block": [1, pid]},
                            "fields": {}, "shadow": False, "topLevel": True,
                            "x": x, "y": y}
        if kids:
            # Inside the body a bare parameter name is an argument reporter, not
            # a variable. Compiling it as a variable is what put `size`, `deg`,
            # `speed` and `height` in the variables palette of five projects.
            self.scope.append(set(args))
            try:
                self.blocks[did]["next"] = self.stack(kids, did)
            finally:
                self.scope.pop()
        return did

    @staticmethod
    def signature(sig):
        body, groups = split_holes(sig)
        name = body.strip()
        name = HOLE_RX.sub("", name).strip()
        return name, [g.strip() for g in groups]

    def call(self, text, groups, parent):
        body = HOLE_RX.sub(lambda m: HOLE % int(m.group(1)), split_holes(text)[0])
        parts = body.strip().split(None, 1)
        name = parts[0]
        if name not in self.procs:
            return None
        proccode, argids, args, kinds = self.procs[name]
        rest = parts[1].strip() if len(parts) > 1 else ""
        vals = [v for v in re.split(r"\s+", rest) if v] if rest else []
        bid = self.nid("c")
        inputs = {}
        for aid, v, kind in zip(argids, vals, kinds):
            inputs[aid] = self.value(v, groups, bid,
                                     {"type": "number" if kind == "%n" else "string",
                                      "default": ""})
        self.blocks[bid] = {
            "opcode": "procedures_call", "next": None, "parent": parent,
            "inputs": inputs, "fields": {}, "shadow": False, "topLevel": False,
            "mutation": {"tagName": "mutation", "children": [], "proccode": proccode,
                         "argumentids": json.dumps(argids), "warp": "false"}}
        return bid

    # -- output -----------------------------------------------------------
    def fix_list_blocks(self):
        """Re-point the two blocks whose wording is ambiguous between a string
        and a list.

        mBlock ships `length of [STRING]` (operator_length) and
        `length of [LIST]` (data_lengthoflist) with identical wording, and the
        same for `[STRING] contains [STRING]?` / `[LIST] contains [ITEM]?`. The
        template resolver cannot tell them apart, and picked the string one —
        so `length of route` compiled to len("route"), which is 5. It uploaded
        without complaint and threw IndexError on the robot, inside whichever
        handler used it.

        The decision needs the full list registry, which only exists once every
        script has been compiled, so it is made here rather than at parse time:
        a literal operand that names a declared list was never a string.
        """
        fixed = 0
        for b in self.blocks.values():
            op = b.get("opcode")
            if op == "operator_length":
                inp = b["inputs"].get("STRING")
                name = inp[1][1] if inp and isinstance(inp[1], list) and inp[1][0] == 10 else None
                if name in self.lists:
                    b["opcode"] = "data_lengthoflist"
                    b["inputs"] = {}
                    b["fields"] = {"LIST": [name, self.lst(name)]}
                    fixed += 1
            elif op == "operator_contains":
                inp = b["inputs"].get("STRING1")
                name = inp[1][1] if inp and isinstance(inp[1], list) and inp[1][0] == 10 else None
                if name in self.lists:
                    b["opcode"] = "data_listcontainsitem"
                    b["inputs"] = {"ITEM": b["inputs"]["STRING2"]}
                    b["fields"] = {"LIST": [name, self.lst(name)]}
                    fixed += 1
        return fixed

    def project_json(self):
        self.fix_list_blocks()
        d = json.loads((SHELL / "project.json").read_text(encoding="utf-8"))
        for b in self.blocks.values():       # every extension is declared
            op = b["opcode"]
            if "." in op and not registration(op.split(".")[0], d["extensions"]):
                raise Fail(f"extension {op.split('.')[0]!r} is not declared by the shell")
        for t in d["targets"]:
            if t["isStage"]:
                # Variables and lists are global and live on the Stage. On the
                # device target mBlock does not show them at all.
                t["variables"] = {vid: [name, 0] for name, vid in self.vars.items()}
                t["lists"] = {lid: [name, []] for name, lid in self.lists.items()}
            if t["name"] == DEVICE:
                t["blocks"] = self.blocks
        return d

    def write(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            def put(name, data):
                info = zipfile.ZipInfo(name, date_time=ZIP_DATE)
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, data)

            put("project.json", json.dumps(self.project_json(), ensure_ascii=False))
            put("mscratch.json", (SHELL / "mscratch.json").read_bytes())
            for asset in sorted(SHELL.glob("*")):
                if asset.suffix in (".svg", ".wav"):
                    put(asset.name, asset.read_bytes())
            put("mblock5", json.dumps({"version": "5.6.0", "createdAt": STAMP}))


# ---------------------------------------------------------------------- driver
CALL_ARG = re.compile(r"^-?\d+(\.\d+)?$")


def arg_kinds(defines, texts):
    """Per custom block, `%n` for a parameter only ever passed numbers, else `%s`.

    mBlock offers a number input and a text input, and writes them differently in
    the proccode. Every lesson block takes a number, but the source does not say
    so — the call sites do.
    """
    out = {}
    for name, node in defines.items():
        _n, args = Project.signature(node[0][len("define"):].strip())
        seen = [[] for _ in args]
        for text in texts:
            for line in text.splitlines():
                body = split_holes(line.strip())[0]
                parts = body.split()
                if not parts or parts[0] != name:
                    continue
                for i, v in enumerate(parts[1:len(args) + 1]):
                    seen[i].append(v)
        out[name] = ["%n" if vals and all(CALL_ARG.match(v) for v in vals) else "%s"
                     for vals in seen]
    return out


_WRAPS = re.compile(r"^(forever|repeat\b|while\b|count with\b|if\b.*\bthen$|else)", re.I)


def script_size(node):
    """(rows, mouths) for one top-level script, counted all the way down.

    Scripts are laid out on the canvas by advancing y, and the advance has to
    cover the WHOLE script. Counting only the immediate children — which is what
    `len(node[1])` does — under-measures anything nested, so a `count with`
    holding an `if` holding three blocks was allotted two rows' worth of space
    and the next script was dropped on top of it.
    """
    text, kids = node
    rows, mouths = 1, (1 if kids and _WRAPS.match(norm(text)) else 0)
    for k in kids:
        r, m = script_size(k)
        rows, mouths = rows + r, mouths + m
    return rows, mouths


def script_h(node):
    """Generous height in canvas px. Overshooting costs a scroll; undershooting
    overlaps two scripts, so this rounds up on purpose."""
    rows, mouths = script_size(node)
    return 48 + 56 * rows + 32 * mouths


def step_file(project, n):
    """G7-C-remembers + step 11 -> G7-C-11. Stage prefix, then the step."""
    return "-".join(project.split("-")[:2]) + f"-{n:02d}"


# ------------------------------------------------------- carry-forward
# Which opcodes bring a variable or list into existence, and which only read one.
# `delete n of` is deliberately absent from CREATES: removing an item does not
# make a list — that is what made an earlier audit call G7-C-14 self-sufficient
# when in fact nothing in it ever put a route together.
CREATES = {"data_setvariableto", "data_addtolist", "data_insertatlist",
           # a for-loop assigns its own counter, so `i` is never a dependency
           "control_for_new", "control_for_each"}
# Emptying a list is not filling one. `delete all of route` makes the list exist
# and leaves it with nothing in it, so carrying only that script would hand a
# student an undo button and no way to record anything to undo.
INITS = {"data_deletealloflist"}
# `change x by 1` reads x before it writes it, so it depends on whoever set it.
READS = {"data_variable", "data_listcontents", "data_itemoflist",
         "data_lengthoflist", "data_listcontainsitem", "data_itemnumoflist",
         "data_changevariableby"}

# sb3 writes a variable or list used as an INPUT as an inline primitive —
# [12, name, id] and [13, name, id] — not as a data_variable block. Reading only
# the block opcodes therefore misses almost every variable read there is, which
# is why variables looked like they had no dependencies at all.
INLINE_VAR, INLINE_LIST = 12, 13


def inline_refs(block):
    """Names of variables and lists referenced inline in a block's inputs."""
    out = set()
    for val in (block.get("inputs") or {}).values():
        for part in (val if isinstance(val, list) else []):
            if (isinstance(part, list) and len(part) >= 2
                    and part[0] in (INLINE_VAR, INLINE_LIST)):
                out.add(part[1])
    return out


def script_state(node, kinds, defines):
    """(creates, inits, reads) for one script, read off its own compiled graph.

    Compiled rather than pattern-matched: the resolver already knows that
    `(route)` in `item (i) of route` is a list and `(i)` is a variable, and
    re-deriving that from the source text is how the two disagree. The probe
    registers every custom-block signature first, or a script that calls one
    fails to compile and silently reports using and creating nothing.
    """
    probe = Project("probe", kinds)
    for d in defines.values():
        try:
            probe.register(d[0][len("define"):].strip())
        except Exception:
            pass
    try:
        probe.stack([node], None, top=True, x=0, y=0)
    except Fail:
        return set(), set(), set()
    creates, inits, reads = set(), set(), set()
    for b in probe.blocks.values():
        op = b.get("opcode", "").split(".")[-1]
        reads |= inline_refs(b)
        for slot in ("VARIABLE", "LIST"):
            f = (b.get("fields") or {}).get(slot)
            if not f:
                continue
            if op in CREATES:
                creates.add(f[0])
            elif op in INITS:
                inits.add(f[0])
            elif op in READS:
                reads.add(f[0])
    return creates, inits, reads - creates


def is_setup(node):
    """A flat initialiser — no loop, no branch. Safe to lift out of its stage."""
    text, kids = node
    if _WRAPS.match(norm(text)):
        return False
    return all(is_setup(k) for k in kids)


def carry_forward(own, prior, kinds, defines, outside=(), injected=()):
    """Earlier scripts this step needs, because it reads state it never creates.

    Not everything before it — only the scripts that build what it uses. A step
    that records a route and a step that edits one belong together; the wall
    counter two steps earlier does not, and including it brings back the
    duplicate `when CyberPi starts up` that crashed the robot.

    Whole steps are considered one at a time, nearest first, and every script in
    the chosen step that touches a missing name comes along. Taking only the
    first match would carry the joystick-up recorder and leave the joystick-left
    one behind, which is a route you can only drive in a straight line.
    """
    have, want = set(), set()
    # The injected My Blocks count as part of this step: `grip` is added to
    # any file that calls it, and it reads ARM_SHUT, so ARM_SHUT is this
    # step's dependency even though no script of its own mentions it.
    for node in list(own) + list(injected):
        c, i, r = script_state(node, kinds, defines)
        have |= c | i
        want |= r
    carried = []
    for _n, nodes in sorted(prior, key=lambda x: -x[0]):
        missing = want - have
        if not missing:
            break
        state = {id(nd): script_state(nd, kinds, defines) for nd in nodes
                 if not ncase(nd[0]).startswith("define ")}
        take = [nd for nd in nodes if id(nd) in state
                and (state[id(nd)][0] | state[id(nd)][1]) & missing]
        if not take:
            continue
        # Whole group to the front, keeping the order the step wrote them in:
        # steps are visited newest-first, so each earlier step lands above the
        # ones already collected — the order a student built them in.
        carried[:0] = take
        for nd in take:
            c, i, r = state[id(nd)]
            have |= c | i
            want |= r                         # it may need setting up in turn

    # Anything still missing lives in an EARLIER STAGE. The arm limits are the
    # real case: `grip` is injected grade-wide, and it reads ARM_SHUT, which
    # step 3 sets. Only flat setup scripts are eligible from outside the stage —
    # a script with a loop in it is a program, not an initialiser, and carrying
    # G7 step 12's speed dial into stage D would put a second `forever` on the
    # motors.
    for _n, nodes in sorted(outside, key=lambda x: -x[0]):
        missing = want - have
        if not missing:
            break
        for nd in nodes:
            if ncase(nd[0]).startswith("define ") or not is_setup(nd):
                continue
            c, i, r = script_state(nd, kinds, defines)
            if not ((c | i) & (want - have)):
                continue
            carried.insert(0, nd)
            have |= c | i
            want |= r
    return carried, sorted(want - have)


def merge_hats(carried, own):
    """Splice carried scripts in, folding any that share a hat with an own script.

    Two scripts under one hat is the whole bug this file exists to avoid. When a
    carried script has the same hat as one of the step's own — G8-D step 17 fills
    the vocabulary in `when CyberPi starts up`, step 19 runs the job loop in the
    same hat — the carried body goes IN FRONT of the own body, because setup runs
    before the loop and the loop never returns.
    """
    own_by_hat = {ncase(n[0]): n for n in own}
    out, folded = [], []
    for node in carried:
        hat = ncase(node[0])
        target = own_by_hat.get(hat)
        if target is None:
            out.append(node)
        else:
            target[1][:0] = node[1]           # prepend the carried body
            folded.append(hat)
    return out, folded


def build(project, steps, defines, check=False, prior=(), outside=()):
    """Compile ONE STEP into its own project. `steps` is a single-entry list.

    It used to be the whole stage — every step's scripts in one file — and that
    produced files nobody could upload. The steps in a stage are not cumulative:
    step 11 is a wall counter, step 12 a speed dial, step 13 a route recorder,
    each with its own `when CyberPi starts up`. Unioned, G7-C-remembers came out
    with three startup hats (two holding `forever` loops) and two handlers on
    button B, and the CyberPi died with a traceback on the first press.

    `defines` still spans the stage, so a step that CALLS a My Block built in an
    earlier step ships with that block's definition.
    """
    text = "\n".join(src for _, _, src in steps)
    p = Project(project, arg_kinds(defines, [text]))
    y, made, failed = 0, 0, []

    # Signatures first, bodies second: a define can call a block defined further
    # down, and a step can call one defined in a later step.
    for _, _, src in steps:
        for node in parse_tree(src):
            if ncase(node[0]).startswith("define "):
                p.register(node[0][len("define"):].strip())
    for name, node in defines.items():
        if re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", text):
            try:
                if p.stack([node], None, top=True, x=60, y=y):
                    y += script_h(node)
            except Fail:
                pass

    for n, title, src in steps:
        # Compile each script into a snapshot so a failure part-way through
        # leaves no half-built blocks behind — an orphan would corrupt the file.
        before = dict(p.blocks)
        own = parse_tree(src)
        injected = [nd for nm, nd in defines.items()
                    if re.search(r"(?<![\w-])" + re.escape(nm) + r"(?![\w-])", src)]
        carried, unmet = carry_forward(own, prior, p.arg_kinds, defines,
                                       outside, injected)
        carried, folded = merge_hats(carried, own)
        try:
            for node in carried + own:
                # A `define` already laid out above returns None instead of a
                # block id. Advancing y for it anyway left a script-sized hole
                # on the canvas for every custom block — three of them in
                # G8-A-05, which opened in mBlock looking like nothing but a
                # column of defines and a page of blank space.
                if p.stack([node], None, top=True, x=60, y=y):
                    y += script_h(node)
            made += 1
        except Fail as e:
            p.blocks.clear()
            p.blocks.update(before)
            failed.append((n, str(e)))
        build.last = {"carried": len(carried), "folded": folded, "unmet": unmet}
    return p, made, failed


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv
    groups = {}
    for g in (7, 8):
        for f in sorted((ROOT / "content" / f"grade{g}" / "steps").glob("*.yaml")):
            d = yaml.safe_load(f.read_text(encoding="utf-8"))
            if d.get("project") and d.get("code"):
                groups.setdefault(d["project"], []).append(
                    (d["n"], d["title"], d["code"]["source"]))
    defines = {}
    for steps in groups.values():
        for _, _, src in steps:
            for node in parse_tree(src):
                if ncase(node[0]).startswith("define "):
                    nm = Project.signature(node[0][len("define"):].strip())[0]
                    defines.setdefault(nm, node)

    # Clearing the directory is only safe on a FULL rebuild. Doing it before a
    # filtered run deleted every project and then wrote back only the filtered
    # one, which is a much worse outcome than a stale file.
    if not check and not args:
        for stale in OUT.glob("*.mblock"):
            stale.unlink()          # the per-stage files are gone; do not leave them

    ok = 0
    for proj in sorted(groups):
        # `G8-D-listens`, `G8-D` and `G8` all select; a bare step number does not.
        if args and not any(proj.startswith(a) for a in args):
            continue
        # G7 -> mBot2 container, G8 -> Rover container. Switched per project,
        # because the two grades are two different devices in mBlock.
        use_device(int(proj[1]))
        for i, (n, title, src) in enumerate(groups[proj]):
            name = step_file(proj, n)
            # Everything earlier in this stage, available to be carried forward
            # when this step reads state it does not create for itself.
            prior = [(pn, parse_tree(psrc)) for pn, _pt, psrc in groups[proj][:i]]
            # Earlier steps in OTHER stages of the same grade. Only flat setup
            # scripts are eligible from here — see carry_forward().
            outside = [(pn, parse_tree(psrc))
                       for oproj, osteps in groups.items()
                       if oproj != proj and oproj[:2] == proj[:2]
                       for pn, _pt, psrc in osteps if pn < n]
            p, made, failed = build(name, [(n, title, src)], defines, check,
                                    prior=prior, outside=outside)
            info = getattr(build, "last", {}) or {}
            scripts = sum(1 for b in p.blocks.values() if b.get("topLevel"))
            status = "OK " if not failed else "FAIL"
            extra = ""
            if info.get("carried"):
                extra += f"  +{info['carried']} carried"
            if info.get("folded"):
                extra += f"  ({len(info['folded'])} folded into own hat)"
            if info.get("unmet"):
                extra += f"  ⚠ still missing: {', '.join(info['unmet'])}"
            print(f"{status} {name:12s} step {n:2d} · {title[:34]:34s} "
                  f"{scripts:2d} scripts  {len(p.blocks):3d} blocks  "
                  f"{len(p.vars)} vars  {len(p.lists)} lists{extra}")
            for _n, line in failed:
                print(f"        omitted — {line!r}")
            if not check and made:
                p.write(OUT / f"{name}.mblock")
                ok += 1
    if not check:
        print(f"\nwrote {ok} .mblock files to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
