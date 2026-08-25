# -*- coding: utf-8 -*-
"""Render curriculum block scripts as scratch-blocks-accurate SVG.

mBlock 5's editor is built on scratch-blocks, so replicating scratch-blocks'
own geometry constants and path fragments (block_render_svg_vertical.js) gives
genuinely IDE-shaped output rather than an approximation of one.

Structure comes from the palette, not from guesswork: tools/mblock_compile.py
already resolves a curriculum line to (opcode, template, typed slot values)
against reference/mblock-palette.json, and that resolution is reused verbatim
here — so a block is drawn exactly as it compiles. A line the resolver cannot
place falls back to the flat pill, which is also where mblock_compile reports a
content error, so the two disagree in the same places and nowhere else.

Importing this is optional: generator/blocks.py degrades to the old pill
rendering if the palette or the resolver is unavailable, so the site still
builds on a machine that has neither.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import mblock_compile as M          # noqa: E402  palette + resolver
# blocks.py imports this module lazily, from inside render(), so this direction
# of the pair is a plain top-level import and the cycle never closes.
import blocks as B                  # noqa: E402  category colours

# ---------------------------------------------------------------- geometry
# scratch-blocks/core/block_render_svg_vertical.js, GRID_UNIT = 4.
GRID = 4
CORNER = 1 * GRID                     # CORNER_RADIUS
# scratch-blocks is a touch UI and pads accordingly — MIN_BLOCK_Y is 12 units
# there. On paper that padding is the whole page budget: at 48 units a Grade 4
# session ran to three pages and tripped tools/verify_chrome.sh. These are the
# tightest values that still print inside two pages with the label at 6.6pt.
# The notch, corner and hat geometry is untouched, so the silhouette is intact;
# only the empty space around the label is smaller than the editor's.
ROW_H = 9 * GRID                      # MIN_BLOCK_Y — a plain stack bar
FIELD_H = 6 * GRID                    # FIELD_HEIGHT — an inset input
# Horizontal metrics stay at scratch-blocks' own values. A script wider than its
# column is scaled to fit, so its printed height is set by the aspect ratio —
# narrowing a block makes it TALLER on the page. Only the vertical metrics above
# are compressed; squeezing these too made grade 6 print worse, not better.
PAD_X = 4 * GRID                      # inner left/right padding
GAP = 2 * GRID                        # SEP_SPACE_X between parts
FONT = 12                             # FIELD_TEXT_FONTSIZE
NOTCH_START = 3 * GRID                # NOTCH_START_PADDING
NOTCH_W = 36                          # width of the notch path below
HAT_H = 16                            # START_HAT rise
MOUTH_X = 4 * GRID                    # C-block spine width
CBOT_H = 5 * GRID                     # C-block closing arm
MOUTH_MIN = 5 * GRID                  # an empty mouth still has a height

NOTCH_L = ("c 2,0 3,1 4,2 l 4,4 c 1,1 2,2 4,2 h 12 "
           "c 2,0 3,-1 4,-2 l 4,-4 c 1,-1 2,-2 4,-2")
NOTCH_R = ("c -2,0 -3,1 -4,2 l -4,4 c -1,1 -2,2 -4,2 h -12 "
           "c -2,0 -3,-1 -4,-2 l -4,-4 c -1,-1 -2,-2 -4,-2")
HAT_PATH = "c 25,-22 71,-22 96,0"

# ---------------------------------------------------------------- text metrics
# Helvetica-Bold AFM widths, 1/1000 em. No browser is available at build time
# and the print harness runs through WeasyPrint, so widths are computed rather
# than measured.
_AFM = {
    " ": 278, "!": 333, '"': 474, "#": 556, "$": 556, "%": 889, "&": 722,
    "'": 238, "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333,
    ".": 278, "/": 278, ":": 333, ";": 333, "<": 584, "=": 584, ">": 584,
    "?": 611, "@": 975, "[": 333, "\\": 278, "]": 333, "^": 584, "_": 556,
    "`": 333, "{": 389, "|": 280, "}": 389, "~": 584,
    "A": 722, "B": 722, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778,
    "H": 722, "I": 278, "J": 556, "K": 722, "L": 611, "M": 833, "N": 722,
    "O": 778, "P": 667, "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722,
    "V": 667, "W": 944, "X": 667, "Y": 667, "Z": 611,
    "a": 556, "b": 611, "c": 556, "d": 611, "e": 556, "f": 333, "g": 611,
    "h": 611, "i": 278, "j": 278, "k": 556, "l": 278, "m": 889, "n": 611,
    "o": 611, "p": 611, "q": 611, "r": 389, "s": 556, "t": 333, "u": 611,
    "v": 556, "w": 778, "x": 556, "y": 556, "z": 500,
}
for _d in "0123456789":
    _AFM[_d] = 556


def measure(text, size=FONT):
    return sum(_AFM.get(c, 600) for c in text) * size / 1000.0


# ---------------------------------------------------------------- colour
def _darken(hex_color, f):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))


def tertiary(c):
    """Scratch's tertiary colour — the outline and the dropdown-chip fill."""
    return _darken(c, 0.80)


# ---------------------------------------------------------------- model
# A node is a dict: shape, color, parts, kids. A part is one of
#   ("text", s) ("field", s, kind) ("menu", s) ("sub", node) ("icon",)
BOOL_OPS = {"operator_or", "operator_and", "operator_not", "operator_equals",
            "operator_gt", "operator_lt", "operator_contains"}
