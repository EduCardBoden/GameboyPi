---
name: case-build
description: Rebuild and verify the GameboyPi OpenSCAD case (collision check of all parts against both shells, STL export, preview renders). Use after any change to gameboy_pi_case.scad, the logo, or part positions shared with design.py.
---

# Rebuild the GameboyPi case

OpenSCAD 2021.01 (CGAL) is slow, so pick the mode that fits:

| Mode | Command (repo root) | Time |
|---|---|---|
| Full: collision check + STLs + previews | `powershell -ExecutionPolicy Bypass -File mechanical/cad-source/build.ps1` | ~25 min |
| STLs + previews only (no geometry near parts changed) | `... build.ps1 -SkipCheck` | ~5 min |
| One part, quick look | `& "C:\Program Files\OpenSCAD\openscad.com" -o $env:TEMP\x.stl -D 'part=\"front\"' mechanical/cad-source/gameboy_pi_case.scad` | 1–3 min |

Always run in the background and wait for the notification.

## Verify
- `mechanical/cad-source/build/collision_report.txt` ends with `Ergebnis: 0 Kollision(en) bei N Bauteilen`. N equals the number of entries in the `.scad` check list (currently 21).
- The build output has no `ERROR` lines (the script filters OpenSCAD output down to ERROR/WARNING/Volumes).
- Look at `mechanical/previews/design_front.png` and `design_back.png` (Read tool). The logo must read correctly from the front and back (not mirrored).
- `bestellung/3_3d_druck/` was refreshed (timestamps).

## Afterwards
If a collision was fixed or a dimension changed, update `documentation/testing.md` (mechanics row) and README risk 5/7 if they're affected.
