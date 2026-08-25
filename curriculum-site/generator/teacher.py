# -*- coding: utf-8 -*-
"""Teacher-solution rendering: answer projects and finished block scripts.

The student lesson gives a goal, the blocks for each phase and the result to aim
at; the finished arrangement is the part the class is meant to work out. The
solution renderer appends that arrangement and its saved mBlock project to the
same page, after a forced print-page break.

The .mblock files are not copied: the compiler's canonical files remain under
`site/assets/projects/` and the merged lesson links to them directly.
"""
import shutil

import blocks
import i18n
import render

PRINT_CSS = """
@page { size: A4; margin: 12mm 13mm; }
/* Each lesson is a table so that its heading lives in a <thead>, which the
   print engine repeats on every page the lesson spills onto. Late lessons
   carry a whole stage's cumulative script and genuinely need two sheets;
   without this, sheet two is a page of anonymous blocks. */
.tsheet { width: 100%; border-collapse: collapse; break-after: page;
  padding-bottom: 4mm; }
.tsheet:last-child { break-after: auto; }
.tsheet > thead > tr > td { padding: 0; }
.tsheet > tbody > tr > td { padding: 0 0 4mm 0; }
.thead { display: flex; align-items: baseline; gap: 3mm; margin-bottom: 1.5mm;
  padding-bottom: 1.2mm; border-bottom: 1.5px solid #e2e8f0; }
.tno { font-size: 8pt; font-weight: bold; text-transform: uppercase;
  letter-spacing: 1px; color: #64748b; }
.tti { font-size: 12pt; font-weight: bold; }
.tmeta { font-size: 8.4pt; color: #64748b; margin-bottom: 2.5mm; }
.tmeta code { background: #f1f5f9; border-radius: 3px; padding: 0 1.2mm;
  font-size: 8pt; }
.trow { display: flex; flex-wrap: wrap; gap: 2mm 4mm; align-items: center;
  margin-bottom: 2.5mm; font-size: 8.6pt; }
.tdl { display: inline-block; font-weight: bold; text-decoration: none;
  border: 1.2px solid currentColor; border-radius: 5px; padding: 0.8mm 2.4mm; }
.tnew { font-size: 8.4pt; color: #334155; margin: 0 0 2.5mm 0; }
.tnew b { color: #16a34a; }
.tlist { width: 100%; border-collapse: collapse; font-size: 9pt; }
.tlist th { text-align: left; font-size: 7.4pt; text-transform: uppercase;
  letter-spacing: 0.08em; color: #64748b; padding: 1.4mm 2mm; }
.tlist td { padding: 1.6mm 2mm; border-top: 1px solid #eef2f7;
  vertical-align: baseline; }
.tlist tr.cp td { background: #fffbeb; }
.tlist code { font-size: 8.4pt; background: #f1f5f9; border-radius: 3px;
  padding: 0 1.2mm; }
.tnote { border-left: 3px solid #f59e0b; background: #fffbeb; padding: 2mm 3mm;
  border-radius: 0 6px 6px 0; font-size: 8.8pt; margin-bottom: 4mm; }
.tgrid { display: flex; flex-wrap: wrap; gap: 4mm; }
.tcard { flex: 1 1 78mm; border: 1px solid #e2e8f0; border-radius: 9px;
  padding: 3mm 3.5mm; }
.tcard h3 { margin: 0 0 1mm 0; font-size: 12pt; }
@media print { .noprint { display: none } }
.inline-solution { break-before: page; page-break-before: always; margin-top: 8mm; }
.inline-solution .tsheet { break-after: auto; }
.solution-head { border-left: 4px solid #f59e0b; background: #fffbeb;
  border-radius: 0 8px 8px 0; padding: 3mm 4mm; margin-bottom: 4mm; }
.solution-head h2 { margin: 0 0 1mm 0; font-size: 16pt; }
.solution-head p { margin: 0; font-size: 8.8pt; color: #64748b; }
@media print {
  html.student-copy .inline-solution { display: none !important; }
  html.solution-copy body > :not(.inline-solution) { display: none !important; }
  html.solution-copy .inline-solution { break-before: auto; page-break-before: auto;
    margin-top: 0; }
}
"""


def _script(s):
    """The finished arrangement for one lesson, drawn at full strength.

    Deliberately NOT dimmed against the previous step. The student page fades
    carried-over blocks to show what today adds, but a sheet a teacher may hand
    out has to be readable on its own, and half a page of pale blocks is not.
    What is new is named in the line above instead.
    """
    src = (s.get("code") or {}).get("source")
    if not src or s["code"].get("lang") != "blocks":
        return ""
    return blocks.render(src)


