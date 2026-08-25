# -*- coding: utf-8 -*-
"""Parts catalog matching the two physical boxes (from Sovi's packing-list photos).

ICONS/SETS hold the English names. Translations live in generator/i18n.py (PARTS,
SET_NAMES) and are looked up per build, so this file stays the single source of
truth for ids, artwork and which box a part belongs to.
"""
import re

import i18n

SETS = {
    "MBOT2": ("mBot2 box", "#2563eb"),
    "ROVER": ("Rover add-on box", "#7c3aed"),
    "CLASS": ("Classroom", "#64748b"),
    "EXTRA": ("Sold separately", "#dc2626"),
}

SL = "#475569"; DK = "#1e293b"; GY = "#94a3b8"; BL = "#7eb3e8"

def _cyberpi(c):
    return (f'<rect x="10" y="5" width="44" height="32" rx="5" fill="{SL}"/>'
            f'<rect x="15" y="10" width="26" height="19" rx="2" fill="#0f172a"/>'
            f'<text x="28" y="23" font-size="8" fill="#7dd3fc" text-anchor="middle">:)</text>'
            f'<circle cx="47" cy="15" r="3" fill="{GY}"/><rect x="44" y="24" width="6" height="4" rx="1" fill="{GY}"/>')
def _shield(c):
    pillars = "".join(f'<rect x="{x}" y="8" width="5" height="10" rx="1.5" fill="{GY}"/>' for x in (16,28,40))
    return (f'{pillars}<rect x="10" y="16" width="44" height="16" rx="3" fill="#14532d"/>'
            f'<circle cx="18" cy="24" r="2.5" fill="#facc15"/><circle cx="32" cy="24" r="2.5" fill="{GY}"/>'
            f'<rect x="40" y="20" width="9" height="8" rx="1" fill="{DK}"/>'
            f'<rect x="12" y="32" width="40" height="6" rx="2" fill="{SL}"/>')
def _chassis(c):
    holes = "".join(f'<circle cx="{18+i*7}" cy="{y}" r="1.5" fill="#fff" opacity="0.7"/>' for i in range(5) for y in (18,26))
    return (f'<polygon points="8,14 56,14 60,20 60,30 56,36 8,36 4,30 4,20" fill="{BL}" stroke="#4a86c8" stroke-width="1.5"/>'
            f'<rect x="24" y="18" width="16" height="12" rx="2" fill="#fff" opacity="0.5"/>{holes}')
def _motor(c):
    return (f'<rect x="8" y="13" width="26" height="16" rx="4" fill="{BL}" stroke="#4a86c8"/>'
            f'<rect x="34" y="10" width="12" height="22" rx="3" fill="{SL}"/>'
            f'<rect x="46" y="18" width="8" height="5" fill="{GY}"/>'
            f'<text x="20" y="40" font-size="7" fill="{SL}" text-anchor="middle">\u00d72</text>')
def _wheelset(c):
    return (f'<circle cx="22" cy="22" r="13" fill="{SL}"/><circle cx="22" cy="22" r="5" fill="{GY}"/>'
            f'<circle cx="45" cy="22" r="13" fill="none" stroke="{DK}" stroke-width="5"/>')
def _miniwheel(c):
    return (f'<path d="M 24,12 Q 40,8 42,20 Q 44,32 30,34 Q 18,34 20,22 Z" fill="{DK}"/>'
            f'<circle cx="31" cy="22" r="5" fill="{GY}"/>')
def _motorcable(c):
    return (f'<rect x="8" y="10" width="8" height="6" rx="1" fill="#fff" stroke="{SL}"/>'
            f'<path d="M 16,13 L 50,19" stroke="{DK}" stroke-width="3"/>'
            f'<rect x="50" y="16" width="8" height="6" rx="1" fill="#fff" stroke="{SL}"/>'
            f'<rect x="8" y="26" width="8" height="6" rx="1" fill="#fff" stroke="{SL}"/>'
            f'<path d="M 16,29 L 50,33" stroke="{DK}" stroke-width="3"/>'
            f'<rect x="50" y="30" width="8" height="6" rx="1" fill="#fff" stroke="{SL}"/>')
