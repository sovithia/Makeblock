# Answer projects (.mblock)

**Generated, not hand-saved.** Build them with:

    cd curriculum-site && ../.venv/bin/python tools/mblock_compile.py

A full run clears this directory first, so anything dropped in by hand is lost.
Verify with `tools/mblock_verify.py` — it checks the block graph, the opcodes
against the installed mBlock app, script overlap, and that no file reads a list
or variable nothing in it ever fills.

## One file per step

Named `<grade>-<stage>-<step>`, not per stage:

    G7-A-01.mblock … G7-A-04.mblock     Stage A · the robot obeys
    G7-B-06 … G7-B-09                   Stage B · the robot decides
    G7-C-11 … G7-C-14                   Stage C · the robot remembers
    G7-D-16 … G7-D-19                   Stage D · the robot is organised
    G7-E-22                             Stage E · the Rescue Run — also the demo
    G8-A-02 … G8-A-04, G8-B-06 … G8-B-09, G8-C-11 … G8-C-14, G8-D-16 … G8-D-19

Each file holds the **whole build so far**, so the last file of a stage is that
stage's finished project, and a student who missed a lesson can be handed the
file for the step the class is on and be caught up.

Per stage rather than per step was tried and abandoned: a stage's steps each
write their own `when CyberPi starts up`, so the merged file had three startup
hats and two handlers on one button, and the CyberPi died with a traceback on the
first press. Do not merge them back — see `carry_forward()` in
`tools/mblock_compile.py`.

Steps with no script produce no file: the design-on-paper, teardown and
freeze-and-run steps (G7 21/23, G8 01/21/22/23).

Access: teacher-facing. Each step page names the file holding the build at that
point, and each checkpoint links the file for the last step of the stage it
closes — a reference for what the class just built rather than a shortcut past it.
