---
name: design-change
description: Use when moving, adding, removing or re-wiring a GameboyPi part (button, connector, module, resistor, mounting hole, GPIO) or changing board size. Walks the change through design.py, the case .scad, both builds and the docs so PCB, case and docs stay in sync.
---

# GameboyPi design change

`electronics/kicad-project/design.py` is the single source of truth. The case copies some positions **by hand**, so a change usually touches both.

## 1. Plan
- Find the part in `design.py` (`part("REF", ...)`, `BUTTONS`, `PI_PINS`). Coordinates are in mm, origin top-left, y down, viewed from the front; `side` = F/B.
- Is the part listed under "Bauteil-Positionen (aus design.py)" in `mechanical/cad-source/gameboy_pi_case.scad` (holes, buttons, LED, switch, jack, pot, LCD, PowerBoost, Pi, battery)? If so, the case must change too.
- A GPIO change also affects `software/configuration/config.txt.append`, `battery_monitor.py` and `documentation/wiring.md`.

## 2. Edit
1. Edit `design.py` (plus `make_pcb.py` if silkscreen, keep-outs or DRC exceptions depend on the position).
2. Mirror any position change into the `.scad` variables. Remember case coords = `P(x, y)` of board coords.
3. Run the quick check (seconds, no layout change):
   `& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\python.exe" electronics/kicad-project/make_sch.py; & "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\python.exe" electronics/kicad-project/check_netlist.py`
   This must print `keine` twice.

## 3. Build & verify
- Run the `pcb-build` skill (re-routes the board).
- If the case changed, run the `case-build` skill (collision check).

## 4. Docs
Update whatever is now wrong: `README.md` (tables, risks), `documentation/wiring.md`, `documentation/testing.md` (counts), `bom/bill-of-materials.csv` + `bestellung/2_bauteile/*` if parts changed. Docs are German.