def _mbuild(c):
    return (f'<rect x="6" y="18" width="10" height="8" rx="1.5" fill="#fff" stroke="{SL}" stroke-width="1.5"/>'
            f'<path d="M 16,22 C 28,14 38,30 48,22" stroke="{DK}" stroke-width="3.5" fill="none"/>'
            f'<rect x="48" y="18" width="10" height="8" rx="1.5" fill="#fff" stroke="{SL}" stroke-width="1.5"/>')
def _screws(c):
    out = ""
    for i,(x,y) in enumerate([(16,12),(26,10),(36,12)]):
        out += (f'<rect x="{x}" y="{y}" width="4" height="16" fill="{SL}"/>'
                f'<circle cx="{x+2}" cy="{y+18}" r="4.5" fill="{GY}"/>'
                f'<line x1="{x-1}" y1="{y+18}" x2="{x+5}" y2="{y+18}" stroke="{SL}" stroke-width="1.2"/>')
    out += f'<circle cx="48" cy="30" r="5" fill="none" stroke="{GY}" stroke-width="3"/>'
    return out
def _ultra(c):
    return (f'<rect x="10" y="10" width="44" height="24" rx="6" fill="#2563eb"/>'
            f'<circle cx="24" cy="22" r="8" fill="{DK}"/><circle cx="40" cy="22" r="8" fill="{DK}"/>'
            f'<circle cx="24" cy="22" r="4" fill="{GY}"/><circle cx="40" cy="22" r="4" fill="{GY}"/>')
def _quadrgb(c):
    dots = "".join(f'<circle cx="{18+i*10}" cy="22" r="3.4" fill="{col}"/>' for i,col in enumerate(("#ef4444","#22c55e","#3b82f6","#f8fafc")))
    return f'<rect x="10" y="14" width="44" height="16" rx="4" fill="{DK}"/>{dots}'
def _usb(c):
    return (f'<rect x="8" y="17" width="12" height="10" rx="2" fill="{SL}"/>'
            f'<path d="M 20,22 C 32,22 30,32 42,32 L 50,32" fill="none" stroke="{SL}" stroke-width="3"/>'
            f'<rect x="50" y="28" width="7" height="8" rx="1.5" fill="{GY}"/>')
def _dongle(c):
    return (f'<rect x="14" y="15" width="22" height="14" rx="3" fill="{SL}"/>'
            f'<rect x="36" y="17" width="13" height="10" fill="{GY}"/>'
            f'<text x="25" y="25" font-size="7" fill="#fff" text-anchor="middle">BT</text>')
def _controller(c):
    return (f'<rect x="8" y="12" width="48" height="22" rx="11" fill="#e2e8f0" stroke="{GY}" stroke-width="1.5"/>'
            f'<circle cx="20" cy="23" r="6" fill="{SL}"/><circle cx="20" cy="23" r="2.5" fill="{GY}"/>'
            f'<circle cx="44" cy="23" r="6" fill="{SL}"/><circle cx="44" cy="23" r="2.5" fill="{GY}"/>'
            f'<circle cx="32" cy="19" r="2" fill="#ef4444"/><circle cx="32" cy="27" r="2" fill="#22c55e"/>')
def _map(c):
    return (f'<rect x="10" y="8" width="44" height="30" rx="2" fill="#fff" stroke="{GY}" stroke-width="1.5"/>'
            f'<path d="M 14,32 C 24,32 22,14 34,14 C 44,14 42,28 50,28" fill="none" stroke="{DK}" stroke-width="3.5"/>')
def _screwdriver(c):
    return (f'<rect x="8" y="18" width="16" height="9" rx="4" fill="#0d9488"/>'
            f'<rect x="24" y="20.5" width="24" height="4" fill="{GY}"/>'
            f'<line x1="48" y1="22.5" x2="55" y2="22.5" stroke="{SL}" stroke-width="2"/>')
def _socket(c):
    return (f'<rect x="12" y="19" width="30" height="6" rx="3" fill="{GY}"/>'
            f'<rect x="24" y="8" width="6" height="28" rx="3" fill="{GY}"/>'
            f'<rect x="42" y="16" width="10" height="12" rx="2" fill="{SL}"/>'
            f'<circle cx="47" cy="22" r="2.6" fill="#fff"/>')
def _servopack(c):
    return (f'<rect x="14" y="10" width="20" height="26" rx="3" fill="{DK}"/>'
            f'<rect x="18" y="6" width="12" height="6" rx="2" fill="{SL}"/>'
            f'<circle cx="24" cy="14" r="3" fill="{GY}"/>'
            f'<path d="M 34,28 C 44,28 42,36 52,36" stroke="{SL}" stroke-width="2.5" fill="none"/>'
            f'<rect x="50" y="33" width="7" height="6" rx="1" fill="#fff" stroke="{SL}"/>')