def _new_here(s, first_seen, notes):
    """One line per block this lesson meets for the first time."""
    src = (s.get("code") or {}).get("source")
    if not src:
        return ""
    idx = blocks.spec_index(src)
    fresh = [k for k in idx if first_seen.get(k) == s["n"]]
    if not fresh:
        return ""
    bits = []
    for k in fresh:
        # the block as it reads in the palette, not its opcode — a teacher
        # scanning this line is looking for something they can point at
        label = blocks.block_label(idx[k]) or k
        note = (notes or {}).get(k)
        bits.append(f'<code>{render.esc(label)}</code>'
                    + (f' — {note}' if note else ""))
    return f'<p class="tnew"><b>{i18n.t("blocks_new")}</b> ' + " · ".join(bits) + "</p>"


def _sheet(c, s, ctx, first_seen, notes, projects_rel):
    """One lesson: heading, project file, new blocks, the whole script."""
    f = ctx.get("step_file")
    dl = (f'<a class="tdl" style="color:{c["dark"]}" '
          f'href="{projects_rel}{f}.mblock">{i18n.t("download")}</a>'
          if f and ctx.get("has_file") else
          f'<span class="muted">{i18n.t("not_built_yet")}</span>')
    kind = ctx.get("kind", "step")
    label = (i18n.t("checkpoint_n", n=i18n.num(ctx["cp_no"])) if kind == "checkpoint"
             else i18n.t("step_n", n=i18n.num(s["n"])))
    script = _script(s)
    if not script:
        outcomes = "".join(f"<li>{x}</li>" for x in s.get("success", []))
        script = (f'<div class="solution-outcomes"><b>'
                  f'{i18n.t("expected_completed_result")}</b><ul>{outcomes}</ul></div>')
    return (f'<table class="tsheet"><thead><tr><td>'
            f'<div class="thead"><span class="tno" style="color:{c["dark"]}">{label}</span>'
            f'<span class="tti">{render.esc(s["title"])}</span>'
            + (f'<span class="tno">{render.esc(f)}</span>' if f else "")
            + f'</div></td></tr></thead><tbody><tr><td>'
            f'<div class="tmeta">{render.esc(s.get("concept", ""))}</div>'
            f'<div class="trow noprint">{dl}</div>'
            f'{_new_here(s, first_seen, notes)}'
            f'{script}</td></tr></tbody></table>')


def inline_solution(c, s, ctx, first_seen, notes, projects_rel):
    """The teacher answer appended to the public lesson's printable page."""
    return (f'<section class="inline-solution">'
            f'<div class="solution-head"><h2>{i18n.t("teacher_solution")}</h2>'
            f'<p>{i18n.t("teacher_solution_note")}</p></div>'
            f'{_sheet(c, s, ctx, first_seen, notes, projects_rel)}'
            f'</section>')


# Where a teacher page reaches the one canonical copy of the projects. Both
# locales use the same string: an en page sits at site/teacher/gradeN/ and a km
# page at site/km/teacher/gradeN/, and site/km/assets symlinks to ../assets.
PROJECTS = "../../assets/projects/"


