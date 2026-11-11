# Prüfstrategie (v1.2)

Ergebnisse und der vollständige Inbetriebnahme-Messplan stehen in [testing.md](testing.md), das Prüfprotokoll mit Datum in [project-log/TEST_RESULTS.md](project-log/TEST_RESULTS.md).

## Automatisch (bei jeder Änderung)

| Stufe | Werkzeug | Auslöser | Erwartung |
|---|---|---|---|
| Netzliste | `check_netlist.py` | Änderung an `design.py` | keine / keine |
| ERC | `kicad-cli sch erc --severity-all` | PCB-Build | 0 / 0 |
| DRC + Parität | `kicad-cli pcb drc --severity-all --schematic-parity` | PCB-Build | 0 Fehler, 0 unverbunden, ≈ 100 Silk-Warnungen |
| Konsistenz | `tools/check_consistency.py` | Änderung an design.py, .scad oder Pi-Konfiguration | 0 Abweichungen |
| Kollision | `mechanical/cad-source/build.ps1` | Änderung an `.scad` | 0 Kollisionen |
| STL | `tools/stl_report.py` | nach STL-Export | 0 offene Kanten |
| Software | `pytest software/tests` | Änderung an `battery_monitor.py` | alle bestanden |
| Shell | `bash -n install.sh` | Änderung an `install.sh` | ok |

## Manuell vor der Bestellung
- Gerber im JLCPCB-Viewer ansehen (Freerouting-Layout wechselt bei jedem Build)
- Probedruck der Frontschale, Taster und Display einlegen

## Physisch nach dem Aufbau (noch offen)

| Bereich | Prüfung | Bezug |
|---|---|---|
| Versorgung | 5,0–5,3 V an TP2 unter Last, `vcgencmd get_throttled` = 0x0 | testing.md 2.3, 4.1 |
| Abschaltlogik | EN < 0,4 V bei AUS, Halten durch Q2, Abschalten nach Halt | 2.2, 3.1–3.2, 4.7 |
| LBO | Low-Pegel an GPIO20 ≤ 0,6 V bei 3,0 V Akku, Abschaltung nach 15 s | 4.5b |
| Akkumessung | ±0,05 V zum Multimeter, `VBAT_CAL` | 4.3 |
| Audio | ≤ 2,0 V_eff am Lautsprecher, Kopfhörer schaltet ab | 4.5, 4.6 |
| Thermik | 30 min Last < 80 °C | 4.8 |
| Mechanik | Tasten gängig, Display mittig, USB/SD/HDMI erreichbar, Schrauben halten | ASSEMBLY_GUIDE.md |
| Laufzeit | Volllade-Entlade-Zyklus mit Spiel, Zeit messen | battery-runtime.md |
