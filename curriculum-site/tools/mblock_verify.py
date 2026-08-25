# -*- coding: utf-8 -*-
"""Structural check on generated .mblock files.

mBlock cannot be driven headlessly, so these files are verified against the sb3
invariants and against the schema of the eight official Makeblock lesson projects.
A pass here does not prove mBlock opens them; it proves the graph is not corrupt.
"""
import json, re, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
PROJ = ROOT / "site" / "assets" / "projects"
SHELL = ROOT / "reference" / "mblock-shell"
PALETTE = json.loads((ROOT / "reference" / "mblock-palette.json").read_text(encoding="utf-8"))

from mblock_compile import SHELLS, registration, use_device  # noqa: E402  one source of truth

# opcodes that are core sb3 and so absent from the extension palette
CORE_OK = {"procedures_definition", "procedures_prototype", "procedures_call",
           "argument_reporter_string_number", "argument_reporter_boolean",
           "data_variable", "data_listcontents"}


def check(path):
    errs, warns = [], []
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        for need in ("project.json", "mscratch.json", "mblock5"):
            if need not in names:
                errs.append(f"missing {need}")
        # Which shell this file came from decides which costumes it should carry;
        # the two devices ship different ones. Match against whichever shell's
        # asset set the file actually satisfies, and complain only if neither.
        shells = {name: {a.name for a in d.glob("*") if a.suffix in (".svg", ".wav")}
                  for name, d in SHELLS.items()}
        if not any(assets <= names for assets in shells.values()):
            short = min((sorted(assets - names) for assets in shells.values()), key=len)
            errs += [f"missing asset {a}" for a in short]
        if "project.json" not in names:
            return errs, warns, {}
        d = json.loads(z.read("project.json").decode("utf-8"))

    targets = {t.get("name"): t for t in d.get("targets", [])}
    # Which device this file is for is read off the file, not assumed: Grade 7 is
    # an mBot2 (`mbotneo`) and Grade 8 the Rover (`rover`), and both are valid.
    device = next((n for n in SHELLS if n in targets), None)
    if device is None:
        errs.append(f"no device target — expected one of {sorted(SHELLS)}")
    if "Stage" not in targets:
        errs.append("no Stage target")
    if device is None or "Stage" not in targets:
        return errs, warns, {}
    # the declared-extension check has to read the shell for THIS device
    use_device(7 if device == "mbotneo" else 8)
    DEVICE = device
    stage, dev = targets["Stage"], targets[DEVICE]
    blocks = dev.get("blocks", {})
    ids = set(blocks)
    # Variables and lists are global: mBlock declares them on the Stage, and a
    # device-local declaration does not show up in the editor at all.
    varids = set(stage.get("variables", {}))
    listids = set(stage.get("lists", {}))
    for t in d["targets"]:
        if not t.get("isStage") and (t.get("variables") or t.get("lists")):
            errs.append(f"{t.get('name')}: variables/lists belong on the Stage")
        if t.get("name") != DEVICE and t.get("blocks"):
            errs.append(f"{t.get('name')}: blocks belong on {DEVICE}")

    tops = 0
    for bid, b in blocks.items():
        op = b["opcode"]
        if op not in PALETTE and op not in CORE_OK and not op.startswith(
                tuple(k + "_" for k in PALETTE)):
            errs.append(f"{bid}: unknown opcode {op}")
        if b.get("topLevel"):
            tops += 1
            if b.get("parent") is not None:
                errs.append(f"{bid}: topLevel with a parent")
            if "x" not in b or "y" not in b:
                errs.append(f"{bid}: topLevel without x/y")
        else:
            if b.get("parent") is None:
                errs.append(f"{bid}: orphan (no parent, not topLevel)")
            elif b["parent"] not in ids:
                errs.append(f"{bid}: parent {b['parent']} does not exist")
        if b.get("next") and b["next"] not in ids:
            errs.append(f"{bid}: next {b['next']} does not exist")
        for slot, val in b.get("inputs", {}).items():
            ref = None
            if isinstance(val, list) and len(val) >= 2:
                if isinstance(val[1], str):
                    ref = val[1]
                elif isinstance(val[1], list) and val[1] and val[1][0] in (12, 13):
                    prim, name, vid = val[1][0], val[1][1], val[1][2]
                    pool = varids if prim == 12 else listids
                    if vid not in pool:
                        errs.append(f"{bid}: input {slot} references undeclared "
                                    f"{'variable' if prim == 12 else 'list'} {name}")
            if ref and ref not in ids:
                errs.append(f"{bid}: input {slot} points at missing block {ref}")
        for slot, f in b.get("fields", {}).items():
            if slot == "VARIABLE" and f[1] not in varids:
                errs.append(f"{bid}: field VARIABLE {f[0]} undeclared")
            if slot == "LIST" and f[1] not in listids:
                errs.append(f"{bid}: field LIST {f[0]} undeclared")
            # A dropdown holds one of the values mBlock defines for it, never the
            # label it shows and never a leftover parse sentinel.
            opts = (PALETTE.get(op) or {}).get("options", {}).get(slot)
            if opts and f[0] not in [v for _, v in opts]:
                errs.append(f"{bid}: field {slot} is {f[0]!r}, not one of "
                            f"{[v for _, v in opts][:6]}")
        for slot in b.get("inputs", {}):
            arg = (PALETTE.get(op) or {}).get("args", {}).get(slot) or {}
            if arg.get("type") == "image":
                errs.append(f"{bid}: {slot} is a decorative icon, not an input")
        if b.get("shadow") and b.get("opcode", "").endswith("_menu"):
            want = b["opcode"] + "_option"
            if want not in b.get("fields", {}):
                errs.append(f"{bid}: menu shadow lacks {want}")

    # Every extension a block comes from must be declared — under the
    # registration name mBlock uses, which is not the opcode prefix:
    # cyberpi -> cyberpi-cyberpi, and every mBuild sensor -> mbuild.
    declared = set(d.get("extensions", []))
    for op in (b["opcode"] for b in blocks.values()):
        if "." not in op:
            continue
        ext = op.split(".")[0]
        if registration(ext, declared) is None:
            errs.append(f"extension {ext} used but not declared in {sorted(declared)}")

    stats = {"scripts": tops, "blocks": len(blocks),
             "vars": len(varids), "lists": len(listids), "exts": len(declared)}
    errs += overlap_errors(dev.get("blocks", {}))
    errs += orphan_list_errors(dev.get("blocks", {}))
    errs += string_op_on_list_errors(dev.get("blocks", {}), stage)
    errs += loop_bound_errors(dev.get("blocks", {}))
    errs += live_only_errors(dev.get("blocks", {}), path)
    return errs, warns, stats