def _track(c):
    return (f'<path d="M 12,14 L 40,10 Q 52,10 52,20 L 50,30 Q 48,36 38,36 L 14,32 Q 8,30 8,22 Q 8,16 12,14 Z" '
            f'fill="none" stroke="{DK}" stroke-width="5" stroke-dasharray="4,2.5"/>')
def _trackhubs(c):
    return (f'<circle cx="20" cy="20" r="12" fill="{SL}"/><circle cx="20" cy="20" r="4.5" fill="{GY}"/>'
            f'<circle cx="44" cy="26" r="8" fill="{DK}"/><circle cx="44" cy="26" r="3" fill="{GY}"/>')
def _dshaft(c):
    return (f'<rect x="8" y="26" width="46" height="5" rx="2.5" fill="{GY}" transform="rotate(-14 31 28)"/>')
def _collarflange(c):
    return (f'<circle cx="20" cy="20" r="9" fill="{GY}"/><circle cx="20" cy="20" r="4" fill="#fff"/>'
            f'<ellipse cx="44" cy="26" rx="11" ry="6" fill="#f59e0b"/>'
            f'<ellipse cx="44" cy="22" rx="7" ry="4" fill="#fbbf24"/><ellipse cx="44" cy="22" rx="3.5" ry="2" fill="#92400e"/>')
def _damper(c):
    return (f'<g transform="rotate(20 20 22)"><rect x="14" y="8" width="5" height="10" fill="#b91c1c"/>'
            f'<polyline points="16,18 13,22 20,26 13,30 16,34" fill="none" stroke="{DK}" stroke-width="2"/>'
            f'<rect x="14" y="34" width="5" height="6" fill="{SL}"/></g>'
            f'<g transform="rotate(20 42 22)"><rect x="38" y="6" width="5" height="10" fill="{SL}"/>'
            f'<polyline points="40,16 37,20 44,24 37,28 40,32" fill="none" stroke="{GY}" stroke-width="2"/>'
            f'<rect x="38" y="32" width="5" height="8" fill="{SL}"/></g>')
def _bracket(c):
    holes = "".join(f'<circle cx="{x}" cy="{y}" r="1.6" fill="#fff"/>' for x,y in [(18,26),(25,26),(32,26),(32,19),(32,12)])
    return (f'<path d="M 12,30 L 38,30 L 38,6 L 30,6 L 30,22 L 12,22 Z" fill="{BL}" stroke="#4a86c8" stroke-width="1.4"/>{holes}'
            f'<path d="M 44,30 L 56,14" stroke="{BL}" stroke-width="6"/>')
def _beamplate(c):
    holes = "".join(f'<circle cx="{14+i*9}" cy="15" r="1.7" fill="#fff"/>' for i in range(5))
    holes2 = "".join(f'<circle cx="{20+i*9}" cy="30" r="1.7" fill="#fff"/>' for i in range(4))
    return (f'<rect x="9" y="10" width="44" height="10" rx="2" fill="{BL}" stroke="#4a86c8" stroke-width="1.3"/>{holes}'
            f'<rect x="15" y="25" width="36" height="10" rx="2" fill="#5c9bd6" stroke="#4a86c8" stroke-width="1.3"/>{holes2}')
def _boards(c):
    return (f'<path d="M 8,16 L 30,12 L 34,20 L 26,30 L 10,28 Z" fill="{DK}"/>'
            f'<path d="M 32,26 L 54,20 L 56,30 L 44,38 L 34,34 Z" fill="{SL}"/>')
def _rubber(c):
    return (f'<path d="M 12,16 C 30,10 44,14 52,18" stroke="{DK}" stroke-width="2.5" fill="none"/>'
            f'<path d="M 12,24 C 30,18 44,22 52,26" stroke="{SL}" stroke-width="2.5" fill="none"/>'
            f'<path d="M 12,32 C 30,26 44,30 52,34" stroke="{DK}" stroke-width="2.5" fill="none"/>')
