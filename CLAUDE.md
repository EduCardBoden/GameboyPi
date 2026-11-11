# GameboyPi – instructions for Claude

DIY Game-Boy-Color-style handheld (Pi Zero 2 W). Design is complete and checked by calculation, but **not physically built yet**. Docs are German; keep them German.
Overview: [README.md](README.md) · How the generators fit together: [ARCHITECTURE.md](ARCHITECTURE.md) · Open risks: README "Offene technische Risiken"

## Golden rules

1. **The PCB is generated.** The single source of truth for parts, nets and positions is `electronics/kicad-project/design.py`. Never hand-edit `GameboyPi.kicad_sch` / `.kicad_pcb`, Gerbers or assembly exports. Edit `design.py` (or `make_sch.py` / `make_pcb.py` / `route.py`) and rebuild.
2. **The case is parametric.** Edit `mechanical/cad-source/gameboy_pi_case.scad` and rebuild. Never edit STLs or previews.
3. **`bestellung/` is the order package.** The build scripts copy into it (Gerber zip, STLs, design PNGs). Only the `.md` files and `2_bauteile/*.csv` there are hand-written.
4. **Keep the docs truthful.** If ERC/DRC/collision results change, update `documentation/testing.md`. If a risk changes, update the README risk list.
5. Pi files (`software/configuration/*`) must stay LF (`.gitattributes`).

## Skills & hooks

- `design-change`: move/add/re-wire a part end to end (design.py → .scad → builds → docs)
- `pcb-build` / `case-build`: run and verify the two builds
- Hook `.claude/hooks/guard-generated.js` blocks Edit/Write on generated files (rule 1–3).

## Build & verify

| What | Command (from the repo root) | Duration |
|---|---|---|
| Everything | VS Code `Ctrl+Shift+B` | ~30 min |
| PCB only | `powershell -ExecutionPolicy Bypass -File electronics/kicad-project/build.ps1` | ~3 min |
| Case: collision check + STL + previews | `powershell -ExecutionPolicy Bypass -File mechanical/cad-source/build.ps1` | ~25 min |
| STL only | add `-SkipCheck` | ~5 min |
| Quick netlist check (no layout change) | `& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\python.exe" electronics/kicad-project/check_netlist.py` | seconds |

The PCB build **re-routes the board** with Freerouting. The result differs every run and rewrites tracked files. Run it only when the electronics changed, then check `build/drc.rpt` (0 errors, 0 unconnected) and compare the warning counts with `testing.md`.

Expected results: ERC 0/0, DRC 0 errors (≈105 cosmetic silk warnings), 0 unconnected pads, netlist check "keine/keine", collision report "0 Kollision(en)".

## Toolchain (hard-coded paths)

- KiCad **10.0** in `%LOCALAPPDATA%\Programs\KiCad\10.0`. Run its `python.exe` for all `electronics/kicad-project/*.py` (they import `pcbnew`). The version appears in `build.ps1`, `make_sch.py`, `make_pcb.py`, `check_netlist.py` and `.vscode/*`; change all of them if you upgrade.
- Freerouting 2.5 jar in `tools/freerouting/` (gitignored), Java ≥ 25. `route.py` finds the newest Microsoft JDK ≥ 25 automatically; you can override it with the `GAMEBOYPI_JAVA` env var.
- OpenSCAD **2021.01** (`C:\Program Files\OpenSCAD`), which is slow (CGAL). The collision check runs 8 parallel jobs.
- Logo tracing (`mechanical/cad-source/logo/trace_logo.py`) needs scikit-image + pymupdf. Run it only if the logo image changes.
