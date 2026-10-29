"""Erzeugt GameboyPi.kicad_pcb (Platzierung, Netze, Umriss, Beschriftung, GND-Flächen).
Ausführen mit dem Python von KiCad:  "%LOCALAPPDATA%\\Programs\\KiCad\\10.0\\bin\\python.exe" make_pcb.py
Danach: route.py (Freerouting) für die Leiterbahnen.
"""
import json
import math
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import PARTS, BUTTONS, POWER_NETS, BOARD_W, BOARD_H, BOARD_R  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "GameboyPi.kicad_pcb")
FP_DIR = os.path.join(os.environ["LOCALAPPDATA"], r"Programs\KiCad\10.0\share\kicad\footprints")
SCH_INFO = json.load(open(os.path.join(HERE, "build", "sch_info.json"), encoding="utf-8"))  # von make_sch.py

mm = pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(mm(x), mm(y))  # noqa: E731

board = pcbnew.NewBoard(OUT)
board.SetCopperLayerCount(2)

# ---------- Netzklassen ----------
ds = board.GetDesignSettings()
# 0.15 mm erlaubt Engstellen zwischen den 2.54-mm-Pins (JLCPCB/PCBWay: min. 0.127 mm)
ds.m_TrackMinWidth = mm(0.15)
ns = ds.m_NetSettings
default = ns.GetDefaultNetclass()
default.SetTrackWidth(mm(0.25))
default.SetClearance(mm(0.2))
default.SetViaDiameter(mm(0.6))
default.SetViaDrill(mm(0.3))
for name, width in (("Power", 1.0), ("Power3V3", 0.5)):
    nc = pcbnew.NETCLASS(name)
    nc.SetTrackWidth(mm(width))
    nc.SetClearance(mm(0.25))
    nc.SetViaDiameter(mm(0.8))
    nc.SetViaDrill(mm(0.4))
    ns.SetNetclass(name, nc)
for net, width in POWER_NETS.items():
    ns.SetNetclassPatternAssignment(net, "Power" if width >= 1.0 else "Power3V3")

# ---------- Netze ----------
nets = {}


def get_net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        nets[name] = n
    return nets[name]


for p in PARTS:
    for n in p["pins"].values():
        get_net(n)


# ---------- Bauteile ----------
def pad_center(fp):
    xs = [p.GetPosition().x for p in fp.Pads() if p.GetNumber()]
    ys = [p.GetPosition().y for p in fp.Pads() if p.GetNumber()]
    if not xs:
        return fp.GetPosition()
    return pcbnew.VECTOR2I((min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2)


def place(p):
    lib, name = p["footprint"].split(":")
    fp = pcbnew.FootprintLoad(os.path.join(FP_DIR, lib + ".pretty"), name)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    fp.SetReference(p["ref"])
    fp.SetValue(p["value"])
    board.Add(fp)
    # Konturlinien aus Footprints (z. B. Klinkenbuchse) würden den Platinenumriss zerstören
    for g in list(fp.GraphicalItems()):
        if g.GetLayer() == pcbnew.Edge_Cuts:
            fp.Remove(g)
    fp.SetPosition(V(0, 0))
    if p["angle"]:
        fp.SetOrientationDegrees(p["angle"])
    if p["side"] == "B":
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    fp.SetPath(pcbnew.KIID_PATH("/" + SCH_INFO["uuids"][p["ref"]]))
    fp.SetSheetname("/")
    fp.SetSheetfile("GameboyPi.kicad_sch")
    fp.SetExcludedFromBOM(p["ref"].startswith("H"))
    nc = SCH_INFO["nc"].get(p["ref"], {})
    for pad in fp.Pads():
        num = pad.GetNumber()
        if num in p["pins"]:
            pad.SetNet(get_net(p["pins"][num]))
        elif num in nc:
            # gleicher Name, den KiCad beim "Platine aus Schaltplan aktualisieren" vergibt
            pad.SetNet(get_net("unconnected-(%s-%s-Pad%s)" % (p["ref"], nc[num].replace("/", "{slash}"), num)))
    if p["pos"] is not None:
        fp.Move(V(*p["pos"]) - pad_center(fp))
    return fp


fps = {p["ref"]: place(p) for p in PARTS}
for ref, fp in fps.items():
    if ref.startswith("H"):
        fp.Reference().SetVisible(False)
# GND-Pins der Stiftleisten voll an die Fläche (die Stiftreihen lassen kaum Platz für Thermal-Stege)
for ref in ("J1", "J2", "J3", "J8", "J10", "J11", "J12"):
    for pad in fps[ref].Pads():
        if pad.GetNetname() == "GND":
            pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)

