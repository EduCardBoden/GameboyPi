"""Entflechtet GameboyPi.kicad_pcb mit Freerouting (DSN -> SES) und füllt die GND-Flächen.

Freerouting kennt keinen Randabstand und hält sich nicht immer an die Kontur. Darum:
  * Export mit einer um 1.3 mm eingerückten Kontur,
  * nach dem Import werden Netze mit Bahnen in der 1-mm-Randzone gelöscht und erneut geroutet,
  * Engstellen unter 0.15 mm (Fertigungsminimum mit Reserve) werden auf 0.15 mm verbreitert.
"""
import glob
import os
import re
import shutil
import subprocess
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from design import BOARD_W, BOARD_H, BOARD_R  # noqa: E402

PCB = os.path.join(HERE, "GameboyPi.kicad_pcb")
DSN = os.path.join(HERE, "build", "GameboyPi.dsn")
SES = os.path.join(HERE, "build", "GameboyPi.ses")
FR_JAR = os.path.join(HERE, "..", "..", "tools", "freerouting", "freerouting-2.5.0.jar")


def find_java():
    """Freerouting 2.5 braucht Java >= 25. Reihenfolge: GAMEBOYPI_JAVA, neuestes Microsoft-JDK >= 25, PATH."""
    if os.environ.get("GAMEBOYPI_JAVA"):
        return os.environ["GAMEBOYPI_JAVA"]
    found = []
    for exe in glob.glob(r"C:\Program Files\Microsoft\jdk-*-hotspot\bin\java.exe"):
        version = [int(x) for x in re.findall(r"\d+", exe.split("jdk-")[1].split("-")[0])]
        if version and version[0] >= 25:
            found.append((version, exe))
    if found:
        return max(found)[1]
    return shutil.which("java") or sys.exit("Java 25+ nicht gefunden (Umgebungsvariable GAMEBOYPI_JAVA setzen)")


JAVA = find_java()
EDGE_MARGIN = 1.0
MIN_TRACK = 0.15
os.makedirs(os.path.dirname(DSN), exist_ok=True)
mm = pcbnew.FromMM
passes = sys.argv[1] if len(sys.argv) > 1 else "40"


def swap_outline_for_routing(board):
    """Entfernt Flächen und echte Kontur, setzt die eingerückte Routing-Kontur. Gibt eine Restore-Funktion zurück."""
    zones = list(board.Zones())
    for z in zones:
        board.Remove(z)
    edges = [d for d in board.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
    for d in edges:
        board.Remove(d)
    inset = []

    def seg(*pts, arc=None):
        s = pcbnew.PCB_SHAPE(board)
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1))
        if arc:
            s.SetShape(pcbnew.SHAPE_T_ARC)
            s.SetCenter(pcbnew.VECTOR2I(mm(arc[0]), mm(arc[1])))
            s.SetStart(pcbnew.VECTOR2I(mm(pts[0]), mm(pts[1])))
            s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T), True)
        else:
            s.SetShape(pcbnew.SHAPE_T_SEGMENT)
            s.SetStart(pcbnew.VECTOR2I(mm(pts[0]), mm(pts[1])))
            s.SetEnd(pcbnew.VECTOR2I(mm(pts[2]), mm(pts[3])))
        board.Add(s)
        inset.append(s)

    W, H, R, i = BOARD_W, BOARD_H, BOARD_R, 1.3
    seg(R, i, W - R, i)
    seg(W - i, R, W - i, H - R)
    seg(W - R, H - i, R, H - i)
    seg(i, H - R, i, R)
    seg(W - R, i, arc=(W - R, R))
    seg(W - i, H - R, arc=(W - R, H - R))
    seg(R, H - i, arc=(R, H - R))
    seg(i, R, arc=(R, R))

    def restore():
        for s in inset:
            board.Remove(s)
        for d in edges:
            board.Add(d)
        for z in zones:
            board.Add(z)
    return restore

def freeroute(board):
    if not pcbnew.ExportSpecctraDSN(board, DSN):
        sys.exit("DSN-Export fehlgeschlagen")
    if os.path.exists(SES):
        os.remove(SES)
    r = subprocess.run([JAVA, "-jar", FR_JAR, "--gui.enabled=false", "-de", DSN, "-do", SES,
                        "--router.autorouter.max_passes=" + passes], capture_output=True, text=True, timeout=1800)
    print("\n".join(l for l in r.stdout.splitlines() if "stage completed" in l)[-1500:])
    if not os.path.exists(SES) or not pcbnew.ImportSpecctraSES(board, SES):
        sys.exit("Freerouting/SES-Import fehlgeschlagen")


def in_edge_zone(p, half_width):
    x, y = pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)
    m = EDGE_MARGIN + pcbnew.ToMM(half_width)
    return x < m or y < m or x > BOARD_W - m or y > BOARD_H - m


# Jeder Durchlauf lädt die Platine frisch (SWIG-Objekte werden nach dem SES-Import ungültig)
for attempt in range(4):
    board = pcbnew.LoadBoard(PCB)
    restore = swap_outline_for_routing(board)
    freeroute(board)
    restore()
    # nur die betroffenen Segmente löschen; Freerouting schließt die Lücke im nächsten Durchlauf
    bad = [t for t in board.GetTracks() if t.GetClass() == "PCB_TRACK" and
           (in_edge_zone(t.GetStart(), t.GetWidth() // 2) or in_edge_zone(t.GetEnd(), t.GetWidth() // 2))]
    if bad:
        print("Segmente in der Randzone, route neu:", sorted({t.GetNetname() for t in bad}))
        for t in bad:
            board.Delete(t)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    unrouted = board.GetConnectivity().GetUnconnectedCount(False)
    pcbnew.SaveBoard(PCB, board)
    if unrouted == 0:  # Randzone ist nach dem Löschen frei; alles verbunden (GND ggf. über die Flächen)
        break
else:
    print("WARNUNG: nach 4 Versuchen noch ungeroutete Verbindungen")

board = pcbnew.LoadBoard(PCB)
# fixierte Stichleitungen (make_pcb.py, SW9) entfernen, wenn Freerouting direkt am Pad angeschlossen hat
ends = {}
for t in board.GetTracks():
    pts = [t.GetPosition()] if t.GetClass() == "PCB_VIA" else [t.GetStart(), t.GetEnd()]
    for p in pts:
        ends[(p.x, p.y)] = ends.get((p.x, p.y), 0) + 1
for t in [t for t in board.GetTracks() if t.GetClass() == "PCB_TRACK" and t.IsLocked()]:
    if ends.get((t.GetEnd().x, t.GetEnd().y), 0) <= 1:
        name = t.GetNetname()
        board.Delete(t)
        print("ungenutzte Stichleitung entfernt:", name)
widened = 0
for t in board.GetTracks():
    if t.GetClass() == "PCB_TRACK" and t.GetWidth() < mm(MIN_TRACK):
        t.SetWidth(mm(MIN_TRACK))
        widened += 1

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
board.BuildConnectivity()
pcbnew.SaveBoard(PCB, board)
print("Leiterbahnen:", sum(1 for t in board.GetTracks() if t.GetClass() == "PCB_TRACK"),
      "Vias:", sum(1 for t in board.GetTracks() if t.GetClass() == "PCB_VIA"),
      "verbreitert:", widened,
      "ungeroutet:", board.GetConnectivity().GetUnconnectedCount(False))
