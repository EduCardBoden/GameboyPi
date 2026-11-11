---
name: pcb-build
description: Rebuild and verify the GameboyPi PCB (schematic, Freerouting autoroute, ERC/DRC, Gerber, BOM, PDFs, STEP). Use after any change to design.py, make_sch.py, make_pcb.py or route.py, or when asked to regenerate manufacturing files.
---

# Rebuild the GameboyPi PCB

**This rewrites tracked files.** Freerouting gives a different layout every run, so only rebuild when the electronics actually changed. Check `git status` first so the diff afterwards is only from the build.

## Run (~3 min, from the repo root)
```
powershell -ExecutionPolicy Bypass -File electronics/kicad-project/build.ps1 *> electronics/kicad-project/build/build.log
```
Run it in the background and wait for the notification. A non-zero exit means a step threw; read the end of `build/build.log`.

## Verify (all must hold)
| Check | Where | Expected |
|---|---|---|
| Netlist matches design.py | build log | `fehlend ... keine`, `zusätzlich ... keine` |
| Routing complete | build log, last `route.py` line | `ungeroutet: 0` |
| ERC | `build/erc.rpt` | `0  Errors 0  Warnings 0` |
| DRC | `build/drc.rpt` | no `; error`, `Found 0 unconnected pads` |
| DRC warnings | `grep -o "^\[[a-z_]*\]" build/drc.rpt \| sort \| uniq -c` | only silk_* / starved_thermal; counts near the table in `documentation/testing.md` |
| Order package | `bestellung/1_platine_JLCPCB/GameboyPi_Gerber.zip` | same hash as `electronics/gerber/GameboyPi_Gerber.zip` |

Known harmless log lines: "Could not add 3D model for J1/RV1" (no STEP model in the KiCad library).

## Afterwards
- Update the DRC warning counts in `documentation/testing.md` if they changed.
- Look at `electronics/assembly/Platine_vorne.png` / `Platine_hinten.png` (Read tool) for anything odd.
- Do not commit unless asked.