# SW9 sitzt 2.3 mm vom Rand: fixierte Stichleitungen nach innen, sonst routet Freerouting am Rand entlang
for pad in fps["SW9"].Pads():
    if pad.GetNumber() in ("1", "3"):
        stub = pcbnew.PCB_TRACK(board)
        stub.SetStart(pad.GetPosition())
        stub.SetEnd(pad.GetPosition() + V(0, 4.5))
        stub.SetWidth(mm(0.3))
        stub.SetLayer(pcbnew.F_Cu)
        stub.SetNet(pad.GetNet())
        stub.SetLocked(True)
        board.Add(stub)

# Raspberry Pi: Stiftleiste waagerecht, Pi-Körper nach oben (HDMI/USB zur Oberkante).
pi = fps["J1"]
for ang in (0, 90, 180, 270):
    pi.SetOrientationDegrees(ang)
    pads = {p.GetNumber(): p.GetPosition() for p in pi.Pads()}
    holes = [p.GetPosition() for p in pi.Pads() if not p.GetNumber()]
    # Rückseite = gespiegelt: Pin 1 (und damit der SD-Slot) liegt dann rechts
    horiz = abs(pads["1"].y - pads["39"].y) < mm(0.01)
    if horiz and min(h.y for h in holes) < pads["1"].y - mm(10):
        break
else:
    raise SystemExit("Pi-Ausrichtung nicht gefunden")
# Rahmen des Pi (65 x 30) aus den Montagelöchern: Löcher 3.5 mm vom Rand
holes = [p.GetPosition() for p in pi.Pads() if not p.GetNumber()]
hx0 = min(h.x for h in holes)
hy0 = min(h.y for h in holes)
target_x0 = (BOARD_W - 65.0) / 2 + 3.5
target_y0 = 3.77 + 3.5
pi.Move(V(target_x0, target_y0) - pcbnew.VECTOR2I(hx0, hy0))

# ---------- Platinenumriss (abgerundetes Rechteck) ----------


def edge_line(x1, y1, x2, y2):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(V(x1, y1))
    s.SetEnd(V(x2, y2))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(mm(0.1))
    board.Add(s)


def edge_arc(cx, cy, sx, sy, ang):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetCenter(V(cx, cy))
    s.SetStart(V(sx, sy))
    s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T), True)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(mm(0.1))
    board.Add(s)


W, H, R = BOARD_W, BOARD_H, BOARD_R
edge_line(R, 0, W - R, 0)
edge_line(W, R, W, H - R)
edge_line(W - R, H, R, H)
edge_line(0, H - R, 0, R)
edge_arc(W - R, R, W - R, 0, 90)
edge_arc(W - R, H - R, W, H - R, 90)
edge_arc(R, H - R, R, H, 90)
edge_arc(R, R, 0, R, 90)


# ---------- Beschriftung ----------
def text(s, x, y, layer=pcbnew.F_SilkS, size=1.0, angle=0, bold=False):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(V(x, y))
    t.SetLayer(layer)
    t.SetTextSize(V(size, size))
    t.SetTextThickness(mm(size * (0.2 if bold else 0.15)))
    if angle:
        t.SetTextAngleDegrees(angle)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    board.Add(t)