_INFIX_BOOL = [(t, op) for t, op, _a, _b in M.INFIX if op in BOOL_OPS]


# mBlock declares a menu once and reuses it across variants of the same block:
# `[DIRECTION] at [POWER] RPM` carries no options, while its sibling
# `[DIRECTION] at [POWER] RPM for [TIME] secs` lists all four. Same extension,
# same slot name, same dropdown — so borrow it, or the block renders with a
# typed-in text field where the editor shows a menu.
_MENU_BY_SLOT = {}
for _s in M.PALETTE.values():
    for _slot, _opts in _s["menus"].items():
        if _opts:
            _MENU_BY_SLOT.setdefault((_s["ext"], _slot), _opts)

# Core sb3 blocks whose field is a dropdown in the editor but which carry no
# menu in the extension palette, because they are not extension blocks.
_CORE_MENU_SLOTS = {("data_setvariableto", "VARIABLE"),
                    ("data_changevariableby", "VARIABLE"),
                    ("data_addtolist", "LIST"), ("data_deleteoflist", "LIST"),
                    ("data_deletealloflist", "LIST"), ("data_showlist", "LIST"),
                    ("data_hidelist", "LIST"),
                    ("data_insertatlist", "LIST"), ("data_replaceitemoflist", "LIST"),
                    ("data_itemoflist", "LIST"), ("data_lengthoflist", "LIST"),
                    ("data_listcontainsitem", "LIST"), ("data_itemnumoflist", "LIST")}


def _slot_kind(spec, slot):
    if spec["menus"].get(slot):
        return "menu"
    if (spec["opcode"], slot) in _CORE_MENU_SLOTS:
        return "menu"
    if _MENU_BY_SLOT.get((spec["ext"], slot)):
        return "menu"
    return "value"


# A decorative icon slot is named `ICON` or `image_2` — bare, or numbered. Not
# any slot merely beginning with those letters: `imageData` on the Magic emoji
# blocks is a real picture input, and matching it dropped the slot entirely, so
# `Set AI Emojis to [imageData]` drew with nothing to set it to.
_ICON_SLOT = re.compile(r"^(icon|image)(_\d+)?$", re.I)


def _is_icon(slot, val):
    return not val and bool(_ICON_SLOT.match(slot))


def expr_node(body):
    """A (...) body -> reporter / boolean / variable node."""
    inner, groups = M.split_holes(body)
    padded = f" {inner} "
    for tok, op in _INFIX_BOOL:
        if tok in padded:
            left, _, right = inner.partition(tok)
            # The curriculum writes predicates with a trailing question mark —
            # `(heard) contains (item (i) of commands) ?` — and it belongs to the
            # block's label, not to the operand. Leaving it on stops the operand
            # from resolving, exactly as it does in the compiler.
            right, mark = right.strip(), ""
            if right.endswith("?"):
                right, mark = right[:-1].strip(), " ?"
            parts = [_operand(left, groups), ("text", tok.strip()),
                     _operand(right, groups)]
            if mark:
                parts.append(("text", "?"))
            return {"shape": "boolean", "color": B.COLORS["operators"],
                    "parts": parts, "kids": []}
    for tok, op, _a, _b in M.INFIX:
        if op not in BOOL_OPS and tok in padded:
            left, _, right = inner.partition(tok)
            return {"shape": "reporter", "color": B.COLORS["operators"],
                    "parts": [_operand(left, groups), ("text", tok.strip()),
                              _operand(right, groups)], "kids": []}

    hit, hgroups = M.resolve(body)
    if hit and not hgroups:
        inner, groups = body, []          # raw reading won; holes were not used
    if hit:
        node = node_from_hit(hit, groups)
        # a predicate reads as a question, and mBlock draws those as hexagons
        pred = hit[1]["opcode"] in BOOL_OPS or "?" in hit[1]["template"]
        node["shape"] = "boolean" if pred else "reporter"
        # Prefer the resolved block's real drawer colour. Wording is only a
        # fallback: reporter templates such as `letter [n] of [text]` contain
        # mostly fields, and their remaining word alone is not enough to infer
        # that they belong to Operators.
        node["color"] = (hit[1].get("cateColor")
                         or B.color(M.HOLE_RX.sub("", inner).strip()))
        return node
    if M.HOLE_RX.fullmatch(inner.strip()):
        return expr_node(groups[int(M.HOLE_RX.fullmatch(inner.strip()).group(1))])
    if M.HOLE_RX.search(inner):
        return {"shape": "reporter", "color": B.color(_unhole(inner, groups)),
                "parts": _mixed(inner, groups), "kids": []}
    # a bare name the student defined — a variable reporter
    return {"shape": "reporter", "color": B.COLORS["variables"],
            "parts": [("text", inner.strip())], "kids": []}


def _unhole(text, groups):
    return M.HOLE_RX.sub(lambda x: "(" + groups[int(x.group(1))] + ")", text)


def _mixed(text, groups):
    """Text with holes in it, as alternating literal / reporter parts.

    Reached when a slot holds prose around a reporter and the whole thing is
    not itself a block — `join ok, (item i of commands)`. Without this the
    sentinel characters leak into the label.
    """
    parts, last = [], 0
    for m in M.HOLE_RX.finditer(text):
        lit = text[last:m.start()].strip()
        if lit:
            parts.append(("field", lit, "str"))
        parts.append(("sub", expr_node(groups[int(m.group(1))])))
        last = m.end()
    tail = text[last:].strip()
    if tail:
        parts.append(("field", tail, "str"))
    return parts


