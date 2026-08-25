# mBot2 Rover Curriculum — Generator Source (handoff package)

Builds the three per-grade teaching guides (Grades 7/8/9, 23 pages each, weasyprint).

## Files
- common.py    — CSS, SVG scene library (60+ session result illustrations), page assembly
- parts.py     — piece/materials catalog: 50 icons, set tags matching the two physical boxes
- grade7.py    — Grade 7 content: 20 full session plans + PARTS lists (box-verified)
- grade8.py    — Grade 8 content (incl. Rover grip-arm corrections)
- grade9.py    — Grade 9 content (Python/Ranger)
- build_all.py — intro pages (cover, overview, box-contents reference) + build runner

## Build
pip install weasyprint --break-system-packages
python3 build_all.py    # outputs 3 PDFs to /home/claude

## State of knowledge (verified so far)
- mBot2 box packing list: photo-verified w/ official quantities (see MBOT2_BOX in build_all.py)
- Rover add-on box list: photo-verified names; printed parts list shows NO quantities.
  ROVER_BOX now carries USED counts / >= minimums derived by summing the printed guide's
  per-step callouts (photo-verified 2026-07). Plastic shock absorbers are never used in the
  build (spares); metal shocks x4, shaft collars x12 (M3x6), tracks x2.
- Battery is built into mBot2 Shield; BT dongle sold separately; Rover form has servo grip arms (L1/R1)
- mBot2 build steps (printed guide pp. 9-14, steps 1-11) and Rover build (printed pp. 5-75,
  phases: brackets x2 -> left wheel -> right wheel -> chassis -> head -> join -> shells -> arms)
  fully extracted; key printed warnings: nut back 90deg CCW after hub screws, track grain
  direction, motor cables CROSSED L<->R, 10cm (not 20cm) sensor cable, board film off first.
- "mBot2 Ranger" (G9) is the kit's official third form. Its guide is digital-only:
  makeblock.com mBot2 Rover product page -> "mBot2 Ranger building guide" link
  (res-us.makeblock.com/doc/Product/mBot2 Ranger Quick Start Guide.zip; blocks bots -
  download manually). WARNING: support.makeblock.com's "mBot Ranger" section is a
  DIFFERENT older product (Me Auriga) - do not use it.

## Annotation status (2026-07)
- G7 S2-3, G8 S2-3, G9 S8-9: fully annotated (guidebox step ranges + screws, watch-out tips
  from printed/digital guide warnings; G7/G8 also have redrawn "expl" scene diagrams). One page each.
- mBot2 Ranger Quick Start Guide (digital PDF, 63 pp / 61 printed) extracted 2026-07:
  sections front unit pp.5-14 / chassis pp.15-29 / robotic arm pp.30-35 / grippers pp.36-43
  (x2, "repeat for the other arm") / finish + cabling pp.44-61.
  KEY: Ranger motor cables are STRAIGHT (left->EM1, right->EM2) - the Rover crossed them.
  Servo cables -> S4 (left) / S3 (right). Gripper->servo plate: M4x10 x4 + nuts x4 per arm.
  Same wheel back-off + track-grain cautions as Rover. Most per-step panel counts are
  outlined vector art (not text) - readable from the projected guide in class; not critical
  for the teaching guides.

## NEXT TASK
1. Optional: verify the two Rover head-phase screw callouts (M4x22 x4, twice) against the
   physical build; one-line fixes in grade8.py if wrong.
2. Optional: spot-check ROVER_BOX minimums against the physical box.
