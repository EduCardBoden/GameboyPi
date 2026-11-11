"""Gehäuseteile (STL) -> STEP-Volumenkörper mit FreeCAD.

Weg: STL-Netz -> B-Rep-Hülle -> ebene Nachbarfacetten zu Flächen zusammenfassen
(removeSplitter) -> Volumenkörper -> STEP. Prüfung: Körper gültig und geschlossen,
Volumen weicht < 0,5 % vom STL ab.

Ergebnis: maßhaltige Volumenkörper für andere CAD-Programme (Messen, Baugruppe,
Passungsprüfung). Rundungen bleiben facettiert ($fn = 64). Editierbare Quelle bleibt
gameboy_pi_case.scad. Der direkte CSG-Import (FreeCAD OpenSCAD-Workbench) scheitert an
den offset()/circle()-Extrusionen dieses Modells (getestet 11.11.2026, FreeCAD 1.1.4).

Aufruf (Repo-Wurzel, nach dem STL-Export):
  & "$env:LOCALAPPDATA\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" tools/scad_to_step.py
Teile einschränken: Umgebungsvariable GB_PARTS=front,back
"""
import glob
import os

import FreeCAD  # noqa: F401  (initialisiert FreeCAD)
import Mesh
import Part

ROOT = os.getcwd()
STL = os.path.join(ROOT, "mechanical", "stl")
OUT = os.path.join(ROOT, "mechanical", "step")
os.makedirs(OUT, exist_ok=True)
want = [p for p in os.environ.get("GB_PARTS", "").split(",") if p]
files = sorted(glob.glob(os.path.join(STL, "*.stl")))
if want:
    files = [f for f in files if os.path.splitext(os.path.basename(f))[0] in want]

fails = 0
lines = []
for f in files:
    name = os.path.splitext(os.path.basename(f))[0]
    mesh = Mesh.Mesh(f)
    shell = Part.Shape()
    shell.makeShapeFromMesh(mesh.Topology, 0.01)
    shell = shell.removeSplitter()          # koplanare Dreiecke -> eine Fläche
    solids = []
    for sh in shell.Shells:
        s = Part.makeSolid(sh)
        if s.Volume < 0:
            s.reverse()
        solids.append(s)
    body = Part.makeCompound(solids)
    vol = sum(s.Volume for s in solids)
    dev = abs(vol - mesh.Volume) / mesh.Volume * 100
    ok = bool(solids) and body.isValid() and all(s.isClosed() for s in solids) and dev < 0.5
    if ok:
        body.exportStep(os.path.join(OUT, name + ".step"))
    else:
        fails += 1
    lines.append("%-20s Körper %3d  Flächen %6d  gültig %-5s  V %8.1f mm³ (STL %8.1f, Abw. %.3f %%)  %s"
                 % (name, len(solids), len(body.Faces), body.isValid(), vol, mesh.Volume, dev, "ok" if ok else "FEHLER"))

lines.append("Ergebnis: %d von %d Teilen als STEP in mechanical/step/" % (len(files) - fails, len(files)))
report = os.path.join(OUT, "step_report.txt")
with open(report, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")
print("\n".join(lines))