def _operand(text, groups):
    text = text.strip()
    m = M.HOLE_RX.fullmatch(text)
    if m:
        return ("sub", expr_node(groups[int(m.group(1))]))
    if M.HOLE_RX.search(text):
        return ("sub", expr_node(_unhole(text, groups)))
    # A zero-input reporter can be written directly on one side of an operator:
    # `(loudness > 60)`. It has no parentheses of its own for split_holes() to
    # preserve, so resolve it here instead of drawing it as a white text field.
    # Unknown names still fall through as fields/variables.
    hit, nested = M.resolve(text)
    if hit and not nested and hit[1].get("blockType") in (
            "number", "string", "boolean", "reporter"):
        return ("sub", expr_node(text))
    return ("field", text, "num" if M.NUM.match(text) else "str")


def _slot_part(spec, slot, raw, groups):
    raw = (raw or "").strip()
    if _is_icon(slot, raw):
        return None
    if _slot_kind(spec, slot) == "menu":
        return ("menu", raw)
    m = M.HOLE_RX.fullmatch(raw)
    if m:
        return ("sub", expr_node(groups[int(m.group(1))]))
    if M.HOLE_RX.search(raw):
        # a slot holding an expression, e.g. `wait until [(dist) < 10]`
        full = M.HOLE_RX.sub(lambda x: "(" + groups[int(x.group(1))] + ")", raw)
        return ("sub", expr_node(full))
    return ("field", raw, "num" if M.NUM.match(raw) else "str")


def node_from_hit(hit, groups):
    _key, spec, vals = hit
    parts, last = [], 0
    for m in M.SLOT.finditer(spec["template"]):
        lit = spec["template"][last:m.start()].strip()
        if lit:
            parts.append(("text", lit))
        p = _slot_part(spec, m.group(1), vals.get(m.group(1), ""), groups)
        if p:
            parts.append(p)
        last = m.end()
    tail = spec["template"][last:].strip()
    if tail:
        parts.append(("text", tail))
    return {"shape": "stack", "color": None, "parts": parts, "kids": [],
            "opcode": spec["opcode"]}


# Control blocks never resolve through find_block: the palette template for a
# C-block includes its [SUBSTACK] slot, which no source line ever carries. The
# compiler solves this with its own CTL table (Project.CTL) and this mirrors it,
# so both agree on what `if … then` means.
CTL = [
    (re.compile(r"^if\s+(?P<c>.*?)\s+then$", re.I), "control_if", "if", "then"),
    (re.compile(r"^else$", re.I), "control_else", "else", None),
    (re.compile(r"^repeat until\s+(?P<c>.*)$", re.I),
     "control_repeat_until", "repeat until", None),
    (re.compile(r"^wait until\s+(?P<c>.*)$", re.I),
     "control_wait_until", "wait until", None),
    (re.compile(r"^while\s+(?P<c>.*?)(?:\s+repeat)?$", re.I),
     "control_while", "while", "repeat"),
    (re.compile(r"^repeat\s+(?P<n>\d+)$", re.I), "control_repeat", "repeat", None),
    (re.compile(r"^forever$", re.I), "control_forever", "forever", None),
    (re.compile(r"^break$", re.I), "control_break_new", "break", None),
    (re.compile(r"^continue$", re.I), "control_continue_new", "continue", None),
]


def control_node(text):
    t = re.sub(r"\s+", " ", text.strip())
    for rx, op, head, tail in CTL:
        m = rx.match(t)
        if not m:
            continue
        parts = [("text", head)]
        if "c" in (m.groupdict() or {}):
            cond = m.group("c")
            holed, groups = M.split_holes(cond)
            parts.append(("sub", expr_node(cond)) if holed.strip()
                         else ("field", "", "str"))
        elif "n" in (m.groupdict() or {}):
            parts.append(("field", m.group("n"), "num"))
        if tail:
            parts.append(("text", tail))
        shape = "c" if op in M.C_BLOCKS or op == "control_else" else "stack"
        return {"shape": shape, "color": B.COLORS["control"], "parts": parts,
                "kids": [], "opcode": op}
    return None


def node_for_line(text, kids):
    node = control_node(text)
    if node:
        node["kids"] = kids
        return node
    # resolve(), not find_block(): it tries the holed reading, then the RAW one
    # when the holed match drops a sentinel into a dropdown. `recognize (4)
    # English 3 secs` is exactly that case — "(4) English" is one menu label, and
    # holing it out renders the dropdown as the sentinel itself.
    hit, groups = M.resolve(text)
    color = B.color(text)
    if not hit:
        # Not every line is a palette block, and most of the ones that are not
        # still are blocks: a My Block the students defined (`celebrate`), and
        # the informal block wording Grades 4-6 are written in. Draw the real
        # silhouette in the right category colour and carry the line as its
        # label — only the inner slot detail is unavailable, not the shape.
        if text.strip().startswith("#"):
            return {"shape": "comment", "color": color,
                    "parts": [("text", text.strip().lstrip("#").strip())],
                    "kids": kids}
        return {"shape": "c" if B.is_wrapper(text) else "stack", "color": color,
                "parts": [("text", text.strip())], "kids": kids}
    node = node_from_hit(hit, groups)
    # Once a line resolves to a real palette block, its drawer is authoritative
    # for colour. Wording guesses misclassify blocks such as `show variable` as
    # Display and `hide variable` as a custom block.
    node["color"] = hit[1].get("cateColor") or color
    if node["opcode"] in M.C_BLOCKS:
        node["shape"] = "c"
    elif re.match(r"^\s*when\b", text, re.I) or "when_" in node["opcode"]:
        node["shape"] = "hat"
    node["kids"] = kids
    return node