# Extensions that exist only while mBlock is driving the robot. Their blocks
# declare platform ["mblockpc","mblockweb"] and carry no MicroPython template,
# so in Upload mode they generate NOTHING and mBlock says nothing about it:
# `joystick LY` vanished mid-expression, leaving `mbot2.drive_speed( / 3, / 3)`,
# and `button L1 pressed?` collapsed to a bare `False`.
LIVE_ONLY_EXTS = ("bluetooth_controller",)
# Nothing in the course may carry a live-only block any more. The controller
# lesson (G8-12) was rewritten to use the CyberPi's own controls once it became
# clear the classroom has no laptops: the Bluetooth controller drives the robot
# from its own firmware, which needs no computer, but no uploaded program can
# read it. Keep this set EMPTY unless a lesson is deliberately taught tethered.
LIVE_MODE_PROJECTS = set()


def live_only_errors(blocks, path):
    """A project meant for upload must contain no live-mode-only blocks."""
    if path.stem in LIVE_MODE_PROJECTS:
        return []
    hits = sorted({blk["opcode"] for blk in blocks.values()
                   if isinstance(blk, dict)
                   and blk["opcode"].split(".")[0] in LIVE_ONLY_EXTS})
    return [f"{op} only works in Live mode — uploaded it compiles to nothing"
            for op in hits]


