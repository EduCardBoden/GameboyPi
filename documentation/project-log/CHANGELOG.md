# Changelog

## v1.2 – 2026-11-11 (Branch `engineering-v1.2`, Basis-Tag `baseline-v1.1`)

### Elektronik
- `electronics/kicad-project/design.py`: R6/R7 10 kΩ → **47 kΩ** (Lautsprecher ≤ 0,5 W); R10 10 kΩ → **100 kΩ** (LBO ≤ 100 µA)
- `electronics/kicad-project/make_sch.py`: Schriftfeld Rev 1.2, Datum 2026-11-11
- `electronics/kicad-project/make_pcb.py`: Bestückungsdruck „GameboyPi v1.2“, Text „SPEAKER 20mm (im Gehaeuse)“ von den Testpunkt-Pads weg nach (59,5 / 105)
- Generiert und neu geroutet: `GameboyPi.kicad_sch`, `.kicad_pcb`, `electronics/gerber/*`, `electronics/assembly/*`, `electronics/schematics/*.pdf`, `bestellung/1_platine_JLCPCB/GameboyPi_Gerber.zip`

### Software
- `software/configuration/battery_monitor.py`: ADC-Lastkorrektur, `VBAT_CAL`, LBO-Entprellung, `PUD_OFF`, testbare Klasse `Monitor`
- `software/configuration/config.txt.append`: `gpio=20=ip,pn`, Kopf v1.2
- `software/configuration/install.sh`: `set -euo pipefail`, Root-Prüfung, Wiederanlauf, Upgrade v1.1 → v1.2
- neu: `software/tests/test_battery_monitor.py` (7 Tests)

### Werkzeuge
- neu: `tools/check_consistency.py` (36 Prüfungen design.py ↔ .scad ↔ Pi-Software)
- neu: `tools/stl_report.py` (geschlossene Hülle, Maße, Masse)
- `.vscode/tasks.json`: Tasks „Konsistenz prüfen“, „STL-Prüfung“, „Software-Tests“

### Dokumentation
- neu: `documentation/PROJECT_OVERVIEW.md`, `HARDWARE_ARCHITECTURE.md`, `PCB_DESIGN.md`, `MECHANICAL_DESIGN.md`, `FIRMWARE_ARCHITECTURE.md`, `FINAL_BOM.md`, `PURCHASING_COMPARISON.md`, `ASSEMBLY_GUIDE.md`, `TESTING_PLAN.md`, `DEVELOPMENT_ROADMAP.md`
- neu: `documentation/project-log/*` (dieses Log)
- neu: `documentation/final-report/GameBoy_Project_Engineering_Documentation.docx`
- geändert: `README.md` (v1.2, Risiken 2 und 4 neu bewertet, Risiken 15 und 16 neu), `documentation/testing.md`, `wiring.md`, `battery-runtime.md` (gemessene Bahnbreiten), `software/setup-guide.md` (Kalibrierung, Lautstärke), `ARCHITECTURE.md`, `CLAUDE.md`, `bom/bill-of-materials.csv`, `bestellung/2_bauteile/digikey_mouser_bom.csv`, `Einkaufsliste.md`

### Unverändert
- `mechanical/cad-source/gameboy_pi_case.scad` und STLs (keine Maßänderung nötig, Konsistenz bestätigt)