def tree(source, carried=frozenset()):
    """Nested source -> render nodes, with `else` folded into its `if`.

    The curriculum writes `if … then` and `else` as sibling lines, but mBlock
    draws one block with two mouths. Rendering them as siblings would show a
    shape that does not exist in the editor.
    """
    counter = [0]

    def walk(nodes):
        out = []
        for t, k in nodes:
            # Pre-order index, assigned before descending, so it lines up with
            # the flat source order the diff was computed on.
            idx = counter[0]
            counter[0] += 1
            n = node_for_line(t, walk(k))
            n["old"] = idx in carried
            if (n.get("opcode") == "control_else" and out
                    and out[-1].get("opcode") == "control_if"):
                prev = out[-1]
                prev["opcode"] = "control_if_else"
                prev["shape"] = "cc"
                prev["kids2"] = n["kids"]
                continue
            out.append(n)
        return out
    return walk(M.parse_tree(source))


# ---------------------------------------------------------------- layout
def measure_parts(parts):
    """Width of one row's content, and the height of its tallest part."""
    w, h = 0.0, FONT * 1.2
    for i, p in enumerate(parts):
        if i:
            w += GAP
        if p[0] == "text":
            w += measure(p[1])
        elif p[0] == "field":
            w += max(FIELD_H, measure(p[1]) + 2 * GRID + 8)
            h = max(h, FIELD_H)
        elif p[0] == "menu":
            w += measure(p[1]) + 2 * GRID + 8 + 12      # + caret
            h = max(h, FIELD_H)
        elif p[0] == "swatch":
            w += FIELD_H * 1.5 * len(p[1])
            h = max(h, FIELD_H)
        else:
            layout(p[1])
            w += p[1]["w"]
            h = max(h, p[1]["h"])
    return w, h


def layout(node):
    cw, ch = measure_parts(node["parts"])
    shape = node["shape"]
    if shape in ("reporter", "boolean"):
        pad = PAD_X if shape == "boolean" else 3 * GRID
        node["w"] = cw + 2 * pad
        node["h"] = max(FIELD_H, ch + 2 * GRID)
        node["rowh"] = node["h"]
        return node

    if shape == "comment":
        node["w"], node["rowh"] = cw, 5 * GRID
        node["h"] = node["rowh"]
        return node

    node["rowh"] = max(ROW_H, ch + 4 * GRID)
    body_w = cw + 2 * PAD_X
    if shape == "hat":
        body_w = max(body_w, 96)
    node["w"] = max(body_w, NOTCH_START + NOTCH_W + PAD_X)

    for k in node["kids"]:
        layout(k)
    stack_h = sum(k["h"] for k in node["kids"])

    # A block's own width is its own content. It is NOT widened to fit the
    # blocks in its mouth or below it — in mBlock a `forever` wrapping a long
    # block stays narrow and the child overhangs it.
    if shape == "c":
        node["mouth"] = max(MOUTH_MIN, stack_h)
        node["h"] = node["rowh"] + node["mouth"] + CBOT_H
    elif shape == "cc":
        node["mouth"] = max(MOUTH_MIN, stack_h)
        for k in node.get("kids2", []):
            layout(k)
        node["mouth2"] = max(MOUTH_MIN,
                             sum(k["h"] for k in node.get("kids2", [])))
        node["elserow"] = 8 * GRID
        node["h"] = (node["rowh"] + node["mouth"] + node["elserow"]
                     + node["mouth2"] + CBOT_H)
    elif shape == "hat":
        node["h"] = HAT_H + node["rowh"] + stack_h
    else:
        node["h"] = node["rowh"] + stack_h
    return node


def bbox_w(node):
    """Widest point of a node including anything overhanging it."""
    w = node["w"]
    if node["shape"] in ("c", "cc"):
        for k in node["kids"] + node.get("kids2", []):
            w = max(w, MOUTH_X + bbox_w(k))
    else:
        for k in node["kids"]:
            w = max(w, bbox_w(k))
    return w


# ---------------------------------------------------------------- emit
def _esc(s):
    # Last line of defence. A sentinel that reaches here is a resolver reading we
    # did not anticipate; showing the original bracketed text is wrong-looking but
    # readable, where "\x000\x00" is neither.
    s = M.HOLE_RX.sub("(…)", s)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def path_stack(w, h, top_notch=True, hat=False):
    p = [f"M {CORNER},{HAT_H if hat else 0}"]
    if hat:
        p.append(HAT_PATH)
        p[0] = f"M 0,{HAT_H}"
    else:
        p.append(f"H {NOTCH_START}")
        if top_notch:
            p.append(NOTCH_L)
        else:
            p.append(f"h {NOTCH_W}")
    p.append(f"H {w - CORNER}")
    y0 = HAT_H if hat else 0
    p.append(f"a {CORNER},{CORNER} 0 0 1 {CORNER},{CORNER}")
    p.append(f"V {h - CORNER}")
    p.append(f"a {CORNER},{CORNER} 0 0 1 {-CORNER},{CORNER}")
    p.append(f"H {NOTCH_START + NOTCH_W}")
    p.append(NOTCH_R)
    p.append(f"H {CORNER}")
    p.append(f"a {CORNER},{CORNER} 0 0 1 {-CORNER},{-CORNER}")
    p.append(f"V {y0 + CORNER}")
    if not hat:
        p.append(f"a {CORNER},{CORNER} 0 0 1 {CORNER},{-CORNER}")
    p.append("Z")
    return " ".join(p)


