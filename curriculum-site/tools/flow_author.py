#!/usr/bin/env python3
"""Insert per-phase `use:` and `expect:` into a lesson's timed flow.

Surgical, not a YAML round-trip: these files were not written by PyYAML's
dumper, and re-dumping them reflows every paragraph in the repo. This edits only
the `steps:` block and leaves every other byte untouched.

    from flow_author import apply
    apply("content/grade7/steps/14.yaml", {
        0: {"expect": "..."},
        1: {"use": ["data_setvariableto"], "expect": "..."},
    })

Re-running is safe: previously inserted keys are replaced, not stacked.
"""
import re
import pathlib
import yaml

KEYS = ("use", "expect")
_KEYLINE = re.compile(r"^  (?:%s):" % "|".join(KEYS))


def _scalar(key, value, indent="  "):
    """`key: value`, wrapped the way the rest of the file is."""
    if isinstance(value, list):
        return [f"{indent}{key}: [{', '.join(value)}]"]
    text = yaml.dump({key: value}, allow_unicode=True, width=98,
                     default_flow_style=False, sort_keys=False).rstrip("\n")
    return [indent + l for l in text.split("\n")]


def _strip_existing(body):
    """Drop previously inserted use:/expect: lines and their wrapped remainder."""
    out, skip = [], False
    for l in body:
        if _KEYLINE.match(l):
            skip = True
            continue
        if skip:
            if l.startswith("    "):          # continuation of a wrapped scalar
                continue
            skip = False
        out.append(l)
    while out and not out[-1].strip():
        out.pop()
    return out


def apply(path, edits):
    p = pathlib.Path(path)
    lines = p.read_text(encoding="utf-8").split("\n")
    try:
        start = lines.index("steps:")
    except ValueError:
        raise SystemExit(f"{path}: no steps: block")
    end = next((i for i in range(start + 1, len(lines))
                if lines[i] and not lines[i].startswith((" ", "-"))), len(lines))
    heads = [i for i in range(start + 1, end) if re.match(r"^- time:", lines[i])]
    stray = set(edits) - set(range(len(heads)))
    if stray:
        raise SystemExit(f"{path}: {len(heads)} phases, no index {sorted(stray)}")
    bounds = heads + [end]
    out = lines[:start + 1]
    for n, h in enumerate(heads):
        body = _strip_existing(lines[h:bounds[n + 1]])
        for k in KEYS:
            if edits.get(n, {}).get(k):
                body += _scalar(k, edits[n][k])
        out += body
    out += lines[end:]
    p.write_text("\n".join(out), encoding="utf-8")
