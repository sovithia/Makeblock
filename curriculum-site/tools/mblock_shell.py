# -*- coding: utf-8 -*-
"""Refresh reference/mblock-shell/ from a project saved by the mBlock IDE.

The shell is everything in a .mblock that is not our blocks: the sprite list, the
device target, the stage assets, the extension declarations, `mscratch.json`, and
the version stamps. It is copied out of a real IDE save rather than written by
hand, because none of it is guessable — the code target is called `mbotneo`, the
extension list uses names like `cyberpi-cyberpi`, and both changed between 5.3
and 5.6.

Run this whenever the curriculum needs an extension the current shell does not
declare. In mBlock: new project, add the device, add the extension (`+ Extension`
under the block palette), drag one of its blocks onto the canvas so the editor
records it, delete the block again, save, then:

    .venv/bin/python tools/mblock_shell.py ~/Desktop/that-project.mblock

Everything else follows: tools/mblock_compile.py reads the extension registration
names straight out of the shell.
"""
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHELL = ROOT / "reference" / "mblock-shell"
KEEP = (".svg", ".wav", ".png", ".mp3")


def refresh(src):
    with zipfile.ZipFile(src) as z:
        names = z.namelist()
        for need in ("project.json", "mscratch.json", "mblock5"):
            if need not in names:
                raise SystemExit(f"{src.name} has no {need} — is it an mBlock save?")
        project = json.loads(z.read("project.json").decode("utf-8"))
        stamp = json.loads(z.read("mblock5").decode("utf-8"))

        blocks = {t["name"]: len(t.get("blocks", {})) for t in project["targets"]}
        for t in project["targets"]:
            t["blocks"], t["variables"], t["lists"] = {}, {}, {}
            t["broadcasts"], t["comments"] = {}, {}
        project["monitors"] = []

        if SHELL.exists():
            shutil.rmtree(SHELL)
        SHELL.mkdir(parents=True)
        (SHELL / "project.json").write_text(
            json.dumps(project, indent=1, ensure_ascii=False), encoding="utf-8")
        (SHELL / "mscratch.json").write_bytes(z.read("mscratch.json"))
        assets = [n for n in names if Path(n).suffix in KEEP]
        for n in assets:
            (SHELL / Path(n).name).write_bytes(z.read(n))

    print(f"shell refreshed from {src}")
    print(f"  mBlock {stamp.get('version')}   vm {project['meta'].get('vm')}")
    print(f"  targets    {', '.join(t['name'] for t in project['targets'])}"
          f"   (code was on: {', '.join(n for n, c in blocks.items() if c) or 'none'})")
    print(f"  extensions {project['extensions']}")
    print(f"  assets     {len(assets)}")
    dev = [t for t in project["targets"] if t.get("deviceId")]
    for t in dev:
        if t.get("loadedExtIds"):
            print(f"  {t['name']} loads {t['loadedExtIds']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: mblock_shell.py <project.mblock>")
    refresh(Path(sys.argv[1]).expanduser())
