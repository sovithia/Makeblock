#!/usr/bin/env python3
"""Language-switch invariants for the built site. Run after build.py.

    ../.venv/bin/python tools/check_language.py

Two things have to hold, and neither is visible by looking at one page:

1. Every page carries exactly one switch, and it points at *its own* counterpart
   in the other locale tree — not at that tree's front page. The two trees are
   built from one generator and mirror each other file for file, so the
   counterpart always exists; this catches the day that stops being true.

2. No other link crosses between the trees. That is what makes a chosen language
   stick: "next step", "all grades" and the search hits are all relative, so once
   a reader is in site/km/ every click keeps them there. A single absolute or
   ../-too-many href would silently dump them back into English.
"""
import re
import sys
from pathlib import Path

SITE = (Path(__file__).resolve().parents[1] / "site")
KM = SITE / "km"
SEG = r'(?:<span class="on"[^>]*>[^<]*</span>|<a [^>]*>[^<]*</a>)'
TOGGLE = re.compile(r'<span class="langtog"[^>]*>(?:' + SEG + r'){2}</span>')


def counterpart(page):
    """The same page in the other tree."""
    rel = page.relative_to(SITE)
    return SITE / (rel.relative_to("km") if rel.parts[0] == "km" else Path("km") / rel)


def main():
    pages = sorted(SITE.rglob("*.html"))
    if not pages:
        sys.exit(f"no pages under {SITE} — run generator/build.py first")
    bad, links = [], 0

    for page in pages:
        html = page.read_text(encoding="utf-8")
        in_km = page.resolve().is_relative_to(KM)


        # --- 1. exactly one switch, aimed at this page's own counterpart
        found = TOGGLE.findall(html)
        if len(found) != 1:
            bad.append(f"{page}: {len(found)} language switches, want 1")
        else:
            tog = TOGGLE.search(html).group(0)
            active = re.findall(r'<span class="on" lang="(\w+)">', tog)
            href = re.findall(r'href="([^"]+)"', tog)
            want = "km" if in_km else "en"
            if active != [want]:
                bad.append(f"{page}: switch marks {active} active, want ['{want}']")
            elif len(href) != 1:
                bad.append(f"{page}: switch has {len(href)} links, want 1")
            elif (page.parent / href[0]).resolve() != counterpart(page).resolve():
                bad.append(f"{page}: switch -> {href[0]}, not its own counterpart")

        # --- 2. every other link stays inside this page's tree
        for m in re.finditer(r'<a ([^>]*)href="([^"]+)"([^>]*)>', html):
            href = m.group(2)
            if href.startswith(("javascript:", "#", "http", "mailto:")):
                continue
            if "${" in href:
                continue            # the search-hit template in SEARCH_JS, not a link
                                    # (it interpolates body[data-root], so hits stay in-tree)
            if "hreflang=" in m.group(1) + m.group(3):
                continue                      # the switch, crossing on purpose
            target = (page.parent / href.split("#")[0]).resolve()
            links += 1
            if not target.exists():
                bad.append(f"{page}: dead link -> {href}")
            elif "assets" in target.parts:
                continue                      # shared across locales by symlink
            elif target.is_relative_to(KM) != in_km:
                bad.append(f"{page}: link leaves its language -> {href}")

    for b in bad:
        print("FAIL", b)
    print(f"{len(pages)} pages · {links} in-tree links · "
          + ("OK" if not bad else f"{len(bad)} PROBLEMS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