def loop_bound_errors(blocks):
    """`count with i` bounds must be a literal or a variable — never a reporter.

    mBlock rounds each bound by emitting `<bound> = int(<bound>) ...` before the
    loop, which assumes the bound is something you can assign to. Hand it a
    reporter and it writes `len(route_list) = ...`, a SyntaxError that mBlock
    reports only once the robot tries to run the program. The fix is to put the
    reporter in a variable first — and note mBlock's `to` is EXCLUSIVE, so a
    loop over a whole list wants `length + 1`.
    """
    out = []
    for blk in blocks.values():
        if not isinstance(blk, dict) or blk.get("opcode") != "control_for_new":
            continue
        for slot in ("start", "end", "step"):
            inp = (blk.get("inputs") or {}).get(slot)
            if not inp:
                continue
            ref = inp[1]
            # [12, name, id] is a variable; [4/6/7, "3"] a literal. A bare block
            # id means a reporter is plugged in, and that is the broken case.
            if isinstance(ref, str):
                op = blocks.get(ref, {}).get("opcode", ref)
                out.append(f"control_for_new {slot!r} is the reporter {op} — "
                           f"mBlock generates an unassignable rounding line for it; "
                           f"put it in a variable first")
    return out


def string_op_on_list_errors(blocks, stage):
    """A string operator must never be handed the NAME of a list.

    mBlock words `length of [STRING]` and `length of [LIST]` identically, and
    likewise `contains`. Picking the string block leaves a file that uploads
    cleanly and then misbehaves on the robot: `length of route` becomes
    len("route") == 5, so a loop bound by it runs five times over a list that
    may hold nothing, and the handler dies with IndexError. Silent in every
    check that came before this one, which is why it has its own.
    """
    names = {v[0] for v in (stage.get("lists") or {}).values()}
    out = []
    for blk in blocks.values():
        if not isinstance(blk, dict):
            continue
        for op, slot, right in (("operator_length", "STRING", "data_lengthoflist"),
                                ("operator_contains", "STRING1", "data_listcontainsitem")):
            if blk.get("opcode") != op:
                continue
            inp = (blk.get("inputs") or {}).get(slot)
            if inp and isinstance(inp[1], list) and inp[1][0] == 10 and inp[1][1] in names:
                out.append(f"{op} is given the list name {inp[1][1]!r} as a string "
                           f"— it should be {right}")
    return out


# Filling a list is `add` / `insert`. `delete all of` only empties it, and
# `delete n of` only shrinks it — neither puts anything in. For a variable the
# only real write is `set`: `change x by 1` reads x first, and a for-loop is the
# one block that assigns its own counter.
_FILL = {"data_addtolist", "data_insertatlist"}
_SET = {"data_setvariableto", "control_for_new", "control_for_each"}
_USE = {"data_itemoflist", "data_lengthoflist", "data_listcontainsitem",
        "data_itemnumoflist", "data_listcontents", "data_changevariableby",
        "data_variable"}


def _inline_refs(block):
    """Variables and lists referenced inline in inputs — [12,…] and [13,…].

    sb3 does not emit a block for a variable used as an input, it inlines a
    primitive. Checking only opcodes therefore sees almost no variable reads at
    all, which is exactly how this check passed while being blind.
    """
    out = set()
    for val in (block.get("inputs") or {}).values():
        for part in (val if isinstance(val, list) else []):
            if isinstance(part, list) and len(part) >= 2 and part[0] in (12, 13):
                out.add(part[1])
    return out


def orphan_list_errors(blocks):
    """A file must be able to produce the data it reads.

    Each project holds one step, so a step that reads state an EARLIER step sets
    up has to carry that earlier script with it. Without it the file uploads,
    runs, and does nothing useful — G7-C-14 offered undo and search over a route
    that nothing could record. See carry_forward() in tools/mblock_compile.py.
    """
    made, used = set(), set()
    for b in blocks.values():
        if not isinstance(b, dict):
            continue
        op = b.get("opcode", "").split(".")[-1]
        used |= _inline_refs(b)
        for slot, makers in (("LIST", _FILL), ("VARIABLE", _SET)):
            f = (b.get("fields") or {}).get(slot)
            if not f:
                continue
            if op in makers:
                made.add(f[0])
            elif op in _USE:
                used.add(f[0])
    return [f"{n!r} is read but nothing in this file ever sets or fills it"
            for n in sorted(used - made)]


