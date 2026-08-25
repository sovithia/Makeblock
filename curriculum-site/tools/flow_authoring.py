#!/usr/bin/env python3
"""Authoring aid for per-phase blocks: what a lesson has, and what is new in it.

Usage:  tools/flow_authoring.py 7 14        one lesson, in detail
        tools/flow_authoring.py --todo      every lesson still missing use:/expect:
"""
import re, sys, glob, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "generator"))
import yaml, blocks


def load(g):
    return [yaml.safe_load(open(f, encoding="utf-8"))
            for f in sorted(glob.glob(f"content/grade{g}/steps/*.yaml"))]


def first_seen_map(units):
    fs = {}
    for u in units:
        src = (u.get("code") or {}).get("source")
        if not src:
            continue
        for k, _spec in blocks.spec_index(blocks.teaching_source(src)).items():
            fs.setdefault(k, u["n"])
    return fs


def detail(g, n):
    units = load(g)
    fs = first_seen_map(units)
    u = next(x for x in units if x["n"] == n)
    src = (u.get("code") or {}).get("source") or ""
    idx = blocks.spec_index(src)
    used = {k for st in u["steps"] for k in (st.get("use") or [])}
    print(f"G{g}-{n:02d}  {u['title']}   ({u.get('concept','')})")
    print(f"  NEW in this lesson:")
    for k in idx:
        if fs.get(k) == n:
            print(f"     {'✓' if k in used else ' '} {k}")
    print(f"  carried in from earlier:")
    for k in idx:
        if fs.get(k) != n:
            print(f"     {'✓' if k in used else ' '} {k}  (first seen step {fs.get(k)})")
    print("  flow:")
    for i, st in enumerate(u["steps"]):
        mark = "·" if (st.get("use") or st.get("expect")) else "!"
        print(f"   {mark} [{i}] {st['time']:>4s}  {' '.join(st['text'].split())[:88]}")
        if st.get("use"):
            print(f"          use:    {st['use']}")
        if st.get("expect"):
            print(f"          expect: {' '.join(st['expect'].split())[:88]}")


def todo():
    tot = done = 0
    for g in (7, 8):
        for u in load(g):
            phases = u.get("steps") or []
            n_ok = sum(1 for st in phases if st.get("expect"))
            tot += len(phases); done += n_ok
            if n_ok < len(phases):
                print(f"  G{g}-{u['n']:02d}  {n_ok}/{len(phases)} phases done  · {u['title'][:40]}")
    print(f"\n  {done}/{tot} phases carry an expected result")


if __name__ == "__main__":
    if "--todo" in sys.argv:
        todo()
    else:
        detail(int(sys.argv[1]), int(sys.argv[2]))


def dump(g, lo, hi):
    units = load(g); fs = first_seen_map(units)
    for u in units:
        if not (lo <= u["n"] <= hi):
            continue
        src = (u.get("code") or {}).get("source") or ""
        idx = blocks.spec_index(src)
        new = [k for k in idx if fs.get(k) == u["n"]]
        old = [k for k in idx if fs.get(k) != u["n"]]
        print(f"\n### G{g}-{u['n']:02d} {u['title']} | concept: {u.get('concept','')}")
        print(f"NEW: {new}")
        print(f"OLD: {old}")
        for i, st in enumerate(u["steps"]):
            print(f"  [{i}] {st['time']} {' '.join(st['text'].split())}")


# Blocks that belong to the safety preamble every launch script now carries —
# a message and a five-second delay so an upload cannot drive the robot off the
# desk. They are scaffolding, not a taught idea, so they are explained in the
# teacher tip rather than given a slot in the timed flow.
PREAMBLE = {"control_wait"}


def audit():
    """Every `use:` key must exist in that lesson's own code, and every block
    a lesson meets for the first time should be shown somewhere in its flow."""
    bad = missed = 0
    for g in (7, 8):
        units = load(g); fs = first_seen_map(units)
        for u in units:
            src = blocks.teaching_source((u.get("code") or {}).get("source") or "")
            idx = blocks.spec_index(src)
            used = [k for st in u["steps"] for k in (st.get("use") or [])]
            for k in used:
                if k not in idx:
                    print(f"  ✗ G{g}-{u['n']:02d}: use: {k} is not in this lesson's code")
                    bad += 1
            for k in idx:
                if k in PREAMBLE:
                    continue
                if fs.get(k) == u["n"] and k not in used:
                    print(f"  ! G{g}-{u['n']:02d}: {k} is NEW here but no phase shows it")
                    missed += 1
            for st in u["steps"]:
                if not st.get("expect"):
                    print(f"  ✗ G{g}-{u['n']:02d}: a phase has no expected result")
                    bad += 1
    print(f"\n  {bad} errors · {missed} unexplained new blocks")
    return bad


# What each `check:` trigger requires the program to actually have.
CHECK_NEEDS = {"on": "when CyberPi starts up", "A": "when button A pressed",
               "B": "when button B pressed", "up": "pulled↑", "down": "pulled↓",
               "left": "pulled←", "right": "pulled→", "mid": "middle pressed",
               "hear": None, "light": None, "see": None}
GATE = "wait until  button  A  pressed?"


def promises():
    """The EXPECTED RESULT panel must describe what the program actually does.

    Three ways it drifts, all of which happened: a `check:` row names a trigger
    the program does not have; a row says `on` when the launch script waits for a
    button; or `success:` still claims the thing starts at power-up after a start
    gate was added. Scenes are judged by eye — this only catches the mechanical
    contradictions.
    """
    bad = 0
    for g in (7, 8):
        for u in load(g):
            src = (u.get("code") or {}).get("source") or ""
            if not src:
                continue
            gated = GATE in src
            hats = [s.strip().split("\n")[0] for s in src.split("\n\n")]
            for c in (u.get("check") or []):
                do = str(c.get("do", "see"))
                if do not in CHECK_NEEDS:
                    print(f"  ! G{g}-{u['n']:02d}: check do={do!r} is not a known trigger")
                    bad += 1
                    continue
                need = CHECK_NEEDS[do]
                # a gated launch script IS started by A, without an A hat
                if need and not any(need in h for h in hats) and not (do == "A" and gated):
                    print(f"  ! G{g}-{u['n']:02d}: check do={do!r} but the program has no {need!r}")
                    bad += 1
                if do == "on" and gated:
                    print(f"  ! G{g}-{u['n']:02d}: check do='on' but the launch script waits for A")
                    bad += 1
            # the same stale claim hides in goal:, build: and the prose
            claim = re.compile(r"starts? (on|at) power[- ]up|on power[- ]up|starts itself", re.I)
            fields = [("goal", [u.get("goal", "")]), ("build", [u.get("build", "")]),
                      ("success", u.get("success") or []), ("teach", u.get("teach") or []),
                      ("tips", u.get("tips") or [])]
            for name, texts in fields:
                for t in texts:
                    if gated and claim.search(str(t)):
                        print(f"  ! G{g}-{u['n']:02d}: {name} claims a power-up start — {str(t)[:50]!r}")
                        bad += 1
    print(f"  {bad} expected-result contradictions" if bad
          else "  every check row matches a real trigger in its program")
    return bad