def _mouth(w, top, bot):
    """Right edge down into a mouth, round the spine, and back out.

    The mouth's TOP edge carries the notch — that is where the first block
    inside snaps on. Its bottom edge is flat, as in the editor.
    """
    return [f"V {top - CORNER}",
            f"a {CORNER},{CORNER} 0 0 1 {-CORNER},{CORNER}",
            f"H {MOUTH_X + NOTCH_START + NOTCH_W}", NOTCH_R,
            f"H {MOUTH_X + CORNER}",
            f"a {CORNER},{CORNER} 0 0 0 {-CORNER},{CORNER}",
            f"V {bot - CORNER}",
            f"a {CORNER},{CORNER} 0 0 0 {CORNER},{CORNER}",
            f"H {w - CORNER}",
            f"a {CORNER},{CORNER} 0 0 1 {CORNER},{CORNER}"]


def _close(w, h):
    return [f"V {h - CORNER}",
            f"a {CORNER},{CORNER} 0 0 1 {-CORNER},{CORNER}",
            f"H {NOTCH_START + NOTCH_W}", NOTCH_R, f"H {CORNER}",
            f"a {CORNER},{CORNER} 0 0 1 {-CORNER},{-CORNER}",
            f"V {CORNER}", f"a {CORNER},{CORNER} 0 0 1 {CORNER},{-CORNER}", "Z"]


def path_c(w, rowh, mouth, h):
    p = [f"M {CORNER},0", f"H {NOTCH_START}", NOTCH_L, f"H {w - CORNER}",
         f"a {CORNER},{CORNER} 0 0 1 {CORNER},{CORNER}"]
    p += _mouth(w, rowh, rowh + mouth)
    p += _close(w, h)
    return " ".join(p)


def path_cc(w, rowh, mouth, elserow, mouth2, h):
    p = [f"M {CORNER},0", f"H {NOTCH_START}", NOTCH_L, f"H {w - CORNER}",
         f"a {CORNER},{CORNER} 0 0 1 {CORNER},{CORNER}"]
    p += _mouth(w, rowh, rowh + mouth)
    p += _mouth(w, rowh + mouth + elserow,
                rowh + mouth + elserow + mouth2)
    p += _close(w, h)
    return " ".join(p)


def path_reporter(w, h):
    r = h / 2.0
    return (f"M {r},0 H {w - r} a {r},{r} 0 0 1 0,{h} H {r} "
            f"a {r},{r} 0 0 1 0,{-h} Z")


def path_boolean(w, h):
    r = h / 2.0
    return (f"M {r},0 H {w - r} L {w},{r} L {w - r},{h} H {r} L 0,{r} Z")


def emit_parts(parts, x, y, rowh, out):
    """Lay parts out on one row; y is the row's top."""
    cx = x
    for i, p in enumerate(parts):
        if i:
            cx += GAP
        if p[0] == "text":
            out.append(f'<text class="bl" x="{cx:.1f}" y="{y + rowh / 2:.1f}">'
                       f'{_esc(p[1])}</text>')
            cx += measure(p[1])
        elif p[0] == "field":
            w = max(FIELD_H, measure(p[1]) + 2 * GRID + 8)
            fy = y + (rowh - FIELD_H) / 2
            r = FIELD_H / 2 if p[2] == "num" else CORNER
            out.append(f'<rect class="bf" x="{cx:.1f}" y="{fy:.1f}" '
                       f'width="{w:.1f}" height="{FIELD_H}" rx="{r}"/>')
            out.append(f'<text class="bft" x="{cx + w / 2:.1f}" '
                       f'y="{fy + FIELD_H / 2:.1f}">{_esc(p[1])}</text>')
            cx += w
        elif p[0] == "menu":
            tw = measure(p[1])
            w = tw + 2 * GRID + 8 + 12
            fy = y + (rowh - FIELD_H) / 2
            out.append(f'<rect class="bm" x="{cx:.1f}" y="{fy:.1f}" '
                       f'width="{w:.1f}" height="{FIELD_H}" rx="{CORNER}"/>')
            out.append(f'<text class="bl" x="{cx + GRID + 4:.1f}" '
                       f'y="{fy + FIELD_H / 2:.1f}">{_esc(p[1])}</text>')
            ax = cx + w - 12
            ay = fy + FIELD_H / 2
            out.append(f'<path class="bc" d="M {ax:.1f},{ay - 2:.1f} '
                       f'l 8,0 l -4,5 Z"/>')
            cx += w
        elif p[0] == "swatch":
            # a colour picker: mBlock fills it with the colour rather than
            # leaving it blank, and the LED ring shows five of them in a row
            sw = FIELD_H * 1.5
            fy = y + (rowh - FIELD_H) / 2
            for j, col in enumerate(p[1]):
                # `.bf` fills white from the stylesheet, and a rule beats a
                # presentation attribute — the colour has to be inline
                out.append(f'<rect class="bf" style="fill:{col}" '
                           f'x="{cx + j * sw:.1f}" y="{fy:.1f}" '
                           f'width="{sw:.1f}" height="{FIELD_H}" rx="{CORNER}"/>')
            cx += sw * len(p[1])
        else:
            node = p[1]
            ny = y + (rowh - node["h"]) / 2
            emit(node, cx, ny, out)
            cx += node["w"]