# Canvas units. A stack block is 48 tall in scratch-blocks, a mouth is at least
# 24, and a C-block's closing arm is another 24.
ROW, ARM, MIN_MOUTH = 48, 24, 24


def stack_h(blocks, bid):
    """True height of the script hanging off bid, mouths and arms included."""
    h = 0
    while bid:
        b = blocks.get(bid)
        if not isinstance(b, dict):
            break
        h += ROW
        for key in ("SUBSTACK", "SUBSTACK2"):
            inp = (b.get("inputs") or {}).get(key)
            if not inp:                     # this block has no mouth at all
                continue
            sub = inp[1] if len(inp) > 1 and isinstance(inp[1], str) else None
            h += max(stack_h(blocks, sub) if sub else 0, MIN_MOUTH) + ARM
        bid = b.get("next")
    return h


def overlap_errors(blocks):
    """Scripts must not be dropped on top of each other.

    The compiler places each script by advancing y, and the advance is an
    estimate. When it under-measures, the next script lands inside the previous
    one — the file still verifies structurally and still runs, but it opens as an
    unreadable pile. Measuring the real height here is what makes the estimate
    safe to keep using.
    """
    tops = sorted(((b["y"], bid) for bid, b in blocks.items()
                   if isinstance(b, dict) and b.get("topLevel") and "y" in b))
    out = []
    for (y, bid), (ny, _) in zip(tops, tops[1:]):
        need = stack_h(blocks, bid)
        if ny - y < need:
            out.append(f"script at y={y} overlaps the next: needs {need}px, "
                       f"has {ny - y}px")
    return out


ASAR = Path("/Applications/mBlock.app/Contents/Resources/app.asar")


def check_core_opcodes():
    """Every hand-written `core` opcode must be a real opcode in the mBlock app.

    Extension blocks come out of exts.zip and are therefore true by construction.
    The core entries do not: CORE and CORE_FROM_MBLOCK in tools/mblock_palette.py
    are typed by hand, and a wrong guess compiles and verifies perfectly and then
    opens in the editor as a red "undefined: …" block. That is how
    `control_break` shipped — mBlock's own opcode is `control_break_new`.

    The app defines these in JS rather than in exts.zip, so grepping the asar for
    the literal opcode is a sound check. Skipped when mBlock is not installed.
    """
    if not ASAR.exists():
        return ["(mBlock not installed — core opcodes unverified)"], 0
    raw = ASAR.read_bytes()
    known = {k.decode() for k in
             set(re.findall(rb'opcode:"([a-zA-Z0-9_]+)"', raw))
             | set(re.findall(rb'"opcode"\s*:\s*"([a-zA-Z0-9_]+)"', raw))}
    core = {k: s for k, s in PALETTE.items() if s.get("core")}
    bad = sorted(f"{k}: opcode {s['opcode']!r} is not a real mBlock opcode"
                 for k, s in core.items() if s["opcode"] not in known)
    return bad, len(core)


def main():
    errs, n = check_core_opcodes()
    if errs and n:
        print(f"CORE OPCODES: {len(errs)} of {n} do not exist in mBlock")
        for e in errs:
            print("        ", e)
        return 1
    print(f"core opcodes: {n}/{n} confirmed against the mBlock app"
          if n else f"core opcodes: {errs[0]}")

    files = sorted(PROJ.glob("*.mblock"))
    if not files:
        print("no .mblock files")
        return 1
    bad = 0
    for f in files:
        errs, warns, st = check(f)
        tag = "ok  " if not errs else "FAIL"
        print(f"{tag} {f.name:24s} {st.get('scripts',0):3d} scripts "
              f"{st.get('blocks',0):4d} blocks  {st.get('vars',0)} vars "
              f"{st.get('lists',0)} lists  {st.get('exts',0)} exts")
        for e in errs[:8]:
            print("        ", e)
        if len(errs) > 8:
            print(f"         … and {len(errs)-8} more")
        bad += bool(errs)
    print(f"\n{len(files)-bad}/{len(files)} structurally valid")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