def _guide(c):
    return (f'<rect x="16" y="8" width="32" height="30" rx="2" fill="#fff" stroke="{GY}" stroke-width="1.5"/>'
            f'<line x1="21" y1="15" x2="43" y2="15" stroke="{SL}" stroke-width="1.5"/>'
            f'<line x1="21" y1="21" x2="43" y2="21" stroke="{GY}" stroke-width="1.2"/>'
            f'<rect x="21" y="25" width="12" height="9" fill="{BL}"/>')
def _tablet(c):
    return (f'<rect x="14" y="8" width="36" height="22" rx="2" fill="{SL}"/>'
            f'<rect x="17" y="11" width="30" height="16" fill="#0f172a"/>'
            f'<text x="32" y="22" font-size="7" fill="#7dd3fc" text-anchor="middle">mBlock</text>'
            f'<polygon points="10,34 54,34 50,30 14,30" fill="{GY}"/>')
def _tablet(c):
    # landscape tablet: the mBlock web IDE only lays out its Devices panel at
    # tablet width, so the icon deliberately reads as a large screen, not a phone
    return (f'<rect x="9" y="7" width="46" height="30" rx="3.5" fill="{SL}"/>'
            f'<rect x="13" y="10" width="38" height="24" rx="1" fill="#0f172a"/>'
            f'<circle cx="11" cy="22" r="0.9" fill="{GY}"/>'
            f'<text x="32" y="24" font-size="7" fill="#7dd3fc" text-anchor="middle">mBlock</text>')
def _webcam(c):
    return (f'<circle cx="32" cy="17" r="11" fill="{SL}"/><circle cx="32" cy="17" r="5.5" fill="{DK}"/>'
            f'<circle cx="33.5" cy="15.5" r="1.6" fill="#7dd3fc"/>'
            f'<path d="M 26,27 L 38,27 L 42,36 L 22,36 Z" fill="{GY}"/>')
def _ruler(c):
    ticks = "".join(f'<line x1="{14+i*6}" y1="16" x2="{14+i*6}" y2="{22 if i%2 else 25}" stroke="{DK}" stroke-width="1.3"/>' for i in range(7))
    return f'<rect x="9" y="15" width="46" height="15" rx="2" fill="#fde68a" stroke="#ca8a04" stroke-width="1.2"/>{ticks}'
def _tape(c):
    return (f'<circle cx="28" cy="20" r="12" fill="#e2e8f0" stroke="{GY}" stroke-width="2"/>'
            f'<circle cx="28" cy="20" r="5" fill="#fff" stroke="{GY}" stroke-width="1.5"/>'
            f'<rect x="38" y="26" width="18" height="7" fill="#e2e8f0" stroke="{GY}" stroke-width="1.2"/>')
def _foam(c):
    return (f'<polygon points="20,14 40,14 48,20 28,20" fill="#fde68a"/>'
            f'<polygon points="20,14 28,20 28,36 20,30" fill="#facc15"/>'
            f'<polygon points="28,20 48,20 48,30 28,36" fill="#fbbf24"/>')
def _ramp(c):
    return (f'<polygon points="10,34 54,34 54,12" fill="{GY}"/>'
            f'<path d="M 22,34 A 12,12 0 0 0 20,28" fill="none" stroke="{DK}" stroke-width="1.6"/>'
            f'<text x="30" y="31" font-size="6.5" fill="{DK}">\u03b8</text>')
def _timer(c):
    return (f'<circle cx="32" cy="24" r="14" fill="#fff" stroke="{SL}" stroke-width="2.5"/>'
            f'<rect x="29" y="5" width="6" height="5" rx="1" fill="{SL}"/>'
            f'<line x1="32" y1="24" x2="32" y2="14" stroke="#ef4444" stroke-width="2"/>'
            f'<line x1="32" y1="24" x2="39" y2="27" stroke="{SL}" stroke-width="2"/>')
def _cards(c):
    return (f'<rect x="12" y="14" width="26" height="18" rx="2" fill="#fff" stroke="{GY}" stroke-width="1.4" transform="rotate(-6 25 23)"/>'
            f'<rect x="22" y="12" width="26" height="18" rx="2" fill="#fff" stroke="{SL}" stroke-width="1.4" transform="rotate(5 35 21)"/>'
            f'<line x1="27" y1="18" x2="43" y2="19" stroke="{GY}" stroke-width="1.2"/>'
            f'<line x1="27" y1="23" x2="40" y2="24" stroke="{GY}" stroke-width="1.2"/>')