def emit(node, x, y, out):
    shape = node["shape"]
    col = node["color"]
    stroke = tertiary(col)
    # Blocks carried over from the previous step are dimmed, so the eye lands
    # on what this lesson actually adds. Children are emitted as siblings in the
    # SVG, so a new block inside an old loop still reads at full strength.
    fade = ' opacity="0.32"' if node.get("old") else ""
    out.append(f'<g transform="translate({x:.1f},{y:.1f})"{fade}>')

    if shape in ("reporter", "boolean"):
        d = (path_reporter if shape == "reporter" else path_boolean)(
            node["w"], node["h"])
        out.append(f'<path d="{d}" fill="{col}" stroke="{stroke}"/>')
        pad = PAD_X if shape == "boolean" else 3 * GRID
        emit_parts(node["parts"], pad, 0, node["h"], out)
        out.append("</g>")
        return

    if shape == "comment":
        out.append(f'<text class="bcm" x="0" y="{node["rowh"] / 2:.1f}">'
                   f'{_esc(node["parts"][0][1])}</text>')
        out.append("</g>")
        emit_children(node, x, y + node["rowh"], out)
        return

    if shape in ("c", "cc"):
        if shape == "c":
            d = path_c(node["w"], node["rowh"], node["mouth"], node["h"])
        else:
            d = path_cc(node["w"], node["rowh"], node["mouth"],
                        node["elserow"], node["mouth2"], node["h"])
        out.append(f'<path d="{d}" fill="{col}" stroke="{stroke}"/>')
        emit_parts(node["parts"], PAD_X, 0, node["rowh"], out)
        if shape == "cc":
            ey = node["rowh"] + node["mouth"]
            emit_parts([("text", "else")], PAD_X, ey, node["elserow"], out)
        out.append("</g>")
        cy = y + node["rowh"]
        for k in node["kids"]:
            emit(k, x + MOUTH_X, cy, out)
            cy += k["h"]
        if shape == "cc":
            cy = y + node["rowh"] + node["mouth"] + node["elserow"]
            for k in node.get("kids2", []):
                emit(k, x + MOUTH_X, cy, out)
                cy += k["h"]
        return

    hat = shape == "hat"
    body_h = node["rowh"] + (HAT_H if hat else 0)
    d = path_stack(node["w"], body_h, hat=hat)
    out.append(f'<path d="{d}" fill="{col}" stroke="{stroke}"/>')
    emit_parts(node["parts"], PAD_X, HAT_H if hat else 0, node["rowh"], out)
    out.append("</g>")
    emit_children(node, x, y + body_h, out)


def emit_children(node, x, y, out):
    cy = y
    for k in node["kids"]:
        emit(k, x, cy, out)
        cy += k["h"]


CSS = """
/* width/height are in mm and the viewBox carries the aspect ratio, so a narrow
   column scales the whole script down rather than clipping or distorting it */
.bsvg { display: block; max-width: 100%; height: auto; margin-bottom: 2.5mm;
        break-inside: avoid; page-break-inside: avoid; }
.bl { font: 600 12px "Helvetica Neue", Helvetica, Arial, sans-serif;
      fill: #fff; dominant-baseline: central; }
.bft { font: 600 12px "Helvetica Neue", Helvetica, Arial, sans-serif;
       fill: #575e75; dominant-baseline: central; text-anchor: middle; }
.bf { fill: #fff; stroke: rgba(0,0,0,.15); }
.bm { fill: rgba(0,0,0,.18); stroke: none; }
.bc { fill: #fff; }
.bcm { font: italic 500 11px "Helvetica Neue", Helvetica, Arial, sans-serif;
       fill: #64748b; dominant-baseline: central; }
.bsvg path { stroke-width: 1; }
"""


# mm per scratch-blocks pixel — set by the print budget, not by taste. It sat at
# 0.180 (a 6.1pt label) for one reason: grade 6 session 7 ran to three pages and
# tripped tools/verify_chrome.sh. Grades 4-6 were archived on 2026-08-19, so that
# constraint is gone and the label is back at 6.6pt.
#
# Lowering this is always safe for pagination — width and height scale together,
# so the aspect ratio, and therefore the height of any script already being
# scaled down to fit its column, does not change. RAISING it can push a session
# onto another page, and can push a single script past the height of one page.
# Re-run the gate and check the tallest script either way.
MM_PER_PX = 0.194