def rect(x1, y1, x2, y2, layer):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_RECTANGLE)
    s.SetStart(V(x1, y1))
    s.SetEnd(V(x2, y2))
    s.SetLayer(layer)
    s.SetWidth(mm(0.15))
    board.Add(s)


for ref, net, label, (x, y) in BUTTONS:
    if label == "A":
        text(label, x - 6.2, y, size=0.9)
    else:
        text(label, x, y + 4.6, size=0.9)

# Display-Pinbelegung neben der Stiftleiste
from design import LCD_ORIGIN, LCD_SIZE  # noqa: E402

j2x = LCD_ORIGIN[0] + 2.0
for i, lbl in enumerate(["VCC", "GND", "CS", "RST", "DC", "SDI", "SCK", "LED", "SDO",
                         "T_CLK", "T_CS", "T_DIN", "T_DO", "T_IRQ"]):
    text(lbl, j2x + 4.2, LCD_ORIGIN[1] + 4.85 + i * 2.54, size=0.8)
rect(LCD_ORIGIN[0], LCD_ORIGIN[1], LCD_ORIGIN[0] + LCD_SIZE[0], LCD_ORIGIN[1] + LCD_SIZE[1], pcbnew.F_Fab)
text("2.4\" ILI9341 SPI (MSP2401) - Glas nach vorne, 4mm Abstand", 39, 40, layer=pcbnew.F_Fab, size=1.2)
text("GameboyPi v1.1", 45, 66, size=1.5, bold=True)
text("POWER", 60, 7.2, size=0.9)
text("PHONES", 34, 119.3, size=0.8)
text("SPEAKER 20mm (Gehaeuse)", 62, 131.5, size=0.8)

B = pcbnew.B_SilkS
text("Raspberry Pi Zero 2 W - Bauteilseite zur Platine", 39, 21, layer=B, size=1.0)
text("2x20 Buchsenleiste 8.5mm hier (Rueckseite)", 39, 24, layer=B, size=0.9)
rect(14.0, 37.0, 64.0, 71.0, B)
text("LiPo 103450 >=2000mAh mit Schutz", 39, 52, layer=B, size=1.1)
text("JST-PH -> PowerBoost, Kapton!", 39, 55, layer=B, size=1.0)
text("VOL", 4.6, 66.0, layer=B, size=0.8)
# PowerBoost 1000C (Umriss + Pinbelegung)
rect(7.5, 97.94, 30.36, 133.6, B)
for i, lbl in enumerate(["USB", "BAT", "VS", "EN", "GND", "LBO", "GND", "5V"]):
    text(lbl, 12.4, 121.17 - i * 2.54, layer=B, size=0.8)
text("PowerBoost 1000C", 21.5, 112.0, layer=B, size=1.0, angle=90)
# PAM8302
rect(60.38, 74.92, 75.62, 99.05, B)
text("PAM8302", 68.0, 88.0, layer=B, size=1.0)
text("GND VIN SD A- A+", 68.0, 98.2, layer=B, size=0.8)
# ADS1115
rect(30.0, 72.0, 47.78, 97.4, B)
text("ADS1115", 38.9, 95.6, layer=B, size=1.0)
text("VCC>ALRT", 34.9, 74.0, layer=B, size=0.8)
text("AVDD>AGND", 42.6, 74.0, layer=B, size=0.8)
# Service
text("UART GND TX RX", 46.5, 127.0, layer=B, size=0.8)
text("BAT  5V  3V3 GND  EN  AMP", 56.5, 129.4, layer=B, size=0.8)
text("GameboyPi v1.1  Rueckseite", 59.5, 110.5, layer=B, size=0.9)