def _patches(c):
    return (f'<rect x="14" y="12" width="16" height="16" rx="2" fill="#ef4444"/>'
            f'<rect x="34" y="16" width="16" height="16" rx="2" fill="#22c55e"/>')
def _protractor(c):
    import math
    ticks = "".join(f'<line x1="32" y1="30" x2="{32+17*math.cos(math.radians(180-a)):.1f}" y2="{30-17*math.sin(math.radians(a)):.1f}" stroke="{GY}" stroke-width="1"/>' for a in (30,60,90,120,150))
    return (f'<path d="M 12,30 A 20,20 0 0 1 52,30 Z" fill="#e0f2fe" stroke="{SL}" stroke-width="1.6"/>{ticks}'
            f'<line x1="12" y1="30" x2="52" y2="30" stroke="{SL}" stroke-width="1.6"/>')
def _boxes(c):
    return (f'<rect x="16" y="16" width="32" height="20" fill="#d6bb6f"/>'
            f'<polygon points="16,16 24,10 56,10 48,16" fill="#e7d193"/>'
            f'<line x1="32" y1="16" x2="32" y2="36" stroke="#b49b55" stroke-width="1.5"/>')
def _trays(c):
    cells = "".join(f'<line x1="{21+i*11}" y1="14" x2="{21+i*11}" y2="34" stroke="{GY}" stroke-width="1.3"/>' for i in range(3))
    return (f'<rect x="10" y="14" width="44" height="20" rx="3" fill="#f1f5f9" stroke="{SL}" stroke-width="1.6"/>{cells}'
            f'<circle cx="15.5" cy="24" r="1.6" fill="{SL}"/><circle cx="26" cy="22" r="1.6" fill="{SL}"/>'
            f'<rect x="34" y="21" width="7" height="4" rx="1" fill="{SL}"/>')
def _kitbox(c):
    return (f'<rect x="14" y="18" width="36" height="18" fill="#5c9bd6"/>'
            f'<polygon points="14,18 6,8 26,8 32,18" fill="{BL}"/>'
            f'<polygon points="50,18 58,8 38,8 32,18" fill="{BL}"/>'
            f'<circle cx="24" cy="26" r="3" fill="#fff" opacity="0.7"/><rect x="32" y="23" width="10" height="6" rx="1" fill="#fff" opacity="0.7"/>')
def _blindfold(c):
    return (f'<path d="M 10,20 C 22,12 42,12 54,20 C 42,28 22,28 10,20 Z" fill="{DK}"/>'
            f'<path d="M 54,20 C 58,18 60,24 56,26" fill="none" stroke="{DK}" stroke-width="2"/>')
def _phone(c):
    return (f'<rect x="22" y="6" width="20" height="34" rx="4" fill="{SL}"/>'
            f'<rect x="25" y="10" width="14" height="24" fill="#0f172a"/>'
            f'<circle cx="32" cy="37" r="1.6" fill="{GY}"/>'
            f'<polygon points="29,18 29,26 36,22" fill="#ef4444"/>')
def _craft(c):
    return (f'<rect x="8" y="16" width="22" height="20" rx="1.5" fill="#e7d193" stroke="#b49b55" stroke-width="1.3"/>'
            f'<polygon points="34,36 38,18 42,18 38,36" fill="#ef4444"/>'
            f'<polygon points="34,36 38,32 42,36" fill="{DK}"/>'
            f'<path d="M 46,14 L 54,22 M 54,14 L 46,22" stroke="{SL}" stroke-width="2"/>'
            f'<circle cx="50" cy="30" r="4.5" fill="#fff" stroke="{DK}" stroke-width="1.2"/>'
            f'<circle cx="50" cy="30" r="2" fill="{DK}"/>')
def _colorcards(c):
    cols = ("#ef4444", "#22c55e", "#3b82f6", "#facc15")
    sq = "".join(f'<rect x="{9+i*12}" y="{14+(i%2)*4}" width="11" height="15" rx="1.5" '
                 f'fill="{col}" stroke="#fff" stroke-width="1"/>' for i, col in enumerate(cols))
    return (f'{sq}<line x1="6" y1="35" x2="58" y2="35" stroke="{DK}" stroke-width="2"/>')
