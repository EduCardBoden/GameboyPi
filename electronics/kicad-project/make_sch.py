"""Erzeugt GameboyPi.kicad_sch aus design.py.
Jeder Pin bekommt ein Netz-Label (oder ein No-Connect-Kreuz) – dadurch ist der Plan ohne Drähte eindeutig.
Schreibt build/sch_info.json (Symbol-UUIDs, offene Pins), das make_pcb.py für die Verknüpfung nutzt.
Reihenfolge: make_sch.py -> make_pcb.py -> route.py
"""
import json
import os
import re
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import PARTS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SYM_DIR = os.path.join(os.environ["LOCALAPPDATA"], r"Programs\KiCad\10.0\share\kicad\symbols")
OUT = os.path.join(HERE, "GameboyPi.kicad_sch")
PROJECT = "GameboyPi"
ROOT_UUID = "6a1c2f4e-9b7d-4c3a-8e21-0f5d6b7a8c90"


def uid():
    return str(uuid.uuid4())


def block_at(text, start):
    """Gibt das Ende des geklammerten Ausdrucks ab text[start] == '(' zurück."""
    depth, i, in_str = 0, start, False
    while i < len(text):
        c = text[i]
        if in_str:
            if c == "\\":
                i += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced")


_lib_cache = {}


def lib_symbol(lib_id):
    lib, name = lib_id.split(":")
    if lib not in _lib_cache:
        with open(os.path.join(SYM_DIR, lib + ".kicad_sym"), encoding="utf-8") as f:
            _lib_cache[lib] = f.read()
    text = _lib_cache[lib]
    m = re.search(r'\n\s*\(symbol "%s"\s' % re.escape(name), text)
    if not m:
        raise KeyError(lib_id)
    s = text.index("(", m.start())
    body = text[s:block_at(text, s)]
    ext = re.search(r'\(extends "([^"]+)"\)', body)
    if ext:
        # abgeleitetes Symbol: Grafik und Pins vom Elternsymbol übernehmen (im Schaltplan wird flach gespeichert)
        parent = ext.group(1)
        pbody, _, _ = lib_symbol(lib + ":" + parent)
        pbody = pbody.replace('(symbol "%s:%s"' % (lib, parent), '(symbol "%s"' % lib_id, 1)
        # Eigenschaften (Value, Description, Filter, ...) des abgeleiteten Symbols übernehmen
        for pm in re.finditer(r'\(property "([^"]+)"', body):
            cblk = body[pm.start():block_at(body, pm.start())]
            pi = pbody.find('(property "%s"' % pm.group(1))
            if pi >= 0:
                pbody = pbody[:pi] + cblk + pbody[block_at(pbody, pi):]
        return lib_symbol_finish(pbody.replace('"%s_' % parent, '"%s_' % name), lib_id)
    body = body.replace('(symbol "%s"' % name, '(symbol "%s"' % lib_id, 1)
    return lib_symbol_finish(body, lib_id)


def lib_symbol_finish(body, lib_id):
    pins, names = [], {}
    for pm in re.finditer(r"\(pin\s+\w+\s+\w+", body):
        pb = body[pm.start():block_at(body, pm.start())]
        at = re.search(r"\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)", pb)
        num = re.search(r'\(number\s+"([^"]*)"', pb)
        names[num.group(1)] = re.search(r'\(name\s+"([^"]*)"', pb).group(1)
        pins.append((num.group(1), float(at.group(1)), float(at.group(2)), int(float(at.group(3)))))
    return body, pins, names


def fmt(v):
    return ("%.4f" % v).rstrip("0").rstrip(".")


def prop(name, value, x, y, hide=False, justify=None):
    j = " (justify %s)" % justify if justify else ""
    h = " (hide yes)" if hide else ""
    return ('\t\t(property "%s" "%s" (at %s %s 0)%s (effects (font (size 1.27 1.27))%s))\n'
            % (name, value, fmt(x), fmt(y), h, j))


