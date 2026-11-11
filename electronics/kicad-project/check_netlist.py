"""Vergleicht die aus dem Schaltplan exportierte Netzliste mit design.py."""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import PARTS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(os.environ["LOCALAPPDATA"], r"Programs\KiCad\10.0\bin\kicad-cli.exe")
NET = os.path.join(HERE, "build", "GameboyPi.net")
subprocess.run([CLI, "sch", "export", "netlist", "-o", NET, os.path.join(HERE, "GameboyPi.kicad_sch")], check=True)
text = open(NET, encoding="utf-8").read()

got = set()
for chunk in re.split(r"\(net\s*\(code", text[text.index("(nets"):])[1:]:
    name = re.search(r'\(name "([^"]+)"\)', chunk).group(1).lstrip("/")
    for ref, pin in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', chunk):
        if not name.startswith("unconnected") and not ref.startswith("#"):
            got.add((ref, pin, name))
want = {(p["ref"], pin, net) for p in PARTS for pin, net in p["pins"].items()}
print("fehlend im Schaltplan:", sorted(want - got) or "keine")
print("zusätzlich im Schaltplan:", sorted(got - want) or "keine")
if want != got:  # build.ps1 bricht über den Exit-Code ab
    sys.exit("Netzliste weicht von design.py ab")