def _router(c):
    waves = "".join(f'<path d="M {44+i*4},{20-i*3} A {6+i*4},{6+i*4} 0 0 1 {44+i*4},{28+i*3}" '
                    f'fill="none" stroke="{c["color"]}" stroke-width="1.6" opacity="{0.9-i*0.22}"/>'
                    for i in range(3))
    return (f'<rect x="10" y="22" width="34" height="12" rx="3" fill="{SL}"/>'
            f'<circle cx="17" cy="28" r="1.8" fill="#22c55e"/><circle cx="23" cy="28" r="1.8" fill="{GY}"/>'
            f'<line x1="36" y1="22" x2="40" y2="10" stroke="{DK}" stroke-width="2"/>{waves}')
def _torch(c):
    import math
    rays = "".join(f'<line x1="34" y1="24" x2="{34 - 20*math.cos(math.radians(a)):.1f}" '
                   f'y2="{24 + 20*math.sin(math.radians(a)):.1f}" stroke="#facc15" '
                   f'stroke-width="2"/>' for a in (-28, 0, 28))
    return (f'<rect x="34" y="15" width="22" height="18" rx="3" fill="{SL}"/>'
            f'<polygon points="34,12 34,36 22,30 22,18" fill="{GY}"/>{rays}')
def _robot(kind):
    def draw(c):
        from scenes import bot
        return bot(32, 21, c["color"], c["dark"], kind, 0, 1.05)
    return draw

ICONS = {
    # ---- mBot2 box (official packing list, verified from the box)
    "cyberpi":    ("CyberPi", "MBOT2", _cyberpi),
    "shield":     ("mBot2 Shield", "MBOT2", _shield),
    "chassis":    ("Chassis", "MBOT2", _chassis),
    "motor":      ("Encoder motor \u00d72", "MBOT2", _motor),
    "wheelset":   ("Wheel hub + slick tyre", "MBOT2", _wheelset),
    "miniwheel":  ("Mini wheel", "MBOT2", _miniwheel),
    "motorcable": ("Motor cable \u00d72", "MBOT2", _motorcable),
    "mbuild":     ("mBuild cables", "MBOT2", _mbuild),
    "screws7":    ("M4 screws", "MBOT2", _screws),
    "screws7s":   ("M2.5\u00d712 screws", "MBOT2", _screws),
    "ultra":      ("Ultrasonic Sensor 2", "MBOT2", _ultra),
    "quadrgb":    ("Quad RGB Sensor", "MBOT2", _quadrgb),
    "usb":        ("USB cable", "MBOT2", _usb),
    "map":        ("Line-following map", "MBOT2", _map),
    "screwdriver":("Screwdriver", "MBOT2", _screwdriver),
    "kitbox":     ("mBot2 box", "MBOT2", _kitbox),
    # ---- Rover add-on box (verified from the box)
    "servopack":  ("Servo pack", "ROVER", _servopack),
    "controller": ("Bluetooth Controller", "ROVER", _controller),
    "track":      ("Track \u00d72", "ROVER", _track),
    "trackhubs":  ("Wheel hubs (large + small)", "ROVER", _trackhubs),
    "dshaft":     ("D shaft", "ROVER", _dshaft),
    "collarflange":("Shaft collar + flange bearing", "ROVER", _collarflange),
    "damper":     ("Shock absorbers", "ROVER", _damper),
    "bracket":    ("Brackets 90\u00b0 / 120\u00b0 / U", "ROVER", _bracket),
    "beamplate":  ("Slide beams + plates", "ROVER", _beamplate),
    "boards":     ("Boards 1\u20138", "ROVER", _boards),
    "rubber":     ("Rubber bands", "ROVER", _rubber),
    "screwsR":    ("Rover screws + nuts", "ROVER", _screws),
    "socket":     ("Socket wrench", "ROVER", _socket),
    "guide":      ("Quick Start Guide", "ROVER", _guide),
    "roverbox":   ("Rover add-on box", "ROVER", _kitbox),
    # ---- not in the boxes
    "dongle":     ("Makeblock BT dongle", "EXTRA", _dongle),
    # ---- classroom
    "tablet":     ("Tablet + mBlock", "CLASS", _tablet),
    # the browser IDE (ide.mblock.cc), NOT the Play Store app — the app has no
    # CyberPi support at all, so the distinction is load-bearing for teachers
    "tablet":     ("Tablet + mBlock Web", "CLASS", _tablet),
    "webcam":     ("Webcam", "CLASS", _webcam),
    "ruler":      ("Ruler / tape measure", "CLASS", _ruler),
    "tape":       ("Masking tape", "CLASS", _tape),
    "foam":       ("Foam blocks", "CLASS", _foam),
    "ramp":       ("Ramp board", "CLASS", _ramp),
    "timer":      ("Stopwatch", "CLASS", _timer),
    "cards":      ("Printed cards", "CLASS", _cards),
    "patches":    ("Color patches", "CLASS", _patches),
    "protractor": ("Protractor", "CLASS", _protractor),
    "boxes":      ("Boxes / obstacles", "CLASS", _boxes),
    "trays":      ("Sorting trays", "CLASS", _trays),
    "blindfold":  ("Blindfold", "CLASS", _blindfold),
    "phone":      ("Phone (video/angle)", "CLASS", _phone),
    "craft":      ("Craft kit (card, markers, tape)", "CLASS", _craft),
    "colorcards": ("Colour cards (8 colours)", "CLASS", _colorcards),
    "router":     ("Wi-Fi router / hotspot", "CLASS", _router),
    "torch":      ("Torch / phone light", "CLASS", _torch),
    "robot_wheel":("mBot2, assembled", "MBOT2", _robot("wheel")),
    "robot_tank": ("Rover, assembled", "ROVER", _robot("tank")),
    "robot_arm":  ("Rover, arms fitted", "ROVER", _robot("arm")),
}