def build(site, grades):
    """Write site/teacher/. `grades` is {n: {grade, steps, rows, first_seen, notes}}."""
    out = site / "teacher"
    # a copy made by an earlier build, back when this tree carried its own
    shutil.rmtree(out / "projects", ignore_errors=True)

    def write(path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    cards = []
    for gnum in sorted(grades):
        g = grades[gnum]
        c = render.grade_c(g["grade"])
        gname = i18n.t("grade_n", n=i18n.num(gnum))
        steps, rows = g["steps"], g["rows"]
        fs, notes = g["first_seen"], g["notes"]
        nfiles = sum(1 for _s, ctx in rows if ctx.get("has_file"))

        # --- the lesson index for this grade
        trs = []
        for s, ctx in rows:
            f = ctx.get("step_file")
            dl = (f'<a href="{PROJECTS}{f}.mblock">{i18n.t("download")}</a>'
                  if f and ctx.get("has_file")
                  else f'<span class="muted">—</span>')
            cls = ' class="cp"' if ctx.get("kind") == "checkpoint" else ""
            trs.append(
                f'<tr{cls}><td>{s["n"]}</td>'
                f'<td><a href="step-{s["n"]:02d}.html">{render.esc(s["title"])}</a></td>'
                f'<td class="muted">{render.esc(s.get("concept",""))}</td>'
                f'<td>{f"<code>{render.esc(f)}</code>" if f else ""}</td>'
                f'<td>{dl}</td></tr>')
        body = (f'<div class="sess"><div class="shead" style="background:linear-gradient'
                f'(110deg,{c["dark"]},{c["color"]})"><div class="sno">'
                f'{i18n.t("teacher_kicker")}</div><h2>'
                f'{i18n.t("grade_n", n=i18n.num(gnum))} · {render.esc(g["grade"]["theme"])}'
                f'</h2></div>'
                f'<div class="trow noprint">'
                f'<a class="tdl" style="color:{c["dark"]}" href="print.html">'
                f'{i18n.t("teacher_print_all")}</a>'
                f'<span class="muted">{i18n.t("teacher_files_n", n=nfiles)}</span></div>'
                f'<table class="tlist"><tr><th>#</th><th>{i18n.t("teacher_lesson")}</th>'
                f'<th>{i18n.t("concept")}</th><th>{i18n.t("project")}</th>'
                f'<th>{i18n.t("teacher_file")}</th></tr>{"".join(trs)}</table></div>')
        write(out / f"grade{gnum}" / "index.html",
              render.page(f"G{gnum} · {i18n.t('teacher_title')}", render.css(c),
                          _chrome(f"teacher/grade{gnum}/index.html", "..")
                          + body, f"<style>{PRINT_CSS}</style>"))

        # --- one page per lesson, and the printable set
        # each lesson carries its neighbours, so a teacher can walk the course
        # the same way the class does
        for s, ctx in rows:
            s["_ctx"] = ctx
        sheets = []
        for i, (s, ctx) in enumerate(rows):
            sheet = _sheet(c, s, ctx, fs, notes, PROJECTS)
            sheets.append(sheet)
            prev = rows[i - 1][0] if i else None
            nxt = rows[i + 1][0] if i + 1 < len(rows) else None
            write(out / f"grade{gnum}" / f"step-{s['n']:02d}.html",
                  render.page(f"G{gnum} · {s['title']}", render.css(c),
                              _chrome(f"teacher/grade{gnum}/step-{s['n']:02d}.html",
                                      "..", "index.html", gname, prev, nxt)
                              + f'<div class="sess">{sheet}</div>',
                              f"<style>{PRINT_CSS}</style>"))

        write(out / f"grade{gnum}" / "print.html",
              render.page(f"G{gnum} · {i18n.t('teacher_print_all')}", render.css(c),
                          _chrome(f"teacher/grade{gnum}/print.html", "..", "index.html", gname)
                          + f'<div class="tnote noprint">{i18n.t("teacher_print_note")}</div>'
                          + "".join(sheets),
                          f"<style>{PRINT_CSS}</style>"))

        cards.append(
            f'<div class="tcard" style="border-color:{c["color"]}">'
            f'<h3 style="color:{c["dark"]}">'
            f'{i18n.t("grade_n", n=i18n.num(gnum))} · {render.esc(g["grade"]["theme"])}</h3>'
            f'<p class="muted">{len(rows)} {i18n.t("teacher_lessons")} · '
            f'{nfiles} {i18n.t("teacher_projects")}</p>'
            f'<p><a href="grade{gnum}/index.html" style="color:{c["dark"]}">'
            f'{i18n.t("teacher_open")}</a> &nbsp;·&nbsp; '
            f'<a href="grade{gnum}/print.html" style="color:{c["dark"]}">'
            f'{i18n.t("teacher_print_all")}</a></p></div>')

    c0 = render.grade_c(grades[sorted(grades)[0]]["grade"])
    write(out / "index.html",
          render.page(i18n.t("teacher_title"), render.css(c0),
                      _chrome("teacher/index.html", ".")
                      + f'<h2 class="section">{i18n.t("teacher_title")}</h2>'
                      f'<div class="tnote">{i18n.t("teacher_lede")}</div>'
                      f'<div class="tgrid">{"".join(cards)}</div>',
                      f"<style>{PRINT_CSS}</style>"))
    return out


def _chrome(rel, root, back=None, back_label=None, prev=None, nxt=None):
    """Nav bar: where you are, the neighbouring lessons, and the language switch.

    `rel` is the page's path relative to its own site root — "teacher/grade7/
    step-13.html" — which is what render.lang_toggle needs to find the same page
    in the other locale. The Khmer teacher site sits at site/km/teacher/, the
    same one-level offset every other page on the site uses, so the switch is
    the one link here that deliberately crosses trees.
    """
    links = [f'<a href="{root}/index.html">{i18n.t("teacher_kicker")}</a>']
    if back:
        links.append('<span class="dim">·</span>')
        links.append(f'<a href="{back}">{back_label}</a>')
    links.append('<span class="spacer"></span>')
    if prev:
        links.append(f'<a href="step-{prev["n"]:02d}.html">&larr; '
                     f'{_label(prev)}</a>')
    if nxt:
        links.append(f'<a href="step-{nxt["n"]:02d}.html">'
                     f'{_label(nxt)} &rarr;</a>')
    links.append(render.lang_toggle(rel))
    return '<div class="chrome">' + "".join(
        l if l.startswith("<span") else f"&nbsp;{l}&nbsp;" for l in links) + '</div>'


def _label(s):
    """"Step 12" / "Checkpoint 2" for a neighbour link."""
    ctx = s.get("_ctx") or {}
    return (i18n.t("checkpoint_n", n=i18n.num(ctx["cp_no"]))
            if ctx.get("kind") == "checkpoint"
            else i18n.t("step_n", n=i18n.num(s["n"])))