def _flat(source):
    """Indented source as a list of (depth, text) — the shape a diff needs."""
    out = []
    for line in source.splitlines():
        if line.strip():
            out.append(((len(line) - len(line.lstrip())) // 2, line.strip()))
    return out


def carried_lines(source, prev):
    """Line keys this step inherits unchanged from the previous step.

    Steps hold the whole project, not a delta, so by the last step of a stage
    most of what is on the page was built two lessons ago. Dimming those is the
    difference between a page a teacher can read at a glance and a wall of
    blocks. difflib on (depth, text) pairs, so a block that moved into a loop
    counts as new — its indentation changed, and so did its meaning.
    """
    if not prev:
        return set()
    a, b = _flat(prev), _flat(source)
    same = set()
    sm = __import__("difflib").SequenceMatcher(a=a, b=b, autojunk=False)
    for op, _i1, _i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            same |= set(range(j1, j2))
    return same


def render(source, mm_per_px=MM_PER_PX, prev=None):
    """One block script as a self-contained, print-safe SVG.

    Sized in mm rather than px: the site and the print harness are both mm-based
    and no browser is available at build time, so the SVG must carry its own
    physical size instead of relying on layout to give it one.
    """
    # ONE SVG PER SCRIPT, not one for the whole stack. An SVG is an unbreakable
    # box: once the steps became cumulative, a stage's last step reached 405mm of
    # blocks, which no page can hold and no print engine can split. Per-script
    # images let the page break between scripts instead of clipping.
    nodes = [layout(n) for n in tree(source, carried_lines(source, prev))]
    parts = []
    for n in nodes:
        out = []
        emit(n, 1, 1, out)
        w, h = bbox_w(n) + 4, n["h"] + 4
        parts.append(f'<svg class="bsvg" width="{w * mm_per_px:.2f}mm" '
                     f'height="{h * mm_per_px:.2f}mm" '
                     f'viewBox="0 0 {w:.0f} {h:.0f}">' + "".join(out) + "</svg>")
    return "".join(parts)


def height_mm(source, mm_per_px=MM_PER_PX):
    """Total rendered height of every script, for page-budget checks."""
    nodes = [layout(n) for n in tree(source)]
    return sum(n["h"] + 4 for n in nodes) * mm_per_px


def tallest_mm(source, mm_per_px=MM_PER_PX):
    """The tallest single script — the one thing that cannot be broken up."""
    nodes = [layout(n) for n in tree(source)]
    return max([(n["h"] + 4) * mm_per_px for n in nodes], default=0)


def width_mm(source, mm_per_px=MM_PER_PX):
    """Natural width, before any scaling down to fit a column.

    The caller needs this to decide WHERE to put a script: shrinking a wide one
    into a narrow column shrinks its labels with it, and a block whose label
    cannot be read is worse than no picture.
    """
    nodes = [layout(n) for n in tree(source)]
    return (max([bbox_w(n) for n in nodes], default=0) + 4) * mm_per_px

# ---------------------------------------------------- blank (palette) blocks
# The shape of a block, for drawing it as it sits in the palette: empty, with no
# values filled in. exts.zip records blockType for every extension block; the
# core sb3 ones carry None and are listed here instead.
_CORE_SHAPE = {
    "control_forever": "c", "control_repeat": "c", "control_if": "c",
    "control_if_else": "cc", "control_while": "c", "control_repeat_until": "c",
    "control_for_new": "c", "control_for_each": "c", "control_else": "c",
    "control_wait": "stack", "control_wait_until": "stack", "control_stop": "stack",
    "control_break_new": "stack", "control_continue_new": "stack",
    "operator_gt": "boolean", "operator_lt": "boolean", "operator_equals": "boolean",
    "operator_and": "boolean", "operator_or": "boolean", "operator_not": "boolean",
    "operator_contains": "boolean", "data_listcontainsitem": "boolean",
    "data_variable": "reporter", "data_listcontents": "reporter",
    "data_itemoflist": "reporter", "data_itemnumoflist": "reporter",
    "data_lengthoflist": "reporter",
}
_TYPE_SHAPE = {"hat": "hat", "command": "stack",
               "number": "reporter", "string": "reporter", "boolean": "boolean"}


# The CyberPi's five-LED ring is a custom face-panel widget, not a slot with a
# declared default, so its colours were read off a screenshot of the real
# palette rather than out of exts.zip.
LED_RING_SLOT = "ledRing"
LED_RING = ["#bf2828", "#eaaa45", "#f5e852", "#92d148", "#7ce0c4"]


def blank_node(spec):
    """One palette block with nothing filled in — inputs empty, menus on default.

    Drawn from the template rather than from a source line, because the point is
    the block as the student meets it in the sidebar: `moves forward ( ) cm`, not
    somebody else's 10.
    """
    parts, last = [], 0
    tmpl = spec["template"]
    for m in M.SLOT.finditer(tmpl):
        lit = tmpl[last:m.start()].strip()
        if lit:
            parts.append(("text", lit))
        slot = m.group(1)
        if _is_icon(slot, ""):
            last = m.end()
            continue
        if _slot_kind(spec, slot) == "menu":
            # mBlock shows a placeholder name in an empty variable/list
            # dropdown rather than a blank chip.
            opts = (spec["menus"].get(slot)
                    or _MENU_BY_SLOT.get((spec["ext"], slot))
                    or ["my list" if slot == "LIST" else
                        "my variable" if slot == "VARIABLE" else " "])
            parts.append(("menu", str(opts[0])))
        else:
            arg = ((spec.get("args") or {}).get(slot) or {})
            t = arg.get("type") or "string"
            kind = "num" if str(t).lower() in (
                "number", "positive", "whole", "integer", "angle", "note") else "str"
            # `showDefaults` draws the block the way the toolbox does, with the
            # factory values already in the slots (`roll 1 LEDs`, `R 255 G 0 B 0`)
            # rather than empty. Nothing in the catalogue sets it, so the lesson
            # pages keep their blanks for the student to fill in.
            if slot == LED_RING_SLOT:
                parts.append(("swatch", LED_RING if spec.get("showDefaults")
                              else ["#ffffff"] * 5))
            elif str(t).lower() == "color":
                parts.append(("swatch", [str(arg.get("default") or "#d0021b")]
                              if spec.get("showDefaults") else ["#ffffff"]))
            elif spec.get("showDefaults") and arg.get("default") not in (None, ""):
                parts.append(("field", str(arg["default"]).strip('"'), kind))
            else:
                parts.append(("field", "", kind))
        last = m.end()
    tail = tmpl[last:].strip()
    if tail:
        parts.append(("text", tail))

    op = spec["opcode"]
    if op == "control_if_else":
        # its template ends "… then else"; the second mouth's label is drawn by
        # the renderer, so the word must not also sit in the parts
        parts = [p for p in parts if not (p[0] == "text" and p[1].strip() == "else")]
        if parts and parts[-1][0] == "text":
            parts[-1] = ("text", parts[-1][1].replace("then else", "then").strip())
    shape = ("c" if (spec.get("branchCount") or 0) > 0
             else _TYPE_SHAPE.get(spec.get("blockType"))
             or _CORE_SHAPE.get(op)
             or ("boolean" if "?" in tmpl else "stack"))
    # Colour from the block as it READS, not from the raw template. Stripping the
    # brackets off `[ICON]when CyberPi starts up` leaves "ICONwhen CyberPi starts
    # up", which matches no rule in _CATS and fell through to My Blocks pink —
    # so every hat and half the display blocks came out the wrong colour while
    # their category heading, computed from these same parts, was right.
    label = " ".join(p[1] for p in parts if p[0] in ("text", "menu")).strip()
    # `paletteColor` is the drawer colour straight out of mBlock's own toolbox
    # definitions. Nothing in the catalogue carries it, so the site is unaffected;
    # tools/export_block_images.py sets it so a reference sheet matches the real
    # palette exactly, including the blocks whose wording guesses wrong (`set
    # brush color` is not a Variables block, `audio speed` is not a sensor).
    # `stop [all]` has only the word "stop" in its text parts; its option is a
    # field. The wording-based fallback therefore mistakes it for My Blocks.
    # mBlock renders this core Control block in the normal Control orange.
    color = ("#ffab19" if op == "control_stop"
             else spec.get("paletteColor") or B.color(label or op))
    return {"shape": shape,
            "color": color,
            "parts": parts or [("text", label or op)], "kids": [],
            "kids2": [], "old": False, "opcode": op, "label": label}


def render_blank(spec, mm_per_px=MM_PER_PX):
    """A single palette block, empty, as its own SVG."""
    n = layout(blank_node(spec))
    out = []
    emit(n, 1, 1, out)
    w, h = bbox_w(n) + 4, n["h"] + 4
    return (f'<svg class="bsvg" width="{w * mm_per_px:.2f}mm" '
            f'height="{h * mm_per_px:.2f}mm" viewBox="0 0 {w:.0f} {h:.0f}">'
            + "".join(out) + "</svg>")


def blank_width_mm(spec, mm_per_px=MM_PER_PX):
    return (bbox_w(layout(blank_node(spec))) + 4) * mm_per_px


def block_of(line):
    """(key, spec) for one source line — the block it uses, values discarded.

    The key identifies the block across the whole course, so `moves forward 10cm`
    and `moves forward 25cm` are one block seen twice, not two. A block the
    students define themselves has no palette entry, so a spec is synthesised
    from its signature and it comes out in the My Blocks colour.
    """
    t = " ".join(str(line).split())
    if not t or t.startswith("#"):
        return None, None
    if t.lower().startswith("define "):
        name, args = M.Project.signature(t[7:].strip())
        tmpl = name + "".join(f" [{a}]" for a in args)
        return "my:" + name, {"ext": "myblocks", "opcode": "my:" + name,
                              "template": tmpl, "slots": list(args), "menus": {},
                              "args": {a: {"type": "string"} for a in args},
                              "blockType": "command", "branchCount": 0}
    ctl = control_node(t)
    if ctl and ctl["opcode"] not in ("control_wait_until",):
        spec = next((v for v in M.PALETTE.values() if v["opcode"] == ctl["opcode"]), None)
        if spec:
            return ctl["opcode"], spec
    hit, _g = M.resolve(t)
    if hit:
        return hit[1]["opcode"], hit[1]
    name = t.split()[0]
    return "my:" + name, {"ext": "myblocks", "opcode": "my:" + name,
                          "template": name, "slots": [], "menus": {}, "args": {},
                          "blockType": "command", "branchCount": 0}


def _fold_else(flat):
    """`if … then` + a sibling `else` are ONE block in the palette.

    The curriculum writes them as two lines, so a naive walk offers the student
    an `if` and a separate `else` — two blocks that do not both exist. Where an
    `else` follows at the same depth, the pair is reported as `control_if_else`
    and the `else` line is dropped.
    """
    out = []
    for i, (depth, text) in enumerate(flat):
        low = " ".join(text.split()).lower()
        if low == "else":
            continue                      # already accounted for by its `if`
        if re.match(r"^if\b.*\bthen$", low):
            nxt = next((d for d, t in flat[i + 1:] if d <= depth), None)
            sib = next(((d, t) for d, t in flat[i + 1:] if d <= depth), None)
            if sib and sib[0] == depth and " ".join(sib[1].split()).lower() == "else":
                out.append((depth, text, "control_if_else"))
                continue
        out.append((depth, text, None))
    return out


def blocks_used(source):
    """[(key, spec)] for a script, in first-appearance order, deduped."""
    seen, out = set(), []
    for _depth, text, force in _fold_else(_flat(source)):
        if force:
            spec = next((v for v in M.PALETTE.values() if v["opcode"] == force), None)
            k = force
        else:
            k, spec = block_of(text)
        if not k or spec is None or k in seen:
            continue
        seen.add(k)
        out.append((k, spec))
    return out