# ---- hardware a lesson's own code proves it needs -------------------------
# Only *detachable* devices belong here. The Bluetooth Controller is a separate
# handheld that has to be carried to the classroom, so code reading its sticks
# or buttons is proof it is needed — and forgetting to list it is exactly the
# drift this catches (G8 12 listed it, 13-15 inherited its code and did not).
#
# Sensors and servos are deliberately NOT derived: from the build steps onward
# they are bolted to the assembled robot, so listing them again would send a
# teacher to fetch a part that is already attached.
IMPLIED = [
    ("controller", re.compile(r"joystick\s+(?:LY|RY|LX|RX)\b"
                              r"|\bbutton\s+(?:L1|R1|L2|R2|[1-4])\s+pressed", re.I)),
]


def imply(unit):
    """Append parts the unit's `code:` proves it needs. Mutates and returns it.

    Applied at load time so every consumer — step page, materials page and the
    shopping list — sees the same list, in both locales, with no chance of the
    two drifting apart."""
    if not isinstance(unit, dict):
        return unit
    src = (unit.get("code") or {}).get("source") or ""
    if not src:
        return unit
    parts = unit.get("parts") or []
    have = {p.get("id") for p in parts}
    add = [pid for pid, rx in IMPLIED if pid not in have and rx.search(src)]
    if not add:
        return unit
    # sit with the hardware, ahead of the classroom items (tape, cards, ...)
    at = next((i for i, p in enumerate(parts)
               if ICONS.get(p.get("id"), (None, "CLASS"))[1] == "CLASS"), len(parts))
    unit["parts"] = parts[:at] + [{"id": pid} for pid in add] + parts[at:]
    return unit


def panel(c, parts, img_available=None, img_base=""):
    """img_available: set of icon ids that have a real manual photo in
    site/assets/parts/<id>.png (extracted by tools/extract_parts_images.py).
    Those render as an <img> in the same 52x36 footprint as the SVG icons;
    everything else keeps its hand-drawn SVG."""
    if not parts:
        return ""
    cells = []
    for pid, note in parts:
        label, sid, draw = ICONS[pid]
        sname, scol = SETS[sid]
        label = i18n.part_label(pid, label)
        sname = i18n.set_name(sid, sname)
        if img_available and pid in img_available:
            icon = (f'<div class="mimg"><img src="{img_base}assets/parts/{pid}.png" '
                    f'alt="{label}"/></div>')
        else:
            icon = f'<svg viewBox="0 0 64 44" width="52"><g>{draw(c)}</g></svg>'
        note_html = f'<div class="mnote">{note}</div>' if note else ''
        cells.append(
            f'<div class="mat">{icon}<div class="mlbl">{label}</div>{note_html}'
            f'<div class="pill" style="background:{scol}">{sname}</div></div>')
    return f'<div class="mats"><div class="mhead">You need \u2014 pieces &amp; materials</div>{"".join(cells)}</div>'
