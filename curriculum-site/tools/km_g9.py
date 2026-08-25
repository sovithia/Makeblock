# -*- coding: utf-8 -*-
"""Grade 9 Khmer: extract the translatable strings, and graft translations back.

Grade 9 was never translated -- content-km/grade9 held byte-identical English
copies. This walks the English YAML in a fixed order, pulls out exactly the
fields Grades 7-8 translate (plus parts notes, which they mostly left English),
and rebuilds the km file from the English structure so no field can be dropped
or reordered by hand.

  extract <nn>          print the ordered translatable strings for one session
  apply   <nn> <json>   graft a JSON list of translations back, in that order

Never translated, by policy inherited from Grades 7-8:
  code.source / code.lang   the programs are Python and stay Python
  result.scene / params     scene art carries hardcoded English captions anyway
  parts[].id, steps[].time  identifiers and durations
  grade.yaml                untranslated for every grade, not just this one
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "content" / "grade9" / "sessions"
KM = ROOT / "content-km" / "grade9" / "sessions"


def slots(d):
    """Yield (container, key) for every translatable string, in a fixed order."""
    def s(c, k):
        if isinstance(c, dict) and c.get(k):
            yield (c, k)
        elif isinstance(c, list) and isinstance(k, int):
            yield (c, k)

    yield from s(d, "title")
    yield from s(d, "goal")
    for i in range(len(d.get("builds_on") or [])):
        yield (d["builds_on"], i)
    for i in range(len(d.get("teach") or [])):
        yield (d["teach"], i)
    for g in d.get("guide") or []:
        yield from s(g, "label")
        yield from s(g, "value")
    for st in d.get("steps") or []:
        yield from s(st, "text")
    for i in range(len(d.get("tips") or [])):
        yield (d["tips"], i)
    for i in range(len(d.get("success") or [])):
        yield (d["success"], i)
    for p in d.get("parts") or []:
        yield from s(p, "note")
    lg = d.get("long")
    if lg:
        yield from s(lg, "goal")
        yield from s(lg.get("recap") or {}, "text")
        for e in lg.get("extend") or []:
            yield from s(e, "spec")
            yield from s(e, "text")
        yield from s(lg.get("log") or {}, "text")
        yield from s(lg.get("review") or {}, "text")
        for p in lg.get("parts") or []:
            yield from s(p, "note")
        for i in range(len(lg.get("success") or [])):
            yield (lg["success"], i)
    b = d.get("bonus")
    if b:
        yield from s(b, "kind")
        yield from s(b, "text")


def load(nn):
    return yaml.safe_load((EN / f"{nn}.yaml").read_text())


def main():
    cmd, nn = sys.argv[1], sys.argv[2]
    d = load(nn)
    if cmd == "extract":
        out = [c[k] for c, k in slots(d)]
        print(json.dumps(out, ensure_ascii=False, indent=1))
        print(f"# {len(out)} strings", file=sys.stderr)
        return
    if cmd == "apply":
        new = json.loads(Path(sys.argv[3]).read_text())
        sl = list(slots(d))
        if len(new) != len(sl):
            sys.exit(f"count mismatch: {len(new)} translations, {len(sl)} slots")
        for (c, k), v in zip(sl, new):
            c[k] = v
        KM.mkdir(parents=True, exist_ok=True)
        (KM / f"{nn}.yaml").write_text(
            yaml.safe_dump(d, allow_unicode=True, sort_keys=False,
                           width=100, default_flow_style=False))
        print(f"wrote {KM / f'{nn}.yaml'}")
        return
    sys.exit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