def glabel(net, x, y, angle):
    """Globales Label – Netzname ohne Blattpfad, passend zu den Netzen der Platine."""
    just = "left" if angle in (0, 90) else "right"
    return ('\t(global_label "%s" (shape passive) (at %s %s %d) (fields_autoplaced yes)'
            ' (effects (font (size 1.27 1.27)) (justify %s)) (uuid "%s"))\n'
            % (net, fmt(x), fmt(y), angle, just, uid()))


# Anordnung auf A3 nach Funktionsgruppen (alle Verbindungen laufen über Labels)
SCH_POS = {"J1": (160.02, 106.68), "J2": (279.4, 101.6)}
GROUPS = {  # Gruppe: (x0, y0, Spalten, Spaltenbreite, Zeilenhöhe)
    "buttons": (45.72, 50.8, 1, 0, 15.24),
    "power": (40.64, 182.88, 7, 27.94, 30.48),
    "adc": (241.3, 152.4, 2, 30.48, 0),
    "audio": (233.68, 182.88, 6, 22.86, 30.48),
    "service": (40.64, 254.0, 9, 15.24, 0),
    "mech": (370.84, 76.2, 1, 0, 12.7),
}
_count = {}
for p in PARTS:
    if p["ref"] in SCH_POS:
        continue
    x0, y0, cols, dx, dy = GROUPS[p["group"]]
    n = _count.get(p["group"], 0)
    _count[p["group"]] = n + 1
    SCH_POS[p["ref"]] = (round(x0 + (n % cols) * dx, 2), round(y0 + (n // cols) * dy, 2))

lib_bodies = {}
out_items = []
uuids = {}
nc_pins = {}

for p in PARTS:
    body, pins, names = lib_symbol(p["lib_id"])
    lib_bodies[p["lib_id"]] = body
    sx, sy = SCH_POS[p["ref"]]
    su = str(uuid.uuid5(uuid.NAMESPACE_URL, "gameboypi/" + p["ref"]))  # stabil -> Platine bleibt verknüpft
    uuids[p["ref"]] = su
    in_bom = "no" if p["ref"].startswith("H") else "yes"
    s = ['\t(symbol (lib_id "%s") (at %s %s 0) (unit 1)\n' % (p["lib_id"], fmt(sx), fmt(sy)),
         "\t\t(exclude_from_sim no) (in_bom %s) (on_board yes) (dnp no)\n" % in_bom,
         '\t\t(uuid "%s")\n' % su]
    # Referenz über dem obersten, Wert unter dem untersten Pin
    pys = [sy - py for _, _, py, _ in pins] or [sy]
    s.append(prop("Reference", p["ref"], sx, min(min(pys), sy) - 3.81))
    s.append(prop("Value", p["value"], sx, max(max(pys), sy) + 3.81))
    s.append(prop("Footprint", p["footprint"], sx, sy, hide=True))
    s.append(prop("Datasheet", "", sx, sy, hide=True))
    s.append(prop("Description", "", sx, sy, hide=True))
    for num in sorted({n for n, *_ in pins}, key=lambda n: (len(n), n)):
        s.append('\t\t(pin "%s" (uuid "%s"))\n' % (num, uid()))
    s.append('\t\t(instances (project "%s" (path "/%s" (reference "%s") (unit 1))))\n\t)\n'
             % (PROJECT, ROOT_UUID, p["ref"]))
    out_items.append("".join(s))

    seen = set()
    for num, px, py, ang in pins:
        x, y = round(sx + px, 2), round(sy - py, 2)
        if (x, y) in seen:
            continue  # gestapelte Pins (z. B. mehrere GND) nur einmal beschriften
        seen.add((x, y))
        net = p["pins"].get(num)
        if net is None:
            nc_pins.setdefault(p["ref"], {})[num] = names[num]
            out_items.append('\t(no_connect (at %s %s) (uuid "%s"))\n' % (fmt(x), fmt(y), uid()))
            continue
        out_items.append(glabel(net, x, y, (ang + 180) % 360))

# PWR_FLAGs, damit der ERC die Versorgungsnetze als getrieben erkennt
flag_body, flag_pins, _ = lib_symbol("power:PWR_FLAG")
lib_bodies["power:PWR_FLAG"] = flag_body
for i, net in enumerate(["+5V", "GND", "+3V3", "VBAT"]):
    fx, fy = 200.66 + i * 20.32, 266.7
    out_items.append(
        '\t(symbol (lib_id "power:PWR_FLAG") (at %s %s 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)\n'
        '\t\t(uuid "%s")\n' % (fmt(fx), fmt(fy), uid())
        + prop("Reference", "#FLG0%d" % (i + 1), fx, fy - 3.81, hide=True)
        + prop("Value", "PWR_FLAG", fx, fy - 3.81)
        + prop("Footprint", "", fx, fy, hide=True)
        + '\t\t(pin "1" (uuid "%s"))\n' % uid()
        + '\t\t(instances (project "%s" (path "/%s" (reference "#FLG0%d") (unit 1))))\n\t)\n'
        % (PROJECT, ROOT_UUID, i + 1))
    _, px, py, _ = flag_pins[0]
    out_items.append(glabel(net, fx + px, fy - py, 270))

notes = [
    "GameboyPi - Raspberry Pi Zero 2 W Handheld im Game-Boy-Color-Format",
    "Strom: LiPo 1S (mit Schutz) -> PowerBoost 1000C (Laden + Load-Sharing + 5.2V Boost) -> +5V",
    "Soft-Power: SW9 EIN haelt PWR_REQ low -> Q1 aus -> EN high. SW9 AUS -> GPIO16 low -> Pi faehrt herunter,",
    "  danach GPIO4 (gpio-poweroff) low -> Q2 aus -> R8 zieht PWR_REQ high -> Q1 zieht EN low -> Boost aus.",
    "Display: 2.4in ILI9341 SPI an SPI0 (CE0), DC=GPIO25, RST=GPIO24, Backlight an 3V3",
    "Audio: PWM GPIO12/13 -> RC-Filter -> Klinke (Schaltkontakte) -> Mix -> RV1 Lautstaerke -> PAM8302 -> Lautsprecher",
    "Tasten gegen GND, interne Pull-ups: UP=5 DOWN=6 LEFT=19 RIGHT=26 A=23 B=22 START=17 SELECT=27",
    "Akku: ADS1115 AIN0 = VBAT/2 (I2C 0x48), LBO ueber BAT85 an GPIO20, UART-Debug an J8",
]
for i, n in enumerate(notes):
    out_items.append('\t(text "%s" (exclude_from_sim no) (at 200.66 %s 0) (effects (font (size 1.524 1.524)) (justify left bottom)) (uuid "%s"))\n'
                     % (n, fmt(30.48 + i * 5.08), uid()))

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write('(kicad_sch (version 20250610) (generator "eeschema") (generator_version "10.0")\n')
    f.write('\t(uuid "%s")\n\t(paper "A3")\n' % ROOT_UUID)
    f.write('\t(title_block (title "GameboyPi") (date "2026-11-11") (rev "1.2") (comment 1 "Raspberry Pi Zero 2 W Handheld"))\n')
    f.write("\t(lib_symbols\n")
    for b in lib_bodies.values():
        f.write("\t\t" + b.strip() + "\n")
    f.write("\t)\n")
    f.writelines(out_items)
    f.write('\t(sheet_instances (path "/" (page "1")))\n\t(embedded_fonts no)\n)\n')
print("gespeichert:", OUT)

# Symbol-UUIDs und Namen der offenen Pins für make_pcb.py (Schaltplan <-> Platine Parität)
os.makedirs(os.path.join(HERE, "build"), exist_ok=True)
with open(os.path.join(HERE, "build", "sch_info.json"), "w", encoding="utf-8") as f:
    json.dump({"uuids": uuids, "nc": nc_pins}, f, indent=1)
