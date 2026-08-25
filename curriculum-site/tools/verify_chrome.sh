#!/bin/zsh
# Browser-print check: paginate each print guide with headless Chrome — the engine
# teachers actually print with — and assert the structure is intact.
#
# Usage: tools/verify_chrome.sh [--project DIR] <grade> [grade ...]
#        tools/verify_chrome.sh 7 8 9
#        (--project DIR still works, but no sibling tree is live: Grades 4-6
#         were archived on 2026-08-19)
#
# It checks every print*.html a grade has, so Grades 4-6 get both the 1 h
# (print.html) and the 2 h (print-long.html) guide.
#
# WHAT IS ASSERTED, and why it is no longer a page count:
#   * the intro is exactly 3 pages, so session 1 starts on page 4
#   * sessions 1..20 all appear, in order, none missing or duplicated
#   * every session starts on a fresh page (guaranteed by .sess page-break-before)
#   * no session spans more than MAX_PP pages
#
# Grades 7-8 have been rebuilt as *step* courses and have no print.html guide —
# each step is its own page, printed individually. There is nothing here for this
# harness to check, so it says so and skips rather than reporting a false failure.
#
# The old version asserted `pages == 23` and that page p held session p-3. Both
# stopped being true in Aug 2026: a session carrying the `long:` band takes two
# pages, and the `bonus:` box pushes most 1 h sessions onto a second page too.
# Both were deliberate. A hardcoded total would have to be re-edited every time
# content legitimately grows, and it cannot tell "the layout blew up" apart from
# "a paragraph got longer" — the ordering invariant can.
#
# English only: it matches the printed "SESSION n / 20" header, which is Khmer in
# site/km. Run it against the English tree.
set -e
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
MAX_PP=2                       # most pages one session may occupy
cd "$(dirname "$0")/.."

BASE="."
if [[ "$1" == "--project" ]]; then
  BASE="$2"; shift 2
fi
[[ -d "$BASE/site" ]] || { echo "no site/ under $BASE — build it first"; exit 2 }
[[ $# -gt 0 ]] || { echo "usage: $0 [--project DIR] <grade> [grade ...]"; exit 2 }

fail=0
for g in "$@"; do
  # (N) = null glob: a grade with no guides reports instead of dying on nomatch
  guides=("$BASE"/site/grade$g/print*.html(N))
  if [[ ${#guides} -eq 0 ]]; then
    if [[ -e "$BASE/site/grade$g/steps.html" ]]; then
      n=$(ls "$BASE"/site/grade$g/step-*.html(N) | wc -l | tr -d " ")
      echo "grade $g: SKIP — step course ($n step pages), no combined print guide"
      continue
    fi
    echo "grade $g: FAIL — no print guide found under $BASE/site/grade$g/"
    fail=1
    continue
  fi
  for guide in $guides; do
    label="grade $g ${guide:t:r}"
    pdf="$(mktemp -t chrome-g$g).pdf"
    "$CHROME" --headless --disable-gpu --no-pdf-header-footer \
      --print-to-pdf="$pdf" "file://${guide:A}" 2>/dev/null
    pages=$(pdfinfo "$pdf" | awk '/^Pages:/{print $2}')

    # page number on which each session starts, in the order encountered
    starts=(); nums=()
    for p in $(seq 1 $pages); do
      head=$(pdftotext -f $p -l $p "$pdf" - 2>/dev/null | head -1 | tr -d ' ')
      if [[ "$head" == SESSION*/20* ]]; then
        n=${${head#SESSION}%%/*}
        starts+=$p; nums+=$n
      fi
    done

    if [[ ${#nums} -eq 0 ]]; then
      echo "$label: FAIL — no session headers found in $pages pages"; fail=1
      rm -f "$pdf"; continue
    fi

    # 1. intro is 3 pages
    if [[ ${starts[1]} != 4 ]]; then
      echo "$label: FAIL — session 1 starts on page ${starts[1]}, expected 4 (3 intro pages)"
      fail=1
    fi
    # 2. sessions 1..20, in order, no gaps or repeats
    expected=1
    for n in $nums; do
      if [[ $n != $expected ]]; then
        echo "$label: FAIL — expected session $expected, found $n"; fail=1; break
      fi
      ((expected++))
    done
    if [[ ${#nums} != 20 ]]; then
      echo "$label: FAIL — ${#nums} sessions, expected 20"; fail=1
    fi
    # 3. no session sprawls
    worst=0; worst_n=0
    for i in {1..${#starts}}; do
      end=$(( i < ${#starts} ? starts[i+1] : pages + 1 ))
      pp=$(( end - starts[i] ))
      (( pp > worst )) && { worst=$pp; worst_n=${nums[i]} }
    done
    if (( worst > MAX_PP )); then
      echo "$label: FAIL — session $worst_n spans $worst pages (max $MAX_PP)"; fail=1
    fi

    echo "$label: $pages pages · 20 sessions in order · at most $worst page(s) each"
    rm -f "$pdf"
  done
done

if [[ $fail = 0 ]]; then
  echo "CHROME PRINT: PASS — sessions complete, ordered, and within $MAX_PP pages each"
else
  echo "CHROME PRINT: FAIL"
fi
exit $fail