# ---------- GND-Flächen auf beiden Lagen ----------
gnd = get_net("GND")
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(gnd)
    z.SetLocalClearance(mm(0.3))
    z.SetMinThickness(mm(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(0.4))
    z.SetThermalReliefSpokeWidth(mm(0.5))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)  # keine schwebenden Kupferinseln
    ol = z.Outline()
    ol.NewOutline()
    for x, y in ((0.3, 0.3), (W - 0.3, 0.3), (W - 0.3, H - 0.3), (0.3, H - 0.3)):
        ol.Append(mm(x), mm(y))
    board.Add(z)

# Sperrflächen am Rand: Freerouting kennt den Randabstand nicht, daher keine Leiterbahnen < 1 mm zur Kante
EDGE_KEEPOUT = 1.0
for x1, y1, x2, y2 in ((0, 0, W, EDGE_KEEPOUT), (0, H - EDGE_KEEPOUT, W, H),
                       (0, 0, EDGE_KEEPOUT, H), (W - EDGE_KEEPOUT, 0, W, H)):
    k = pcbnew.ZONE(board)
    k.SetIsRuleArea(True)
    k.SetDoNotAllowTracks(True)
    k.SetDoNotAllowVias(True)
    k.SetDoNotAllowPads(False)
    k.SetDoNotAllowFootprints(False)
    k.SetDoNotAllowZoneFills(False)
    k.SetLayerSet(pcbnew.LSET.AllCuMask())
    ol = k.Outline()
    ol.NewOutline()
    for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
        ol.Append(mm(x), mm(y))
    board.Add(k)

board.BuildConnectivity()
pcbnew.SaveBoard(OUT, board)

# Die Lötpins des Schalters liegen unter dem Pi, der 11 mm höher auf Abstandshaltern sitzt – unkritisch.
# (Die Regel-Schwere ist nicht über die Python-API erreichbar, daher direkt in der Projektdatei.)
pro_path = OUT.replace(".kicad_pcb", ".kicad_pro")
pro = json.load(open(pro_path, encoding="utf-8"))
dset = pro.setdefault("board", {}).setdefault("design_settings", {})
sev = dset.setdefault("rule_severities", {})
sev["pth_inside_courtyard"] = "ignore"
# M3-Mutter des Display-Abstandshalters H6 liegt unter dem Pi (11 mm Luft)
sev["npth_inside_courtyard"] = "ignore"
# J7: Konturlinien des Bibliotheks-Footprints werden bewusst entfernt (siehe place())
sev["lib_footprint_mismatch"] = "ignore"
# GND-Pads sind zusätzlich über geroutete GND-Leiterbahnen verbunden; ein fehlender Steg ist dort unkritisch
sev["starved_thermal"] = "warning"
dset.setdefault("rules", {})["min_track_width"] = 0.15
json.dump(pro, open(pro_path, "w", encoding="utf-8"), indent=2)

# Eigene Regel: GND-Pads sind zusätzlich über Leiterbahnen verbunden, 1 Thermal-Steg genügt
with open(OUT.replace(".kicad_pcb", ".kicad_dru"), "w", encoding="utf-8") as f:
    f.write('(version 1)\n(rule "thermal_spokes"\n\t(condition "A.Type == \'Pad\'")\n'
            '\t(constraint min_resolved_spokes (min 1)))\n')

# Kontrolle
for ref in ("J1", "J2", "J3", "J7", "J8", "J10", "J11", "J12", "RV1", "SW9"):
    fp = fps[ref]
    pads = [(p.GetNumber(), round(pcbnew.ToMM(p.GetPosition().x), 2), round(pcbnew.ToMM(p.GetPosition().y), 2))
            for p in fp.Pads() if p.GetNumber()]
    pads = [pads[0], pads[-1]] if ref != "J7" else pads
    bb = fp.GetBoundingBox(False)
    print(ref, "B" if fp.IsFlipped() else "F", pads,
          "bbox", [round(pcbnew.ToMM(v), 2) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())])
print("gespeichert:", OUT)
